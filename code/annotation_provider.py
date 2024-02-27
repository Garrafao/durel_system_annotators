from __future__ import annotations

import json
from collections.abc import Iterable
import os
import csv
import random

import logging


def add_use_row(row, uses):
    """
    :note:
        The following example shows the expected format of the uses dict returned.
        {
            dataID: {
                'dataID': str,
                'context': str,
                'indices_target_token': [tuple(int, int)],
                'indices_target_sentence': [tuple(int, int)],
                'lemma': str,
            }
        }
    """
    if row['identifier_system'] in uses:
        raise ValueError(f"Duplicate identifier '{row['identifier_system']}' in uses file.")
    uses[row['identifier_system']] = {
        'dataID': row['identifier_system'],
        'context': row['context'],
        'indices_target_token': [tuple(int(i) for i in index.split(':'))
                                 for index in row['indexes_target_token'].split(',')],
        'indices_target_sentence': [tuple(int(i) for i in index.split(':'))
                                    for index in row['indexes_target_token'].split(',')],
        'lemma': row['lemma']
    }


def add_instances_row(row, instances):
    if row['id'] in instances:
        raise ValueError(f"Duplicate instanceID '{row['id']}' in instances file.")
    instances[row['id']] = row.copy()


def instance_to_annotation(instance: dict, judgment: str, annotator: str) -> list:
    """
    Converts a given instance to an annotation dictionary.

    :param instance: The instance to convert.
    :type instance: dict
    :param judgment: The judgment for the instance.
    :type judgment: str
    :param annotator: The annotator that made the judgment.
    :type annotator: str
    :return: The converted annotation dictionary.
    :rtype: dict
    """
    return [instance['internal_identifier1'], instance['internal_identifier2'],
            annotator, str(judgment), '', instance['lemma'], '']


class AnnotationProvider:

    def __init__(self, settings: json, path: str, prefix: str = '', debug: bool = False):
        """
        Initialize a new instance of the class.

        :param path: (str) The path to the directory containing the files.
        :param prefix: (str) A prefix to prepend to the file names. Default is an empty string.
        :param debug: (bool) Enable debugging mode. Default is False.

        :raises FileNotFoundError: If the specified path does not exist or if the required files are not found.

        :note:
        - The class assumes that the path argument points to a directory containing the following files:
          - `{prefix}uses.tsv`: A file containing a list of uses.
          - `{prefix}instances.tsv`: A file containing a list of instances.
        - The class also assumes that the uses and instances files have the same format.
        """

        self._DEBUG = debug
        self.prefix = prefix
        self.settings = settings
        if self._DEBUG:
            logging.basicConfig(
                format=settings['log_formatting'], level=logging.DEBUG)

        self._check_path_exists(path)
        self._path = path

        self._uses = self._load('uses')
        self._instances = self._load('instances')
        self._instances_with_token_index = self._create_instances_with_token_index()

        self._annotations = []

    def _check_path_exists(self, path):
        if not os.path.exists(path):
            if self._DEBUG:
                logging.warning(f"Path '{path}' does not exist.")
            raise FileNotFoundError(f"Path '{path}' does not exist.")

    def _create_file_path(self, text: str, path: str = None) -> str:
        if path is None:
            path = self._path
        return os.path.join(path, '{}{}{}'.format(self.prefix, text, self.settings['file_extension']))

    def _create_instances_with_token_index(self):
        instances_with_token_index = {}
        for instance in self._instances.values():
            instances_with_token_index[instance['id']] = dict()
            instances_with_token_index[instance['id']]['lemma'] = (
                self.get_lemma_by_identifier(instance['internal_identifier1']))
            sentence_left = self.get_sentence_by_identifier(instance['internal_identifier1'])
            sentence_right = self.get_sentence_by_identifier(instance["internal_identifier2"])
            instances_with_token_index[instance['id']]['sentence_left'] = sentence_left
            instances_with_token_index[instance['id']]['sentence_right'] = sentence_right
            instances_with_token_index[instance['id']]['token_index_of_sentence_left'] = \
                self.get_token_index_of_sentence_by_identifier(
                    instance["internal_identifier1"])
            instances_with_token_index[instance['id']]['token_index_of_sentence_right'] = \
                self.get_token_index_of_sentence_by_identifier(
                    instance['internal_identifier2'])
        return instances_with_token_index

    def get_token_index_of_sentence_by_identifier(self, identifier):
        return self._uses[identifier]["indices_target_token"][0]

    def get_sentence_by_identifier(self, identifier) -> str:
        return self._uses[identifier]["context"]

    def get_lemma_by_identifier(self, identifier) -> str:
        return self._uses[identifier]["lemma"]

    def _load(self, filetype: str) -> dict[str, dict]:
        """
        Load the file.

        :param filetype: (str) The file type of the file that should be parsed. Should be 'uses' or 'instances'.

        :returns: A dictionary containing the data, indexed by their respective ids.
        :rtype: dict[str, dict]

        :raises ValueError: If the file is not in the correct format.
        """
        self._check_path_exists(self._create_file_path(filetype))
        if self._DEBUG:
            logging.debug(f"Loading {filetype} files from '{self._path}'.")
        data_dictionary = {}
        with open(self._create_file_path(filetype), 'r') as f:
            reader = csv.DictReader(f, delimiter=self.settings['delimiter'], quoting=csv.QUOTE_NONE, strict=True)
            data = list(reader)
            for row in data:
                if filetype == 'uses':
                    add_use_row(row, data_dictionary)
                elif filetype == 'instances':
                    add_instances_row(row, data_dictionary)
        if self._DEBUG:
            logging.debug(
                f"Loaded {len(data_dictionary)} {filetype} from path '{self._path}'.")
        return data_dictionary

    def get_instances_iterator(self, random_order: bool = False) -> Iterable:
        if random_order:
            return iter([self._instances[index]
                         for index in random.sample(sorted(self._instances), len(self._instances))])
        return iter(self._instances.values())

    def add_annotation(self, instance: dict, judgment: str, annotator: str):
        annotation = instance_to_annotation(instance, judgment, annotator)
        self._annotations.append(annotation)

    def flush_annotation(self, path: str = None):
        """
        Write the annotation set to the annotation file.
        If a custom path is provided, the annotation file is written to this path,
        else it is written to the path where the uses & instance file are.
        If a file with the provided name exists, the function appends to the existing file.

        After the annotation set is written to the file, the annotation set is cleared.

        :param path: (str, optional) The path to write the annotation file to, by default None
        """
        dest_file = self._create_file_path(self.settings['annotations_filename'], path)

        with open(dest_file, 'w+') as f:
            # Write Header if file is empty
            if os.stat(dest_file).st_size == 0:
                f.write(str.join(self.settings['delimiter'], self.settings['annotations_columns'][:-1]))
                f.write('\n')
            # Write Judgements
            for annotation in self._annotations:
                f.write(str.join(self.settings['delimiter'], annotation[:-1]))
                f.write('\t\n')

        self._annotations = []

    def flush_instance_with_token_index(self, path: str = None):
        dest_file = self._create_file_path(self.settings['token_index_filename'], path)

        with open(dest_file, 'w+', encoding='utf-8') as f:
            # No need to write header file as wic data file does not have header
            for key, instance in self._instances_with_token_index.items():
                line = str.join(self.settings['delimiter'], [instance['lemma'], instance['sentence_left'],
                                                             str(instance['token_index_of_sentence_left']),
                                                             instance['sentence_right'],
                                                             str(instance['token_index_of_sentence_right'])])
                f.write(line)
                f.write('\n')

    def _setup_flush_path(self, filetype, path: str = None):
        dest_file = (self._create_file_path(filetype, path))
        self._check_path_exists(dest_file)

        if self._DEBUG:
            logging.info(f"Writing to file: '{dest_file}'")

        return dest_file
