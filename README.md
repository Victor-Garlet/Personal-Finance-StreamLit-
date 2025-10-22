# 💰 Personal-Finance-StreamLit

This project is an interactive Streamlit application that helps users **track income and expenses, monitor wealth growth, and set realistic financial goals**.  
It integrates data visualization, statistical analysis, and real interest rate adjustments (via Brazil's Central Bank API) to help you make smarter financial decisions.

---

## 📊 Features

- **Upload CSV financial data** (date, institution, and amount)
- **Automatic data visualization**
  - Time-series analysis
  - Distribution by financial institution
  - Wealth evolution over time
- **Smart metrics calculation**
  - Monthly and yearly growth (absolute and relative)
  - Rolling averages (6M, 12M, 24M)
  - Cumulative performance indicators
- **Goal tracking**
  - Define custom targets
  - Compare projected vs. achieved performance
  - Visualize progress toward annual goals
- **Integrated SELIC rate**
  - Automatic interest rate retrieval from the Central Bank of Brazil API
  - Realistic net worth projections

---

## 🧠 Tech Stack

- **Python 3.11+**
- **Streamlit** – front-end framework for interactive dashboards  
- **Pandas** – data manipulation and aggregation  
- **Requests** – API integration with BCB (Central Bank of Brazil)  
- **Datetime** – time-based data transformations  

---

## 🧩 App Structure
📂 moneydesk/
┣ 📜 app.py # Main Streamlit script
┣ 📦 requirements.txt # Dependencies
┗ 📄 README.md # Documentation
