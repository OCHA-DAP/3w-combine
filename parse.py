""" Download and parse the 3W files.

Reads from standard input.

Writes to standard output.
"""

import csv, hxl, logging, sys

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("3wtest-parser")

scan_data = hxl.data(hxl.make_input(sys.stdin.buffer))

ROLE_PRIORITIES = {
    "funder": 0,
    "prog": 1,
    "impl": 3,
    "partner": 3
}

HEADER_ROW = [
    "Org name",
    "Org role",
    "Org type",
    "Cluster",
    "Country p-code",
    "Admin1 name",
    "Admin1 p-code",
    "Admin2 name",
    "Admin2 p-code",
    "Provider",
    "Dataset",
    "Hash",
]

TAG_ROW = [
    "#org+name",
    "#org+role",
    "#org+type",
    "#sector",
    "#country+code",
    "#adm1+name",
    "#adm1+code",
    "#adm2+name",
    "#adm2+code",
    "#meta+provider",
    "#meta+dataset",
    "#meta+columns_hash",
]

def run(scan_data, file):
    output = csv.writer(file)
    output.writerow(HEADER_ROW)
    output.writerow(TAG_ROW)
    for scan_row in scan_data:
        provider_code = scan_row.get("#org+id")
        dataset_code = scan_row.get("#x_dataset+id")
        countries = scan_row.get("#country+name").upper().split(" | ")
        parse_dataset(output, scan_row, provider_code, dataset_code, countries)

def parse_dataset(output, scan_row, provider_code, dataset_code, countries):
    url = scan_row.get("#x_resource+url")
    try:
        dataset = hxl.data(url, http_headers={"User-Agent": "HDX-Developer-2015"})
        priority_org_index = get_priority_org_index(dataset.columns) # which org gets the +type ?
        sector_index = get_index("#sector", dataset.columns)
        adm1_name_index = get_index("#adm1-code", dataset.columns)
        adm1_code_index = get_index("#adm1+code", dataset.columns)
        adm2_name_index = get_index("#adm2-code", dataset.columns)
        adm2_code_index = get_index("#adm2+code", dataset.columns)
        indexed_columns = []
        for i, column in enumerate(get_org_columns(dataset.columns)):
            org_role = get_role(column)
            if i == priority_org_index:
                org_type_index = get_index("#org+type", dataset.columns)
            else:
                org_type_index = None
            indexed_columns.append({
                "org_name_index": i,
                "org_role": org_role,
                "org_type_index": org_type_index,
                "sector_index": sector_index,
                "adm1_name_index": adm1_name_index,
                "adm1_code_index": adm1_code_index,
                "adm2_name_index": adm2_name_index,
                "adm2_code_index": adm2_code_index,
            })
        parse_data_rows(output, scan_row, provider_code, dataset_code, dataset.columns_hash, countries, dataset, indexed_columns)
        logger.debug("Successfully opened %s", url)
    except hxl.input.HXLTagsNotFoundException as e1:
        logger.debug("No HXL hashtags in %s", url)
    except Exception as e2:
        logger.exception(e2)

def parse_data_rows(output, scan_row, provider_code, dataset_code, columns_hash, countries, dataset, indexed_columns):
    for data_row in dataset:
        for country_code in countries:
            for indexed_column in indexed_columns:                    
                output.writerow([
                    get_value(data_row.values, indexed_column["org_name_index"]),
                    indexed_column["org_role"],
                    get_value(data_row.values, indexed_column["org_type_index"]),
                    get_value(data_row.values, indexed_column["sector_index"]),
                    country_code,
                    get_value(data_row.values, indexed_column["adm1_name_index"]),
                    get_value(data_row.values, indexed_column["adm1_code_index"]),
                    get_value(data_row.values, indexed_column["adm2_name_index"]),
                    get_value(data_row.values, indexed_column["adm2_code_index"]),
                    provider_code,
                    dataset_code,
                    columns_hash,
                ])

def get_index(pattern, columns):
    pattern = hxl.TagPattern.parse(pattern)
    for i, column in enumerate(columns):
        if pattern.match(column):
            return i
    return -1

def get_value(values, i):
    """ Look up a value in an array, returning None for out-of-range indices
    """
    if i is not None and i < len(values) and i >= 0:
        return values[i]
    else:
        return None

def get_role(column):
    """ Get an organisation's role from well-known attributes
    """
    for role in ("funder", "prog", "impl", "partner",):
        if role in column.attributes:
            return role
    return None

def get_org_columns(columns):
    """ Return indices for all columns that contain an org name
    """
    result = []
    for i, column in enumerate(columns):
        if column.tag == "#org" and "type" not in column.attributes and "code" not in column.attributes:
            result.append(column)
    return result

def get_priority_org_index(columns):
    """ Return the index of the column with the priority org for type info
    """
    last_priority = -1
    index = -1
    for i, column in enumerate(columns):
        if column.tag == "#org" and "type" not in column.attributes and "code" not in column.attributes:
            role = get_role(column)
            priority = ROLE_PRIORITIES.get(role, 2)
            if priority > last_priority:
                index = i
                last_priority = priority
    return index

run(scan_data, sys.stdout)
exit();
