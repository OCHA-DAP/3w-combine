""" Merge multiple 3Ws into one (step 2)

Usage:
    python combine-3w.py SCAN.csv > COMBINED.csv

This is the most-complex script in the workflow. It takes the output
from scan-hdx.py (a list of candidate HXLated 3W resources from OCHA
offices, with metadata) and does the following:

- download each of the resources
- determines if it is actually a 3W and HXLated
- extracts the org information into separate columns

The output is not yet aggregated to a 3W-OP.

"""

import csv, hxl, logging, sys

logger = logging.getLogger(__file__)
""" Logger object for this module """


ROLE_MAP = {
    'funder': 'funder',
    'funding': 'funder',
    'prog': 'prog',
    'impl': 'impl',
    'partner': 'impl',
}
""" Map of HXL attributes to org roles """


HEADER_ROW = (
    "Org name",
    "Org acronym",
    "Org role",
    "Org type",
    "Cluster or sector",
    "Country name",
    "Country code",
    "Admin1 name",
    "Admin1 code",
    "Admin2 name",
    "Admin2 code",
    "Dateset id",
    "Dataset start date",
    "Dataset end date",
    "Resource id",
    "Resource update date",
    "Provider name",
    "Provider HDX id",
)
""" Row of human-readable column labels """


HASHTAG_ROW = (
    "#org+name",
    "#org+acronym",
    "#org+role",
    "#org+type",
    "#sector+name",
    "#country+name",
    "#country+code",
    "#adm1+name",
    "#adm1+code",
    "#adm2+name",
    "#adm2+code",
    "#x_dataset+id",
    "#date+dataset+start",
    "#date+dataset+end",
    "#x_resource+id",
    "#date+resource+updated",
    "#meta+provider+name",
    "#meta+provider+id",
)
""" Row of machine-readable #HXL hashtags """


OPTS = hxl.InputOptions(
    allow_local=True,
    http_headers={"User-Agent": "HDX-Developer-2015"},
)
""" Input options for opening HXLated datasets """


def to_str (v):
    """ Convert value to a string, returning an empty string for None """
    if v is None:
        return ''
    else:
        return str(v)


#
# Special handling for orgs
#

def prescan_orgs(cols):
    """ Prescan columns to figure out where we're going to pull our organisation information

    The result is a dict keyed by role (see the values of ROLE_MAP).

    The value for each role is a dict with the keys 'name', 'acronym', and 'type', pointing to the zero-based
    column numbers containing the name and acronym (if present). At least one of 'name' or 'acronym' will
    always be present. If there is no column for a value (e.g. no acronym), the key will not appear.

    Example:

      {
        'impl': {
          'name': 0,
          'acronym': 1,
          'type': 2,
        'funder': {
          'name': 3,
        },
      }

    """
    
    def get_org_role(col):
        """ Find the first role attribute for an #org column """
        for att, role in ROLE_MAP.items():
            if att in col.attributes:
                return role
        return ''


    result = {}

    # First, get the org names
    for i, col in enumerate(cols):

        # FIXME special case for Mali
        if col.tag == '#actor':
            result['funder'] = {
                'name': i,
            }
            continue

        if col.tag != '#org' or ('acronym' in col.attributes) or ('type' in col.attributes):
            continue

        role = get_org_role(col)
        result[role] = { 'name': i, }

    # Next, get the org acronyms
    for i, col in enumerate(cols):
        if col.tag != '#org' or 'acronym' not in col.attributes:
            continue
        role = get_org_role(col)
        if role in result:
            result[role]['acronym'] = i
        else:
            result[role] = {
                'name': i,
                'acronym': i,
            }

    # Finally, get the org types
    for i, col in enumerate(cols):
        if col.tag != '#org' or 'type' not in col.attributes:
            continue

        role = get_org_role(col)
        if role in result:
            result[role]['type'] = i
        else:
            logger.error("Org type but no org name or acronym")

    return result


#
# Main generation function
#

def generate_3w(file_or_url):
    """ Generator to produce the combined 3W dataset

    This function yields one array at a time, representing
    a row in the output CSV (including headers and HXL hashtags).

    """

    def get_value(row, info, key):
        """ Look up a value by position using key in info

        This function uses the indices produced by prescan_orgs, above.

        """
        if key in info:
            try:
                return row.values[info[key]]
            except IndexError:
                pass
        return ''

    # Keep track of resources we've already seen
    resources_seen = set()

    # yield the first two rows
    yield HEADER_ROW
    yield HASHTAG_ROW

    # parse each of the input resources
    with hxl.data(file_or_url, OPTS) as resources:

        # We assume the first usable resource is the most recent
        for resource in resources.sort('#date+resource', True):

            country_name = resource.get("#country+name")
            country_code = resource.get("#country+code").upper()
            date_start = resource.get("#date+dataset+start")
            date_end = resource.get("#date+dataset+end")
            date_updated = resource.get("#date+resource+updated")
            source_name = resource.get("#org+name")
            source_id = resource.get("#org+id")
            url = resource.get("#x_resource+url")

            # If we've already seen this resource, skip
            if url in resources_seen:
                logger.warning("Skipping repeated resource %s", url)
                continue
            else:
                resources_seen.add(url)

            logger.info("Trying %s from %s", url, source_id)

            try:
                # Try reading the 3W data from HDX or a remote site via the resource URL
                with hxl.data(url, OPTS) as input:

                    # See if this is really a 3W (must have #org, #sector, and at least one of #country or #adm1)
                    if '#org' not in input.tags or '#sector' not in input.tags or ('#country' not in input.tags and '#adm1' not in input.tags):
                        logger.warning("Missing #org, #sector, or #country/#adm1 (probably not a 3W): %s", url)
                        continue

                    # Does the 3W include its own country data?
                    has_country_info = '#country' in input.tags

                    # Prescan column positions for different types of org info
                    # The indices will work with the embedded get_value() function
                    org_info = prescan_orgs(input.columns)

                    # Process the data rows, repeating for each org
                    for row in input:

                        # Override the dataset country name if necessary
                        local_country_name = row.get("#country-code") if has_country_info else country_name
                        local_country_code = row.get("#country+code") if has_country_info else country_code

                        if not local_country_code:
                            continue

                        # This is the same for all copies of the row
                        rest_of_row = [
                            row.get("#sector"),
                            local_country_name,
                            local_country_code,
                            row.get("#adm1-code"),
                            row.get("#adm1+code"),
                            row.get("#adm2-code"),
                            row.get("#adm2+code"),
                            resource.get("#x_dataset+id"),
                            date_start,
                            date_end,
                            resource.get("#x_resource+id"),
                            date_updated,
                            source_name,
                            source_id,
                        ]

                        for role, info in org_info.items():

                            org_name = get_value(row, info, 'name')

                            # Ignore an empty org name
                            if not org_name:
                                continue
                            
                            yield [
                                org_name,
                                get_value(row, info, 'acronym'),
                                role,
                                get_value(row, info, 'type'),
                            ] + rest_of_row

            except IOError as e:
                logger.warning("%s: %s", url, str(e))


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    output = csv.writer(sys.stdout)
    for row in generate_3w(sys.argv[1]):
        output.writerow(row)
