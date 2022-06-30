VENV=venv/bin/activate

SCAN=output/ocha-3w-resources.csv

PARSE=output/ocha-3w-orgs.csv

OUTPUT_DIR=output

DOWNLOAD_DIR=$(OUTPUT_DIR)/downloads

DOWNLOADED=$(DOWNLOAD_DIR)/.downloaded

all: combine

scan: $(SCAN)

parse: $(PARSE)

$(VENV): requirements.txt
	rm -rf venv && virtualenv venv && . $(VENV) && pip install -r requirements.txt

$(SCAN): scan.py $(VENV)
	. $(VENV) && python scan.py > output/temp.csv && mv output/temp.csv $(SCAN)

$(PARSE): $(SCAN) $(VENV) FORCE
	. $(VENV) && cat $(SCAN) | python parse.py

download: $(DOWNLOADED)

$(DOWNLOADED):
	. $(VENV) && rm -rf $(DOWNLOAD_DIR) && python download-3w.py $(DOWNLOAD_DIR) && touch $(DOWNLOADED)

combine: $(VENV) $(DOWNLOADED)
	. $(VENV) && python combine-3w.py $(DOWNLOAD_DIR)/*.csv > $(OUTPUT_DIR)/combined-3w.csv

FORCE:

clean:
	rm -rf $(SCAN) $(PARSE) $(DOWNLOAD_DIR)
