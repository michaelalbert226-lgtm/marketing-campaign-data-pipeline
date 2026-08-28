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

idx = df["MntWines"].idxmax()
print(df.loc[idx])
print("\n")
print(idx)
print(df.shape) 

heading("RICHEST CUSTOMER")
idx = df["Income"].idxmax()
print(df.loc[idx])

heading("POOREST CUSTOMER")
idx = df["Income"].idxmin()
print(df.loc[idx])

heading("CUSTOMER WHO SPENT THE MOST ON MEAT PRODUCTS")
idx = df["MntMeatProducts"].idxmax()
print(df.loc[idx])

heading("CUSTOMER WHO VISITED THE WEBSITE THE MOST")
idx = df["NumWebVisitsMonth"].idxmax()
print(df.loc[idx])

heading("NUMBER OF CUSTOMERS WITH NO CHILDREN")
idx = df["Kidhome"]==0
print(idx.sum())

heading("SHOW DETAILS OF CUSTOMERS WITH NO CHILDREN")
idx = df["Kidhome"]==0
print(df.loc[idx])