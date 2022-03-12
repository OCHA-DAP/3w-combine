""" Create a HXLated CSV of all HXLated HDX resources from OCHA offices (excluding FTS)

Writes to standard output.
"""

import ckancrawler, csv, logging, re, sys

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("3wtest-scan")

crawler = ckancrawler.Crawler("https://data.humdata.org", delay=0, user_agent="HDX-Developer-2015")

output = csv.writer(sys.stdout)

output.writerow([
    "Org id",
    "Org name",
    "Dataset id",
    "Dataset name",
    "Dateset date",
    "Country codes",
    "Country names",
    "Resource id",
    "Resource description",
    "Resource URL",
    "Resource date",
])

output.writerow([
    "#org+id",
    "#org+name",
    "#x_dataset+id",
    "#x_dataset+title",
    "#date+dataset",
    "#country+name+list",
    "#country+code+list",
    "#x_resource+id",
    "#x_resource+description",
    "#x_resource+url",
    "#date+resource+revised",
])
    

for package in crawler.packages(q="vocab_Topics=who%20is%20doing%20what%20and%20where%20-%203w%20-%204w%20-%205w&vocab_Topics=hxl"):
    org = package["organization"]
    countries = package["groups"]

    # OCHA offices only
    if re.match("^ocha-.*", org["name"]) and org["name"] != "ocha-fts":
        for resource in package["resources"]:
            output.writerow([
                org["name"], # "name" means "id" in CKAN-speak
                org["title"],
                package["name"],
                package["title"],
                package["dataset_date"],
                " | ".join(country["name"] for country in countries),
                " | ".join(country["title"] for country in countries),
                resource["name"],
                resource["description"],
                resource["url"],
                resource["last_modified"][:10], # just the date portion
            ]);

exit();
