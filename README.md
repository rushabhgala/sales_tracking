# 📘 Sales Tracking App

A simple, fast, and mobile-friendly **Flask application** to track daily, weekly, and monthly sales of menu items.

## 🚀 Features

### ✔ Menu Management
- Add new items  
- Edit item name & price  
- Delete items  
- Automatically calculates revenue

### ✔ Sales Logging
- Log item sales for any date  
- Store quantity sold  
- Auto-calculated earnings (₹)

### ✔ Analytics & Dashboard
- Daily sales summary  
- Weekly totals  
- Monthly totals  
- Best-selling items  
- Detailed per-item breakdown  
- 4 interactive charts using Chart.js:
  - Weekly quantity  
  - Weekly earnings  
  - Monthly quantity  
  - Monthly earnings

### ✔ API Endpoints (used by charts)
- `/api/daily`
- `/api/weekly`
- `/api/monthly`
- `/api/item_summary/<item_id>`
- `/api/item_week_breakdown/<item_id>`
- `/api/item_month_breakdown/<item_id>`

---


## 🛠 Installation

### 1. Clone the project
```bash
git clone https://github.com/rushabhgala/sales_tracking.git
cd sales_tracking
```

### 2. Set up virtual environment
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the server
```bash
python app.py
```
