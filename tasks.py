#!/usr/bin/env python

import argparse
import csv
import re
import sys
import os
import json

# The format is (id, lemma, left, word, right, sense_id, senses)
HEADER = ('id', 'lemma', 'left', 'word', 'right', 'sense_id', 'senses')

SEPARATOR = re.compile(' *[,;] +\d+ +- +')
MEANING   = re.compile('^\d+ +- +')

parser = argparse.ArgumentParser()
parser.add_argument('--summary', required=True, type=argparse.FileType('r', encoding='UTF-8'))
parser.add_argument('word', type=argparse.FileType('r', encoding='UTF-8'), nargs='+')
args = parser.parse_args()

senses = {}

reader = csv.DictReader(args.summary, delimiter=',')

for row in reader:
    senses[row['word']] = {i + 1: sense for i, sense in enumerate(re.split(SEPARATOR, re.sub(MEANING, '', row['meaning BTS']).strip()))}

print('\t'.join(HEADER))

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

        print('\t'.join((str(id), lemma, left, word, right, str(sense_id), json.dumps(senses[lemma]))))

        id += 1
