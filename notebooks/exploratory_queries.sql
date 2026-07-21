-- =====================================================
-- Exploratory SQL Queries
-- Nifty 100 Financial Analytics Project
-- =====================================================


---------------------------------------------------------
-- 1. Total Companies
---------------------------------------------------------

SELECT COUNT(*) AS total_companies
FROM companies;


---------------------------------------------------------
-- 2. Companies by Sector
---------------------------------------------------------

SELECT
    broad_sector,
    COUNT(*) AS companies
FROM sectors
GROUP BY broad_sector
ORDER BY companies DESC;


---------------------------------------------------------
-- 3. Top 10 Companies by Market Cap
---------------------------------------------------------

SELECT
    company_id,
    market_cap_crore
FROM market_cap
ORDER BY market_cap_crore DESC
LIMIT 10;


---------------------------------------------------------
-- 4. Top ROE Companies
---------------------------------------------------------

SELECT
    company_id,
    return_on_equity_pct
FROM financial_ratios
ORDER BY return_on_equity_pct DESC
LIMIT 10;


---------------------------------------------------------
-- 5. Lowest Debt to Equity
---------------------------------------------------------

SELECT
    company_id,
    debt_to_equity
FROM financial_ratios
ORDER BY debt_to_equity ASC
LIMIT 10;


---------------------------------------------------------
-- 6. Highest Revenue CAGR
---------------------------------------------------------

SELECT
    company_id,
    revenue_cagr_5yr
FROM financial_ratios
ORDER BY revenue_cagr_5yr DESC
LIMIT 10;


---------------------------------------------------------
-- 7. Highest PAT CAGR
---------------------------------------------------------

SELECT
    company_id,
    pat_cagr_5yr
FROM financial_ratios
ORDER BY pat_cagr_5yr DESC
LIMIT 10;


---------------------------------------------------------
-- 8. Companies with Negative Free Cash Flow
---------------------------------------------------------

SELECT
    company_id,
    free_cash_flow_cr
FROM financial_ratios
WHERE free_cash_flow_cr < 0;


---------------------------------------------------------
-- 9. Sector Average PE
---------------------------------------------------------

SELECT
    s.broad_sector,
    ROUND(AVG(f.pe_ratio),2) AS avg_pe
FROM financial_ratios f
JOIN sectors s
ON f.company_id=s.company_id
GROUP BY s.broad_sector
ORDER BY avg_pe DESC;


---------------------------------------------------------
-- 10. Benchmark Companies
---------------------------------------------------------

SELECT
    peer_group_name,
    company_id
FROM peer_groups
WHERE is_benchmark=1;