CUTOFF_DATE="2022-02-28"

# Output files

OUTPUT_DIR=./output
SCANNED=$(OUTPUT_DIR)/ocha-3w-resources.csv
COMBINED_RAW=$(OUTPUT_DIR)/combined-3w-raw.csv
COMBINED_CLEANED=$(OUTPUT_DIR)/combined-3w-clean.csv

# Reports
REPORT_COUNTRY=$(OUTPUT_DIR)/3w-op-country.csv
REPORT_ADMIN1=$(OUTPUT_DIR)/3w-op-admin1.csv
REPORT_ADMIN2=$(OUTPUT_DIR)/3w-op-admin2.csv
REPORTS=$(REPORT_COUNTRY) $(REPORT_ADMIN1) $(REPORT_ADMIN2)

# Support files

INPUT_DIR=./input
SECTOR_MAP=$(INPUT_DIR)/sector-map.csv
SECTOR_NAME_MAP=$(INPUT_DIR)/sector-name-map.csv

# Virtual environment

VENV=venv/bin/activate


all: reports

scan: $(SCANNED)

combine: $(COMBINED_RAW)

cleaned: $(COMBINED_CLEANED)

reports: report-country report-admin1 report-admin2

report-country: $(REPORT_COUNTRY)

report-admin1: $(REPORT_ADMIN1)

report-admin2: $(REPORT_ADMIN2)

$(SCANNED): scan-hdx.py $(VENV)
	rm -f $(SCANNED)
	. $(VENV) && python scan-hdx.py $(CUTOFF_DATE) > output/temp.csv
	mv output/temp.csv $(SCANNED)

$(COMBINED_RAW): combine-3w.py $(SCANNED) $(VENV)
	rm -f $(COMBINED_RAW)
	. $(VENV) && python combine-3w.py $(SCANNED) > output/temp.csv
	mv output/temp.csv $(COMBINED_RAW)

$(COMBINED_CLEANED): clean-3w.sh $(COMBINED_RAW) $(SECTOR_MAP) $(SECTOR_NAME_MAP) $(VENV)
	rm -f $(COMBINED_CLEANED)
	. $(VENV) && cat $(COMBINED_RAW) | sh clean-3w.sh $(SECTOR_MAP) $(SECTOR_NAME_MAP) > output/temp.csv
	mv output/temp.csv $(COMBINED_CLEANED)

#
# Reports
#

$(REPORT_COUNTRY): $(COMBINED_CLEANED) $(VENV)
	rm -f $(REPORT_COUNTRY)
	. $(VENV) && cat $(COMBINED_CLEANED) \
	| hxlexpand -t country+name,country+code \
	| hxlcount -t org+name,org+acronym,sector+name+norm,sector+code,country+name,country+code \
	| hxlcut -x meta+count \
	> output/temp.csv
	mv output/temp.csv $(REPORT_COUNTRY)

$(REPORT_ADMIN1): $(COMBINED_CLEANED) $(VENV)
	rm -f $(REPORT_ADMIN1)
	. $(VENV) && cat $(COMBINED_CLEANED) \
	| hxlexpand -t country+name,country+code \
	| hxlcount -t org+name,org+acronym,sector+name+norm,sector+code,country+name,country+code,adm1+name,adm1+code \
	| hxlcut -x meta+count \
	> output/temp.csv
	mv output/temp.csv $(REPORT_ADMIN1)

$(REPORT_ADMIN2): $(COMBINED_CLEANED) $(VENV)
	rm -f $(REPORT_ADMIN2)
	. $(VENV) && cat $(COMBINED_CLEANED) \
	| hxlexpand -t country+name,country+code \
	| hxlcount -t org+name,org+acronym,sector+name+norm,sector+code,country+name,country+code,adm1+name,adm1+code,adm2+name,adm2+code \
	| hxlcut -x meta+count \
	> output/temp.csv
	mv output/temp.csv $(REPORT_ADMIN2)

#
# General management
#

build-venv: $(VENV)

$(VENV): requirements.txt
	rm -rf venv && python3 -m venv venv && . $(VENV) && pip install -r requirements.txt

clean-reports:
	rm -f $(REPORTS)

clean: clean-reports
	rm -f $(COMBINED_CLEAN)

clean-all: clean
	rm -f $(COMBINED_RAW) $(SCANNED)
