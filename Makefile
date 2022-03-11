VENV="venv/bin/activate"

SCAN="output/$(shell date +%Y%m%d)-ocha-3w-resources.csv"

scan: $(SCAN)

$(VENV): requirements.txt
	rm -rf venv
	python3 -m venv venv
	. $(VENV) && pip install -r requirements.txt

$(SCAN): scan.py $(VENV)
	. $(VENV) && python scan.py > output/temp.csv && mv output/temp.csv $(SCAN)
