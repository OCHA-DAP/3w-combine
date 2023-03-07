#!/bin/sh
########################################################################
# Normalise 3W data using libhxl scripts
#
# Usage:
#   $ sh normalise-3w.sh SECTOR-MAP < INPUT.csv > OUTPUT.csv
#
# Started by David Megginson
########################################################################

if [ $# -ne 1 ]; then
    echo "Usage: $0 <sector-map>" >&2
    exit 2
fi

SECTOR_MAP=$2

hxlselect -q "date > $CUTOFF_DATE" |                               # exclude activites before the cutoff date
    hxlselect -q '#org+name ~ .*[a-zA-Z].*' |                      # exclude activities with blank orgs
    hxlsort -t date -r |                                           # sort by date
    hxladd --spec 'Sector code#sector+code={{#sector!}}' |         # add a new column for the sector code
    hxlreplace --map $SECTOR_MAP |                                 # normalise sector codes
    hxldedup -t org,sector,country,adm1,adm2 |                     # deduplicate to get a 3W-OP
    hxlsort -t country+name,adm1+name,adm2+name,sector,org+name    # organise the result
