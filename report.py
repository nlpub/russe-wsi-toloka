#!/usr/bin/env python

import argparse
import csv
import json
import sys
from collections import namedtuple

Task = namedtuple('Task', 'id lemma left word right sense_id hint senses')
Aggregation = namedtuple('Aggregation', 'id lemma left word right sense_id confidence')

parser = argparse.ArgumentParser()
parser.add_argument('--unsure', type=float, default=.85)
parser.add_argument('tasks', type=argparse.FileType('r', encoding='UTF-8'))
parser.add_argument('toloka', type=argparse.FileType('r', encoding='UTF-8'))
args = parser.parse_args()

tasks, senses = [], {}

reader = csv.DictReader(args.tasks, delimiter='\t')

for row in reader:
    id = int(row['INPUT:id'])

    lemma = row['INPUT:lemma']
    sense_id = int(row['GOLDEN:sense_id'])

    left, word, right = row['INPUT:left'], row['INPUT:word'], row['INPUT:right']

    hint = row['HINT:text']

    if not lemma in senses:
        senses[lemma] = json.loads(row['INPUT:senses'])

    tasks.append(Task(id, lemma, left, word, right, sense_id, hint, senses[lemma]))

reader = csv.DictReader(args.toloka, delimiter='\t')

aggregations = {}

for row in reader:
    id = int(row['INPUT:id'])
    lemma = row['INPUT:lemma']
    left, word, right = row['INPUT:left'], row['INPUT:word'], row['INPUT:right']
    sense_id = int(row['OUTPUT:sense_id'])
    confidence = float(row['CONFIDENCE:sense_id'].strip('%')) / 100

    aggregations[id] = Aggregation(id, lemma, left, word, right, sense_id, confidence)

writer = csv.writer(sys.stdout, delimiter='\t')
writer.writerow(
    ('id', 'lemma', 'changed', 'unsure', 'prior_sense_id', 'sense_id', 'confidence', 'left', 'word', 'right', 'senses'))

for task in tasks:
    if task.id in aggregations:
        aggregation = aggregations[task.id]
        assert task.lemma == aggregation.lemma, 'task and aggregation lemmas differ'
        assert task.left == aggregation.left, 'task and aggregation lefts differ'
        assert task.word == aggregation.word, 'task and aggregation words differ'
        assert task.right == aggregation.right, 'task and aggregation rights differ'

        changed = int(task.sense_id != aggregation.sense_id)
        unsure = int(aggregation.confidence < args.unsure)
        confidence = aggregation.confidence
        aggregated_sense_id = aggregation.sense_id
    else:
        changed, unsure = int(True), int(True)
        confidence, aggregated_sense_id = 0, 0

    if aggregated_sense_id > len(senses[task.lemma]):
        print('Task %d, word "%s" has strange sense_id=%d.' % (task.id, task.lemma, aggregated_sense_id),
              file=sys.stderr)

    senses_str = '; '.join('%d - %s' % (sense['sense'], sense['definition'])
                           for sense in senses[task.lemma])

    writer.writerow((task.id, task.lemma, changed, unsure,
                     task.sense_id, aggregated_sense_id, '%.4f' % confidence,
                     task.left, task.word, task.right,
                     senses_str))
