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

heading("CUSTOMERS WITH INCOME HIGHER THAN 70000")
high_income = df[df["Income"] > 70000]
print(f"Income higher than 70000: {high_income.shape[0]}")

heading("CUSTOMERS WITH NO TEENS AND NO KIDS")
no_teens_no_kids = df[
    (df["Kidhome"] == 0) &
    (df["Teenhome"] == 0)
]

print(f"Number of customers with no teens and no kids: {no_teens_no_kids.shape[0]}")

heading("SHOW CUSTOMERS WHO ARE GRADUATED OR MASTERS")
grad_or_masters = df[
    (df["Education"] == "Graduation") |
    (df["Education"] == "Master")   
]
print(f"NUMBER OF GRADUATE AND MASTERS: {grad_or_masters.shape[0]}")

heading("CUSTOMERS THAT ARE NOT MARRIED")
not_married = df[df["Marital_Status"] != "Married"]
print(f"Number of customers who are not married: {not_married.shape[0]}")

df [
    (df["Income"] > 60000) &
    (df["MntWines"] > 500) &
    (df["Kidhome"] == 0) &
    (df["NumWebVisitsMonth"] < 5)
]

heading("MINI CHALLENGE:  NO HINTS")
mini_challenge = df[
    (df["Marital_Status"] == "Married") &
    (df["AcceptedCmp1"] == 1) 
]
print(f"Number of customers who are married and accepted the first campaign: {mini_challenge.shape[0]}")
