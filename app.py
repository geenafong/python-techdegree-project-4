from peewee import *
import csv

with open("store-inventory/inventory.csv", "r") as file:
    reader = csv.reader(file)
    rows = list(reader)
    for row in rows:
        print(", ".join(row))
# import csv
# reader = csv.DictReader(open("store-inventory/inventory.csv"))
# dict_obj = next(reader)
