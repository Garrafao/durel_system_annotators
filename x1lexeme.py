import torch
from model import Model
from helper_functions import *
#from transformers import XLMRobertaModel
from transformers import AutoTokenizer, AutoModel
from sklearn.preprocessing import StandardScaler
from scipy.spatial.distance import cosine


def make_inference_for_dataset(path_of_dataset):
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
    sentences_left_train, sentences_right_train = get_sentences_from_dataset(path_of_dataset)
    tokenizer = AutoTokenizer.from_pretrained('pierluigic/xl-lexeme')
    #tokenizer = get_XLMRTokenizer()
    max_length = 512
    get_max_sentence_length_of_a_dataset_by_tokenizer(tokenizer, path_of_dataset)
    input_ids_left, input_ids_right, attention_masks_left, attention_masks_right, subword_spans_left, subword_spans_right, list_token_index_of_sentence_left, list_token_index_of_sentence_right,tokens_left, tokens_right = get_input_ids_and_so_on(tokenizer, path_of_dataset, max_length)

    model = AutoModel.from_pretrained('pierluigic/xl-lexeme',output_hidden_states=True)
    #model = XLMRobertaModel.from_pretrained('xlm-roberta-base', output_hidden_states=True)
    save_embeddings(device, input_ids_left, attention_masks_left, subword_spans_left, list_token_index_of_sentence_left, tokens_left, './temp/token_embeddings_left.npy', model)

    save_embeddings(device, input_ids_right, attention_masks_right, subword_spans_right, list_token_index_of_sentence_right, tokens_right, './temp/token_embeddings_right.npy', model)

    embeddings_left = np.load('./temp/token_embeddings_left.npy')
    #print(embeddings_left[0])
    embeddings_right = np.load('./temp/token_embeddings_right.npy')
    #print(embeddings_right[0])
    concatenation = np.hstack((embeddings_left, embeddings_right))
    '''
    X_test = concatenation
    sc = StandardScaler()

    X_train = np.load('computational-annotator-pilot/X_train.npy')
    print(X_train.shape)
    X_train = sc.fit_transform(X_train)
    X_test = sc.transform(X_test)

    X_test = torch.from_numpy(X_test.astype(np.float32))

    # define your model
    model = Model(1536)

    # load the saved weights
    model.load_state_dict(torch.load('computational-annotator-pilot/weight/xmlr+mlp+binary.pth'))
    with torch.no_grad():
        y_predicted = model(X_test)
        y_predicted_cls = y_predicted.round()
    cls_list = y_predicted_cls[:, 0].tolist()'''

#t>0.5 == 1 and 0 otherwise for pierligue model the threshold 
    cls_list = []
    for (l,r) in zip(embeddings_left,embeddings_right):
        cls_list.append(cosine(l, r))
    print(cls_list)
    for index, d in enumerate(cls_list):
        if d >= 0.5:
            cls_list[index] = 1
        else:
            cls_list[index] = 4
    print('x1-lexeme',cls_list)
    return cls_list

if __name__ == "__main__":
    make_inference_for_dataset('tmp/instances_with_token_index.csv')
