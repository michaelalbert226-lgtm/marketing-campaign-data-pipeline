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

def validate_allowed_values(df, column, allowed_values):

    invalid_count = (
        ~df[column].isin(allowed_values)
    ).sum()

    return invalid_count

heading("DUPLICATE ANALYSIS")
print(df["Dt_Customer"].head(10))
print(df["Dt_Customer"].dtype)
#change dt_customer to date
df["Dt_Customer"] = pd.to_datetime(df["Dt_Customer"],  format="%d-%m-%Y")
print(df["Dt_Customer"].dtype)

df["Customer_Year"] = df["Dt_Customer"].dt.year

df["Customer_Month"] = df["Dt_Customer"].dt.month
heading("SHOW THE FIRST 5 ROWS OF THE NEW COLUMNS")
print(df[[
    "Dt_Customer",
    "Customer_Year",
    "Customer_Month"
]].head())

heading("CUSTOMERS WHO JOINED IN 2014")
customers_2014 = df[df["Customer_Year"] == 2014]
print(f"Number of customers who joined in 2014: {customers_2014.shape[0]}")

heading("SUSPICIOUS BIRTH YEARS")
print(df[df["Customer_Year"] < 1900].shape[0])

heading("test date range")
test_income = pd.Series([
    "50000",
    "60000",
    "unknown",
    "70000",
    "N/A"
])

test_income = pd.to_numeric(test_income, errors="coerce")
print(test_income)
test_income = test_income.fillna(0)
print(test_income)

heading("SUSPICIOUS BIRTH YEARS")

suspicious = df[df["Year_Birth"] < 1900]

print(suspicious[[
    "ID",
    "Year_Birth",
    "Income",
    "Education",
    "Marital_Status",
    "Dt_Customer"
]])

df.loc[df["Year_Birth"] < 1900, "Year_Birth"] = pd.NA
print(df["Year_Birth"].isna().sum())
print(df.shape)

heading("INSPECTING EDUCATION")
text_clean_df = df.copy()
print(df["Education"].value_counts())

heading("EDUCATION WITH WHITESPACE")
print(
    text_clean_df[text_clean_df["Education"].str.strip() 
    != text_clean_df["Education"]]["Education"]             
)

heading("unique values of education")
print(df["Education"].unique())
print(df["Education"].value_counts())

text_clean_df["Education"] = text_clean_df["Education"].str.strip()
text_clean_df["Marital_Status"] = text_clean_df["Marital_Status"].str.strip()
print(text_clean_df["Education"].unique())
print(text_clean_df["Marital_Status"].unique())
text_clean_df["Education"] = text_clean_df["Education"].str.lower()
print(text_clean_df["Education"].value_counts())
education_mapping = {
        "graduation": "Graduation",
        "phd": "PhD",
        "master": "Master",
        "basic": "Basic",
        "2n cycle": "2n Cycle"
}
text_clean_df["Education"] = text_clean_df["Education"].replace(education_mapping)
print(text_clean_df["Education"].value_counts())

heading("INSPECTING YOLO & ABSURD")
for status in ["Absurd", "YOLO"]:
    customers = text_clean_df[
        text_clean_df["Marital_Status"] == status
    ]

    print(f"\n{status}")
    print(f"Number of customers: {customers.shape[0]}")
    print(f"Customer IDs: {customers['ID'].tolist()}")

    heading("Challenge 7 — Data Validation")
    valid_education = [
    "Basic",
    "2n Cycle",
    "Graduation",
    "Master",
    "PhD"
]

invalid_education = text_clean_df[
    ~text_clean_df["Education"].isin(valid_education)
]

print(f"Number of invalid education records: {invalid_education.shape[0]}")
print(invalid_education)



heading("PART 4 PRACTICAL ASSIGNMENT")

# Create a copy
clean_df = df.copy()

# -----------------------------
# CLEAN EDUCATION
# -----------------------------

clean_df["Education"] = (
    clean_df["Education"]
    .str.strip()
    .str.title()
)

mapped_education = {
    "Phd": "PhD",
    "2N Cycle": "2n Cycle"
}

clean_df["Education"] = clean_df["Education"].replace(
    mapped_education
)

# -----------------------------
# CLEAN MARITAL STATUS
# -----------------------------

clean_df["Marital_Status"] = (
    clean_df["Marital_Status"]
    .str.strip()
)

# -----------------------------
# VALIDATE EDUCATION
# -----------------------------

heading("VALIDATE EDUCATION")

allowed_education = [
    "Basic",
    "2n Cycle",
    "Graduation",
    "Master",
    "PhD"
]

invalid_education = clean_df[
    ~clean_df["Education"].isin(allowed_education)
]

print(
    f"Invalid Education records: "
    f"{invalid_education.shape[0]}"
)

# -----------------------------
# INVESTIGATE MARITAL STATUS
# -----------------------------

heading("MARITAL STATUS")

print(
    clean_df["Marital_Status"].value_counts()
)

print("\nAbsurd and YOLO customers:")

print(
    clean_df[
        clean_df["Marital_Status"].isin(
            ["Absurd", "YOLO"]
        )
    ][["ID", "Marital_Status"]]
)

# -----------------------------
# VALIDATE FINAL DATA
# -----------------------------

heading("FINAL VALIDATION")

print("Shape:", clean_df.shape)

print("\nMissing values:")
print(clean_df.isna().sum())

print("\nEducation:")
print(clean_df["Education"].value_counts())

print("\nMarital Status:")
print(clean_df["Marital_Status"].value_counts())

# -----------------------------
# SAVE
# -----------------------------

"""cleaned_dataset_path = (
    BASE_DIR
    / "datasets"
    / "marketing_campaign_cleaned1.csv"
)

clean_df.to_csv(
    cleaned_dataset_path,
    index=False
)

print(
    f"\nCleaned dataset saved to: "
    f"{cleaned_dataset_path}"
)

heading("outliers")
outlier_df = df.copy()
Q1 = outlier_df["Income"].quantile(0.25)
Q3 = outlier_df["Income"].quantile(0.75)

IQR = Q3 - Q1

lower_bound = Q1 - 1.5 * IQR
upper_bound = Q3 + 1.5 * IQR

print("Q1:", Q1)
print("Q3:", Q3)
print("IQR:", IQR)
print("Lower bound:", lower_bound)
print("Upper bound:", upper_bound)

income_outliers = outlier_df[
    (outlier_df["Income"] < lower_bound) |
    (outlier_df["Income"] > upper_bound)
]

print(income_outliers.shape[0])
print(
    income_outliers[
        ["ID", "Year_Birth", "Income"]
    ]
)

heading("YEAR OF BIRTH ANALYSIS")
min = clean_df["Year_Birth"].min()
max = clean_df["Year_Birth"].max()
mean = clean_df["Year_Birth"].mean()
median = clean_df["Year_Birth"].median()

print(f'THE SMALLEST YEAR BIRTH IS: {min}')
print(f'THE BIGGEST YEAR BIRTH IS:',max )
print(f'THE AVERAGE YEAR BIRTH IS:',mean )
print(f'THE MEDIAN YEAR BIRTH IS:',median )

heading("INCOME QUARTILES")

Q1 = clean_df["Income"].quantile(0.25)
Q3 = clean_df["Income"].quantile(0.75)

IQR = Q3 - Q1

print(f"Q1: {Q1}")
print(f"Q3: {Q3}")
print(f"IQR: {IQR}")

heading("INCOME OUTLIER BOUNDARIES")

lower_bound = Q1 - 1.5 * IQR
upper_bound = Q3 + 1.5 * IQR

print(f"Lower boundary: {lower_bound}")
print(f"Upper boundary: {upper_bound}")

heading("INCOME OUTLIERS")

income_outliers = clean_df[
    (clean_df["Income"] < lower_bound) |
    (clean_df["Income"] > upper_bound)
]

print(f"Number of income outliers: {income_outliers.shape[0]}")

print(
    income_outliers[
        ["ID", "Year_Birth", "Education", "Income"]
    ]
)

heading("INVESTIGATE SUSPICIOUS INCOME")

suspicious_customer = clean_df[
    clean_df["ID"] == 9432
]

print(suspicious_customer.T)

heading("INCOME OUTLIER SUMMARY")

print(
    income_outliers["Income"].describe()
)

heading("SUSPICIOUS CUSTOMER 9432")

suspicious_customer = clean_df[
    clean_df["ID"] == 9432
]

print(suspicious_customer.T)

heading("FLAG SUSPICIOUS INCOME")
clean_df["Income_Suspicious"] = (
    clean_df["Income"] == 666666
)
print(
    clean_df[
        clean_df["Income_Suspicious"]
    ][["ID", "Income", "Income_Suspicious"]]
)


clean_df["Invalid_Birth_Year"] = (
    clean_df["Year_Birth"] < 1900
)

clean_df["Invalid_Kids"] = (
    clean_df["Kidhome"] < 0
)

clean_df["Invalid_Teens"] = (
    clean_df["Teenhome"] < 0
)
print("Invalid birth years:", clean_df["Year_Birth"].sum())
print("Invalid kids:", clean_df["Kidhome"].sum())
print("Invalid teens:", clean_df["Teenhome"].sum())
print("Suspicious income:", clean_df["Income_Suspicious"].sum())


print("Minimum Year_Birth:", clean_df["Year_Birth"].min())
print("Minimum Kidhome:", clean_df["Kidhome"].min())
print("Minimum Teenhome:", clean_df["Teenhome"].min())
print("Maximum Kidhome:", clean_df["Kidhome"].max())"""


heading("DATA QUALITY REPORT")

print("Total rows:", clean_df.shape[0])
print("Total columns:", clean_df.shape[1])

print("Invalid birth years:",
      (clean_df["Year_Birth"] < 1900).sum())

print("Invalid kids:",
      (clean_df["Kidhome"] < 0).sum())

print("Invalid teens:",
      (clean_df["Teenhome"] < 0).sum())

print("Suspicious income:",
      (clean_df["Income"] == 666666).sum())

heading("DATA QUALITY REPORT")

quality_report = pd.DataFrame({
    "Rule": [
        "Invalid Birth Years",
        "Invalid Kids",
        "Invalid Teens",
        "Suspicious Income"
    ],
    
    "Failed_Rows": [
        (clean_df["Year_Birth"] < 1900).sum(),
        (clean_df["Kidhome"] < 0).sum(),
        (clean_df["Teenhome"] < 0).sum(),
        (clean_df["Income"] == 666666).sum()
    ]
})

print(quality_report)

heading("INVALID INCOME")

invalid_income = clean_df["Income"] < 0

print(
    "Invalid income:",
    invalid_income.sum()
)

heading("BIRTH YEAR")
MIN_BIRTH_YEAR = 1900
MAX_BIRTH_YEAR = 2026
invalid_birth_year = (
    (clean_df["Year_Birth"] < MIN_BIRTH_YEAR) |
    (clean_df["Year_Birth"] > MAX_BIRTH_YEAR)
)
print(
    "Invalid birth years:",
    invalid_birth_year.sum()
)

heading("INVALID KIDHOME")
invalid_kids = (
    (clean_df["Kidhome"] < 0) |
    (clean_df["Kidhome"] > 2)
)

print(
    "Invalid Kidhome:",
    invalid_kids.sum()
)

heading("INVALID TEENS") 
invalid_teens = (
    (clean_df["Teenhome"] < 0) |
    (clean_df["Teenhome"] > 2)
)
print("Invalid teens:", invalid_teens.sum())

heading("TOTAL CHILDREN")
clean_df["Total_Children"] = (
    clean_df["Kidhome"] +
    clean_df["Teenhome"]
)
print(
    clean_df[
        ["ID", "Kidhome", "Teenhome", "Total_Children"]
    ].head(10)
)

heading("INVALID TOTAL CHILDREN")

invalid_total_children = (
    clean_df["Total_Children"] < 0
)

print(
    "Invalid Total_Children:",
    invalid_total_children.sum()
)

heading("INVALID TOTAL CALCULATION")
invalid_total_calculation = (
    clean_df["Total_Children"] !=
    (clean_df["Kidhome"] + clean_df["Teenhome"])
)
print(
    "Incorrect Total_Children calculations:",
    invalid_total_calculation.sum()
)

heading("TOTAL SPENDING")

clean_df["Total_Spending"] = (
    clean_df["MntWines"]
    + clean_df["MntFruits"]
    + clean_df["MntMeatProducts"]
    + clean_df["MntFishProducts"]
    + clean_df["MntSweetProducts"]
    + clean_df["MntGoldProds"]
)

print(
    clean_df[
        [
            "ID",
            "MntWines",
            "MntFruits",
            "MntMeatProducts",
            "MntFishProducts",
            "MntSweetProducts",
            "MntGoldProds",
            "Total_Spending"
        ]
    ].head(10)
)
invalid_spending = (
    clean_df["Total_Spending"] < 0
)
print("invalid spending:", invalid_spending.sum())

heading("suspecious spending")
suspicious_spending = (
    clean_df["Total_Spending"] > clean_df["Income"]
)

print(
    "Customers spending more than their income:",
    suspicious_spending.sum()
)

campaign_columns = [
    "AcceptedCmp1",
    "AcceptedCmp2",
    "AcceptedCmp3",
    "AcceptedCmp4",
    "AcceptedCmp5",
    "Response"
]

for column in campaign_columns:
    print(column, ":", clean_df[column].unique())

    heading("CAMPAIGN VALIDATION")

invalid_count = validate_allowed_values(
    clean_df,
    "AcceptedCmp1",
    [0, 1]
)

print("Invalid values:", invalid_count)

invalid_count = validate_allowed_values(
    clean_df,
    "Education",
    ["Basic", "2n Cycle", "Graduation", "Master", "PhD"]
)

print("Invalid Education values:", invalid_count)

heading("AUTOMATED CAMPAIGN VALIDATION")

for column in campaign_columns:

    invalid_count = validate_allowed_values(
        clean_df,
        column,
        [0, 1]
    )

    print(
        column,
        "Invalid values:",
        invalid_count
    )

    heading("FINAL DATA QUALITY REPORT")

quality_report = pd.DataFrame({
    "Rule": [
        "Invalid Income",
        "Invalid Birth Years",
        "Invalid Kidhome",
        "Invalid Teenhome",
        "Invalid Total Children",
        "Incorrect Total Children Calculation",
        "Invalid Total Spending",
        "Suspicious Income"
    ],

    "Failed_Rows": [
        (clean_df["Income"] < 0).sum(),
        (
            (clean_df["Year_Birth"] < 1900) |
            (clean_df["Year_Birth"] > 2026)
        ).sum(),
        (
            (clean_df["Kidhome"] < 0) |
            (clean_df["Kidhome"] > 2)
        ).sum(),
        (
            (clean_df["Teenhome"] < 0) |
            (clean_df["Teenhome"] > 2)
        ).sum(),
        (clean_df["Total_Children"] < 0).sum(),
        (
            clean_df["Total_Children"] !=
            (clean_df["Kidhome"] + clean_df["Teenhome"])
        ).sum(),
        (clean_df["Total_Spending"] < 0).sum(),
        (clean_df["Income"] == 666666).sum()
    ]
})

print(quality_report)

total_failures = quality_report["Failed_Rows"].sum()

if total_failures == 0:
    print("DATASET STATUS: PASS")
else:
    print("DATASET STATUS: REVIEW REQUIRED")