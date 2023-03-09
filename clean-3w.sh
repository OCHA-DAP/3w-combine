#!/bin/sh
########################################################################
# Clean combined 3W data using libhxl scripts
#
# Usage:
#   $ sh clean-3w.sh CUTOFF-DATE SECTOR-MAP < INPUT.csv > OUTPUT.csv
#
# Started by David Megginson
########################################################################

if [ $# -ne 2 ]; then
    echo "Usage: $0 <cutoff-date> <sector-map>" >&2
    exit 2
fi

CUTOFF_DATE=$1
SECTOR_MAP=$2

hxlselect -q "date > $CUTOFF_DATE" |                               # exclude activites before the cutoff date
    hxlselect -q '#org+name ~ .*[a-zA-Z].*' |                      # exclude activities with blank orgs
    hxlsort -t date -r |                                           # sort by date
    hxladd --spec 'Sector code#sector+code={{#sector+name}}' |         # add a new column for the sector code
    hxlreplace --map $SECTOR_MAP |                                 # normalise sector codes
    hxldedup -t org,sector,country,adm1,adm2 |                     # deduplicate to get a 3W-OP
    hxlsort -t country+name,adm1+name,adm2+name,sector,org+name    # organise the result
