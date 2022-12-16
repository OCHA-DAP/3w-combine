""" Convert output from hxlcount to something wordcloud.com can use as input
Assumes only 1 column counted.

"""

import csv, hxl, sys

input = hxl.data(sys.argv[1], hxl.InputOptions(allow_local=True))

output = csv.writer(sys.stdout, delimiter=';')

output.writerow(["weight", "word",])

for row in input:
    output.writerow([row.get("#meta+count"), row.values[0],])

sys.exit(0)
