# Get external data sets for integration testing and transform them into our format
import os
from pathlib import Path
import requests
import csv
import zipfile
from collections import defaultdict
import numpy as np

class NotImplementedException(Exception):
    pass

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

def wug2anno(input_path, output_path, label_set='1,2,3,4',non_label='-',aggregation_mode='median',preprocessing_mode='raw'):
    '''
    Load WUG-formatted data set, transform it to format of DURel system annotators and export.
    '''        
    print('input_path:', input_path, 'label_set:', label_set, 'non_label:', non_label, 'aggregation_mode:', aggregation_mode, 'preprocessing_mode:', preprocessing_mode)
    uses_all, labels_all = [], []
    normalization_errors = 0
    for condition in ['uses','judgments']:
        for p in Path(input_path+'/data').glob('*/{0}.csv'.format(condition)):

            with open(p, encoding='utf-8') as csvfile: 
                reader = csv.DictReader(csvfile, delimiter='\t',quoting=csv.QUOTE_NONE,strict=True)
                data = [row for row in reader]

            if condition == 'uses':
                output_data = []
                for row in data:
                    row_out = {}
                    row_out['lemma'] = row['lemma']
                    row_out['identifier_system'] = row['identifier']
                    context_raw = row['context']
                    if preprocessing_mode=='raw':
                        row_out['context'] = context_raw
                        row_out['indexes_target_token'] = row['indexes_target_token']
                        row_out['indexes_target_sentence'] = row['indexes_target_sentence']                    
                    elif preprocessing_mode=='normalized':
                        
                        context_tokenized = row['context_tokenized']
                        context_normalized = row['context_normalized']

                        print('context_raw:', [context_raw])
                        print('context_tokenized:', [context_tokenized])
                        print('context_normalized:', [context_normalized])
                        
                        if context_normalized != '':
                            # Catch normalization errors
                            context = context_normalized
                            try:
                                assert len(context_tokenized.split(' ')) == len(context_normalized.split(' '))
                            except AssertionError:
                                #raise AssertionError
                                print('normalization_error')
                                context = context_tokenized
                                normalization_errors += 1
                        else:
                            context = context_tokenized
                            
                        # Catch normalization errors
                        if row['identifier'] == 'beyer_poetik01_1882-7284-11' or row['identifier'] == 'beyer_poetik01_1882-17923-12':
                            row_out['context'] = row['context']
                            row_out['indexes_target_token'] = row['indexes_target_token']
                            row_out['indexes_target_sentence'] = row['indexes_target_sentence']                    
                            output_data.append(row_out)
                            normalization_errors += 1
                            continue
                            
                        # Construct character indices from token indices
                        indexes = row['indexes_target_sentence_tokenized'].split(':')
                        index_start_sentence, index_end_sentence = int(indexes[0]), int(indexes[1])
                        tokens = context.split(' ')
                        index_start = int(np.sum([len(t)+1 for t in tokens[:index_start_sentence]])) if index_start_sentence!=0 else 0
                        index_end = int(np.sum([len(t)+1 for t in tokens[:index_end_sentence]])) if index_end_sentence!=0 else 0
                        index_target = int(row['indexes_target_token_tokenized'])
                        #print(index_target)
                        target_from_tokenized_or_normalized = tokens[index_target]
                        index_target_start = int(np.sum([len(t)+1 for t in tokens[:index_target]])) if index_target!=0 else 0
                        index_target_end = index_target_start+len(target_from_tokenized_or_normalized)
                        #print(index_target_start, index_target_end, )
                        row_out['context'] = context
                        row_out['indexes_target_token'] = str(index_target_start)+':'+str(index_target_end)
                        row_out['indexes_target_sentence'] = str(index_start)+':'+str(index_end)

                        # Check output data
                        context = row_out['context']
                        index_target_start = int(row_out['indexes_target_token'].split(':')[0])
                        index_target_end = int(row_out['indexes_target_token'].split(':')[1])
                        target = context[index_target_start:index_target_end]
                        print('context:', [context])
                        print('context_original:', [row['context']])
                        print('index_target_start, index_target_end:', index_target_start, index_target_end)
                        print('target versus target_from_tokenized_or_normalized: ', [target, target_from_tokenized_or_normalized])
                        # Check that constructed target tokens have desired properties
                        assert 0 <= index_target_start <= len(context)
                        assert 0 <= index_target_end <= len(context)
                        assert len(target) > 0
                        punctuation = [' ', '.', ',', '!', '"', '\'']
                        assert not target[0] in punctuation
                        assert not target[-1] in punctuation                        
                        print('--')
                    else:
                        raise NotImplementedException("No valid reprocessing option provided with:", preprocessing_mode)                        
                    output_data.append(row_out)
                    
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

    # Create instances
    instances_all = [{'id':i,'internal_identifier1':row['internal_identifier1'],'internal_identifier2':row['internal_identifier2'],'label_set':label_set,'non_label':non_label,'lemma':row['lemma']} for i, row in enumerate(labels_all)]       
    
    # Check whether there is a mismatch between number of pairs in gold and instances
    assert len(labels_all) == len(instances_all)
    
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

    print('number of normalization errors:', normalization_errors)        
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
    
def tempowic2anno(input_path, output_path, label_set='1,4',non_label='-'):
    '''
    Load WUG-formatted data set, transform it to format of DURel system annotators and export.
    '''
    print('input_path:', input_path, 'label_set:', label_set, 'non_label:', non_label)
    for condition in ['uses','judgments']:
        for p in Path(input_path+'/data').glob('*/{0}.csv'.format(condition)):

            with open(p, encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile, delimiter='\t',quoting=csv.QUOTE_NONE,strict=True)
                data = [row for row in reader]

            if condition == 'uses':
                output_data = [{'lemma':row['lemma'],'identifier_system':row['identifier'],'context':row['context'],'indexes_target_token':row['indexes_target_token'],'indexes_target_sentence':row['indexes_target_sentence']} for row in data]

            if condition == 'judgments':
                output_data = [{'internal_identifier1':row['identifier1'],'internal_identifier2':row['identifier2'],'label':row['judgment'],'lemma':row['lemma']} for row in data]

            data_output_path = output_path + '/data/{0}/'.format(str(p).split('/')[-2])
            Path(data_output_path).mkdir(parents=True, exist_ok=True)

            if condition == 'judgments':
                # Export labels
                with open(data_output_path + '{0}.csv'.format('labels'), 'w') as f:
                    w = csv.DictWriter(f, output_data[0].keys(), delimiter='\t', quoting = csv.QUOTE_NONE, quotechar='')
                    w.writeheader()
                    w.writerows(output_data)

                # Export instances
                output_data_instances = [{'id':i,'internal_identifier1':row['internal_identifier1'],'internal_identifier2':row['internal_identifier2'],'label_set':label_set,'non_label':non_label,'lemma':row['lemma']} for i, row in enumerate(output_data)]
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

    print('-----')


aggregation_mode='binarize-median'
datasets_path = 'tests/datasets/'
Path(datasets_path).mkdir(parents=True, exist_ok=True)

# testWUG EN (V1.0.0),  DWUG EN (V2.0.1),  DWUG DE (V2.3.0),  DWUG DE (V2.0.1)
sources_wug = [('testwug_en', 'https://zenodo.org/record/7946753/files/testwug_en.zip?download=1','raw'), ('dwug_en','https://zenodo.org/record/7387261/files/dwug_en.zip?download=1','raw'), ('dwug_de','https://zenodo.org/record/7441645/files/dwug_de.zip?download=1','normalized'), ('dwug_sv','https://zenodo.org/record/7389506/files/dwug_sv.zip?download=1','raw')]
for dataset, link, preprocessing_mode in sources_wug:
    r = requests.get(link, allow_redirects=True)
    f = datasets_path + dataset + '.zip'
    open(f, 'wb').write(r.content)

    with zipfile.ZipFile(f) as z:
        z.extractall(path=datasets_path)

    data_path = datasets_path + dataset + '/'
    data_transformed_path = datasets_path + dataset + '_transformed/'
    Path(data_transformed_path).mkdir(parents=True, exist_ok=True)

    # Load, transform and store data set
    wug2anno(input_path=data_path, output_path=data_transformed_path, label_set='1,4',non_label='-',aggregation_mode=aggregation_mode, preprocessing_mode=preprocessing_mode)


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



# Tempowic to anno
# run evonlp2wug.sh first to download data and convert it to wug format
datasets_path = 'tests/datasets/TempoWic/'
for dataset in ["tempowic_train_all", "tempowic_trial_all", "tempowic_validation_all"]:
    data_path = datasets_path + dataset + '/'
    data_transformed_path = datasets_path + dataset + '_transformed/'
    Path(data_transformed_path).mkdir(parents=True, exist_ok=True)

    # Load, transform and store data set
    tempowic2anno(input_path=data_path, output_path=data_transformed_path, label_set='1,4',non_label='-')



