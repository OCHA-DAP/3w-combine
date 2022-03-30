VENV=venv/bin/activate

SCAN=output/ocha-3w-resources.csv

PARSE=output/ocha-3w-orgs.csv

all: scan parse

venv_activate: $(VENV)

scan: $(SCAN)

parse: $(PARSE)

$(VENV): requirements.txt
	rm -rf venv && virtualenv venv && . $(VENV) && pip install -r requirements.txt

$(SCAN): scan.py $(VENV)
	. $(VENV) && python scan.py > output/temp.csv && mv output/temp.csv $(SCAN)

$(PARSE): $(SCAN) $(VENV) FORCE
	. $(VENV) && cat $(SCAN) | python parse.py

FORCE:

clean:
	rm -rf $(SCAN) $(PARSE)
