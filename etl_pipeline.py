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

    birth_year_mask = (
    (df["Year_Birth"] < 1900) |
    (df["Year_Birth"] > 2026)
)

    income_mask = (
        df["Income"] == 666666
    )

    rejected_mask = (
        birth_year_mask |
        income_mask
    )

    rejected_records = df[rejected_mask].copy()
    total_records = len(df)
    rejected_count = len(rejected_records)
    valid_count = total_records - rejected_count

    rejection_rate = (
        rejected_count / total_records * 100
    )
    

    valid_records = df[~rejected_mask].copy()
    print("Total records:", len(df))
    print("Valid records:", len(valid_records))
    print("Rejected records:", len(rejected_records))

    rejected_records["rejected_reason"] = ""

    rejected_records.loc[
        birth_year_mask & income_mask,
        "rejected_reason"
    ] = "Invalid Birth Year; Suspicious Income"

    rejected_records.loc[
        birth_year_mask & ~income_mask,
        "rejected_reason"
    ] = "Invalid Birth Year"

    rejected_records.loc[
        income_mask & ~birth_year_mask,
        "rejected_reason"
    ] = "Suspicious Income"

    rejected_records_path = (
        BASE_DIR
        / "datasets"
        / "rejected_records.csv"
    )

    rejected_records.to_csv(
        rejected_records_path,
        index=False
    )

    logging.info(
        f"Rejected records saved to: {rejected_records_path}"
    )

    print(
        f"Rejected records saved to: {rejected_records_path}"
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

    return quality_report, status, valid_records, rejected_records
#-------------------------------------------------
#-------------------------------------------------
def pipeline_summary(df, valid_records, rejected_records, status):

    print("\n" + "=" * 70)
    print("PIPELINE SUMMARY")
    print("=" * 70)

    total_records = len(df)
    valid_count = len(valid_records)
    rejected_count = len(rejected_records)

    rejection_rate = (
        rejected_count / total_records * 100
    )

    print("Total records:", total_records)
    print("Valid records:", valid_count)
    print("Rejected records:", rejected_count)
    print(f"Rejection rate: {rejection_rate:.2f}%")
    print("Dataset status:", status)

    logging.info(
        f"Pipeline summary | "
        f"Total: {total_records} | "
        f"Valid: {valid_count} | "
        f"Rejected: {rejected_count} | "
        f"Rejection rate: {rejection_rate:.2f}% | "
        f"Status: {status}"
    )

    return (
    total_records,
    valid_count,
    rejected_count,
    rejection_rate
)
#-------------------------------------------------
#-------------------------------------------------
def save_pipeline_summary(
    total_records,
    valid_records,
    rejected_records,
    rejection_rate,
    status
):

    summary_path = (
        BASE_DIR
        / "datasets"
        / "pipeline_summary.csv"
    )

    summary = pd.DataFrame({
        "Metric": [
            "Total Records",
            "Valid Records",
            "Rejected Records",
            "Rejection Rate",
            "Dataset Status"
        ],

        "Value": [
            total_records,
            valid_records,
            rejected_records,
            f"{rejection_rate:.2f}%",
            status
        ]
    })

    summary.to_csv(
        summary_path,
        index=False
    )

    print(
        f"Pipeline summary saved to: {summary_path}"
    )

    logging.info(
        f"Pipeline summary saved to: {summary_path}"
    )
#-------------------------------------------------
#-------------------------------------------------
def load_data(valid_records, quality_report):

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
    valid_records.to_csv(
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
    quality_report, status, valid_records, rejected_records = validate_data(df)

    #PIPELINE SUMMARY
    total_records, valid_count, rejected_count, rejection_rate = pipeline_summary(
    df,
    valid_records,
    rejected_records,
    status
)

    #SAVE PIPELINE SUMMARY
    save_pipeline_summary(
    total_records,
    valid_count,
    rejected_count,
    rejection_rate,
    status
)

    # LOAD
    if len(rejected_records) > 0:

        logging.warning(
        f"{len(rejected_records)} records rejected."
    )

    print(
        f"⚠️ {len(rejected_records)} records rejected and quarantined."
    )

    if len(valid_records) > 0:

        load_data(valid_records, quality_report)

        logging.info(
            f"{len(valid_records)} valid records loaded successfully."
        )

        print(
            f"LOAD COMPLETED: {len(valid_records)} valid records loaded."
        )

    else:

        logging.error("No valid records available for loading.")

        print("❌ No valid records available for loading.")


if __name__ == "__main__":
    main()  






