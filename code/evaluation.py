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
                df.loc[df['judgment'] == 2, 'judgment'] = 'F'
                df.loc[df['judgment'] == 3, 'judgment'] = 'T'

            df_sorted_pred = df.sort_values(['identifier1','identifier2'])
            predicted_values = df_sorted_pred['judgment']
        #with open(usage_dir+'judgments.csv','r') as f:
        with open(usage_dir+'labels.csv','r') as f:
            df = pd.read_csv(f,sep='\t', index_col=False)

            if dataset  in ['testwug_en_transformed_binarize-median']: # to do: Do we need this condition?

                df.loc[df['label'] == 2, 'label'] = 1
                df.loc[df['label'] == 3, 'label'] = 4
            df_sorted_gold = df.sort_values(['identifier1','identifier2'])
            gold_values = df_sorted_gold['label']
            #print(type(gold_values)
        assert len(predicted_values)==len(gold_values)

        if annotator in ["XL-Lexeme-Binary"]:
            accuracy = round(accuracy_score(gold_values, predicted_values),3)
            print("Accuracy:",round(accuracy,3))
        else:
            accuracy = 'NA'
        correlation, p_value = spearmanr(gold_values, predicted_values)
        save_detailed_results(df_sorted_gold,df_sorted_pred,usage_dir,custom_dir,dataset,annotator,accuracy,correlation,p_value,debug)
        return (accuracy,correlation,p_value)


def save_detailed_results(df_sorted_gold,df_sorted_pred,usage_dir,custom_dir,dataset,annotator,accuracy,correlation,p_value,debug):
    if debug:
        logging.basicConfig(format=settings['log_formatting'], level=logging.DEBUG)
        logging.info("Debug mode is on.")
        logging.info(f"Annotator: '{annotator}'")
        logging.info(f"Accuracy: '{accuracy}'")
        logging.info(f"Spearmanr correlation: '{correlation}'")
        logging.info(f"Spearmanr p,value: '{p_value}'")


    output_df =pd.DataFrame([dict(zip(['Annotator','Data','accuracy','correlation','p-value'],[annotator,dataset, accuracy,round(correlation,3),p_value]))])
    output_df.to_csv(custom_dir+dataset+'-'+annotator+'-output.csv',index=False,sep='\t')
