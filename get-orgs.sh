#!/bin/bash

SOURCE=output/combined-3w.csv
VENV=venv/bin/activate

. $VENV

echo "Implementing orgs..."
cat $SOURCE | hxlcut -i org+impl+name,org+impl+type | hxlselect -q "#org+impl+name is not empty" | hxlrename -r "#org+impl+name:Org name#org+name" | hxlrename -r "#org+impl+type:Org type#org+type" | hxladd -b -s "Acronym#org+acronym=" | hxladd -s "Org role#org+role=impl" > output/orgs-impl.csv

echo "Programming orgs..."
cat $SOURCE | hxlcut -i org+prog+name,org+prog+type | hxlselect -q "#org+prog+name is not empty" | hxlrename -r "#org+prog+name:Org name#org+name" | hxlrename -r "#org+prog+type:Org type#org+type" | hxladd -b -s "Acronym#org+acronym=" | hxladd -s "Org role#org+role=prog" > output/orgs-prog.csv

echo "Funding orgs..."
cat $SOURCE | hxlcut -i org+funder+name,org+funder+type | hxlselect -q "#org+funder+name is not empty" | hxlrename -r "#org+funder+name:Org name#org+name" | hxlrename -r "#org+funder+type:Org type#org+type" | hxladd -b -s "Acronym#org+acronym=" | hxladd -s "Org role#org+role=funder" > output/orgs-funder.csv

echo "Participating orgs..."
cat $SOURCE | hxlcut -i org+participating+acronym,org+participating+name,org+participating+type | hxlselect -q "#org+participating+name is not empty" | hxlrename -r "#org+participating+acronym:Acronym#org+acronym" | hxlrename -r "#org+participating+name:Org name#org+name" | hxlrename -r "#org+participating+type:Org type#org+type" | hxladd -s "Org role#org+role=participating" > output/orgs-participating.csv

echo "Merging..."
cat $SOURCE | hxlappend -a output/orgs-impl.csv -a output/orgs-prog.csv -a output/orgs-funder.csv -a output/orgs-participating.csv
