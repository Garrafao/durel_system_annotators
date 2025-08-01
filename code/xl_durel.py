import logging

import numpy as np
import pandas as pd
import torch
from WordTransformer import WordTransformer
from WordTransformer.InputExample import InputExample
from scipy.spatial.distance import cosine

logger = logging.getLogger(__name__)


def specify_xl_durel_annotator(thresholds: list[int]) -> str:
    if thresholds is not None and len(thresholds) == 1:
        return "XL-DURel-Binary"
    elif thresholds is not None and len(thresholds) == 3:
        return "XL-DURel-Multi-Threshold"
    else:
        return "XL-DURel-Cosine"


def create_annotations_for_input_data(df: pd.DataFrame, batch_size: int,
                                      thresholds: list[float] = None, model_dir: str = None) -> list[int]:
    def select_torch():
        # If there's a GPU available...
        if torch.cuda.is_available():
            # Tell PyTorch to use the GPU.
            torch.device("cuda")
            logger.info('There are %d GPU(s) available.' % torch.cuda.device_count())
            logger.info('We will use the GPU: {0}'.format(torch.cuda.get_device_name(0)))

        # If not...
        else:
            torch.device("cpu")
            logger.info('No GPU available, using the CPU instead.')

    def map_judgment_list():
        """
        The `map_judgment_list` method is a helper function that maps the values in the `judgment_list` variable based
        on a set of thresholds.
        """
        for index, s in enumerate(judgment_list):
            # We always map the values that are lower than the first threshold to 1
            if s <= thresholds[0]:
                judgment_list[index] = 1
            # If we have more thresholds (3), we have additional mappings
            elif len(thresholds) == 3 and thresholds[0] < s <= thresholds[1]:
                judgment_list[index] = 2
            elif len(thresholds) == 3 and thresholds[1] < s <= thresholds[2]:
                judgment_list[index] = 3
            # All other values are mapped to 4
            else:
                judgment_list[index] = 4

    # Setup
    select_torch()
    left_sentence_and_token_index, right_sentence_and_token_index = (
        get_contexts_and_token_indices(df))

    # Compute embeddings
    model = WordTransformer('sachinn1/xl-durel', cache_folder=model_dir)
    embeddings_left = compute_embeddings_xldurel(left_sentence_and_token_index, batch_size, model)
    embeddings_right = compute_embeddings_xldurel(right_sentence_and_token_index, batch_size, model)

    # Calculate cosine similarity judgments
    judgment_list = []
    for (l, r) in zip(embeddings_left, embeddings_right):
        # judgment_list.append(cosine(l, r)) # for cosine distance
        judgment_list.append(1 - cosine(l, r))  # for cosine similarity

    # Mapping similarity to labels
    if thresholds is not None and len(thresholds) > 0:
        map_judgment_list()

    return judgment_list


def compute_embeddings_xldurel(sentence_and_token_index: list[tuple], batch_size: int, model) -> np.ndarray:
    """
    This function computes embeddings for given sentences and token indices.

    :param sentence_and_token_index: A list of tuples, each containing a sentence and a corresponding token index.
    :param batch_size: The batch size for computing embeddings.
    :type sentence_and_token_index: list[tuple]
    :param model: The model that will be used to encode the given sentences.

    :return: Embeddings for the given sentences and token indices.
    :rtype: np.ndarray
    """
    token_embeddings_output = [InputExample(texts=sen,
                                            positions=[int(idx.split(':')[0]), int(idx.split(':')[1])])
                               for sen, idx in sentence_and_token_index]
    validate_input_examples(sentence_and_token_index, token_embeddings_output)
    token_embeddings_output = model.encode(token_embeddings_output, batch_size=batch_size)
    token_embeddings_output = np.array(token_embeddings_output)
    return token_embeddings_output


def validate_input_examples(sentence_and_token_index: list[tuple], token_embeddings_output: list[InputExample]):
    i = 0
    for sentence_original, index_string in sentence_and_token_index:
        sentence_input_example = token_embeddings_output[i].texts
        index_start = int(index_string.split(':')[0])
        index_end = int(index_string.split(':')[1])
        assert sentence_original[index_start:index_end] == sentence_input_example[index_start:index_end]
        i += 1


def get_contexts_and_token_indices(df: pd.DataFrame) -> tuple:
    """
    Get the left and right sentences along with their corresponding token index from a dataset.

    :param df: The dataset.

    :return: A tuple containing two iterators. The first iterator provides (sentence_left, token_index_of_sentence_left)
    pairs, and the second iterator provides (sentence_right, token_index_of_sentence_right) pairs.
    """
    sentences_left = df['context1'].tolist()
    token_index_of_sentence_left = df['indexes_target_token1'].tolist()
    sentences_right = df['context2'].tolist()
    token_index_of_sentence_right = df['indexes_target_token2'].tolist()

    return zip(sentences_left, token_index_of_sentence_left), zip(sentences_right, token_index_of_sentence_right)
