from pathlib import Path
import pandas as pd
import logging 


BASE_DIR = Path(__file__).resolve().parent
DATASET = BASE_DIR / "datasets" / "marketing_campaign.csv"

#logs-------------------------------------------------
LOG_DIR = BASE_DIR / "logs"         #Create a path to a folder called logs.
LOG_DIR.mkdir(exist_ok=True)        #Create the logs folder if it doesn't already exist.(if the folder exists, dont complain)

LOG_FILE = LOG_DIR / "pipeline.log" #Our log file would be called pipeline.log

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,             #Record INFO, WARNING, ERROR and CRITICAL messages.
    format="%(asctime)s | %(levelname)s | %(message)s"   #controls how the log looks. e.g time | INFO | Message.      
)

#functions--------------------------------------------
def extract_data(dataset_path):
    print("\n" + "=" * 70)
    print("EXTRACT")
    print("=" * 70)

    try:

        df = pd.read_csv(
            dataset_path,
            sep="\t"
        )

        print("Data extracted successfully.")
        print("Rows:", df.shape[0])
        print("Columns:", df.shape[1])

        logging.info("Data extracted successfully.")
        logging.info(f"Rows: {df.shape[0]}")
        logging.info(f"Columns: {df.shape[1]}")

        return df
    except FileNotFoundError:
        print("❌ EXTRACT FAILED")
        print("File not found:", dataset_path)

        logging.error(f"File not found: {dataset_path}")

        return None
    except pd.errors.ParserError:

        print("❌ EXTRACT FAILED")
        print("Could not parse the CSV file.")

        return None
#--------------------------------------------------------------------------
def transform_data(df):

    print("\n" + "=" * 70)
    print("TRANSFORM")
    print("=" * 70)

    logging.info("Transformation started.")

    # Convert customer date
    df["Dt_Customer"] = pd.to_datetime(
        df["Dt_Customer"],
        format="%d-%m-%Y",
        errors="coerce"
    )


    # Clean Education
    df["Education"] = (
        df["Education"]
        .str.strip()
        .str.title()
    )

    df["Education"] = df["Education"].replace({
        "Phd": "PhD"
    })

    # Clean Marital Status
    df["Marital_Status"] = (
        df["Marital_Status"]
        .str.strip()
    )

    df["Marital_Status"] = df["Marital_Status"].replace({
        "Alone": "Single",
        "YOLO": "Single",
        "Absurd": "Single"
    })

    # Income flag
    df["Income_Missing"] = df["Income"].isna()

    # Derived columns
    df["Customer_Year"] = df["Dt_Customer"].dt.year

    df["Customer_Month"] = df["Dt_Customer"].dt.month

    df["Total_Children"] = (
        df["Kidhome"] + df["Teenhome"]
    )

    df["Total_Spending"] = (
        df["MntWines"]
        + df["MntFruits"]
        + df["MntMeatProducts"]
        + df["MntFishProducts"]
        + df["MntSweetProducts"]
        + df["MntGoldProds"]
    )

    # Quality flags
    df["Birth_Year_Invalid"] = (
        (df["Year_Birth"] < 1900) |
        (df["Year_Birth"] > 2026)
    )

    df["Income_Suspicious"] = (
        df["Income"] == 666666
    )
    logging.info("Transformation completed.")

    return df
#-----------------------------------------------------
#-----------------------------------------------------
#ALLOWED VALUES
def validate_allowed_values(df, column, allowed_values):

    invalid_count = (
        ~df[column].isin(allowed_values)
    ).sum()

    return invalid_count
#--------------------------------------------------------------------------
#--------------------------------------------------------------------------
def validate_data(df):

    print("\n" + "=" * 70)
    print("VALIDATE")
    print("=" * 70)

    # -------------------------
    # Basic validation rules
    # -------------------------
    invalid_dates = df["Dt_Customer"].isna().sum()
    if invalid_dates > 0:
        logging.warning(
        f"{invalid_dates} invalid customer dates detected."
    )

    invalid_income = (
        df["Income"] < 0
    ).sum()

    invalid_birth_years = (
        (df["Year_Birth"] < 1900) |
        (df["Year_Birth"] > 2026)
    ).sum()

    if invalid_birth_years > 0:
        logging.warning(
            f"{invalid_birth_years} invalid birth years detected."
        )

    invalid_kids = (
        (df["Kidhome"] < 0) |
        (df["Kidhome"] > 2)
    ).sum()

    invalid_teens = (
        (df["Teenhome"] < 0) |
        (df["Teenhome"] > 2)
    ).sum()

    incorrect_total_children = (
        df["Total_Children"] !=
        (df["Kidhome"] + df["Teenhome"])
    ).sum()

    invalid_total_spending = (
        df["Total_Spending"] < 0
    ).sum()

    suspicious_income = (
        df["Income"] == 666666
    ).sum()

    if suspicious_income > 0:
        logging.warning(
            f"{suspicious_income} suspicious income records detected."
            )

    # -------------------------
    # Campaign validation
    # -------------------------

    campaign_columns = [
        "AcceptedCmp1",
        "AcceptedCmp2",
        "AcceptedCmp3",
        "AcceptedCmp4",
        "AcceptedCmp5",
        "Response"
    ]

    campaign_invalid = 0

    for column in campaign_columns:

        invalid_count = validate_allowed_values(
            df,
            column,
            [0, 1]
        )

        campaign_invalid += invalid_count

        print(
            column,
            "Invalid values:",
            invalid_count
        )

    # -------------------------
    # Quality report
    # -------------------------
    heading("quality_report")
    quality_report = pd.DataFrame({
        "Rule": [
            "Invalid Income",
            "Invalid Customer Dates",
            "Invalid Birth Years",
            "Invalid Kidhome",
            "Invalid Teenhome",
            "Incorrect Total Children",
            "Invalid Total Spending",
            "Suspicious Income",
            "Invalid Campaign Values"
        ],

        "Failed_Rows": [
            invalid_income,
            invalid_dates,
            invalid_birth_years,
            invalid_kids,
            invalid_teens,
            incorrect_total_children,
            invalid_total_spending,
            suspicious_income,
            campaign_invalid
        ]
    })

    print("\n")
    print(quality_report)

    # -------------------------
    # Dataset status
    # -------------------------

    total_failures = (
        quality_report["Failed_Rows"].sum()
    )

    if total_failures == 0:
        status = "PASS"
    else:
        status = "REVIEW REQUIRED"

    print("\nDATASET STATUS:", status)
    logging.info("Validation completed.")
    logging.info(f"Dataset status: {status}")

    return quality_report, status
#-------------------------------------------------
#-------------------------------------------------
def load_data(df, quality_report):

    print("\n" + "=" * 70)
    print("LOAD")
    print("=" * 70)

    logging.info("Loading Data.")
    # Output paths
    output_dataset = (
        BASE_DIR
        / "datasets"
        / "marketing_campaign_cleaned.csv"
    )

    quality_report_path = (
        BASE_DIR
        / "datasets"
        / "data_quality_report.csv"
    )

    # Save cleaned dataset
    df.to_csv(
        output_dataset,
        index=False
    )

    print(
        f"Cleaned dataset loaded to: {output_dataset}"
    )

    # Save quality report
    quality_report.to_csv(
        quality_report_path,
        index=False
    )

    print(
        f"Quality report loaded to: {quality_report_path}"
    )
    logging.info(f"Cleaned dataset saved to: {output_dataset}")
    logging.info(f"Quality report saved to: {quality_report_path}")
    logging.info("Load completed successfully.")
#-------------------------------------------------
#-------------------------------------------------

def heading(title):
    print("=" * 50)
    print(" > " * 5 + title + " > " * 5)
    print("=" * 50)


def main():
    #EXTRACT
    logging.info("Pipeline started.")
    df = extract_data(DATASET)

    # TRANSFORM
    if df is None:
        logging.error("❌ Pipeline stopped: extraction failed.")
        return
    
    df = transform_data(df)

    # VALIDATE
    quality_report, status = validate_data(df)

    # LOAD
    if status == "PASS":
        load_data(df, quality_report)
        
        print("LOAD COMPLETED SUCCESSFULLY")
    else:
        logging.warning("⚠️ Pipeline stopped: data quality review required.")
        print("⚠️ Pipeline stopped: data quality review required.")


if __name__ == "__main__":
    main()  






