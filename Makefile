export LANG=en_US.UTF-8
export LC_COLLATE=C

TRAIN := $(shell find train -maxdepth 1 -regex '.*/[А-Яа-яЁё]+\.csv' | sort)
TEST  := $(shell find test  -maxdepth 1 -regex '.*/[А-Яа-яЁё]+\.csv' | sort)

all: train test

train:

test: tasks-test.tsv toloka-test.tsv

toloka-train.tsv:
	./toloka.awk -F$$'\t' -vOFS=$$'\t' -vGOLD=1 tasks-train.tsv > toloka-train.tsv

toloka-test.tsv:
	./toloka.awk -F$$'\t' -vOFS=$$'\t' tasks-test.tsv > toloka-test.tsv

tasks-test.tsv:
	./tasks.py --summary=test/summary.csv $(TEST) >tasks-test.tsv

clean:
	rm -fv *.tsv
