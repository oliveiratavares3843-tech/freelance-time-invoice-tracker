import streamlit as st
import pandas as pd
import sqlite3
from datetime import date
from fpdf import FPDF

# Page Configuration
st.set_page_config(
    page_title="Freelance Time & Invoice Tracker",
    page_icon="⏱️",
    layout="wide"
)

# Database Initialization
def init_db():
    conn = sqlite3.connect("freelance_tracker.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS work_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            work_date TEXT,
            client_platform TEXT,
            task_description TEXT,
            hours REAL,
            hourly_rate REAL,
            total_usd REAL
        )
    """)
    conn.commit()
    conn.close()

def add_log(work_date, client_platform, task_description, hours, hourly_rate):
    total_usd = round(hours * hourly_rate, 2)
    conn = sqlite3.connect("freelance_tracker.db")
    c = conn.cursor()
    c.execute("""
        INSERT INTO work_logs (work_date, client_platform, task_description, hours, hourly_rate, total_usd)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (str(work_date), client_platform, task_description, hours, hourly_rate, total_usd))
    conn.commit()
    conn.close()

def get_logs():
    conn = sqlite3.connect("freelance_tracker.db")
    df = pd.read_sql_query("SELECT * FROM work_logs ORDER BY work_date DESC", conn)
    conn.close()
    return df

def delete_log(log_id):
    conn = sqlite3.connect("freelance_tracker.db")
    c = conn.cursor()
    c.execute("DELETE FROM work_logs WHERE id = ?", (log_id,))
    conn.commit()
    conn.close()

# PDF Invoice Generator
def generate_invoice_pdf(df, client_name, freelancer_name, freelancer_email, invoice_number):
    pdf = FPDF()
    pdf.add_page()
    
    # Header
    pdf.set_font("Helvetica", "B", 20)
    pdf.cell(0, 10, "INVOICE", ln=True, align="R")
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 6, f"Invoice #: {invoice_number}", ln=True, align="R")
    pdf.cell(0, 6, f"Date: {date.today().strftime('%Y-%m-%d')}", ln=True, align="R")
    pdf.ln(10)

    # From / To Details
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(95, 6, "From:", ln=False)
    pdf.cell(95, 6, "Bill To:", ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(95, 6, freelancer_name, ln=False)
    pdf.cell(95, 6, client_name, ln=True)
    pdf.cell(95, 6, freelancer_email, ln=True)
    pdf.ln(10)

    # Table Header
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_fill_color(230, 230, 230)
    pdf.cell(28, 8, "Date", border=1, fill=True)
    pdf.cell(82, 8, "Description", border=1, fill=True)
    pdf.cell(25, 8, "Hours", border=1, align="R", fill=True)
    pdf.cell(27, 8, "Rate (USD)", border=1, align="R", fill=True)
    pdf.cell(28, 8, "Amount", border=1, align="R", fill=True, ln=True)

    # Table Rows
    pdf.set_font("Helvetica", "", 9)
    for _, row in df.iterrows():
        desc = str(row["task_description"])[:42]
        pdf.cell(28, 8, str(row["work_date"]), border=1)
        pdf.cell(82, 8, desc, border=1)
        pdf.cell(25, 8, f"{row['hours']:.2f}", border=1, align="R")
        pdf.cell(27, 8, f"${row['hourly_rate']:.2f}", border=1, align="R")
        pdf.cell(28, 8, f"${row['total_usd']:.2f}", border=1, align="R", ln=True)

    # Total
    total_amount = df["total_usd"].sum()
    total_hours = df["hours"].sum()
    pdf.ln(4)
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(135, 8, f"Total Hours: {total_hours:.2f} hrs", ln=False)
    pdf.cell(55, 8, f"Total Due: USD ${total_amount:,.2f}", align="R", ln=True)

    return bytes(pdf.output())

# Initialize App
init_db()

st.title("⏱️ Freelance Time & Invoice Tracker")
st.markdown("Track remote work hours, calculate USD/BRL net earnings, and generate professional PDF invoices.")

# Sidebar - Currency & Tax Settings
st.sidebar.header("💱 Exchange & Net Settings")
usd_to_brl = st.sidebar.number_input("USD to BRL Exchange Rate", min_value=1.0, value=5.64, step=0.05)
fee_percent = st.sidebar.slider("Transfer Fee & Tax Deduction (%)", min_value=0.0, max_value=30.0, value=8.0, step=0.5)

st.sidebar.divider()
st.sidebar.header("➕ Log Work Session")
with st.sidebar.form("log_form", clear_on_submit=True):
    work_date = st.date_input("Date", value=date.today())
    client_platform = st.text_input("Client / Platform", placeholder="e.g., Alignerr, Turing, Direct Client")
    task_description = st.text_input("Task Description", placeholder="e.g., Python API Development / AI Evaluation")
    hours = st.number_input("Hours Worked", min_value=0.25, max_value=24.0, value=2.0, step=0.25)
    hourly_rate = st.number_input("Hourly Rate (USD)", min_value=1.0, max_value=500.0, value=25.0, step=1.0)
    submitted = st.form_submit_button("Save Work Log", use_container_width=True)

    if submitted:
        if client_platform.strip() and task_description.strip():
            add_log(work_date, client_platform.strip(), task_description.strip(), hours, hourly_rate)
            st.sidebar.success("Work session logged!")
            st.rerun()
        else:
            st.sidebar.error("Please fill in Client and Task Description.")

# Load Data
df = get_logs()

if df.empty:
    st.info("No work logs recorded yet. Use the sidebar on the left to add your first work session.")
else:
    # Filter by Client
    clients = ["All Clients"] + sorted(df["client_platform"].unique().tolist())
    selected_client = st.selectbox("Filter by Client / Platform", clients)

    filtered_df = df if selected_client == "All Clients" else df[df["client_platform"] == selected_client]

    # Metrics Calculation
    total_hours = filtered_df["hours"].sum()
    gross_usd = filtered_df["total_usd"].sum()
    gross_brl = gross_usd * usd_to_brl
    net_brl = gross_brl * (1 - (fee_percent / 100))

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Hours", f"{total_hours:.2f} h")
    col2.metric("Gross Earnings (USD)", f"${gross_usd:,.2f}")
    col3.metric("Gross Earnings (BRL)", f"R$ {gross_brl:,.2f}")
    col4.metric("Estimated Net (BRL)", f"R$ {net_brl:,.2f}", delta=f"-{fee_percent}% fees/taxes", delta_color="inverse")

    st.divider()

    # Tabs for Data & Invoice Generation
    tab1, tab2 = st.tabs(["📊 Work Logs & Analytics", "📄 Generate PDF Invoice"])

    with tab1:
        st.subheader("Recorded Work Sessions")
        display_df = filtered_df.rename(columns={
            "id": "ID",
            "work_date": "Date",
            "client_platform": "Client / Platform",
            "task_description": "Description",
            "hours": "Hours",
            "hourly_rate": "Rate (USD)",
            "total_usd": "Total (USD)"
        })
        st.dataframe(display_df, use_container_width=True, hide_index=True)

        # Bar Chart by Client
        st.subheader("Earnings by Client / Platform (USD)")
        chart_data = df.groupby("client_platform")["total_usd"].sum()
        st.bar_chart(chart_data)

        # Delete entry option
        with st.expander("🗑️ Delete a Work Log"):
            log_to_delete = st.selectbox("Select Log ID to Remove", filtered_df["id"].tolist())
            if st.button("Delete Selected Entry"):
                delete_log(log_to_delete)
                st.warning(f"Log ID {log_to_delete} deleted.")
                st.rerun()

    with tab2:
        st.subheader("Export Professional Invoice (PDF)")
        c1, c2 = st.columns(2)
        with c1:
            freelancer_name = st.text_input("Your Full Name / Business Name", value="Euclides Tavares de Oliveira")
            freelancer_email = st.text_input("Your Contact Email", placeholder="your.email@example.com")
        with c2:
            bill_to = st.text_input("Bill To (Client Name)", value=selected_client if selected_client != "All Clients" else "International Client")
            invoice_num = st.text_input("Invoice Number", value=f"INV-{date.today().strftime('%Y%m')}-001")

        if st.button("Generate Invoice PDF", type="primary"):
            pdf_bytes = generate_invoice_pdf(filtered_df, bill_to, freelancer_name, freelancer_email, invoice_num)
            st.download_button(
                label="⬇️ Download Invoice PDF",
                data=pdf_bytes,
                file_name=f"{invoice_num}.pdf",
                mime="application/pdf"
            )

