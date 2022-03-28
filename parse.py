""" Download and parse the 3W files.

Reads from standard input.

Writes to standard output.
"""

import csv, hxl, logging, sys

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("3wtest-parser")

scan_data = hxl.data(hxl.make_input(sys.stdin.buffer))

HEADER_ROW = [
    "Provider",
    "Dataset",
    "Hash",
    "Country code",
    "Org name",
    "Org role",
    "Function",
    "Attributes",
]

TAG_ROW = [
    "#meta+provider+code",
    "#meta+dataset+code",
    "#meta+columns_hash",
    "#country+code",
    "#org+name",
    "#org+role",
    "#org+function",
    "#meta+attributes+list",
]

def run(scan_data, file):
    output = csv.writer(file)
    output.writerow(HEADER_ROW)
    output.writerow(TAG_ROW)
    for scan_row in scan_data:
        provider_code = scan_row.get("#org+id")
        dataset_code = scan_row.get("#x_dataset+id")
        countries = scan_row.get("#country+name").split(" | ")
        parse_dataset(output, scan_row, provider_code, dataset_code, countries)

def parse_dataset(output, scan_row, provider_code, dataset_code, countries):
    url = scan_row.get("#x_resource+url")
    try:
        dataset = hxl.data(url, http_headers={"User-Agent": "HDX-Developer-2015"})
        indexed_columns = []
        for i, column in enumerate(dataset.columns):
            if column.tag == "#org":
                role = get_role(column)
                function = get_function(column)
                indexed_columns.append((i, column, role, function, column.attributes))
        logger.info("Successfully opened %s", url)
        parse_data_rows(output, scan_row, provider_code, dataset_code, dataset.columns_hash, countries, dataset, indexed_columns)
    except:
        logger.warning("Cannot parse %s as HXL data", url)

def parse_data_rows(output, scan_row, provider_code, dataset_code, columns_hash, countries, dataset, indexed_columns):
    for data_row in dataset:
        for country_code in countries:
            for indexed_column in indexed_columns:
                try:
                    value= data_row.values[indexed_column[0]]
                except:
                    value=None
                output.writerow([
                    provider_code,
                    dataset_code,
                    columns_hash,
                    country_code,
                    value,
                    indexed_column[2],
                    indexed_column[3],
                    " | ".join(indexed_column[4]),
                ])

def get_function(column):
    for function in ("type", "code", "abbrev", "acronym", "name",):
        if function in column.attributes:
            return function
    return None

def get_role(column):
    for role in ("funder", "prog", "impl", "partner",):
        if role in column.attributes:
            return role
    return None
            
run(scan_data, sys.stdout)
exit();
