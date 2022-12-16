""" Create a HXLated CSV of all HXLated HDX resources from OCHA offices (excluding FTS)

Writes to standard output.
"""

import ckancrawler, csv, logging, re, sys

from urllib.parse import quote

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("3wtest-scan")

OLD_TAG="who is doing what and where - 3w - 4w - 5w"
NEW_TAG="who is doing what and where-3w-4w-5w"

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
    
def process(tag):
    for package in crawler.packages(fq="vocab_Topics:\"{}\"".format(tag)):

        # Check if it's HXLated
        if 'hxl' not in [tag["name"] for tag in package["tags"]]:
            logger.warning("Skipping %s (not HXLated)", package["name"])
            continue

        org = package["organization"]
        countries = package["groups"]

        # OCHA offices only
        if re.match("^ocha-.*", org["name"]) and org["name"] not in ("ocha-ds", "ocha-fiss", "ocha-fts", "ocha-naas",):
            for resource in package["resources"]:
                output.writerow([
                    org["name"], # "name" means "id" in CKAN-speak
                    org["title"],
                    package["name"],
                    package["title"],
                    package["dataset_date"],
                    " | ".join([country["name"].upper() for country in countries]),
                    " | ".join([country["title"] for country in countries]),
                    resource["name"],
                    resource["description"],
                    resource["url"],
                    resource["last_modified"][:10], # just the date portion
                ]);

if __name__ == "__main__":
    for tag in (OLD_TAG, NEW_TAG,):
        print("Tag:", tag, file=sys.stderr)
        process(tag)


