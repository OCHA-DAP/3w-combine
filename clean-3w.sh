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
    echo "Usage: $0 <sector-map> <sector-name-map> < INPUT.csv > OUTPUT.csv" >&2
    exit 2
fi

SECTOR_MAP=$1
SECTOR_NAME_MAP=$2

COLUMNS="org+name,org+acronym,country+name,country+code,adm1+name,adm1+code,adm2+name,adm2+code"

hxlcount -t "$COLUMNS,sector+name" |                                           # initial aggregation to reduce processing time down the pipeline
    hxlselect -q '#org+name ~ .*[a-zA-Z].*' |                      # exclude activities with blank orgs
    hxladd --spec 'Sector code#sector+code={{#sector+name}}' |     # add a new column for the sector code
    hxlreplace --map $SECTOR_MAP |                                 # normalise sector codes
    hxlexpand -t sector+code -s '|' |                              # split multiple codes after replacement
    hxladd --spec 'Sector normalised name#sector+name+norm={{#sector+code}}' | # add a new column for the normalised sector name
    hxlreplace --map $SECTOR_NAME_MAP |                            # add sector names corresponding to codes
    hxlexpand -t org+name -s '|' |                                 # split multiple orgs
    hxlcount -t "$COLUMNS,sector+name+norm,sector+code" |          # second aggregation after normalisation
    hxlcut -x meta+count                                           # the count column is meaningless
