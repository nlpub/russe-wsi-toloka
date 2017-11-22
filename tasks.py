#!/usr/bin/env python

import argparse
import csv
import re
import sys
import os
import json
from collections import defaultdict

SEPARATOR = re.compile(' *[,;] +\d+ +- +')
MEANING   = re.compile('^(\d+ +-){0,1} *(\'){0,1}')

parser = argparse.ArgumentParser()
parser.add_argument('--summary', required=True, type=argparse.FileType('r', encoding='UTF-8'))
parser.add_argument('--train', type=int)
parser.add_argument('word', type=argparse.FileType('r', encoding='UTF-8'), nargs='+')
args = parser.parse_args()

senses = {}

reader = csv.DictReader(args.summary, delimiter=',')

for row in reader:
    senses[row['word']] = {i + 1: re.sub(MEANING, '', sense)
                           for i, sense in enumerate(re.split(SEPARATOR, row['meaning BTS'].strip()))}

writer = csv.writer(sys.stdout, delimiter='\t', quoting=csv.QUOTE_MINIMAL)

if args.train is None:
    writer.writerow((
        'INPUT:id',
        'INPUT:lemma',
        'INPUT:left',
        'INPUT:word',
        'INPUT:right',
        'INPUT:senses'
    ))
else:
    writer.writerow((
        'INPUT:id',
        'INPUT:lemma',
        'INPUT:left',
        'INPUT:word',
        'INPUT:right',
        'GOLDEN:sense_id',
        'HINT:text',
        'INPUT:senses'
    ))

    count = defaultdict(lambda: defaultdict(lambda: 0))

def json_senses(lemma):
    array = [{'sense': sense, 'definition': definition} for sense, definition in senses[lemma].items()]
    return json.dumps(array)

id = 1

for f in args.word:
    lemma, *_ = os.path.basename(f.name).rpartition('.')

    reader = csv.reader(f, delimiter=',')

    for row in reader:
        if not row[0]:
            continue

        sense_id = int(row[0])

        if not sense_id in senses[lemma]:
            print('%s: sense_id is %d, but we have only %d' % (f.name, sense_id, max(senses[lemma].keys())), file=sys.stderr)
            continue

        left, word, right = row[1:4]

        if args.train is None:
            writer.writerow((str(id), lemma, left, word, right, json_senses(lemma)))
            id += 1
        else:
            if count[lemma][sense_id] < args.train:
                hint = 'В данном случае, слово «%s» имеет значение «%s».' % (lemma, senses[lemma][sense_id])
                writer.writerow((str(id), lemma, left, word, right, str(sense_id), hint, json_senses(lemma)))
                id += 1

            count[lemma][sense_id] += 1
