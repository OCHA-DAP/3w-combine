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
    "Org type",
    "Attributes",
]

TAG_ROW = [
    "#meta+provider+code",
    "#meta+dataset+code",
    "#meta+columns_hash",
    "#country+code",
    "#org+name",
    "#org+role",
    "#org+type",
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
            if column.tag == "#org" and "type" not in column.attributes and "code" not in column.attributes:
                role = get_role(column)
                type_index = get_type_index(column, dataset.columns)
                indexed_columns.append((i, role, type_index, column.attributes))
        logger.info("Successfully opened %s", url)
        parse_data_rows(output, scan_row, provider_code, dataset_code, dataset.columns_hash, countries, dataset, indexed_columns)
    except hxl.input.HXLTagsNotFoundException as e1:
        logger.debug("No HXL hashtags in %s", url)
    except Exception as e2:
        logger.exception(e2)

def parse_data_rows(output, scan_row, provider_code, dataset_code, columns_hash, countries, dataset, indexed_columns):
    for data_row in dataset:
        for country_code in countries:
            for indexed_column in indexed_columns:
                value= get_value(data_row.values, indexed_column[0])
                role = indexed_column[1]
                type = get_value(data_row.values, indexed_column[2])
                attributes = indexed_column[3]
                    
                output.writerow([
                    provider_code,
                    dataset_code,
                    columns_hash,
                    country_code,
                    value,
                    role,
                    type,
                    " | ".join(attributes),
                ])

def get_value(values, i):
    if i < len(values) and i > -1:
        return values[i]
    else:
        return None

def get_role(column):
    for role in ("funder", "prog", "impl", "partner",):
        if role in column.attributes:
            return role
    return None

def get_type_index(column, columns):
    for i, col in enumerate(columns):
        if col.tag == "#org" and "type" in col.attributes:
            return i
    return -1
            
run(scan_data, sys.stdout)
exit();
