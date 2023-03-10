#!/bin/sh
########################################################################
# Clean combined 3W data using libhxl scripts
#
# Usage:
#   $ sh clean-3w.sh CUTOFF-DATE SECTOR-MAP < INPUT.csv > OUTPUT.csv
#
# Started by David Megginson
########################################################################

if [ $# -ne 1 ]; then
    echo "Usage: $0 <sector-map>" >&2
    exit 2
fi

SECTOR_MAP=$1

hxlselect -q '#org+name ~ .*[a-zA-Z].*' |                      # exclude activities with blank orgs
    hxlsort -t date -r |                                           # sort by date
    hxladd --spec 'Sector code#sector+code={{#sector+name}}' |     # add a new column for the sector code
    hxlreplace --map $SECTOR_MAP |                                 # normalise sector codes
    hxlexpand -t sector+code -s '|' |                              # split multiple codes after replacement
    hxldedup -t org,sector,country,adm1,adm2 |                     # deduplicate to get a 3W-OP
    hxlsort -t country+name,adm1+name,adm2+name,sector,org+name    # organise the result
