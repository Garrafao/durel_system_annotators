# Get external data sets for integration testing and transform them into our format
import os
from pathlib import Path
import requests
import csv
import zipfile
from collections import defaultdict
import numpy as np

def aggregate_wug(judgments, aggregation_mode='binarize-median'):
    '''
    Load WUG-formatted list of judgments as list of dictionaries and aggregate.
    '''        
    # Ignores order, maps all instances with median judgment below 2.5 to 1 and above or equal 2.5 to 4
    if aggregation_mode == 'binarize-median':
        pair2judgments = defaultdict(lambda: [])
        for row in judgments:
           judgment = float(row['judgment'])
           if judgment != 0.0: # exclude 'cannot decide' judgments
            pair2judgments[frozenset((row['identifier1'],row['identifier2']))].append(judgment) 
        pair2label = {tuple(pair):np.median(judgments) for pair, judgments in pair2judgments.items()} # aggregate with median
        pair2label = {pair:1 if label<2.5 else 4 for pair, label in pair2label.items()} # binarize

    # Ignores order, takees median of judgments as label (special case: will not chaange judgment if there is only one) 
    if aggregation_mode == 'median':
        pair2judgments = defaultdict(lambda: [])
        for row in judgments:
           judgment = float(row['judgment'])
           if judgment != 0.0: # exclude 'cannot decide' judgments
            pair2judgments[frozenset((row['identifier1'],row['identifier2']))].append(judgment) 
        pair2label = {tuple(pair):np.median(judgments) for pair, judgments in pair2judgments.items()} # aggregate with median

    return pair2label

def wug2anno(input_path, output_path, label_set='1,2,3,4',non_label='-',aggregation_mode='median'):
    '''
    Load WUG-formatted data set, transform it to format of DURel system annotators and export.
    '''        
    print('input_path:', input_path, 'label_set:', label_set, 'non_label:', non_label, 'aggregation_mode:', aggregation_mode)
    uses_all, labels_all, instances_all = [], [], []
    for condition in ['uses','judgments']:
        for p in Path(input_path+'/data').glob('*/{0}.csv'.format(condition)):

            with open(p, encoding='utf-8') as csvfile: 
                reader = csv.DictReader(csvfile, delimiter='\t',quoting=csv.QUOTE_NONE,strict=True)
                data = [row for row in reader]

            if condition == 'uses':
                output_data = [{'lemma':row['lemma'],'identifier_system':row['identifier'],'context':row['context'],'indexes_target_token':row['indexes_target_token'],'indexes_target_sentence':row['indexes_target_sentence']} for row in data]
                uses_all += output_data
            if condition == 'judgments':
                lemma = data[0]['lemma'] # infer lemma from first row
                pair2label = aggregate_wug(data, aggregation_mode=aggregation_mode)
                output_data = [{'internal_identifier1':id1,'internal_identifier2':id2,'label':l,'lemma':lemma} for (id1, id2), l in pair2label.items()]
                labels_all += output_data

            data_output_path = output_path + '/data_split/{0}/'.format(str(p).split('/')[-2])
            Path(data_output_path).mkdir(parents=True, exist_ok=True)

            if condition == 'judgments':
                # Export labels
                with open(data_output_path + '{0}.csv'.format('labels'), 'w') as f:  
                    w = csv.DictWriter(f, output_data[0].keys(), delimiter='\t', quoting = csv.QUOTE_NONE, quotechar='')
                    w.writeheader()
                    w.writerows(output_data)

                # Export instances
                output_data_instances = [{'id':i,'internal_identifier1':row['internal_identifier1'],'internal_identifier2':row['internal_identifier2'],'label_set':label_set,'non_label':non_label,'lemma':row['lemma']} for i, row in enumerate(output_data)]
                instances_all += output_data_instances
                with open(data_output_path + '{0}.csv'.format('instances'), 'w') as f:  
                    w = csv.DictWriter(f, output_data_instances[0].keys(), delimiter='\t', quoting = csv.QUOTE_NONE, quotechar='')
                    w.writeheader()
                    w.writerows(output_data_instances)
                    
                # Check whether there is a mismatch between number of pairs in gold and instances
                assert len(output_data) == len(output_data_instances)
            else:            
                # Export uses
                with open(data_output_path + '{0}.csv'.format(condition), 'w') as f:  
                    w = csv.DictWriter(f, output_data[0].keys(), delimiter='\t', quoting = csv.QUOTE_NONE, quotechar='')
                    w.writeheader()
                    w.writerows(output_data)
    
    # Check identifier uniqueness
    ids = [row['identifier_system'] for row in uses_all]
    assert len(ids) == len(set(ids))
    
    # Export concatenated data 
    data_output_path = output_path + '/data/{0}/'.format('all')
    Path(data_output_path).mkdir(parents=True, exist_ok=True)
    
    for condition, output_data in [('uses',uses_all),('labels',labels_all), ('instances',instances_all)]:
        with open(data_output_path + '{0}.csv'.format(condition), 'w') as f:  
            w = csv.DictWriter(f, output_data[0].keys(), delimiter='\t', quoting = csv.QUOTE_NONE, quotechar='')
            w.writeheader()
            w.writerows(output_data)
                    
    print('-----')
      
          
               
def wic2anno(input_path, output_path, label_set='1,2,3,4',non_label='-'):
    '''
    Load WiC data set, transform it to format repository format and export.
    '''
    print('input_path:', input_path, 'label_set:', label_set, 'non_label:', non_label)
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
                identifier_strict = row['lemma']+'%%'+indexes_target_token+'%%'+context
                #identifier_relaxed = lemma+'-'+str(j) # not needed now
                identifier2use[identifier_strict]={'lemma':lemma,'identifier_system':identifier_strict,'context':context,'indexes_target_token':indexes_target_token,'indexes_target_sentence':indexes_target_sentence}
                #print(context, context[indexes_target_token_start:indexes_target_token_end], context[0:len(context)])
                lemmas.append(lemma)
                pair.append(identifier_strict)
                #print(pair)
                j+=1
            #print('--')
            pair.append(lemma)
            pairs.append(tuple(pair))

        #print(list(identifier2use.values())[0])
        print('total number of processed sentences versus number of extracted unique sentences:', j, len(identifier2use.keys()))

        lemmas = list(set(lemmas))
        uses = list(identifier2use.values())

        #for lemma in lemmas:
        #    data_output_path = output_path + '/data/{0}/'.format(lemma)

        datatype='uses'

        data_output_path = output_path + '{0}/data/{1}/'.format(split,'all')
        Path(data_output_path).mkdir(parents=True, exist_ok=True)

        # Export data
        with open(data_output_path + '{0}.csv'.format(datatype), 'w') as f:  
            w = csv.DictWriter(f, uses[0].keys(), delimiter='\t', quoting = csv.QUOTE_NONE, quotechar='')
            w.writeheader()
            w.writerows(uses)

        # Load gold annotations
        condition='gold'
        with open(input_path + split + '/{0}.{1}.txt'.format(split, condition), encoding='utf-8') as csvfile: 
            reader = csv.DictReader(csvfile, fieldnames=["label"], delimiter='\t',quoting=csv.QUOTE_NONE,strict=True)
            data = [row for row in reader]

        labels = [{'internal_identifier1':identifier1,'internal_identifier2':identifier2,'label':data[i]['label'],'lemma':lemma} for (identifier1, identifier2, lemma) in pairs]

        datatype='labels'

        print('number of gold labels:', len(labels))

        # Export data
        with open(data_output_path + '{0}.csv'.format(datatype), 'w') as f:  
            w = csv.DictWriter(f, labels[0].keys(), delimiter='\t', quoting = csv.QUOTE_NONE, quotechar='')
            w.writeheader()
            w.writerows(labels)

        instances = [{'id':i,'internal_identifier1':identifier1,'internal_identifier2':identifier2,'label_set':label_set,'non_label':non_label,'lemma':lemma} for i, (identifier1, identifier2, lemma) in enumerate(pairs)]

        print('number of annotation instances:', len(instances))

        datatype='instances'

        # Export data
        with open(data_output_path + '{0}.csv'.format(datatype), 'w') as f:  
            w = csv.DictWriter(f, instances[0].keys(), delimiter='\t', quoting = csv.QUOTE_NONE, quotechar='')
            w.writeheader()
            w.writerows(instances)

        # Check whether there is a mismatch between identifiers in uses and instances
        #print(set([identifier for pair in pairs for identifier in pair[:3]]))
        assert set([row['identifier_system'] for row in uses]) == set([identifier for pair in pairs for identifier in pair[:2]])
    print('-----')


aggregation_mode='binarize-median'
datasets_path = 'tests/datasets/'
Path(datasets_path).mkdir(parents=True, exist_ok=True)

# testWUG EN (V1.0.0),  DWUG EN (V2.0.1),  DWUG DE (V2.3.0),  DWUG DE (V2.0.1)
sources_wug = [('testwug_en', 'https://zenodo.org/record/7946753/files/testwug_en.zip?download=1'), ('dwug_en','https://zenodo.org/record/7387261/files/dwug_en.zip?download=1'), ('dwug_de','https://zenodo.org/record/7441645/files/dwug_de.zip?download=1'), ('dwug_sv','https://zenodo.org/record/7389506/files/dwug_sv.zip?download=1')]
for dataset, link in sources_wug:
    r = requests.get(link, allow_redirects=True)
    f = datasets_path + dataset + '.zip'
    open(f, 'wb').write(r.content)

    with zipfile.ZipFile(f) as z:
        z.extractall(path=datasets_path)

    data_path = datasets_path + dataset + '/'
    data_transformed_path = datasets_path + dataset + '_transformed/'
    Path(data_transformed_path).mkdir(parents=True, exist_ok=True)

    # Load, transform and store data set
    wug2anno(input_path=data_path, output_path=data_transformed_path, label_set='1,4',non_label='-',aggregation_mode=aggregation_mode)


# WiC data set (WUG version)
dataset = 'https://pilehvar.github.io/wic/package/WiC_dataset.zip'
r = requests.get(dataset, allow_redirects=True)
f = datasets_path + 'WiC_dataset.zip'
open(f, 'wb').write(r.content)

wic_path = datasets_path + 'WiC_dataset/'
Path(wic_path).mkdir(parents=True, exist_ok=True)

with zipfile.ZipFile(f) as z:
    z.extractall(path=wic_path)

wic_transformed_path = datasets_path + 'WiC_dataset_transformed/'

# Load, transform and store data set (for dev, train, test)
wic2anno(input_path=wic_path, output_path=wic_transformed_path, label_set='F,T',non_label='-')


