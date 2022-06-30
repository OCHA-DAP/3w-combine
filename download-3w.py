""" Download local copies for 3W datasets from a master spreadsheet of links
"""

import csv, hxl, logging, os, sys
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__file__)

LIST = "https://docs.google.com/spreadsheets/d/1CWV75enZEh26lYuidnCKyEyQxpzEzcIJp_qF-i_jhik/edit#gid=1013429077"

# Command line
if len(sys.argv) == 2:
    dir = sys.argv[1]
else:
    logger.fatal("Usage: %s <output-dir>", sys.argv[0])
    sys.exit(2)

# Each of LIST is information about one OCHA 3W dataset
with hxl.data(LIST) as input:

    # Create the output directory if necessary
    path = Path(__file__).parent / dir
    path.mkdir(parents=True, exist_ok=True)

    # Read each row of 3W dataset info
    for info in input:
        country_name = info.get("#country+name").upper()
        country_code = info.get("#country+code").upper()
        dataset = info.get("#x_dataset+code")
        url = info.get("#x_resource+url")

        logger.info("Processing %s %s %s", country_code, dataset, url)

        name_spec = "Country name#country+name=" + country_name
        code_spec = "Country code#country+code=" + country_code

        try:
            source = hxl.data(url, hxl.input.InputOptions(scan_ckan_resources=True)).add_columns((name_spec, code_spec,), True)
            source.columns # make sure the source is valid

            # The output file
            file = path / (country_code + ".csv")

            # Read the 3W row by row and write to the output file
            with open(file, "w") as output:
                writer = csv.writer(output)
                writer.writerow(source.headers)
                writer.writerow(source.display_tags)
                for row in source:
                    writer.writerow(row.values)
                        
        except Exception as e:
            # Simply note anything that doesn't parse and keep going
            logger.exception(e)

sys.exit(0)

                

            


