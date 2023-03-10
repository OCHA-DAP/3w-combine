3W test for HDX
===============

Scan HXLated 3W datasets on HDX and aggregate into a single basic 3W-OP (operational presence). Current cutoff is after 2022-02-28. There are three steps involved:

1. Scanning HDX for appropriate datasets and resources.
2. Parsing the resources and merging them into a combined 3W.
3. Postprocessing, including date filtering and deduplication.
4. Generating aggregated reports

You can run the entire process with a single command:

```
$ make all
```

This will place the final combined 3W in the file ``output/combined-3w-clean.csv`` and generate reports.

## Algorithm

Include all datasets meeting the following criteria:

* with the HDX vocabulary topics "hxl" and "who is doing what and where-3w-4w-5w"
* owned by an HDX org whose identifier starts with "ocha-" and is not one of "ocha-ds", "ocha-fiss", "ocha-fts", or "ocha-naas" (which are not OCHA field offices)
* dataset end date is on or after CUTOFF_DATE, or is "*"

Include all resources from the above datasets that meet the following criteria:

* modified date is on or after CUTOFF_DATE
* can be parsed as HXL
* include the HXL hashtags "#org", "#sector", and at least one of "#country" or "#adm1"

Create a raw combined 3W using the following steps:

* add metadata (country, provider org, dates, etc) from scanned HDX metadata
* repeat the row for each associated org
* determine the org role from the associated attribute (+funder, +impl, etc) and place in a separate column
* determine the acronym associated with each org, if present (default to +impl if multiple orgs and just one acronym)
* determine the type associated with each org, if present (default to +impl if multiple orgs and just one type)
* extract the basic 3W information

Create a cleaned 3W-OP using the following steps:

* exclude activities that do not list an org (not relevant for a 3W-OP)
* add a column with standard sector codes, using input/sector-map.csv for mapping
* repeat rows if there are multiple sectors (one sector per row)

Create aggregated 3W-OP reports:

* aggregate by org name/acronym/role/type, sector, and country
* aggregate by org name/acronym/role/type, sector, country, and adm1
* aggregate by org name/acronym/role/type, sector, country, adm1, and adm2


## Step 1: Scanning HDX

Scan for all resources in HDX datasets that meet the following conditions:

* Has the HDX vocabulary topics "hxl" and "who is doing what and where-3w-4w-5w"
* Has an HDX org identifier that starts with "ocha-" and is not one of "ocha-ds", "ocha-fiss", "ocha-fts", or "ocha-naas" (which are not OCHA field offices)

The output will contain metadata from HDX including the country, provider org, and resource revision date (among other fields).

Usage:

```
$ pip3 install -r requirements.txt
$ python3 scan.py > output/ocha-3w-resources.csv
```

or the following, which will automatically set up a virtual environment with the required packages and save the result to ``output/ocha-3w-resources.csv``:

```
$ make scan
```


## Step 2: Creating a raw combined 3W

Combine HXL resources discovered by ``scan.py`` above, including only the newest valid 3W resource for each country. As well as meeting the criteria for ``scan.py``, the resource must be parseable as HXL and include all of the following hashtags (in any order, with any attributes):

* #org
* #sector
* #adm1

The resulting file is an 3W-OP (operational presence), but is not yet cleaned or deduplicated

Usage:

```
$ pip3 install -r requirements.txt
$ python3 combine-3w.py output/ocha-3w-resources.csv > output/combined-3w-raw.csv
```

or the following, which will automatically set up a virtual environment with the required packages and save the result to ``combined-3w-raw.csv``:

```
$ make combine
```


## Step 3: Postprocessing the combined 3W

To finish off the combined 3W, it's necessary to remove duplicate entries for the same organisation in the same location, and set a cutoff date. To include entries updated only after 2021-12-31, use the following commands:

```
$ cat output/combined-3w-raw.csv \
      | hxlselect -q 'date > 2021-12-31' \
      | hxlselect -q '#org+name ~ .*[a-zA-Z].*' \
      | hxlsort -t date -r \
      | hxldedup -t org,sector,country,adm1,adm2 \
      | hxlsort -t country+name,adm1+name,adm2+name,org+name \
      > output/combined-3w-clean.csv
```

or the following, which will automatically set up a virtual environment with the required packages and save the result in ``output/combined-3w-clean.csv``:

```
$ make fix
```


## Step 4: Generate reports

To generate a collection of aggregated reports from the cleaned 3W, use the command

```
$ make reports
```

This will use HXL utilities to generate the following:

- ``3w-op-country.csv`` — operational-presence by country
- ``3w-op-admin1.csv`` — operational-presence by administrative level 1 subdivision
- ``3w-op-admin2.csv`` — operational-presence by administrative level 2 subdivision


## Author

These scripts were created by David Megginson at the Centre for Humanitarian Data.
