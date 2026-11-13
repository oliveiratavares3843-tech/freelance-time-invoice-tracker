# ⏱️ Freelance Time & Invoice Tracker

A web-based time tracking, currency conversion, and automated PDF invoicing system built with **Python**, **Streamlit**, **Pandas**, and **SQLite**. Designed for remote software engineers and freelancers working with international clients.

## 🚀 Live Demo
[Click here to open the live application](https://seu-link-aqui.streamlit.app) *(replace with your Streamlit Cloud link after deploying)*

## ✨ Key Features
- **Work Session Logging:** Record daily hours, hourly rates (USD), project descriptions, and client names with persistent SQLite storage.
- **Multi-Currency & Net Income Calculator:** Real-time conversion from USD to BRL with customizable exchange rates and tax/transfer fee deductions.
- **Interactive Analytics:** Filter records by client/platform and visualize revenue distribution with dynamic charts.
- **Automated PDF Invoicing:** Generate and download clean, client-ready invoices in PDF format with itemized billing tables.

## 🛠️ Tech Stack
- **Language:** Python 3
- **Frontend / UI:** Streamlit
- **Data Processing:** Pandas
- **Database:** SQLite3
- **PDF Generation:** FPDF2

## 📦 How to Run Locally
1. Clone the repository:
   ```bash
   git clone https://github.com
   cd freelance-time-invoice-tracker
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   streamlit run app.py
   ```

