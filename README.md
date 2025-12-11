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

## 📂 Project Structure
sales_tracking/
│
├── app.py # Main Flask app
├── api.py # JSON API endpoints
├── models.py # Database models
├── stats.py # Analytics logic
├── database.py # DB engine + session
├── requirements.txt # Python dependencies
│
├── templates/ # HTML templates
│ ├── index.html
│ ├── items.html
│ ├── edit_item.html
│ ├── stats.html
│ └── dashboard.html
│
└── menu_tracker.db # SQLite DB (ignored in Git)

## 🛠 Installation

### 1. Clone the project
```bash
git clone https://github.com/rushabhgala/sales_tracking.git
cd sales_tracking

### 2. Set up virtual environment
python3 -m venv .venv
source .venv/bin/activate

### 3. Install dependencies
pip install -r requirements.txt

### 4. Run the server
python app.py

