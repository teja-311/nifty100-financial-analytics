import sqlite3
import pandas as pd
import streamlit as st

DB_PATH = "db/nifty100.db"


@st.cache_data(ttl=600)
def query(sql):

    conn = sqlite3.connect(DB_PATH)

    df = pd.read_sql(sql, conn)

    conn.close()

    return df


def get_companies():
    return query("SELECT * FROM companies")


def get_ratios():
    return query("SELECT * FROM financial_ratios")


def get_pl():
    return query("SELECT * FROM profitandloss")


def get_bs():
    return query("SELECT * FROM balancesheet")


def get_cf():
    return query("SELECT * FROM cashflow")


def get_sectors():
    return query("SELECT * FROM sectors")


def get_peers():
    return query("SELECT * FROM peer_groups")


def get_market():
    return query("SELECT * FROM market_cap")

def get_documents():

    return query("""
        SELECT
            d.company_id,
            c.company_name,
            d.year,
            d.annual_report
        FROM documents d
        LEFT JOIN companies c
            ON d.company_id = c.id
        ORDER BY c.company_name, d.year DESC
    """)