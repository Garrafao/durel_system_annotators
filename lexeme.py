import torch
from model import Model
from sklearn.preprocessing import StandardScaler
from scipy.spatial.distance import cosine
import sys
import pandas as pd
import numpy as np
from WordTransformer import WordTransformer
from InputExample import InputExample
import ast


def make_inference_for_dataset(path_of_dataset,subword_aggregation,prediction_type,thresholds):
    '''use GPU if possible'''
    # If there's a GPU available...
    if torch.cuda.is_available():

        # Tell PyTorch to use the GPU.
        device = torch.device("cuda")

        print('There are %d GPU(s) available.' % torch.cuda.device_count())

        print('We will use the GPU:', torch.cuda.get_device_name(0))

    # If not...
    else:
        print('No GPU available, using the CPU instead.')
        device = torch.device("cpu")
    left_sentnece_and_token_index, right_sentnece_and_token_index = get_left_rigt_sentences_and_token_index(path_of_dataset)

    # comment/uncomment the following 3  lines as the WordTransformer module is not executing successfully because of installation issue with the sqlite3 on server for the moment i am computing embeddings on my local machine and copying the embeddings in the temp folder and loading them here

    model = WordTransformer('pierluigic/xl-lexeme')
    #save_embeddings_lexeme(device, left_sentnece_and_token_index, './temp/token_embeddings_left.npy', model,subword_aggregation)
    #save_embeddings_lexeme(device, right_sentnece_and_token_index, './temp/token_embeddings_right.npy', model,subword_aggregation)

    #embeddings_left = np.load('./temp/token_embeddings_left.npy')

    #embeddings_right = np.load('./temp/token_embeddings_right.npy')

    embeddings_left = compute_embeddings_lexeme(device, left_sentnece_and_token_index, model,subword_aggregation)
    embeddings_right = compute_embeddings_lexeme(device, right_sentnece_and_token_index, model,subword_aggregation)


    #t>0.5 == 1 and 0 otherwise for pierligue model the threshold
    cls_list = []
    for (l,r) in zip(embeddings_left,embeddings_right):
        #cls_list.append(cosine(l, r)) # for cosine distance
        cls_list.append(1-cosine(l, r)) # for cosine similarity

    # similarity to labels
    if prediction_type == 'label':
        assert len(thresholds) == 3, "Thresholds list must have exactly 3 values"

        for index, s in enumerate(cls_list):
            if s <= thresholds[0]:
                cls_list[index] = 1
            elif thresholds[0] < s <= thresholds[1]:
                cls_list[index] = 2
            elif thresholds[1] < s <= thresholds[2]:
                cls_list[index] = 3
            else:
                cls_list[index] = 4

    return cls_list
    '''
    if prediction_type == 'label':
        assert len(thresholds) == 4
        for index, s in enumerate(cls_list):
            if s <= 0.5:
                cls_list[index] = 1
            else:
                cls_list[index] = 4
    return cls_list'''

def compute_embeddings_lexeme(device, sentnece_and_token_index, model,subword_aggregation):

    token_embeddings_output = list()
    for i,(sen,idx) in enumerate(sentnece_and_token_index):
        print("Sentence being processed:  "+str(i))
        idx_tuple = ast.literal_eval(idx)

        #print("Sentence being processed: "+ sen)
        examples = InputExample(texts='"'+sen+'"', positions=[idx_tuple[0],idx_tuple[1]])
        outputs = model.encode(examples)

        token_embeddings_output.append(outputs)
        #print(sen,idx,outputs)
    #print(token_embeddings_output)
    token_embeddings_output = np.array(token_embeddings_output)
    return token_embeddings_output


def save_embeddings_lexeme(device, sentnece_and_token_index, saving_path, model,subword_aggregation):

    print("enter save_embeddings function")

    token_embeddings_output = list()
    for (sen,idx) in sentnece_and_token_index:
        idx_tuple = ast.literal_eval(idx)
        examples = InputExample(texts='"'+sen+'"', positions=[idx_tuple[0],idx_tuple[1]])
        outputs = model.encode(examples)
        #print('outputs',outputs)

        token_embeddings_output.append(outputs)
        #print(sen,idx,outputs)

    token_embeddings_output = np.array(token_embeddings_output)
    np.save(saving_path, token_embeddings_output)

def get_left_rigt_sentences_and_token_index(path_of_dataset):
    df = pd.read_csv(path_of_dataset, delimiter="\t",header=None,
                    names=["word", "sentence_left", "token_index_of_sentence_left", "sentence_right", "token_index_of_sentence_right"], quoting = 3)
    sentences_left = df.sentence_left.tolist()
    token_index_of_sentence_left = df.token_index_of_sentence_left.tolist()
    sentences_right = df.sentence_right.tolist()
    token_index_of_sentence_right = df.token_index_of_sentence_right.tolist()

    return (zip(sentences_left,token_index_of_sentence_left),zip(sentences_right,token_index_of_sentence_right))

if __name__ == "__main__":
    subword_aggregation = "average"
    thresholds = [0.2,0.4,0.6]
    make_inference_for_dataset('./temp/instances_with_token_index.csv',subword_aggregation,thresholds)
