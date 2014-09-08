"""Insert KAF annotations into a FoLiA file.
Usage: python kaf2folia.py <kaf tags file> <folia file>
The folia file is the FoLiA XML file used to generate the KAF input files.
"""

import argparse
import codecs

class Annotation:
    def __init__(self, level, label, annotation_id, word_id):
        self.level = level
        self.label = label
        self.annotation_id = annotation_id
        self.word_ids = [word_id]


    def entity_id(self, annotation_class):
        return '{}.{}'.format(annotation_class, self.annotation_id)


    def folia_entity_class(self):
        tag_levels = {
            1: 'ee:emotionLabel1',
            2: 'ee:emotionLabel2',
            3: 'ee:category',
            4: 'ee:sensation',
            5: 'ee:sentation_modifier',
            6: 'ee:relation'
        }

        return '{}-{}'.format(tag_levels[self.level], self.label)


def add_entity(entity_layer, annotation, annotation_class):
    return 'Adding {} ({}; {})'.format(annotation.entity_id(annotation_class),
                                      annotation.folia_entity_class(),
                                      ' - '.join(annotation.word_ids))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('tag', help='the name of the KAF tag file ' \
                        'containing the annotations')
    parser.add_argument('folia', help='the name of the FoLiA XML file ')

    args = parser.parse_args()

    tag_file = args.tag
    folia_file = args.folia

    # Load KAF tags file
    with codecs.open(tag_file,'r','utf-8',errors='ignore') as f:
        lines = f.readlines()

    # Tag file is tab separated file
    # Each line contains 24 fields:
    # fields[0]: word id
    # fields[1]: token
    # fields[2]: lemma
    # fields[3]: pos tag
    # fields[4]: empty
    # fields[5]: tag level 1 label
    # fields[6]: tag id (level 1)
    # fields[7]: tag level 2 label
    # fields[8]: tag id (level 2)
    # fields[9]: tag level 3 label
    # fields[10]: tag id (level 3)
    # fields[11]: tag level 4 label
    # fields[12]: tag id (level 4)
    # fields[13]: tag level 5 label
    # fields[14]: tag id (level 5)
    # fields[15]: tag level 6 label
    # fields[16]: tag id (level 6)

    # NOT USED IN THE EMBODIED EMOTIONS PROJECT
    # fields[17]: tag level 7 label
    # fields[18]: tag id (level 7)
    # fields[19]: tag level 8
    # fields[20]: tag id (level 8)
    # fields[21]: number (unclear what it means)
    # fields[22]: 'true' (unclear what it means)
    # fields[23]: number (unclear what it means)

    annotations = {}

    # (annotation label, annotation id, level)
    levels = [(5, 6, 1), (7, 8, 2), (9, 10, 3), (11, 12, 4), (13, 14, 5),
              (15, 16, 6)]

    for line in lines:

        fields = line.strip().split('\t')

        for level in levels:
            word_id = fields[0]
            annotation_id = int(fields[level[1]])
            annotation_label = fields[level[0]]

            if annotation_id != 0:

                if not annotations.get(annotation_id):
                    # new annotation
                    annotations[annotation_id] = Annotation(level[2],
                                                            annotation_label,
                                                            annotation_id,
                                                            word_id)
                else:
                    # known annotation: append word_id
                    annotations[annotation_id].word_ids.append(word_id)

    order = annotations.keys()
    order.sort()

    for a in order:
        print add_entity(None, annotations[a], 'embodied_emotions')

    # Load FoLiA file
    #with open(folia_file, 'r') as f:
    #    soup = BeautifulSoup(f, 'xml')
