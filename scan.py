import ckancrawler, csv, logging, re, sys

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger("3wtest")
"""Set up a logger"""

crawler = ckancrawler.Crawler("https://data.humdata.org", delay=0, user_agent="HDX-Developer-2015")

output = csv.writer(sys.stdout)

output.writerow([
    "Org id",
    "Dataset name",
    "Dataset title",
    "Resource name",
    "Resource URL",
])

output.writerow([
    "#org+id",
    "#x_dataset+id",
    "#x_dataset+title",
    "#x_resource_id",
    "#meta+url",
])
    

for package in crawler.packages(q="vocab_Topics=who%20is%20doing%20what%20and%20where%20-%203w%20-%204w%20-%205w&vocab_Topics=hxl"):
    org = package["organization"]["name"]
    if re.match("^ocha-.*", org) and org != "ocha-fts":
        title = package["title"]
        name = package["name"]
        for resource in package["resources"]:
            filename = resource["name"]
            url = resource["url"]
            output.writerow([
                org, name, title, filename, url
            ]);

