from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
DATASET = BASE_DIR  / "datasets" / "marketing_campaign.csv"

#load the dataset
df = pd.read_csv(DATASET, sep="\t")

def heading(title):
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)

heading("FIRST 10 ROWS")
print(df)

#describe statistics of the dataset
heading("DESCRIBE")
print(df.describe(include="all"))

# Count customers by education level
heading("EDUCATION LEVELS")
print(df["Education"].value_counts())

# Count customers by marital status
heading("MARITAL STATUSES")
print(df["Marital_Status"].value_counts())

heading("DUPLICATE ROWS")
print(df.duplicated().sum())

heading("AVERAGE INCOME")
print(df["Income"].mean())

