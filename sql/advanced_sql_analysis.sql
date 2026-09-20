/*
===========================================================
Advanced SQL Analytical Reporting
Project: Marketing Campaign Data Pipeline
Database: MarketingCampaignDB
Author: Michael Albert
===========================================================

Purpose:
This script contains advanced SQL analysis developed for
the Marketing Campaign Data Pipeline project.

Topics covered:
- Common Table Expressions (CTEs)
- Subqueries
- Window Functions
- Ranking
- Running Totals
- PARTITION BY
- SQL Views
- Customer Segmentation
- Campaign Analysis
- Performance Optimization
- Analytical Reporting

Database:
MarketingCampaignDB

SQL Server:
Michael\SQLEXPRESS
===========================================================
*/


/* =========================================================
   SECTION 1: CTEs & CUSTOMER SEGMENTATION
   =========================================================

   Goal:
   Create a reusable analytical result that classifies
   customers based on TotalSpending.
*/

WITH CustomerSegments AS
(
    SELECT
        CustomerID,
        Education,
        Income,
        TotalSpending,
        Response,

        CASE
            WHEN TotalSpending >= 1000 THEN 'High Value'
            WHEN TotalSpending >= 500 THEN 'Medium Value'
            ELSE 'Low Value'
        END AS CustomerSegment

    FROM dbo.CustomerSpendingAnalysis
)

SELECT
    CustomerSegment,
    COUNT(*) AS CustomerCount,
    SUM(TotalSpending) AS TotalSegmentSpending,
    AVG(TotalSpending) AS AverageSegmentSpending

FROM CustomerSegments

GROUP BY CustomerSegment

ORDER BY TotalSegmentSpending DESC;


/* =========================================================
   SECTION 2: WINDOW FUNCTIONS & CUSTOMER RANKING
   =========================================================

   Goal:
   Rank customers by spending without collapsing the
   individual customer rows.

   RANK() assigns the same rank to tied values and leaves
   gaps after ties.
*/

SELECT
    CustomerID,
    Education,
    TotalSpending,

    RANK() OVER (
        ORDER BY TotalSpending DESC
    ) AS SpendingRank

FROM dbo.CustomerSpendingAnalysis

ORDER BY SpendingRank;

/* ---------------------------------------------------------
   Rank customers within each customer segment.
   --------------------------------------------------------- */

SELECT
    CustomerID,
    Education,
    TotalSpending,
    CustomerSegment,

    RANK() OVER (
        PARTITION BY CustomerSegment
        ORDER BY TotalSpending DESC
    ) AS SegmentSpendingRank

FROM dbo.CustomerSpendingAnalysis

ORDER BY
    CustomerSegment,
    SegmentSpendingRank;


    /* =========================================================
   SECTION 3: LAG, LEAD & RUNNING TOTALS
   =========================================================

   Goal:
   Compare customers with previous/next rows and calculate
   cumulative spending using window functions.
*/


/* ---------------------------------------------------------
   3.1 LAG()
   Compare a customer's spending with the previous customer.
   --------------------------------------------------------- */

SELECT
    CustomerID,
    TotalSpending,

    LAG(TotalSpending) OVER (
        ORDER BY TotalSpending DESC
    ) AS PreviousSpending,

    TotalSpending
        - LAG(TotalSpending) OVER (
            ORDER BY TotalSpending DESC
          ) AS SpendingDifference

FROM dbo.CustomerSpendingAnalysis

ORDER BY TotalSpending DESC;


/* ---------------------------------------------------------
   3.2 LEAD()
   Compare a customer's spending with the next customer.
   --------------------------------------------------------- */

SELECT
    CustomerID,
    TotalSpending,

    LEAD(TotalSpending) OVER (
        ORDER BY TotalSpending DESC
    ) AS NextSpending,

    LEAD(TotalSpending) OVER (
        ORDER BY TotalSpending DESC
    ) - TotalSpending AS DifferenceToNextCustomer

FROM dbo.CustomerSpendingAnalysis

ORDER BY TotalSpending DESC;


/* ---------------------------------------------------------
   3.3 RUNNING TOTAL
   Calculate cumulative spending as customers are ordered
   from highest to lowest spending.
   --------------------------------------------------------- */

SELECT
    CustomerID,
    TotalSpending,

    SUM(TotalSpending) OVER (
        ORDER BY TotalSpending DESC
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) AS RunningTotal

FROM dbo.CustomerSpendingAnalysis

ORDER BY TotalSpending DESC;


/* =========================================================
   SECTION 4: PERCENTAGE ANALYSIS WITH OVER()
   =========================================================

   Goal:
   Calculate each customer's percentage contribution to
   their customer segment's total spending.

   Unlike GROUP BY, the OVER() function allows us to
   calculate the segment total while keeping every
   individual customer row.
*/


SELECT
    CustomerID,
    Education,
    TotalSpending,
    CustomerSegment,

    SUM(TotalSpending) OVER (
        PARTITION BY CustomerSegment
    ) AS SegmentTotalSpending,

    ROUND(
        TotalSpending * 100.0 /
        SUM(TotalSpending) OVER (
            PARTITION BY CustomerSegment
        ),
        2
    ) AS SegmentSpendingPercentage

FROM dbo.CustomerSpendingAnalysis

ORDER BY
    CustomerSegment,
    SegmentSpendingPercentage DESC;


    /* =========================================================
   SECTION 5: OVER() WITHOUT PARTITION BY
   =========================================================

   Goal:
   Calculate each customer's percentage contribution to
   the total spending of all customers.

   Without PARTITION BY, the window function operates
   across the entire result set.
*/


SELECT
    CustomerID,
    Education,
    TotalSpending,
    CustomerSegment,

    SUM(TotalSpending) OVER () AS OverallTotalSpending,

    ROUND(
        TotalSpending * 100.0 /
        SUM(TotalSpending) OVER (),
        2
    ) AS OverallSpendingPercentage

FROM dbo.CustomerSpendingAnalysis

ORDER BY
    OverallSpendingPercentage DESC;



/* =========================================================
   SECTION 6: SQL VIEWS
   =========================================================

   Goal:
   Understand how SQL Views provide a reusable analytical
   layer for reporting.

   The CustomerSpendingAnalysis view already exists in the
   MarketingCampaignDB database.

   Instead of recreating the production view here, we will
   query and inspect the existing view.
*/


/* ---------------------------------------------------------
   6.1 QUERY THE EXISTING VIEW
   --------------------------------------------------------- */

SELECT
    CustomerID,
    Education,
    Income,
    TotalSpending,
    CustomerSegment,
    Response

FROM dbo.CustomerSpendingAnalysis

ORDER BY TotalSpending DESC;


/* ---------------------------------------------------------
   6.2 FILTER THE VIEW
   ---------------------------------------------------------

   Example:
   Retrieve only High Value customers.
   --------------------------------------------------------- */

SELECT
    CustomerID,
    Education,
    Income,
    TotalSpending,
    CustomerSegment,
    Response

FROM dbo.CustomerSpendingAnalysis

WHERE CustomerSegment = 'High Value'

ORDER BY TotalSpending DESC;


/* ---------------------------------------------------------
   6.3 USE THE VIEW FOR SUMMARY REPORTING
   --------------------------------------------------------- */

SELECT
    CustomerSegment,
    COUNT(*) AS CustomerCount,
    SUM(TotalSpending) AS TotalSpending,
    ROUND(AVG(TotalSpending), 2) AS AverageSpending

FROM dbo.CustomerSpendingAnalysis

GROUP BY CustomerSegment

ORDER BY TotalSpending DESC;


    /* =========================================================
   SECTION 7: REUSABLE REPORTING QUERIES
   =========================================================

   Goal:
   Build reusable business reports from the
   CustomerSpendingAnalysis view.
*/


/* ---------------------------------------------------------
   7.1 CUSTOMER SEGMENT PERFORMANCE
   --------------------------------------------------------- */

SELECT
    CustomerSegment,
    COUNT(*) AS CustomerCount,
    SUM(TotalSpending) AS TotalSpending,
    ROUND(AVG(TotalSpending), 2) AS AverageSpending

FROM dbo.CustomerSpendingAnalysis

GROUP BY CustomerSegment

ORDER BY TotalSpending DESC;


/* ---------------------------------------------------------
   7.2 CUSTOMER SEGMENT RESPONSE RATE
   --------------------------------------------------------- */

SELECT
    CustomerSegment,
    COUNT(*) AS CustomerCount,

    SUM(
        CASE
            WHEN Response = 1 THEN 1
            ELSE 0
        END
    ) AS Responders,

    ROUND(
        SUM(
            CASE
                WHEN Response = 1 THEN 1
                ELSE 0
            END
        ) * 100.0 / COUNT(*),
        2
    ) AS ResponseRate

FROM dbo.CustomerSpendingAnalysis

GROUP BY CustomerSegment

ORDER BY ResponseRate DESC;


/* ---------------------------------------------------------
   7.3 EDUCATION PERFORMANCE
   --------------------------------------------------------- */

SELECT
    Education,
    COUNT(*) AS CustomerCount,
    ROUND(AVG(TotalSpending), 2) AS AverageSpending,

    SUM(
        CASE
            WHEN Response = 1 THEN 1
            ELSE 0
        END
    ) AS Responders

FROM dbo.CustomerSpendingAnalysis

GROUP BY Education

ORDER BY AverageSpending DESC;


/* =========================================================
   SECTION 8: SQL PERFORMANCE BASICS
   =========================================================

   Goal:
   Inspect indexes and measure query performance.

   Topics:
   - Index inspection
   - Logical reads
   - Query performance
   - Nonclustered indexes
*/


/* ---------------------------------------------------------
   8.1 INSPECT EXISTING INDEXES
   --------------------------------------------------------- */

SELECT
    t.name AS TableName,
    i.name AS IndexName,
    i.type_desc AS IndexType

FROM sys.indexes AS i

INNER JOIN sys.tables AS t
    ON i.object_id = t.object_id

WHERE t.name IN
(
    'Customers',
    'CustomerProductSpending',
    'CustomerPurchaseBehavior',
    'CampaignResponses'
)

ORDER BY
    t.name,
    i.name;


    /* ---------------------------------------------------------
   8.2 MEASURE QUERY PERFORMANCE
   --------------------------------------------------------- */

SET STATISTICS IO ON;

SELECT
    CustomerID,
    TotalSpending

FROM dbo.CustomerProductSpending

WHERE TotalSpending >= 1000;

SET STATISTICS IO OFF;

/* ---------------------------------------------------------
   8.3 ACTUAL EXECUTION PLAN
   ---------------------------------------------------------

   Goal:
   Inspect how SQL Server executes the query and determine
   whether the TotalSpending index is being used.
*/

SELECT
    CustomerID,
    TotalSpending

FROM dbo.CustomerProductSpending

WHERE TotalSpending >= 1000;


/* =========================================================
   SECTION 9: FINAL ADVANCED SQL ANALYTICAL QUERY
   =========================================================

   Goal:
   Identify the top 10 spending customers within each
   customer segment.

   The analysis combines:
   - CTEs
   - RANK()
   - PARTITION BY
   - OVER()
   - Percentage calculations
   - CASE expressions
*/


WITH CustomerAnalysis AS
(
    SELECT
        CustomerID,
        Education,
        Income,
        TotalSpending,
        CustomerSegment,
        Response,

        /* Rank customers within each segment */
        RANK() OVER (
            PARTITION BY CustomerSegment
            ORDER BY TotalSpending DESC
        ) AS SegmentSpendingRank,

        /* Customer's percentage of segment spending */
        ROUND(
            TotalSpending * 100.0 /
            SUM(TotalSpending) OVER (
                PARTITION BY CustomerSegment
            ),
            2
        ) AS SegmentSpendingPercentage

    FROM dbo.CustomerSpendingAnalysis
)

SELECT
    CustomerID,
    Education,
    Income,
    TotalSpending,
    CustomerSegment,
    SegmentSpendingRank,

    CAST(
        SegmentSpendingPercentage AS DECIMAL(10,2)
    ) AS SegmentSpendingPercentage,

    CASE
        WHEN Response = 1 THEN 'Responded'
        ELSE 'Did Not Respond'
    END AS CampaignResponse

FROM CustomerAnalysis

WHERE SegmentSpendingRank <= 10

ORDER BY
    CustomerSegment,
    SegmentSpendingRank;