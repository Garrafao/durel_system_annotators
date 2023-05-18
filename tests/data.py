# Get external data sets for integration testing and transform them into our format
import os
from pathlib import Path
import requests
import csv
import subprocess


def wug2anno(input_path, output_path, label_set='1,2,3,4'):
    '''
    Load WUG-formatted data set, transform it to format of DURel system annotators and export.
    '''        
    for condition in ['uses','instances','judgments']:
        for p in Path(input_path+'/data').glob('*/{0}.csv'.format(condition)):

            with open(p, encoding='utf-8') as csvfile: 
                reader = csv.DictReader(csvfile, delimiter='\t',quoting=csv.QUOTE_NONE,strict=True)
                data = [row for row in reader]

            if condition == 'uses':
                data = [{'lemma':row['lemma'],'identifier_system':row['identifier'],'context':row['context'],'indexes_target_token':row['indexes_target_token'],'indexes_target_sentence':row['indexes_target_sentence']} for row in data]
            if condition == 'instances':
                data = [{'id':i,'internal_identifier1':row['identifier1'],'internal_identifier2':row['identifier2'],'label_set':label_set,'non_label':'-','lemma':row['lemma']} for i, row in enumerate(data)]

            if condition == 'judgments':
                data = [{'internal_identifier1':row['identifier1'],'internal_identifier2':row['identifier2'],'annotator':row['annotator'],'judgment':row['judgment'],'comment':row['comment'],'lemma':row['lemma']} for row in data]

            data_output_path = output_path + '/data/{0}/'.format(str(p).split('/')[-2])
            Path(data_output_path).mkdir(parents=True, exist_ok=True)
            
            # Export data
            with open(data_output_path + '{0}.csv'.format(condition), 'w') as f:  
                w = csv.DictWriter(f, data[0].keys(), delimiter='\t', quoting = csv.QUOTE_NONE, quotechar='')
                w.writeheader()
                w.writerows(data)
               
def wic2wug(input_path, output_path):
    '''
    Load WiC data set, transform it to format WUG format and export.
    '''
    for split in ['dev', 'train', 'test']:

        print('split:', split)

        # Load use pairs
        condition='data'
        with open(input_path + split + '/{0}.{1}.txt'.format(split, condition), encoding='utf-8') as csvfile: 
            reader = csv.DictReader(csvfile, fieldnames=["lemma", "pos", "indices", "sent1", "sent2"], delimiter='\t',quoting=csv.QUOTE_NONE,strict=True)
            data = [row for row in reader]

        identifier2use = {}
        pairs = []
        lemmas = []
        j = 0
        for row in data:
            pair = []
            for i in [0, 1]:
                lemma = row['lemma']
                id = int(row['indices'].split('-')[i])
                context = row['sent{0}'.format(i+1)]
                context_previous = ' '.join(context.split(' ')[:id])
                if len(context_previous)>0:
                    indexes_target_token_start = len(context_previous)+1
                else:
                    indexes_target_token_start = len(context_previous)
                target_token = context.split(' ')[id]
                indexes_target_token_end = indexes_target_token_start + len(target_token)
                indexes_target_token = '{0}:{1}'.format(indexes_target_token_start,indexes_target_token_end)
                indexes_target_sentence = '0:{0}'.format(len(context))
                identifier_strict = row['lemma']+'\t'+indexes_target_token+'\t'+context
                identifier_relaxed = lemma+'-'+str(j)
                identifier2use[identifier_strict]={'lemma':lemma,'identifier':identifier_relaxed,'description':'','date':'','grouping':'1','context':context,'indexes_target_token':indexes_target_token,'indexes_target_sentence':indexes_target_sentence}
                #print(context, context[indexes_target_token_start:indexes_target_token_end], context[0:len(context)])
                lemmas.append(lemma)
                pair.append(identifier_relaxed)
                #print(pair)
                j+=1
            #print('--')
            pair.append(lemma)
            pairs.append(tuple(pair))

        #print(list(identifier2use.values())[0])
        print('total number of processed sentences versus number of extracted unique sentences:', j, len(identifier2use.keys()))

        lemmas = list(set(lemmas))
        data = list(identifier2use.values())

        #for lemma in lemmas:
        #    data_output_path = output_path + '/data/{0}/'.format(lemma)

        datatype='uses'

        data_output_path = output_path + '{0}/data/{1}/'.format(split,'all')
        Path(data_output_path).mkdir(parents=True, exist_ok=True)

        # Export data
        with open(data_output_path + '{0}.csv'.format(datatype), 'w') as f:  
            w = csv.DictWriter(f, data[0].keys(), delimiter='\t', quoting = csv.QUOTE_NONE, quotechar='')
            w.writeheader()
            w.writerows(data)

        # Load gold annotations
        condition='gold'
        with open(input_path + split + '/{0}.{1}.txt'.format(split, condition), encoding='utf-8') as csvfile: 
            reader = csv.DictReader(csvfile, fieldnames=["judgment"], delimiter='\t',quoting=csv.QUOTE_NONE,strict=True)
            data = [row for row in reader]

        data = [{'identifier1':identifier1,'identifier2':identifier2,'annotator':'gold','judgment':data[i]['judgment'],'comment':'','lemma':lemma} for i, (identifier1, identifier2, lemma) in enumerate(pairs)]

        datatype='judgments'

        print('number of gold judgments:', len(data))

        # Export data
        with open(data_output_path + '{0}.csv'.format(datatype), 'w') as f:  
            w = csv.DictWriter(f, data[0].keys(), delimiter='\t', quoting = csv.QUOTE_NONE, quotechar='')
            w.writeheader()
            w.writerows(data)

        data = [{'lemma':lemma,'identifier1':identifier1,'identifier2':identifier2} for (identifier1, identifier2, lemma) in pairs]

        print('number of annotation instances:', len(data))

        datatype='instances'

        # Export data
        with open(data_output_path + '{0}.csv'.format(datatype), 'w') as f:  
            w = csv.DictWriter(f, data[0].keys(), delimiter='\t', quoting = csv.QUOTE_NONE, quotechar='')
            w.writeheader()
            w.writerows(data)
                    

datasets_path = 'tests/datasets/'
Path(datasets_path).mkdir(parents=True, exist_ok=True)

# testWUG EN (V1.0.0)
dataset = 'https://zenodo.org/record/7946753/files/testwug_en.zip?download=1'
r = requests.get(dataset, allow_redirects=True)
f = datasets_path + 'testwug_en.zip'
open(f, 'wb').write(r.content)

import zipfile
with zipfile.ZipFile(f) as z:
    z.extractall(path=datasets_path)

testwug_en_path = datasets_path + 'testwug_en/'
testwug_en_transformed_path = datasets_path + 'testwug_en_transformed/'
Path(testwug_en_transformed_path).mkdir(parents=True, exist_ok=True)

# Load, transform and store data set
wug2anno(input_path=testwug_en_path, output_path=testwug_en_transformed_path, label_set='1,2,3,4')


# WiC data set (WUG version)
dataset = 'https://pilehvar.github.io/wic/package/WiC_dataset.zip'
r = requests.get(dataset, allow_redirects=True)
f = datasets_path + 'WiC_dataset.zip'
open(f, 'wb').write(r.content)

wic_path = datasets_path + 'WiC_dataset/'
Path(wic_path).mkdir(parents=True, exist_ok=True)

import zipfile
with zipfile.ZipFile(f) as z:
    z.extractall(path=wic_path)

wic_wug_path = datasets_path + 'WiC_dataset_wug/'

# Load, transform and store data set in WUG format (for dev, train, test)
wic2wug(wic_path, wic_wug_path)

wic_wug_transformed_path = datasets_path + 'WiC_dataset_wug_transformed/'

# Load, transform and store data set
for split in ['dev', 'train', 'test']:
    Path(wic_wug_transformed_path+split).mkdir(parents=True, exist_ok=True)
    wug2anno(input_path=wic_wug_path+split, output_path=wic_wug_transformed_path+split, label_set='F,T')


