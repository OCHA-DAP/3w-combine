""" Merge multiple 3Ws into one

Usage:
    python combine-3w.py <file_or_url> [file_or_url..]

"""

import csv, hxl, logging, sys

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__file__)


COLUMN_DEFNS = [
    [
        "Implementing organisation name",
        "#org+impl+name",
        ["#org+name+impl-type", "#org+impl-acronym-type",],
    ],
    [
        "Implementing organisation acronym",
        "#org+impl+acronym",
        ["#org+impl+acronym-type",],
    ],
    [
        "Implementing organisation type",
        "#org+impl+type",
        ["#org+impl-name+type",],
    ],
    [
        "Programming organisation name",
        "#org+prog+name",
        ["#org+name+prog-type", "#org+prog-acronym-type", "#org+name+leader-type", "#org+leader-acronym-type",],
    ],
    [
        "Programming organisation acronym",
        "#org+prog+acronym",
        ["#org+prog+acronym-type", "#org+leader+acronym-type",],
    ],
    [
        "Programming organisation type",
        "#org+prog+type",
        ["#org+prog-name+type", "#org+leader-name+type",],
    ],
    [
        "Funding organisation name",
        "#org+funder+name",
        ["#org+name+funder-type", "#org+funder-acronym-type", "#org+name+funding-type", "#org+funding-acronym-type",],
    ],
    [
        "Funding organisation acronym",
        "#org+funder+acronym",
        ["#org+funder+acronym-type", "#org+funding+acronym-type",],
    ],
    [
        "Funding organisation type",
        "#org+funder+type",
        ["#org+funder-name+type", "#org+funding-name+type",],
    ],
    [
        "Participating organisation name",
        "#org+participating+name",
        ["#org+name-type-impl-prog-leader", "#org-acronym-type-impl-prog-leader"],
    ],
    [
        "Participating organisation acronym",
        "#org+participating+acronym",
        ["#org+acronym-type-impl-prog-leader"],
    ],
    [
        "Participating organisation type",
        "#org+participating+type",
        ["#org+type-impl"],
    ],
    [
        "Sector or cluster",
        "#sector",
        ["#sector"],
    ],
    [
        "Activity",
        "#activity",
        ["#activity"],
    ],
    [
        "Country",
        "#country+name",
        ["#country+name"],
    ],
    [
        "Country code",
        "#country+code",
        ["#country+code"],
    ],
    [
        "ADM1",
        "#adm1+name",
        ["#adm1-code"],
    ],
    [
        "ADM1 p-code",
        "#adm1+code",
        ["#adm1+code"],
    ],
    [
        "ADM2",
        "#adm2+name",
        ["#adm2-code"],
    ],
    [
        "ADM2 p-code",
        "#adm2+code",
        ["#adm2+code"],
    ],
]


if len(sys.argv) < 2:
    print("Usage: python {} <file_or_url> [file_or_url..]", file=sys.stderr)
    sys.exit(2)

output = csv.writer(sys.stdout)

# text headers
output.writerow([defn[0] for defn in COLUMN_DEFNS])

# HXL hashtags
output.writerow([defn[1] for defn in COLUMN_DEFNS])

def get_matching_value (pattern, row):
    pattern = hxl.model.TagPattern.parse(pattern)
    for i, value in enumerate(row.values):
        if i < len(row.columns) and row.columns[i] and pattern.match(row.columns[i]):
            return value
    return None

for file_or_url in sys.argv[1:]:
    with hxl.data(file_or_url, hxl.input.InputOptions(allow_local=True)) as source:
        logger.info("Processing %s", file_or_url)
        for row in source:
            values = []
            for defn in COLUMN_DEFNS:
                for pattern in defn[2]:
                    value = get_matching_value(pattern, row)
                    if value is not None:
                        break
                values.append(value)
            output.writerow(values)
                        
