"""some helper functions"""
import torch, pandas as pd
from typing import List

def get_sentences_from_dataset(path_of_dataset):
    df = pd.read_csv(path_of_dataset, delimiter="\t",header=None, 
                    names=["word", "sentence_left", "token_index_of_sentence_left", "sentence_right", "token_index_of_sentence_right"])
    sentences_left = df.sentence_left.tolist()
    sentences_right = df.sentence_right.tolist()
    # print(df.sample)
    word_count_left = df.sentence_left.str.split(" ").str.len()
    word_count_right = df.sentence_right.str.split(" ").str.len()
    sentence_maximum_length = max(word_count_left.max(), word_count_right.max())
    print("maximum sentence length of the dataset " + path_of_dataset.split("/")[-1] + " is: " + str(sentence_maximum_length))
    # print(df.sentence_left[word_count_left.idxmax()])
    # print(df.sentence_right[word_count_right.idxmax()])
    # print(word_count_left.idxmax())
    # print(word_count_right.idxmax())
    return sentences_left, sentences_right

from collections import defaultdict
def get_index_of_duplicates(seq):
    tally = defaultdict(list)
    for i,item in enumerate(seq):
        if (item != None):
          tally[item].append(i + 1)
    tally = dict(tally)
    # for key in tally.copy():
    #   if len(tally[key]) == 1:
    #     del tally[key]
    return tally

def get_max_sentence_length_of_a_dataset_by_tokenizer(tokenizer, path_of_dataset):
    df = pd.read_csv(path_of_dataset, delimiter="\t",header=None, 
                    names=["word", "sentence_left", "token_index_of_sentence_left", "sentence_right", "token_index_of_sentence_right"])
    sentences_left = df.sentence_left.tolist()
    sentences_right = df.sentence_right.tolist()

    max_len = 0
    # For every sentence...
    for sent in sentences_left + sentences_right:

        # Tokenize the text and add `[CLS]` and `[SEP]` tokens.
        input_ids = tokenizer.encode(sent, add_special_tokens=True)

        # Update the maximum sentence length.
        max_len = max(max_len, len(input_ids))
    print('Max sentence length of whole dataset by tokenizer is:', max_len)

from transformers import BertTokenizerFast, XLMRobertaTokenizerFast
def get_BERT_tokenizer():
    # Load the BERT tokenizer.
    print('Loading BERT tokenizer...')
    tokenizer = BertTokenizerFast.from_pretrained('bert-base-uncased', do_lower_case=True)
    return tokenizer

def get_XLMRTokenizer():
    print('Loading XLMR tokenizer...')
    tokenizer = XLMRobertaTokenizerFast.from_pretrained("xlm-roberta-base")
    return tokenizer

def get_word_from_id_for_XLMR(id):
    tokenizer = XLMRobertaTokenizerFast.from_pretrained('xlm-roberta-base')
    word_id = id
    word = tokenizer.decode([word_id])
    return word

import ast
def get_input_ids_and_so_on(tokenizer, path_of_dataset, max_length):
    df = pd.read_csv(path_of_dataset, delimiter="\t",header=None, 
                    names=["word", "sentence_left", "token_index_of_sentence_left", "sentence_right", "token_index_of_sentence_right"])
    sentences_left = df.sentence_left.tolist()
    sentences_right = df.sentence_right.tolist()

    # Tokenize all of the sentences and map the tokens to thier word IDs.
    input_ids_left = []
    input_ids_right = []
    attention_masks_left = []
    attention_masks_right = []
    subword_spans_left = []
    subword_spans_right = []
    list_token_index_of_sentence_left = [ast.literal_eval(string) for string in df.token_index_of_sentence_left.tolist()]
    list_token_index_of_sentence_right = [ast.literal_eval(string) for string in df.token_index_of_sentence_right.tolist()]
    tokens_left = []
    tokens_right = []
    # For every sentence...
    for sent in sentences_left:
        # `encode_plus` will:
        #   (1) Tokenize the sentence.
        #   (2) Prepend the `[CLS]` token to the start.
        #   (3) Append the `[SEP]` token to the end.
        #   (4) Map tokens to their IDs.
        #   (5) Pad or truncate the sentence to `max_length`
        #   (6) Create attention masks for [PAD] tokens.
        encoded_dict = tokenizer.encode_plus(
                            sent,                      # Sentence to encode.
                            add_special_tokens = True, # Add '[CLS]' and '[SEP]'
                            max_length = max_length,           # Pad & truncate all sentences.
                            padding='max_length',
                            return_attention_mask = True,   # Construct attn. masks.
                            return_tensors = 'pt',     # Return pytorch tensors.
                    )
        
        # Add the encoded sentence to the list.    
        input_ids_left.append(encoded_dict['input_ids'])
        
        # And its attention mask (simply differentiates padding from non-padding).
        attention_masks_left.append(encoded_dict['attention_mask'])

        tokens = encoded_dict.tokens()
        subword_spans = [encoded_dict.token_to_chars(i) for i in range(len(tokens))]
        subword_spans_left.append(subword_spans)
        tokens_left.append(tokens)

    for sent in sentences_right:
        encoded_dict = tokenizer.encode_plus(
                            sent,                      # Sentence to encode.
                            add_special_tokens = True, # Add '[CLS]' and '[SEP]'
                            max_length = max_length,           # Pad & truncate all sentences.
                            padding='max_length',
                            return_attention_mask = True,   # Construct attn. masks.
                            return_tensors = 'pt',     # Return pytorch tensors.
                    )
        
        input_ids_right.append(encoded_dict['input_ids'])
        attention_masks_right.append(encoded_dict['attention_mask'])
        
        tokens = encoded_dict.tokens()
        subword_spans = [encoded_dict.token_to_chars(i) for i in range(len(tokens))]
        subword_spans_right.append(subword_spans)
        tokens_right.append(tokens)

    # Convert the lists into tensors.
    input_ids_left = torch.cat(input_ids_left, dim=0)
    attention_masks_left = torch.cat(attention_masks_left, dim=0)

    input_ids_right = torch.cat(input_ids_right, dim=0)
    attention_masks_right = torch.cat(attention_masks_right, dim=0)

    # labels = torch.tensor(labels)

    # Print sentence 0, now as a list of IDs.
    print('sample sentence original: ', sentences_left[0])
    print('sample sentence Token IDs:', input_ids_left[0])

    return (input_ids_left, input_ids_right, attention_masks_left, attention_masks_right, subword_spans_left, subword_spans_right, list_token_index_of_sentence_left, list_token_index_of_sentence_right, tokens_left, tokens_right)

from transformers import BertModel
import numpy as np
def save_embeddings(device, input_ids_list, attention_masks, subword_span_list, list_token_index_of_sentence, tokens_list, saving_path, model):
    print("enter save_embeddings function")

    input_ids_list = input_ids_list.to(device)
    attention_masks = attention_masks.to(device)
    model = model.to(device)
    print("input ids are on cuda: " + str(input_ids_list.is_cuda))
    print("attention masks are on cude: " + str(attention_masks.is_cuda))


    token_embeddings_output = list()
    layers_list = [1, 12]
    # print(list_token_index_of_sentence)

    for i in range(len(input_ids_list)):
        input_ids = input_ids_list[i]
        subword_spans = subword_span_list[i]
        # print(subword_spans)
        # subwords_bool_mask = [
        #         span.start >= list_token_index_of_sentence[i][0] and span.end <= (list_token_index_of_sentence[i][1] + 1)
        #         if span is not None
        #         else False
        #         for span in subword_spans
        #     ]
        subwords_bool_mask = []
        for span in subword_spans:
            if span is not None:
                token_index = list_token_index_of_sentence[i]
                if span.start >= token_index[0] and span.end <= (token_index[1] + 1):
                    subwords_bool_mask.append(True)
                    print(span)
                else:
                    subwords_bool_mask.append(False)
            else:
                subwords_bool_mask.append(False)
        # print(subwords_bool_mask)
        extracted_subwords = [
                tokens_list[i][j] for j, value in enumerate(subwords_bool_mask) if value
                ]
        # print(attention_masks[i])
        # print(extracted_subwords)
        with torch.no_grad():
            outputs = model(input_ids.unsqueeze(0), token_type_ids=None, attention_mask=attention_masks[i].unsqueeze(0))        

        embedding = (
            torch.stack(outputs[2], dim=0)  # (layer, batch, subword, embedding)
            .squeeze(dim=1)  # (layer, subword, embedding)
            .permute(1, 0, 2)[  # (subword, layer, embedding)
                torch.tensor(subwords_bool_mask), :, :
            ]
        )
        print(f"Size of pre-subword-agregated tensor: {embedding.shape}")
        
        # embedding.shape[0] refers to the number of subwords
        if embedding.shape[0] == 1:
            # print(embedding[0].shape)
            sum_vec = np.sum([np.array(embedding[0][layer].cpu()) for layer in layers_list], axis=0)
            token_embeddings_output.append(sum_vec)
        else:
            sum_vec = np.sum([np.array(embedding[0][layer].cpu()) for layer in layers_list], axis=0)
            for i in range(1, len(embedding.shape[0])):
                sum_vec = np.add(sum_vec, np.sum([np.array(embedding[i][layer].cpu()) for layer in layers_list], axis=0))
            sum_vec = sum_vec/len(embedding.shape[0])
            # print(sum_vec.shape)
            token_embeddings_output.append(sum_vec)

    token_embeddings_output = np.array(token_embeddings_output)
    # print(token_embeddings_output.shape)
    # print(token_embeddings_output)
    np.save(saving_path, token_embeddings_output)


def save_embeddings_old(device, input_ids, attention_masks, index_padded, saving_path, model):
    print("enter save_embeddings function")

    input_ids = input_ids.to(device)
    attention_masks = attention_masks.to(device)
    print("input ids are on cuda: " + str(input_ids.is_cuda))
    print("attention masks are on cude: " + str(attention_masks.is_cuda))

    # model = BertModel.from_pretrained('bert-base-uncased', output_hidden_states=True)
    
    model = model.to(device)

    set_length = len(input_ids)
    # print(set_length)
    token_embeddings_output = list()

    layers_list = [1, 12]

    model.eval()
    for index in range(set_length):
        if index % 10 == 0:
            print("loop through " + str(index) + "th data points in save_embeddings function")
        with torch.no_grad():
            outputs = model(input_ids[index].unsqueeze(0), token_type_ids=None, attention_mask=attention_masks[index].unsqueeze(0))
            hidden_states = outputs[2]
            token_embeddings = torch.stack(hidden_states, dim=0)
            # print(token_embeddings.shape)
            token_embeddings = torch.squeeze(token_embeddings, dim=1)
            # print(token_embeddings.shape)
            token_embeddings = token_embeddings.permute(1, 0, 2)
            # print(token_embeddings.shape)
            if type(index_padded[index]) is int:
                # print("enter this condition")

                sum_vec = np.sum([np.array(token_embeddings[index_padded[index]][layer].cpu()) for layer in layers_list], axis=0)
                token_embeddings_output.append(sum_vec)
            else:
                sum_vec = np.sum([np.array(token_embeddings[index_padded[index][0]][layer].cpu()) for layer in layers_list], axis=0)
                for i in range(1, len(index_padded[index])):
                    sum_vec = np.add(sum_vec, np.sum([np.array(token_embeddings[index_padded[index][i]][layer].cpu()) for layer in layers_list], axis=0))
                sum_vec = sum_vec/len(index_padded[index])
                # print(sum_vec.shape)
                token_embeddings_output.append(sum_vec)

    token_embeddings_output = np.array(token_embeddings_output)
    # print(token_embeddings_output.shape)
    # print(token_embeddings_output)
    np.save(saving_path, token_embeddings_output)

import re
def convert_raw_sentence_to_wic_format(sentence):
    output_string = re.sub(r'(?<!\w)[^\w\s]|[^\w\s](?!s)', ' \\g<0> ', sentence)
    output_string = re.sub(r'\s+', ' ', output_string)
    output_string = re.sub(r"(?<=[\w\d])'(?=s)", " '", output_string)
    return output_string

def get_index_of_keyword(keyword, sentence):
    # print("keyword is: " + keyword)
    # print("sentence is: " + sentence)
    token_list = sentence.split()
    for index, _ in enumerate(token_list):
        if keyword == token_list[index].lower():
            return index