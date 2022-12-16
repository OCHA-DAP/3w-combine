3W test for HDX
===============

Scan HXLated 3W datasets on HDX and aggregate into a single basic 3W-OP (operational presence). Current cutoff is after 2021-12-31.

## Utilities

### scan.py

Scan for all resources in HDX datasets that meet the following conditions:

* Has the HDX vocabulary topics "hxl" and "who is doing what and where - 3w - 4w - 5w" (old) or "who is doing what and where-3w-4w-5w" (new)
* Has an HDX org identifier that starts with "ocha-" and is not one of "ocha-ds", "ocha-fiss", "ocha-fts", or "ocha-naas" (which are not OCHA field offices)

The output will contain metadata from HDX including the country, provider org, and resource revision date (among other fields).

Usage:

  $ python3 scan.py > output/ocha-3w-resources.csv
  
or

  $ make scan
  
### combine-3w.py

Combine HXL resources discovered by ``scan.py`` above, including only the newest valid 3W resource for each country. As well as meeting the criteria for ``scan.py``, the resource must be parseable as HXL and include all of the following hashtags (in any order, with any attributes):

* #org
* #sector
* #adm1

The 3W is an 3W-OP (operational presence), but is not yet deduplicated.

Usage:

  $ python3 combine-3w.py output/ocha-3w-resources.csv > output/combined-3w-raw.csv
  
or

  $ make combine
  
### Cleaning

To finish off the combined 3W, it's necessary to remove duplicate entries for the same organisation in the same location, and set a cutoff date. To include entries updated only after 2021-12-31, use the following commands:

  $ cat output/combined-3w-raw.csv \\
		| hxlselect -q 'date > 2021-12-31' \\
		| hxlselect -q '#org+name ~ .*[a-zA-Z].*' \\
		| hxlsort -t date -r \\
		| hxldedup -t org,sector,country,adm1,adm2 \\
		| hxlsort -t country+name,adm1+name,adm2+name,org+name \\
		> output/combined-3w-clean.csv
  
or

  $ make fix

