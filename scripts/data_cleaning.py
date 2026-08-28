from pathlib import Path
import pandas as pd
from etl_pipeline import extract_data

BASE_DIR = Path(__file__).resolve().parent.parent
DATASET = BASE_DIR  / "datasets" / "marketing_campaign.csv"

#load the dataset
df = pd.read_csv(DATASET, sep="\t")
def heading(title):
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)


try:

    number = int(input("Enter a number: "))

    print("You entered:", number)

except ValueError:

    print("ERROR: Please enter a valid number.")