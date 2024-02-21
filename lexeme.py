import ast
import logging

import numpy as np
import pandas as pd
import torch
from scipy.spatial.distance import cosine

from InputExample import InputExample
from WordTransformer import WordTransformer

logger = logging.getLogger(__name__)


def make_inference_for_dataset(path_of_dataset: str, delimiter: str, columns: list[str],
                               thresholds: list[float] = None) -> list[int]:
    def select_torch():
        # If there's a GPU available...
        if torch.cuda.is_available():
            # Tell PyTorch to use the GPU.
            torch.device("cuda")
            logger.info('There are %d GPU(s) available.' % torch.cuda.device_count())
            logger.info('We will use the GPU:', torch.cuda.get_device_name(0))

        # If not...
        else:
            torch.device("cpu")
            logger.info('No GPU available, using the CPU instead.')

    def map_cls_list():
        for index, s in enumerate(cls_list):
            # We always map the values that are lower than the first threshold to 1
            if s <= thresholds[0]:
                cls_list[index] = 1
            # If we have more thresholds (3), we have additional mappings
            elif len(thresholds) == 3 and thresholds[0] < s <= thresholds[1]:
                cls_list[index] = 2
            elif len(thresholds) == 3 and thresholds[1] < s <= thresholds[2]:
                cls_list[index] = 3
            # All other values are mapped to 4
            else:
                cls_list[index] = 4

    select_torch()
    left_sentence_and_token_index, right_sentence_and_token_index = (
        get_left_right_sentences_and_token_index(path_of_dataset, delimiter, columns))

    model = WordTransformer('pierluigic/xl-lexeme')

    embeddings_left = compute_embeddings_lexeme(left_sentence_and_token_index, model)
    embeddings_right = compute_embeddings_lexeme(right_sentence_and_token_index, model)

    # t>0.5 == 1 and 0 otherwise for pierluigic model the threshold
    cls_list = []
    for (l, r) in zip(embeddings_left, embeddings_right):
        # cls_list.append(cosine(l, r)) # for cosine distance
        cls_list.append(1 - cosine(l, r))  # for cosine similarity

    # Mapping similarity to labels
    if thresholds is not None and len(thresholds) > 0:
        map_cls_list()

    return cls_list


def compute_embeddings_lexeme(sentence_and_token_index: list[tuple], model) -> np.ndarray:
    """

    This method is used to compute token embeddings for a given sentence and token index.

    Parameters:
    sentence_and_token_index (list[tuple]): A list of tuples containing sentences and token indices. Each tuple
    consists of a sentence (string) and a token index (string representation of a tuple in the format
    (start_index, end_index)).
    model (object): An instance of the model used for computing embeddings.

    Returns:
    token_embeddings_output (numpy array): Array containing the computed token embeddings for each sentence and
    token index. The shape of the array is (num_sentences, num_tokens, embedding_size).

    Example usage:
    ```
    sentence_and_token_index = [('This is a sentence.', '(5, 7)'), ('Another sentence here.', '(8, 14)')]
    model = SomeModel()

    embeddings = compute_embeddings_lexeme(sentence_and_token_index, model)

    # Output:
    # Array of computed token embeddings
    ```
    """
    token_embeddings_output = list()
    for i, (sen, idx) in enumerate(sentence_and_token_index):
        print("Sentence being processed:  " + str(i))
        idx_tuple = ast.literal_eval(idx)

        # print("Sentence being processed: "+ sen)
        examples = InputExample(texts='"' + sen + '"', positions=[idx_tuple[0], idx_tuple[1]])
        outputs = model.encode(examples)

        token_embeddings_output.append(outputs)
        # print(sen,idx,outputs)
    # print(token_embeddings_output)
    token_embeddings_output = np.array(token_embeddings_output)
    return token_embeddings_output


def save_embeddings_lexeme(sentence_and_token_index: list[tuple], saving_path: str, model):
    """
    Save embeddings to a specified file.

    Parameters:
    sentence_and_token_index: A list of tuples containing the sentence and token index.
    saving_path: A string specifying the path where the embeddings will be saved.
    model: The embedding model.
    """
    logger.info("Saving embeddings to %s", saving_path)

    token_embeddings_output = list()
    for (sen, idx) in sentence_and_token_index:
        idx_tuple = ast.literal_eval(idx)
        examples = InputExample(texts='"' + sen + '"', positions=[idx_tuple[0], idx_tuple[1]])
        outputs = model.encode(examples)
        token_embeddings_output.append(outputs)

    token_embeddings_output = np.array(token_embeddings_output)
    np.save(saving_path, token_embeddings_output)


def get_left_right_sentences_and_token_index(path_of_dataset: str, delimiter: str, columns: list[str]):
    """
    Get the left and right sentences along with their corresponding token indices from a given dataset.

    Parameters:
    path_of_dataset (str): The path to the dataset file.
    delimiter (str): The delimiter used in the dataset file.
    columns (list[str]): A list of column names for the dataset.

    Returns:
    A tuple of two generators, each containing the sentence and token index pairs for the left and right fragments.

    Example usage:
        df_path = 'data/dataset.csv'
        df_delimiter = ','
        df_columns = ['sentence_left', 'token_index_sentence_left', 'sentence_right', 'token_index_sentence_right']
        left_sentences, right_sentences = get_left_right_sentences_and_token_index(df_path, df_delimiter, df_columns)
        for left_sentence, left_token_index in left_sentences:
            print(f"Left Sentence: {left_sentence}, Token Index: {left_token_index}")
        for right_sentence, right_token_index in right_sentences:
            print(f"Right Sentence: {right_sentence}, Token Index: {right_token_index}")
    """
    df = pd.read_csv(path_of_dataset, delimiter=delimiter, header=None,
                     names=columns, quoting=3)
    sentences_left = df.sentence_left.tolist()
    token_index_of_sentence_left = df.token_index_of_sentence_left.tolist()
    sentences_right = df.sentence_right.tolist()
    token_index_of_sentence_right = df.token_index_of_sentence_right.tolist()

    return zip(sentences_left, token_index_of_sentence_left), zip(sentences_right, token_index_of_sentence_right)


if __name__ == "__main__":
    default_thresholds = [0.2, 0.4, 0.6]
    default_columns = ["word", "sentence_left", "token_index_of_sentence_left",
                       "sentence_right", "token_index_of_sentence_right"]
    default_delimiter = "\t"
    default_path = './temp/instances_with_token_index.csv'
    make_inference_for_dataset(default_path, default_delimiter, default_columns, default_thresholds)
