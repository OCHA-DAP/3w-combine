""" Merge multiple 3Ws into one

Usage:
    python combine-3w.py <scan-result>

"""

import csv, hxl, logging, sys

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__file__)

OPTS = hxl.InputOptions(allow_local=True, http_headers={"User-Agent": "HDX-Developer-2015"})

HEADER_ROW = (
    "Org name",
    "Cluster or sector",
    "Country name",
    "Country code",
    "Admin1 name",
    "Admin1 code",
    "Admin2 name",
    "Admin2 code",
    "Date updated",
    "Provider name",
    "Provider HDX id",
)

HASHTAG_ROW = (
    "#org+name",
    "#sector",
    "#country+name",
    "#country+code",
    "#adm1+name",
    "#adm1+code",
    "#adm2+name",
    "#adm2+code",
    "#date+updated",
    "#meta+provider+name",
    "#meta+provider+id",
)


def generate_3w(file_or_url):
    """ Generator to produce the combined 3W dataset """
    countries_seen = set()

    # yield the first two rows
    yield HEADER_ROW
    yield HASHTAG_ROW

    # parse each of the input resources
    with hxl.data(file_or_url, OPTS) as resources:

        for resource in resources.sort('#date+resource', True):

            country_name = resource.get("#country+name")
            country_code = resource.get("#country+code")
            date_updated = resource.get("#date+resource")
            source_name = resource.get("#org+name")
            source_id = resource.get("#org+id")
            url = resource.get("#x_resource+url")

            if country_code in countries_seen:
                print("Skipping older dataset from {}".format(country_name), file=sys.stderr)
                continue

            print("Trying {} from {}...".format(url, source_id), file=sys.stderr)

            try:
                with hxl.data(url, OPTS) as input:

                    # See if this is really a 3W
                    for hashtag in ('#org', '#sector', '#adm1'):
                        if hashtag not in input.tags:
                            logger.warning("Missing %s (probably not a 3W): %s", hashtag, url)
                            continue

                    # If we get this far, it parsed as HXL, so add it to the countries seen
                    countries_seen.add(country_code)

                    # Does the 3W include its own country data?
                    has_country_info = '#country' in input.tags

                    # Process the data rows, repeating for each org
                    for row in input:

                        # This is the same for all rows
                        rest_of_row = [
                            row.get("#sector"),
                            row.get("#country-code") if has_country_info else country_name,
                            row.get("#country+code") if has_country_info else country_code,
                            row.get("#adm1-code"),
                            row.get("#adm1+code"),
                            row.get("#adm2-code"),
                            row.get("#adm2+code"),
                            date_updated,
                            source_name,
                            source_id,
                        ]

                        # TODO add acronym, role, and type when available
                        for org_name in row.get_all("#org-type-acronym"):
                            if org_name:
                                yield [org_name] + rest_of_row

            except IOError as e:
                logger.warning("%s: %s", url, str(e))



if __name__ == '__main__':
    output = csv.writer(sys.stdout)
    for row in generate_3w(sys.argv[1]):
        output.writerow(row)
