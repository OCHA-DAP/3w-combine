CUTOFF_DATE="2022-02-28"

SCAN=output/ocha-3w-resources.csv

OUTPUT_DIR=output

DOWNLOAD_DIR=$(OUTPUT_DIR)/downloads

DOWNLOADED=$(DOWNLOAD_DIR)/.downloaded

COMBINED_RAW=$(OUTPUT_DIR)/combined-3w-raw.csv

COMBINED_FIXED=$(OUTPUT_DIR)/combined-3w-clean.csv

VENV=venv/bin/activate


all: scan combine fix

scan: scan-hdx.py $(VENV)
	. $(VENV) && python scan.py > output/temp.csv && mv output/temp.csv $(SCAN)

combine: combine-3w.py $(VENV) 
	. $(VENV) && python combine-3w.py $(SCAN) > $(COMBINED_RAW)

fix: $(VENV)
	. $(VENV) && cat $(COMBINED_RAW) \
		| hxlselect -q "date > $(CUTOFF_DATE)" \
		| hxlselect -q '#org+name ~ .*[a-zA-Z].*' \
		| hxlsort -t date -r \
		| hxldedup -t org,sector,country,adm1,adm2 \
		| hxlsort -t country+name,adm1+name,adm2+name,sector,org+name \
		> $(COMBINED_FIXED)

$(VENV): requirements.txt
	rm -rf venv && python3 -m venv venv && . $(VENV) && pip install -r requirements.txt


