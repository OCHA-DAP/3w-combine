VENV=venv/bin/activate

SCAN=output/ocha-3w-resources.csv

PARSE=output/ocha-3w-orgs.csv

OUTPUT_DIR=output

DOWNLOAD_DIR=$(OUTPUT_DIR)/downloads

DOWNLOADED=$(DOWNLOAD_DIR)/.downloaded

COMBINED=$(OUTPUT_DIR)/combined-3w.csv

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
	. $(VENV) && python combine-3w.py $(DOWNLOAD_DIR)/*.csv > $(COMBINED)

org-data: $(OUTPUT_DIR)/org-data.csv

$(OUTPUT_DIR)/org-data.csv: $(OUTPUT_DIR)/orgs-impl.csv $(OUTPUT_DIR)/orgs-funder.csv $(OUTPUT_DIR)/orgs-prog.csv $(OUTPUT_DIR)/orgs-participating.csv
	cp $(OUTPUT_DIR)/orgs-impl.csv $@
	hxlclean --remove-headers --strip-tags $(OUTPUT_DIR)/orgs-funder.csv >> $@
	hxlclean --remove-headers --strip-tags $(OUTPUT_DIR)/orgs-prog.csv >> $@
	hxlclean --remove-headers --strip-tags $(OUTPUT_DIR)/orgs-participating.csv >> $@

$(OUTPUT_DIR)/orgs-impl.csv: $(COMBINED)
	cat $(COMBINED) | hxlcut -i org+impl+name,org+impl+type | hxlselect -q "#org+impl+name is not empty" | hxlrename -r "#org+impl+name:Org name#org+name" | hxlrename -r "#org+impl+type:Org type#org+type" | hxladd -b -s "Acronym#org+acronym=" | hxladd -s "Org role#org+role=impl" > $@

$(OUTPUT_DIR)/orgs-funder.csv: $(COMBINED)
	cat $(COMBINED) | hxlcut -i org+funder+name,org+funder+type | hxlselect -q "#org+funder+name is not empty" | hxlrename -r "#org+funder+name:Org name#org+name" | hxlrename -r "#org+funder+type:Org type#org+type" | hxladd -b -s "Acronym#org+acronym=" | hxladd -s "Org role#org+role=funder" > $@

$(OUTPUT_DIR)/orgs-prog.csv: $(COMBINED)
	cat $(COMBINED) | hxlcut -i org+prog+name,org+prog+type | hxlselect -q "#org+prog+name is not empty" | hxlrename -r "#org+prog+name:Org name#org+name" | hxlrename -r "#org+prog+type:Org type#org+type" | hxladd -b -s "Acronym#org+acronym=" | hxladd -s "Org role#org+role=prog" > $@

$(OUTPUT_DIR)/orgs-participating.csv: $(COMBINED)
	cat $(COMBINED) | hxlcut -i org+participating+acronym,org+participating+name,org+participating+type | hxlselect -q "#org+participating+name is not empty" | hxlrename -r "#org+participating+acronym:Acronym#org+acronym" | hxlrename -r "#org+participating+name:Org name#org+name" | hxlrename -r "#org+participating+type:Org type#org+type" | hxladd -s "Org role#org+role=participating" > $@

FORCE:

clean:
	rm -rf $(SCAN) $(PARSE) $(DOWNLOAD_DIR)
