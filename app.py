
import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
from pathlib import Path

st.set_page_config(
    page_title="Electricity Bill Estimation System",
    page_icon="⚡",
    layout="wide"
)

DB_PATH = Path(__file__).with_name("electricity_web.db")


def get_connection():
    return sqlite3.connect(DB_PATH)


def create_database():
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS bills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            consumer TEXT,
            units REAL,
            amount REAL,
            bill_date TEXT
        )
    """)
    conn.commit()
    conn.close()


def calculate_amount(units):
    if units <= 100:
        return 0
    elif units <= 200:
        return (units - 100) * 2.25
    elif units <= 400:
        return 100 * 2.25 + (units - 200) * 4.50
    else:
        return 100 * 2.25 + 200 * 4.50 + (units - 400) * 6


def get_bills():
    conn = get_connection()
    df = pd.read_sql_query(
        "SELECT * FROM bills ORDER BY id DESC", conn
    )
    conn.close()
    return df


create_database()

st.title("⚡ Electricity Bill Estimation System")
st.caption("Calculate, manage and track electricity bills")

st.info(
    "Note: The tariff rates used here are illustrative sample rates "
    "for academic demonstration, not official electricity tariffs."
)

menu = st.sidebar.radio(
    "Navigation",
    ["Home", "Calculate Bill", "Bill History",
     "Dashboard", "Search Consumer", "Monthly Report"]
)

if menu == "Home":
    st.subheader("Welcome!")
    st.write(
        "This application helps users estimate electricity bills, "
        "save customer records and view billing reports."
    )

    df = get_bills()

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Bills", len(df))
    col2.metric("Total Units", f"{df['units'].sum():.0f}" if not df.empty else "0")
    col3.metric("Total Amount", f"₹{df['amount'].sum():,.2f}" if not df.empty else "₹0.00")

    st.subheader("Energy Saving Tips")
    st.write("- Switch off unused electrical appliances.")
    st.write("- Use LED bulbs.")
    st.write("- Avoid unnecessary air conditioner usage.")
    st.write("- Choose energy-efficient appliances.")

elif menu == "Calculate Bill":
    st.subheader("Calculate Electricity Bill")

    with st.form("bill_form"):
        name = st.text_input("Customer Name")
        consumer = st.text_input("Consumer Number")
        units = st.number_input(
            "Electricity Units",
            min_value=0.0,
            step=1.0
        )

        submitted = st.form_submit_button("Calculate Bill")

    if submitted:
        if not name.strip() or not consumer.strip():
            st.error("Please enter customer name and consumer number.")
        else:
            amount = calculate_amount(units)
            bill_date = datetime.now().strftime("%Y-%m-%d")

            conn = get_connection()
            conn.execute(
                """INSERT INTO bills
                (name, consumer, units, amount, bill_date)
                VALUES (?, ?, ?, ?, ?)""",
                (name.strip(), consumer.strip(), units, amount, bill_date)
            )
            conn.commit()
            conn.close()

            st.success("Bill saved successfully!")
            st.metric("Estimated Electricity Bill", f"₹{amount:,.2f}")

            st.write("### Bill Receipt")
            st.write("Customer:", name)
            st.write("Consumer Number:", consumer)
            st.write("Units Consumed:", units)
            st.write("Bill Date:", bill_date)
            st.write("Amount:", f"₹{amount:,.2f}")

elif menu == "Bill History":
    st.subheader("Bill History")
    df = get_bills()

    if df.empty:
        st.info("No bills have been saved yet.")
    else:
        st.dataframe(df, use_container_width=True)

        st.download_button(
            "Download Bill History as CSV",
            df.to_csv(index=False).encode("utf-8"),
            file_name="electricity_bills.csv",
            mime="text/csv"
        )

elif menu == "Dashboard":
    st.subheader("Dashboard")
    df = get_bills()

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Bills", len(df))
    col2.metric("Total Units", f"{df['units'].sum():,.0f}" if not df.empty else "0")
    col3.metric("Total Revenue", f"₹{df['amount'].sum():,.2f}" if not df.empty else "₹0.00")

    if not df.empty:
        st.subheader("Bill Amounts")
        st.bar_chart(df.set_index("id")["amount"])

elif menu == "Search Consumer":
    st.subheader("Search Consumer")

    consumer = st.text_input("Enter Consumer Number")

    if st.button("Search"):
        conn = get_connection()
        df = pd.read_sql_query(
            """SELECT * FROM bills
            WHERE consumer = ?
            ORDER BY id DESC""",
            conn,
            params=(consumer.strip(),)
        )
        conn.close()

        if df.empty:
            st.warning("No records found.")
        else:
            st.dataframe(df, use_container_width=True)

elif menu == "Monthly Report":
    st.subheader("Monthly Bill Report")

    df = get_bills()

    if df.empty:
        st.info("No bill records available.")
    else:
        df["bill_date"] = pd.to_datetime(df["bill_date"])
        df["month"] = df["bill_date"].dt.strftime("%B %Y")

        months = sorted(df["month"].unique(), reverse=True)
        selected_month = st.selectbox("Select Month", months)

        report = df[df["month"] == selected_month]

        st.metric("Bills Generated", len(report))
        st.metric("Total Units", f"{report['units'].sum():,.0f}")
        st.metric("Total Amount", f"₹{report['amount'].sum():,.2f}")

        st.dataframe(
            report.drop(columns=["month"]),
            use_container_width=True
        )

st.sidebar.caption("Electricity Bill Estimation System")
st.sidebar.caption("Academic Capstone Project")

