from scipy.stats import spearmanr
from sklearn.metrics import accuracy_score
import pandas as pd
from xl_lexeme import specify_xl_lexeme_annotator
import json
import logging

settings_file_location = "./settings/repository-settings.json"

with open(settings_file_location) as settings_file:
    settings = json.load(settings_file)


def evaluate(custom_dir,custom_filename,usage_dir,thresholds,debug,dataset): # to do: it would be better to specify the metric as input
        annotator = specify_xl_lexeme_annotator(thresholds)
        with open(custom_dir+custom_filename+settings['file_extension'], 'r') as f:
            df = pd.read_csv(f,sep='\t', index_col=False)

            if dataset in ['wic_test','wic_dev','wic_train']: # to do: this seems old code, maybe remove
                #print('we are in wic')
                df.loc[df['judgment'] == 1, 'judgment'] = 'F'
                df.loc[df['judgment'] == 4, 'judgment'] = 'T'

            df_sorted_pred = df.sort_values(['identifier1','identifier2'])
            predicted_values = df_sorted_pred['judgment']
        #with open(usage_dir+'judgments.csv','r') as f:
        with open(usage_dir+'labels.csv','r') as f:
            df = pd.read_csv(f,sep='\t', index_col=False)

            if dataset  in ['testwug_en_transformed_median','testwug_en_transformed_binarize-median']: # to do: Do we need this condition?

                df.loc[df['label'] == 2, 'label'] = 1
                df.loc[df['label'] == 3, 'label'] = 4
            df_sorted_gold = df.sort_values(['identifier1','identifier2'])
            #gold_values = df_sorted_gold['judgment']
            gold_values = df_sorted_gold['label']
        #print(gold_values,predicted_values)
        #print(usage_directory)
        assert len(predicted_values)==len(gold_values)

        if annotator in ["XL-Lexeme-Binary"]:
            accuracy = round(accuracy_score(gold_values, predicted_values),3)
            print("Accuracy:",round(accuracy,3))
        else:
            accuracy = 'NA'
        correlation, p_value = spearmanr(gold_values, predicted_values)
        #print(predicted_values)
        #print('Corr:',round(correlation,3),'P-Value:',round(p_value,3))
        save_detailed_results(df_sorted_gold,df_sorted_pred,usage_dir,custom_dir,dataset,annotator,accuracy,correlation,p_value,debug)
        return (accuracy,correlation,p_value)

#def print_results(custom_dir,custom_filename,usage_dir):
def save_detailed_results(df_sorted_gold,df_sorted_pred,usage_dir,custom_dir,dataset,annotator,accuracy,correlation,p_value,debug):
    if debug:
        logging.basicConfig(format=settings['log_formatting'], level=logging.DEBUG)
        logging.info("Debug mode is on.")
        logging.info(f"Annotator: '{annotator}'")
        logging.info(f"Accuracy: '{accuracy}'")
        logging.info(f"Spearmanr correlation: '{correlation}'")
        logging.info(f"Spearmanr p,value: '{p_value}'")

    #print(usage_dir)

    output_df =pd.DataFrame([dict(zip(['accuracy','correlation','p-value'],[accuracy,round(correlation,3),p_value]))])
    output_df.to_csv(custom_dir+dataset+'-'+annotator+'-output.csv',index=False,sep='\t')
    '''
    with open(usage_dir+'uses.csv','r') as f:
        df_uses = pd.read_csv(f,sep='\t', quoting=3)
    #print('\t'.join(['id1','id2','prediction','gold']))
    columns = ['Identifier1', 'Identifier2', 'Prediction','Gold']
    results_df = pd.DataFrame(columns=columns)
    for index, row in df_sorted_pred.iterrows():
            #try:
            id1 = row['identifier1']
            id2 = row['identifier2']
            #print(id1,id2)
            #print(df_uses.loc[(df_uses['identifier_system'] == id2)])
            extracted_value = df_sorted_gold.loc[(df_sorted_gold['identifier1'] == id1) & (df_sorted_gold['identifier2'] == id2)].values[0]  # Extract value from df2 based on 'B' column
            extracted_use1 = df_uses.loc[(df_uses['identifier_system'] == id1)].values[0]  # Extract value from df2 based on 'B' column
            extracted_use2 = df_uses.loc[(df_uses['identifier_system'] == id2)].values[0]  # Extract value from df2 based on 'B' column
            values = [id1+':'+extracted_use1[2],id2+':'+extracted_use2[2],row['judgment'],extracted_value[2]]
            #row = {'Column1': value[0], 'Column2': value[1], 'Column3': value[2]}
            row_data = dict(zip(columns, values))
            row_data = pd.DataFrame([row_data])
            print(id1+':'+extracted_use1[2],id2+':'+extracted_use2[2],row['label'],extracted_value[3])
            results_df = pd.concat([results_df, row_data], ignore_index=True)
            results_df = results_df.append(row_data, ignore_index=True)
            #except:
            #continue
    results_df.to_csv(custom_dir+dataset+'-'+annotator+'-output-labels.csv', index=False,sep='\t')
    '''
