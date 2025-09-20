import os
import csv
from app.db.mongo import species_collection

BATCH_SIZE = 5000

text_file = os.path.join(os.path.dirname(__file__), '..', 'src', 'plantlst.txt')

batch = []

with open(text_file, newline='', encoding='utf-8') as csvfile:
    reader = csv.reader(csvfile)
    next(reader)  # пропускаем заголовок
    for row in reader:
        if len(row) < 5:
            continue

        batch.append({
            "name": row[3],
            "scientific_name": row[2],
            "family": row[4]
        })

        if len(batch) >= BATCH_SIZE:
            species_collection.insert_many(batch)
            batch = []

if batch:
    species_collection.insert_many(batch)

print("✅ All species inserted!")