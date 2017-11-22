export LANG=en_US.UTF-8
export LC_COLLATE=C

TRAIN := $(shell find train -maxdepth 1 -regex '.*/[А-Яа-яЁё]+\.csv' | sort)
TEST  := $(shell find test  -maxdepth 1 -regex '.*/[А-Яа-яЁё]+\.csv' | sort)

all: tasks-train.tsv tasks-test.tsv

tasks-train.tsv:
	./tasks.py --summary=train/summary.csv --train=5 --shuffle=1 $(TRAIN) >tasks-train.tsv

tasks-test.tsv:
	./tasks.py --summary=test/summary.csv $(TEST) >tasks-test.tsv

clean:
	rm -fv *.tsv
