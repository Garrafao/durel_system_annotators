# Get external data sets for integration testing and transform them into our format
import os
from pathlib import Path
import requests
import csv

def wug2anno(input_path, output_path):
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
                data = [{'id':i,'internal_identifier1':row['identifier1'],'internal_identifier2':row['identifier2'],'label_set':'1,2,3,4','non_label':'-','lemma':row['lemma']} for i, row in enumerate(data)]

            if condition == 'judgments':
                data = [{'internal_identifier1':row['identifier1'],'internal_identifier2':row['identifier2'],'annotator':row['annotator'],'judgment':row['judgment'],'comment':row['comment'],'lemma':row['lemma']} for row in data]

            data_output_path = output_path + '/data/{0}/'.format(str(p).split('/')[-2])
            Path(data_output_path).mkdir(parents=True, exist_ok=True)
            
            # Export data
            with open(data_output_path + '{0}.csv'.format(condition), 'w') as f:  
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
wug2anno(input_path=testwug_en_path, output_path=testwug_en_transformed_path)




