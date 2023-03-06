""" Scan HDX to create a HXLated CSV of all HXLated 3W resources from OCHA field offices

Started 2022 by David Megginson

"""

import ckancrawler, csv, logging, re, sys


#
# Logging
#

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("3wtest-scan")


#
# Constants
#

HDX_SITE = 'https://data.humdata.org'
""" HDX site to query """

USER_AGENT = 'HDX-Developer-2015'
""" User-agent string to exclude from analytics """

DELAY = 0
""" Delay in seconds between CKAN API requests """

TAG_3W = 'who is doing what and where-3w-4w-5w'
""" CKAN tag for 3W """

TAG_HXL = 'hxl'
""" CKAN tag for HXL """

ORG_RE = r'^ocha-.*'
""" Everything matching this pattern is assumed to be an OCHA org """

ORG_EXCLUSIONS = ('ocha-ds', 'ocha-fiss', 'ocha-fts', 'ocha-naas',)
""" Anything in this list is not an OCHA field office """


#
# Main processing
#

def scan(url, outfile):
    """ Scan an HDX site for OCHA 3W resources and save to a HXLated CSV file.

    Parameters:

    url (string) The URL of the HDX site to scan
    outfile (file) A file-like object to which to save the CSV output

    """

    crawler = ckancrawler.Crawler(url, delay=DELAY, user_agent=USER_AGENT)

    output = csv.writer(outfile)

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

    # All packages tagged as 3Ws
    for package in crawler.packages(fq="vocab_Topics:\"{}\"".format(TAG_3W)):

        org = package["organization"]

        # Check if it's from an OCHA field office
        if not re.match(ORG_RE, org["name"]) or org["name"] in ORG_EXCLUSIONS:
            logger.warning("Skipping %s from %s (not from an OCHA field office)", package["name"], org["name"])
            continue
            
        # Check if it's HXLated
        if TAG_HXL not in [tag["name"] for tag in package["tags"]]:
            logger.warning("Skipping %s from %s (not HXLated)", package["name"], org["name"])
            continue

        # OK, good to go!
        logger.info("Found OCHA 3W dataset %s", package["name"])

        countries = package["groups"]

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


#
# Command-line entry point (if called as a script)
#

if __name__ == "__main__":
    scan(HDX_SITE, sys.stdout)

# end

