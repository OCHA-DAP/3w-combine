""" Download and parse the 3W files.

Reads from standard input.

Writes to standard output.
"""

import csv, hxl, logging, sys

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("3wtest-parser")

scan_data = hxl.data(hxl.make_input(sys.stdin.buffer))

countries = {}

def run(scan_data):
    for scan_row in scan_data:
        countries = scan_row.get("#country+name").split(" | ")
        parse_dataset(scan_row, countries)

def parse_dataset(scan_row, countries):
    url = scan_row.get("#x_resource+url")
    try:
        dataset = hxl.data(url, http_headers={"User-Agent": "HDX-Developer-2015"})
        indexed_columns = []
        for i, column in enumerate(dataset.columns):
            if column.tag == "#org":
                indexed_columns.append((i, column,))
        logger.info("Successfully opened %s", url)
        parse_data_rows(scan_row, countries, dataset, indexed_columns)
    except hxl.HXLException as e:
        logger.warning("Cannot parse %s as HXL data", url)

def parse_data_rows(scan_row, countries, dataset, indexed_columns):
    for data_row in dataset:
        for indexed_column in indexed_columns:
            value= data_row.values[indexed_column[0]]
            print(str(indexed_column[1]) + "=" + value)
            
run(scan_data)
exit();
