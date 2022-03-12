VENV=venv/bin/activate

SCAN=output/$(shell date +%Y%m%d)-ocha-3w-resources.csv

PARSE=output/$(shell date +%Y%m%d)-ocha-3w-orgs.csv

all: scan parse

venv_activate: $(VENV)

scan: $(SCAN)

parse: $(PARSE)

$(VENV): requirements.txt
	rm -rf venv && virtualenv venv && . $(VENV) && pip install -r requirements.txt

$(SCAN): scan.py $(VENV)
	. $(VENV) && python scan.py > output/temp.csv && mv output/temp.csv $(SCAN)

$(PARSE): $(SCAN) $(VENV)
	. $(VENV) && cat $(SCAN) | python parse.py
