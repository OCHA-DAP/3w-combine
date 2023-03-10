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

def scan(url, outfile, cutoff_date):
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
        "Dateset start date",
        "Dateset end date",
        "Country names",
        "Country codes",
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
        "#date+dataset+start",
        "#date+dataset+end",
        "#country+name+list",
        "#country+code+list",
        "#x_resource+id",
        "#x_resource+description",
        "#x_resource+url",
        "#date+resource+revised",
    ])

    # All packages tagged as 3Ws
    for package in crawler.packages(fq="vocab_Topics:\"{}\"".format(TAG_3W)):

        # Figure out the start and end dates for the dataset
        result = re.match(r'^\[(.+) TO (.+)\]$', package['dataset_date'])
        if not result:
            logger.error("Bad dataset date '%s' for %s", package[dataset_date], package['name'])
            continue
        dataset_start_date = result.group(1)[:10]
        dataset_end_date = result.group(2)[:10]

        # Skip if the dataset is before the cutoff
        if dataset_end_date != '*' and dataset_end_date < cutoff_date:
            logger.info("Skipping dataset %s (end date %s is too early)", package['name'], dataset_end_date)
            continue
        
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

            modified_date = resource["last_modified"][:10] # just the date portion

            if modified_date < cutoff_date:
                logger.info("Skipping resource %s in dataset %s: modified date %s is before cutoff", resource["name"], package["name"], modified_date)
                continue

            # Repeat for each country
            for country in countries:
                output.writerow([
                    org["name"], # "name" means "id" in CKAN-speak
                    org["title"],
                    package["name"],
                    package["title"],
                    dataset_start_date,
                    dataset_end_date if dataset_end_date != '*' else '',
                    country["title"], # the country name
                    country["name"].upper(), # the country code
                    resource["name"],
                    resource["description"],
                    resource["url"],
                    modified_date
                ]);


#
# Command-line entry point (if called as a script)
#

if __name__ == "__main__":

    if len(sys.argv) != 2:
        logger.error("Usage: %s CUTOFF_DATE > OUTPUT.csv", sys.argv[0])
        sys.exit(2)

    cutoff_date = sys.argv[1]
    
    scan(HDX_SITE, sys.stdout, cutoff_date)

# end

