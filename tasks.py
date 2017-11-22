#!/usr/bin/env python

import argparse
import csv
import re
import sys
import random
import os
import json
from collections import namedtuple, defaultdict
from functools import lru_cache

SEPARATOR = re.compile(' *[,;] +\d+ +- +')
MEANING   = re.compile('^(\d+ +-){0,1} *(\'){0,1}')

Task = namedtuple('Task', 'id lemma left word right sense_id hint senses')

parser = argparse.ArgumentParser()
parser.add_argument('--summary', required=True, type=argparse.FileType('r', encoding='UTF-8'))
parser.add_argument('--shuffle', type=int)
parser.add_argument('--train', type=int)
parser.add_argument('word', type=argparse.FileType('r', encoding='UTF-8'), nargs='+')
args = parser.parse_args()

if args.shuffle is not None:
    random.seed(args.shuffle)

senses = {}

reader = csv.DictReader(args.summary, delimiter=',')

for row in reader:
    senses[row['word']] = {i + 1: re.sub(MEANING, '', sense)
                           for i, sense in enumerate(re.split(SEPARATOR, row['meaning BTS'].strip()))}

@lru_cache(len(senses))
def senses_array(lemma):
    return [{'sense': sense, 'definition': definition}
             for sense, definition in senses[lemma].items()]

count, id = defaultdict(lambda: defaultdict(lambda: 0)), 1

tasks = []

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

        hint = 'В данном случае, слово «%s» имеет значение «%s».' % (lemma, senses[lemma][sense_id])

        if args.train is None or count[lemma][sense_id] < args.train:
            tasks.append(Task(id, lemma, *row[1:4], sense_id, hint, senses[lemma]))
            id += 1

        count[lemma][sense_id] += 1

if args.shuffle:
    random.shuffle(tasks)

writer = csv.writer(sys.stdout, delimiter='\t', quoting=csv.QUOTE_MINIMAL)

if args.train is None:
    writer.writerow(('INPUT:id', 'INPUT:lemma', 'INPUT:left', 'INPUT:word',
                     'INPUT:right', 'INPUT:senses'))
else:
    writer.writerow(('INPUT:id', 'INPUT:lemma', 'INPUT:left', 'INPUT:word',
                     'INPUT:right', 'GOLDEN:sense_id', 'HINT:text',
                     'INPUT:senses'))

for task in tasks:
    senses_json = json.dumps(senses_array(task.senses))

    if args.train is None:
        writer.writerow((task.id, task.lemma, task.left, task.word, task.right, senses_json))
    else:
        writer.writerow((task.id, task.lemma, task.left, task.word, task.right, task.sense_id, task.hint, senses_json))
