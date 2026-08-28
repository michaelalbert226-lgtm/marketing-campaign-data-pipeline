"""
Lesson 1
Inspecting Data with pandas

Author: Michael Albert
"""

import pandas as pd

# Read the dataset
df = pd.read_csv("C:\\Users\\micha\\Desktop\\Data_Engineering_Bootcamp\\datasets\\marketing_campaign.csv", sep="\t")

print("=" * 70)
print("FIRST FIVE ROWS")
print("=" * 70)
print(df.head())

print("\n")

print("=" * 70)
print("LAST FIVE ROWS")
print("=" * 70)
print(df.tail())

print("\n")

print("=" * 70)
print("SHAPE")
print("=" * 70)
print(df.shape)

print("\n")

print("=" * 70)
print("COLUMN NAMES")
print("=" * 70)
print(df.columns)

print("\n")

print("=" * 70)
print("DATA TYPES")
print("=" * 70)
print(df.dtypes)

print("\n")

print("=" * 70)
print("DATASET INFO")
print("=" * 70)
df.info()