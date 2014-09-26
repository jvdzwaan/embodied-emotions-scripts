#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Script to put a folia xml file in ElasticSearch.
"""
import sys
import os
import argparse
from elasticsearch import Elasticsearch
from lxml import etree
from bs4 import BeautifulSoup
from emotools.plays import extract_character_name, xml_id2play_id
from emotools.bs4_helpers import sentence, note


def create_index(es, index_name, type_name):
    config = {}
    config['mappings'] = {
        type_name: {
            '_id': {
                'path': 'event_id'
            },
            'properties': {
                'event_id': {
                    'type': 'string',
                    'include_in_all': 'false',
                    'index': 'not_analyzed'
                },
                'text_id': {
                    'type': 'string',
                    'include_in_all': 'false',
                    'index': 'not_analyzed'
                },
                'event_class': {
                    'type': 'string',
                    'include_in_all': 'false',
                    'index': 'not_analyzed'
                },
                'speaker': {
                    'type': 'string',
                    'include_in_all': 'false',
                    'index': 'not_analyzed'
                },
                'order': {
                    'type': 'integer',
                },
                'text': {
                    'type': 'string',
                    'include_in_all': 'false',
                    'index': 'analyzed'
                },
            }
        }
    }
    es.indices.create(index=index_name, body=config, ignore=400)


def event2es(event_xml, event_order, es, index_name, type_name):

    events = event_xml.find_all('event')
    if len(events) > 1:
        print 'subevents!'
        print events[0].attrs.get('xml:id')
        sys.exit(1)
    elif len(events) == 1:
        event = events[0]
        event_id = event.attrs.get('xml:id')
        play_id = xml_id2play_id(event_id)

        cls = event.attrs.get('class')
        if cls == 'speakerturn':
            actor = extract_character_name(event.attrs.get('actor'))

        text = []
        for elem in event.descendants:
            if sentence(elem) and not note(elem.parent):
                text.append(elem.t.string)

        doc = {
            'event_id': event_id,
            'text_id': play_id,
            'event_class': cls,
            'order': event_order,
            'text': ' '.join(text)
        }
        if cls == 'speakerturn':
            doc['actor'] = actor

        es.index(index_name, type_name, doc)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('dir', help='the name of the directory containing the '
                        'FoLiA XML files that should be processed')
    args = parser.parse_args()

    input_dir = args.dir

    # TODO: ES host + port as script arguments
    es = Elasticsearch()

    # TODO: index name as script argument
    index_name = 'embodied_emotions'
    type_name = 'event'
    create_index(es, index_name, type_name)

    event_tag = '{http://ilk.uvt.nl/folia}event'

    os.chdir(input_dir)
    for file_name in os.listdir(input_dir):
        print file_name

        # load document
        context = etree.iterparse(file_name,
                                  events=('start', 'end'),
                                  tag=event_tag)

        order = 0
        delete = True
        for event, elem in context:
            if event == 'start':
                delete = False
            if event == 'end':
                order += 1
                event_xml = BeautifulSoup(etree.tostring(elem), 'xml')
                event2es(event_xml, order, es, index_name, type_name)
                delete = True

            if delete:
                elem.clear()
                while elem.getprevious() is not None:
                    del elem.getparent()[0]
        del context
