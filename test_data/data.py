# Get external data sets for integration testing and transform them into our format
import csv
import shutil
import zipfile
from collections import defaultdict
from pathlib import Path

import numpy as np
import requests

# Needed because of TempoWiC
import os
import json
import spacy
from requests import RequestException

nlp = spacy.load("en_core_web_sm")


class NotImplementedException(Exception):
    pass


def aggregate_wug(judgments):
    """
    Load WUG-formatted list of judgments as list of dictionaries and aggregate.
    """
    pair2judgments = defaultdict(lambda: [])
    for row in judgments:
        judgment = float(row['judgment'])
        if judgment != 0.0:  # exclude 'cannot decide' judgments
            pair2judgments[frozenset((row['identifier1'], row['identifier2']))].append(judgment)
    pair2label = {tuple(pair): np.median(judgments) for pair, judgments in
                  pair2judgments.items()}  # aggregate with median
    # Ignores order, maps all instances with median judgment below 2.5 to 1 and above or equal 2.5 to 4
    if aggregation_mode == 'binarize-median':
        pair2label = {pair: 1 if label < 2.5 else 4 for pair, label in pair2label.items()}  # binarize
    if aggregation_mode == 'median':
        pair2label = pair2label  # median

    return pair2label


def wug2anno(input_path, output_path):
    """
    Load WUG-formatted data set, transform it to format of DURel system annotators and export.
    """
    print('input_path:', input_path, 'aggregation_mode:',
          aggregation_mode, 'preprocessing_mode:', preprocessing_mode)
    uses_all, labels_all = [], []
    normalization_errors = 0
    for condition in ['uses', 'judgments']:
        for p in Path(input_path + '/data').glob('*/{0}.csv'.format(condition)):

            with open(p, encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile, delimiter='\t', quoting=csv.QUOTE_NONE, strict=True)
                data = [row for row in reader]

            if condition == 'uses':
                output_data = []
                for row in data:
                    row_out = {'lemma': row['lemma'], 'identifier': row['identifier']}
                    context_raw = row['context']
                    if preprocessing_mode == 'raw':
                        row_out['context'] = context_raw
                        row_out['indexes_target_token'] = row['indexes_target_token']
                        row_out['indexes_target_sentence'] = row['indexes_target_sentence']
                    elif preprocessing_mode == 'normalized':

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
                                # raise AssertionError
                                print('normalization_error')
                                context = context_tokenized
                                normalization_errors += 1
                        else:
                            context = context_tokenized

                        # Catch normalization errors
                        if (row['identifier'] == 'beyer_poetik01_1882-7284-11' or
                                row['identifier'] == 'beyer_poetik01_1882-17923-12'):
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
                        index_start = int(np.sum(
                            [len(t) + 1 for t in tokens[:index_start_sentence]])) if index_start_sentence != 0 else 0
                        index_end = int(
                            np.sum([len(t) + 1 for t in tokens[:index_end_sentence]])) if index_end_sentence != 0 else 0
                        index_target = int(row['indexes_target_token_tokenized'])
                        # print(index_target)
                        target_from_tokenized_or_normalized = tokens[index_target]
                        index_target_start = int(
                            np.sum([len(t) + 1 for t in tokens[:index_target]])) if index_target != 0 else 0
                        index_target_end = index_target_start + len(target_from_tokenized_or_normalized)
                        # print(index_target_start, index_target_end, )
                        row_out['context'] = context
                        row_out['indexes_target_token'] = str(index_target_start) + ':' + str(index_target_end)
                        row_out['indexes_target_sentence'] = str(index_start) + ':' + str(index_end)

                        # Check output data
                        context = row_out['context']
                        index_target_start = int(row_out['indexes_target_token'].split(':')[0])
                        index_target_end = int(row_out['indexes_target_token'].split(':')[1])
                        target = context[index_target_start:index_target_end]
                        print('context:', [context])
                        print('context_original:', [row['context']])
                        print('index_target_start, index_target_end:', index_target_start, index_target_end)
                        print('target versus target_from_tokenized_or_normalized: ',
                              [target, target_from_tokenized_or_normalized])
                        # Check that constructed target tokens have desired properties
                        assert 0 <= index_target_start <= len(context)
                        assert 0 <= index_target_end <= len(context)
                        assert len(target) > 0
                        punctuation = [' ', '.', ',', '!', '"', '\'']
                        assert not target[0] in punctuation
                        assert not target[-1] in punctuation
                        print('--')
                    else:
                        raise NotImplementedException("No valid preprocessing option provided with:", preprocessing_mode)
                    output_data.append(row_out)

                uses_all += output_data
            if condition == 'judgments':
                lemma = data[0]['lemma']  # infer lemma from first row
                pair2label = aggregate_wug(data)
                # to do: new instance construction needs access to judgments and uses and thus cannot
                # be calculated by itself
                output_data = [{'identifier1': id1, 'identifier2': id2, 'label': l, 'lemma': lemma}
                               for (id1, id2), l in
                               pair2label.items()]
                labels_all += output_data

            # to do: data export for split data currently not possible
            # data_output_path = output_path + '/data_split/{0}/'.format(str(p).split('/')[-2])
            # Path(data_output_path).mkdir(parents=True, exist_ok=True)
            # name = 'labels' if condition == 'judgments' else condition
            # Export data
            # with open(data_output_path + '{0}.csv'.format(name), 'w') as file:
            #    w = csv.DictWriter(file, output_data[0].keys(), delimiter='\t', quoting=csv.QUOTE_NONE,
            #                           escapechar='\\')
            #    w.writeheader()
            #    w.writerows(output_data)

    create_and_save_output_data(uses_all, labels_all, output_path)
    print('number of normalization errors:', normalization_errors)
    print('-----')


def create_and_save_output_data(uses_all, labels_all, output_path):
    # print(uses_all)
    # Get mapping from identifiers to uses
    id2use_all = {row['identifier']: row for row in uses_all}

    instances_all = create_instance(id2use_all, labels_all, uses_all)

    # Export concatenated data
    data_output_path = output_path + '/data/{0}/'.format('all')
    Path(data_output_path).mkdir(parents=True, exist_ok=True)

    for condition, output_data in [('uses', uses_all), ('labels', labels_all), ('instances', instances_all)]:
        with open(data_output_path + '{0}.csv'.format(condition), 'w') as file:
            w = csv.DictWriter(file, output_data[0].keys(), delimiter='\t', quoting=csv.QUOTE_NONE,
                               escapechar='\\')
            # to do: this is dangerous! It can introduce additional characters and make the target word indices wrong.
            # I did not yet find a good way to solve this.
            w.writeheader()
            w.writerows(output_data)


def create_instance(id2use_all, labels_all, uses_all):
    # Create instances
    instances_all = [{'lemma': row['lemma'], 'identifier1': id2use_all[row['identifier1']]['identifier'],
                      'context1': id2use_all[row['identifier1']]['context'],
                      'indexes_target_token1': id2use_all[row['identifier1']]['indexes_target_token'],
                      'identifier2': id2use_all[row['identifier2']]['identifier'],
                      'context2': id2use_all[row['identifier2']]['context'],
                      'indexes_target_token2': id2use_all[row['identifier2']]['indexes_target_token'],
                      } for row in labels_all]

    # Check whether there is a mismatch between number of pairs in gold and instances
    assert len(labels_all) == len(instances_all)

    # Check identifier uniqueness
    ids = [row['identifier'] for row in uses_all]
    assert len(ids) == len(set(ids))
    return instances_all


def wic2anno(input_path, output_path):
    """
    Load WiC data set, transform it to format repository format and export.
    """
    print('input_path:', input_path)
    for split in ['dev', 'train', 'test']:

        print('split:', split)

        # Load use pairs
        condition = 'data'
        with open(input_path + split + '/{0}.{1}.txt'.format(split, condition), encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile, fieldnames=["lemma", "pos", "indices", "sent1", "sent2"], delimiter='\t',
                                    quoting=csv.QUOTE_NONE, strict=True)
            data = [row for row in reader]

        identifier2use = {}
        pairs = []
        lemmas = []
        j = 0
        for row in data:
            pair = []
            for i in [0, 1]:
                lemma = row['lemma']
                row_id = int(row['indices'].split('-')[i])
                context = row['sent{0}'.format(i + 1)]
                context_previous = ' '.join(context.split(' ')[:row_id])
                if len(context_previous) > 0:
                    indexes_target_token_start = len(context_previous) + 1
                else:
                    indexes_target_token_start = len(context_previous)
                target_token = context.split(' ')[row_id]
                indexes_target_token_end = indexes_target_token_start + len(target_token)
                indexes_target_token = '{0}:{1}'.format(indexes_target_token_start, indexes_target_token_end)
                indexes_target_sentence = '0:{0}'.format(len(context))
                identifier_strict = row['lemma'] + '%%' + indexes_target_token + '%%' + context
                # identifier_relaxed = lemma+'-'+str(j) # not needed now
                identifier2use[identifier_strict] = {'lemma': lemma, 'identifier': identifier_strict,
                                                     'context': context, 'indexes_target_token': indexes_target_token,
                                                     'indexes_target_sentence': indexes_target_sentence}
                # print(context, context[indexes_target_token_start:indexes_target_token_end], context[0:len(context)])
                lemmas.append(lemma)
                pair.append(identifier_strict)
                # print(pair)
                j += 1
            # print('--')
            pair.append(lemma)
            pairs.append(tuple(pair))

        # print(list(identifier2use.values())[0])
        print('total number of processed sentences versus number of extracted unique sentences:', j,
              len(identifier2use.keys()))

        list(set(lemmas))
        uses_all = list(identifier2use.values())

        # for lemma in lemmas:
        #    data_output_path = output_path + '/data/{0}/'.format(lemma)

        datatype = 'uses'

        data_output_path = output_path + '{0}/data/{1}/'.format(split, 'all')
        Path(data_output_path).mkdir(parents=True, exist_ok=True)

        # Export data
        with open(data_output_path + '{0}.csv'.format(datatype), 'w') as file:
            w = csv.DictWriter(file, uses_all[0].keys(), delimiter='\t', quoting=csv.QUOTE_NONE, escapechar='\\')
            w.writeheader()
            w.writerows(uses_all)

        # Load gold annotations
        condition = 'gold'
        with open(input_path + split + '/{0}.{1}.txt'.format(split, condition), encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile, fieldnames=["label"], delimiter='\t', quoting=csv.QUOTE_NONE, strict=True)
            data = [row for row in reader]

        labels_all = [{'identifier1': identifier1, 'identifier2': identifier2, 'label': data[i]['label'],
                       'lemma': lemma} for i, (identifier1, identifier2, lemma) in enumerate(pairs)]

        datatype = 'labels'

        print('number of gold labels:', len(labels_all))

        # Export data
        with open(data_output_path + '{0}.csv'.format(datatype), 'w') as file:
            w = csv.DictWriter(file, labels_all[0].keys(), delimiter='\t', quoting=csv.QUOTE_NONE, escapechar='\\')
            w.writeheader()
            w.writerows(labels_all)

        # Get mapping from identifiers to uses
        id2use_all = identifier2use  # exists already, renaming for compatibility

        instances_all = create_instance(id2use_all, labels_all, uses_all)

        print('number of annotation instances:', len(instances_all))

        datatype = 'instances'

        # Export data
        with open(data_output_path + '{0}.csv'.format(datatype), 'w') as file:
            w = csv.DictWriter(file, instances_all[0].keys(), delimiter='\t', quoting=csv.QUOTE_NONE, escapechar='\\')
            w.writeheader()
            w.writerows(instances_all)

        # Check whether there is a mismatch between identifiers in uses and instances
        # print(set([identifier for pair in pairs for identifier in pair[:3]]))
        assert set([row['identifier'] for row in uses_all]) == set(
            [identifier for pair in pairs for identifier in pair[:2]])
    print('-----')


def tempowic2anno(input_path, output_path):
    """
    Load WUG-formatted data set, transform it to format of DURel system annotators and export.
    """
    print('input_path:', input_path)
    uses_all = []
    labels_all = []
    for p in Path(input_path + '/data').glob('*/{0}.csv'.format('uses')):
        print('current path:', p)

        with open(p, encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile, delimiter='\t', quoting=csv.QUOTE_NONE, strict=True)
            data = [row for row in reader]

        output_data = [{'lemma': row['lemma'], 'identifier': row['identifier'], 'context': row['context'],
                        'indexes_target_token': row['indexes_target_token'],
                        'indexes_target_sentence': row['indexes_target_sentence']} for row in data]

        uses_all += output_data
        # to do: export data here per lemma (split)

    for p in Path(input_path + '/data').glob('*/{0}.csv'.format('labels')):
        print('current path:', p)

        with open(p, encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile, delimiter='\t', quoting=csv.QUOTE_NONE, strict=True)
            data = [row for row in reader]

            output_data = [{'identifier1': row['identifier1'], 'identifier2': row['identifier2'],
                            'label': row['label'], 'lemma': row['lemma']} for row in data]

        labels_all += output_data

        # data_output_path = output_path + '/data/{0}/'.format(str(p).split('/')[-2])
        # Path(data_output_path).mkdir(parents=True, exist_ok=True)

    create_and_save_output_data(uses_all, labels_all, output_path)

    print('-----')


def tempowic2wug(data, labels, datadir, split):
    """
    Bring TempoWiC data set into WUG format.
    """
    print('data:', data, 'labels:', labels, 'datadir:', datadir, 'split:', split)

    # parse an JSON file by name
    with open(data) as jsonfile:
        data_instances = [json.loads(line) for line in jsonfile.readlines()]

    lemma2group2context = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: None)))
    for data_instance in data_instances:
        identifier = data_instance['id']
        lemma = data_instance['word']  # this should be lemmatized
        tweet1 = data_instance['tweet1']
        context = data2context_tempowic(tweet1, '1', lemma, identifier)
        lemma2group2context[lemma][identifier]['1'] = context
        tweet2 = data_instance['tweet2']
        context = data2context_tempowic(tweet2, '2', lemma, identifier)
        lemma2group2context[lemma][identifier]['2'] = context

    with open(labels, encoding='utf-8') as csvfile:
        table = [row for row in csv.reader(csvfile, delimiter='\t')]

    lemma2data = defaultdict(lambda: [])
    for row in table:
        lemma = row[0].split('-')[1]
        id1 = row[0]
        id2 = row[0]
        comment = ' '
        judgment = row[1]
        # print(type(judgment))
        if judgment == '0':
            # print(judgment)
            judgment = 4
        else:
            judgment = 1
        annotator = np.nan
        data = {'identifier1': id1 + '-tweet1', 'identifier2': id2 + '-tweet2', 'annotator': annotator,
                'label': int(judgment), 'comment': comment,
                'lemma': lemma}
        # todo: this could be considerably simplified as it does not have to have the judgment file structure
        lemma2data[lemma].append(data)

    all_output_folder = datadir + '/tempowic_' + split + '_all/data/all/'
    if not os.path.exists(all_output_folder):
        os.makedirs(all_output_folder)

    with open(all_output_folder + 'labels.csv', 'w') as output_file:
        w = csv.DictWriter(output_file, [lemma2data[lemma] for lemma in lemma2data][0][0].keys(), delimiter='\t',
                           quoting=csv.QUOTE_NONE, escapechar='\\')
        w.writeheader()
        for lemma in lemma2data:
            w.writerows(lemma2data[lemma])

    with open(all_output_folder + 'uses.csv', 'w') as output_file:
        w = csv.DictWriter(output_file,
                           [list(lemma2group2context[lemma].values()) for lemma in lemma2data][0][0]['1'].keys(),
                           delimiter='\t', quoting=csv.QUOTE_NONE, escapechar='\\')
        w.writeheader()
        for lemma in lemma2data:
            contexts = list(lemma2group2context[lemma].values())
            rows = [context['1'] for context in contexts] + [context['2'] for context in contexts]
            w.writerows(rows)

    print('-----')


def data2context_tempowic(tweet, grouping, lemma, identifier) -> dict:
    date = tweet['date']
    text = tweet['text']
    text_start = tweet['text_start']
    text_end = tweet['text_end']
    indexes_target_token = str(text_start) + ':' + str(text_end)
    annotated = annotate_text_word_tempowic(text, text[text_start:text_end])

    context = {'lemma': lemma, 'pos': nlp(lemma)[0].pos_, 'date': date, 'grouping': grouping,
               'identifier': identifier + '-tweet' + grouping, 'description': '-', 'context': text,
               'indexes_target_token': indexes_target_token,
               'context_tokenized': ' '.join(annotated['context_tokenized']),
               'indexes_target_token_tokenized': annotated['indexes_target_token_tokenized'],
               'indexes_target_sentence': annotated['indexes_target_sentence'],
               'indexes_target_sentence_tokenized': annotated['indexes_target_sentence_tokenized'],
               'context_lemmatized': ' '.join(annotated['context_lemmatized']),
               'context_pos': ' '.join(annotated['context_pos'])}

    return context


def annotate_text_word_tempowic(text, word):
    annotations = nlp(text)
    indexes_target_sentence = '-'
    indexes_target_sentence_tokenized_s = 0
    indexes_target_sentence_tokenized_e = 0
    word = word.replace('\'s', '')
    for n, sent in enumerate(annotations.sents):
        if word in [t.text for t in sent]:
            indexes_target_sentence_tokenized_e = indexes_target_sentence_tokenized_s + len([t.text for t in sent])
            s = text.find(str(sent))
            if s != -1:
                e = s + len(str(sent))
                indexes_target_sentence = str(s) + ':' + str(e)
                break
        else:
            indexes_target_sentence_tokenized_s += len([t.text for t in sent])

    context_tokenized = [str(token) for token in annotations]
    indexes_target_sentence_tokenized = str(indexes_target_sentence_tokenized_s) + ':' + str(
        indexes_target_sentence_tokenized_e)
    # print(n,indexes_target_sentence_tokenized_s,indexes_target_sentence_tokenized_e,word,context_tokenized)
    assert (context_tokenized[indexes_target_sentence_tokenized_s:indexes_target_sentence_tokenized_e] ==
            [t.text for t in [sen for sen in annotations.sents][n]])

    context_lemmatized = [str(token.lemma_.lower()) for token in annotations]
    context_pos = [str(token.pos_) for token in annotations]

    assert len(context_tokenized) == len(context_lemmatized) and len(context_tokenized) == len(context_pos)

    indexes_target_token_tokenized = context_tokenized.index(word)

    return {'context_lemmatized': context_lemmatized, 'indexes_target_sentence': indexes_target_sentence,
            'context_pos': context_pos, 'indexes_target_sentence_tokenized': indexes_target_sentence_tokenized,
            'context_tokenized': context_tokenized,
            'indexes_target_token_tokenized': indexes_target_token_tokenized}


def remove_extracted_dir():
    try:
        shutil.rmtree(data_path)
    except OSError as e:
        print("Error: %s : %s" % (data_path, e.strerror))


if __name__ == '__main__':
    aggregation_modes = ['binarize-median', 'median']
    datasets_path = 'test_data/datasets/'
    Path(datasets_path).mkdir(parents=True, exist_ok=True)

    # testWUG EN (V1.0.0),  DWUG EN (V2.0.1),  DWUG DE (V2.3.0),  DWUG DE (V2.0.1)
    sources_wug = [('testwug_en', 'https://zenodo.org/record/7946753/files/testwug_en.zip?download=1', 'raw'),
                   ('dwug_en', 'https://zenodo.org/record/7387261/files/dwug_en.zip?download=1', 'raw'),
                   ('dwug_de', 'https://zenodo.org/record/7441645/files/dwug_de.zip?download=1', 'normalized'),
                   ('dwug_sv', 'https://zenodo.org/record/7389506/files/dwug_sv.zip?download=1', 'raw'),
                   ('WiC_dataset', 'https://pilehvar.github.io/wic/package/WiC_dataset.zip', ''),
                   ('TempoWiC_Starting_Kit',
                    'https://codalab.lisn.upsaclay.fr/my/datasets/download/3e22f138-ca00-4b10-a0fd-2e914892200d', '')]

    for dataset, link, preprocessing_mode in sources_wug:
        f = datasets_path + dataset + '.zip'

        # 1 - Get zip file
        if not os.path.exists(f):
            try:
                r = requests.get(link, allow_redirects=True)
            except RequestException as error:
                print(f"Request Exception occurred: {error}")
                continue
            with open(f, 'wb') as fp:
                fp.write(r.content)

        # 2 - Extract zip file
        if dataset == 'WiC_dataset':
            wic_path = datasets_path + 'WiC_dataset/'
            Path(wic_path).mkdir(parents=True, exist_ok=True)
            extraction_path = wic_path
        else:
            extraction_path = datasets_path

        try:
            with zipfile.ZipFile(f) as z:
                z.extractall(path=extraction_path)
        except zipfile.BadZipFile as error:
            print(f"Bad zip file: {error}. Zenodo download could be broken.")
            os.remove(f)
            continue

        # 3 - Transform
        data_path = datasets_path + dataset + '/'

        if dataset == 'WiC_dataset':
            data_transformed_path = datasets_path + dataset + '_transformed/'
            # Load, transform and store data set (for dev, train, test)
            wic2anno(input_path=extraction_path, output_path=data_transformed_path)
            remove_extracted_dir()

        elif dataset == 'TempoWiC_Starting_Kit':
            # Transform dataset to WUG format
            for data_part, name in [('train', 'labels'), ('trial', 'gold'), ('validation', 'labels')]:
                tempowic2wug(data_path + 'data/' + data_part + '.data.jl',
                             data_path + 'data/' + data_part + '.' + name + '.tsv',
                             datasets_path, data_part)

            # Tempowic to anno
            # run evonlp2wug.sh first to download data and convert it to wug format
            for dataset_part in ["tempowic_train_all", "tempowic_trial_all", "tempowic_validation_all"]:
                data_path = datasets_path + dataset_part + '/'
                data_transformed_path = datasets_path + dataset_part + '_transformed/'
                Path(data_transformed_path).mkdir(parents=True, exist_ok=True)

                # Load, transform and store data set
                tempowic2anno(input_path=data_path, output_path=data_transformed_path)
                remove_extracted_dir()

        else:  # WUGs
            for aggregation_mode in aggregation_modes:
                data_transformed_path = datasets_path + dataset + '_transformed_' + aggregation_mode
                Path(data_transformed_path).mkdir(parents=True, exist_ok=True)

                # Load, transform and store data set
                wug2anno(input_path=data_path, output_path=data_transformed_path)
            remove_extracted_dir()
