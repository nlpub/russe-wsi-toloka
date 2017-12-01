export LANG=en_US.UTF-8
export LC_COLLATE=C

TRAIN := $(shell find train -maxdepth 1 -regex '.*/[А-Яа-яЁё]+\.csv' | sort)
TEST  := $(shell find test  -maxdepth 1 -regex '.*/[А-Яа-яЁё]+\.csv' | sort)

all: tasks-train.tsv tasks-test.tsv

tasks-train.tsv:
	./tasks.py --summary=train/summary.csv --train=5 --shuffle=1 $(TRAIN) >tasks-train.tsv

tasks-test.tsv:
	./tasks.py --summary=test/summary.csv $(TEST) >tasks-test.tsv

tasks-eval.tsv:
	./tasks.py --train=9999 --summary=test/summary.csv $(TEST) >tasks-eval.tsv

report.tsv:
	./report.py tasks-eval.tsv aggregated_results_pool_1036853__2017_12_01.tsv > report.tsv

clean:
	rm -fv *.tsv
