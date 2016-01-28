import codecs
import argparse
import os
import glob
import json

from bs4 import BeautifulSoup
from random import randint


def event(emotion_label, text_id):
    group_score = randint(75, 100)
    event_object = {
        'actors': {},
        'climax-score': 0,
        'event': emotion_label,
        'group': "{}:[\"{}\"]".format(group_score, text_id),
        'groupName': "[\"{}\"]".format(text_id),
        'groupScore': str(group_score),
        'labels': ['bla'],
        'mentions': [],
        'prefLabel': ["offer"],
        'time': "20090730"
    }

    return event_object


def mention(emotion, soup, text_id):
    terms = [t['id'] for t in emotion.find_all('target')]
    tokens = [soup.find('term', id=t).span.target['id'] for t in terms]
    sentence = soup.find('wf', id=tokens[0])['sent']

    if terms > 1:
        begin = soup.find('wf', id=tokens[0])['offset']
        wf = soup.find('wf', id=tokens[-1])
        end = int(wf['offset']) + int(wf['length'])
    else:
        wf = soup.find('wf', id=tokens[0])
        begin = int(wf['offset'])
        end = begin + int(wf['length'])
    chars = [str(begin), str(end)]

    mention = {
        'char': chars,
        'sentence': sentence,
        'terms': terms,
        'tokens': tokens,
        'uri': [str(text_id)]
    }
    return mention


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('input_dir', help='directory containing naf XML files')
    parser.add_argument('output_dir', help='the directory where the '
                        'generated JSON files should be saved')
    args = parser.parse_args()

    input_dir = args.input_dir
    output_dir = args.output_dir

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    xml_files = glob.glob('{}/*.xml'.format(input_dir))

    for i, fi in enumerate(xml_files):
        print '{} ({} of {})'.format(fi, (i + 1), len(xml_files))
        text_id = fi[-20:-7]

        print text_id

        with codecs.open(fi, 'rb', encoding='utf-8') as f:
            soup = BeautifulSoup(f, 'lxml')

        num_sentences = int((soup.find_all('wf')[-1]).get('sent'))

        events = {}

        emotions = soup.find_all('emotion')
        for emotion in emotions:
            # for some reason, BeautifulSoup does not see the capitals in
            # <externalRef>
            emotion_labels = emotion.find_all('externalref')
            ems = [l['reference'] for l in emotion_labels if l['reference'].startswith('emotionType:')]
            for el in emotion_labels:
                if el['resource'] == 'heem':
                    label = el['reference']
                    if not events.get(label):
                        events[label] = event(label, text_id)
                    events[label]['mentions'].append(mention(emotion, soup, text_id))
                elif el['resource'] == 'heem:bodyParts':
                    for e in ems:
                        events[e]['actors'][el['reference']] = [el['reference']]
        print events.keys()

        json_out = {
            'timeline': {
                'events': [],
                'sources': []
            }
        }

        json_out['timeline']['sources'] = [{'uri': 'alew001besl01', 'text': 'bla bla'}]

        for event, data in events.iteritems():
            data['climax-score'] = len(data['mentions'])/num_sentences*100.0
            #        'actors': {},
            #        'climax-score': 0,
            #        'event': 'emotion_label',
            #        'group': "100:[\"{}\"]".format(text_id),
            #        'groupName': "[\"{}\"]".format(text_id),
            #        'groupScore': "100",
            #        'labels': [],
            #        'mentions': [],
            #        'prefLabel': ["offer"],
            #        'time': "20090730"
            json_out['timeline']['events'].append(data)
        with codecs.open(os.path.join(output_dir, '{}.json'.format(text_id)), 'wb', encoding='utf-8') as f:
            json.dump(json_out, f, sort_keys=True, indent=4)
