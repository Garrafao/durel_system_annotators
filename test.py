import csv

with open("faulty_csv.csv", 'r') as f:
        reader = csv.DictReader(f, delimiter='\t',quoting=csv.QUOTE_NONE,strict=True)
        data = list(reader)
        print(data)