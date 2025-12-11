from datetime import date, timedelta
from sqlalchemy import func

from models import MenuItem, SaleLog


# ---------------------------------------------------------
# HELPER
# ---------------------------------------------------------

def get_week_start(d):
    return d - timedelta(days=d.weekday())


# ---------------------------------------------------------
# A) DAILY / WEEKLY / MONTHLY — USER SCOPED
# ---------------------------------------------------------

def get_daily_sales(db, target_date):
    """Return sales per item and total earnings for a specific date."""
    rows = (
        db.query(
            MenuItem.name,
            MenuItem.price,
            func.sum(SaleLog.quantity).label("qty")
        )
        .join(SaleLog, SaleLog.item_id == MenuItem.id)
        .filter(SaleLog.date == target_date)
        .group_by(MenuItem.name, MenuItem.price)
        .all()
    )

    total_qty = sum(row.qty for row in rows)
    total_earn = sum(row.qty * row.price for row in rows)

    return rows, total_qty, total_earn



def get_weekly_sales(db, start_date):
    """Return sales for a 7-day period starting at start_date."""
    end_date = start_date + timedelta(days=7)

    rows = (
        db.query(
            MenuItem.name,
            MenuItem.price,
            func.sum(SaleLog.quantity).label("qty")
        )
        .join(SaleLog, SaleLog.item_id == MenuItem.id)
        .filter(SaleLog.date >= start_date)
        .filter(SaleLog.date < end_date)
        .group_by(MenuItem.name, MenuItem.price)
        .all()
    )

    total_qty = sum(row.qty for row in rows)
    total_earn = sum(row.qty * row.price for row in rows)

    return rows, total_qty, total_earn



def get_monthly_sales(db, year, month):
    """Return sales for a given month."""
    rows = (
        db.query(
            MenuItem.name,
            MenuItem.price,
            func.sum(SaleLog.quantity).label("qty")
        )
        .join(SaleLog, SaleLog.item_id == MenuItem.id)
        .filter(func.extract("year", SaleLog.date) == year)
        .filter(func.extract("month", SaleLog.date) == month)
        .group_by(MenuItem.name, MenuItem.price)
        .all()
    )

    total_qty = sum(row.qty for row in rows)
    total_earn = sum(row.qty * row.price for row in rows)

    return rows, total_qty, total_earn



# ---------------------------------------------------------
# B) ITEM-SPECIFIC — USER SCOPED
# ---------------------------------------------------------

def get_item_summary(db, item_id):
    """Return today, week, month totals for ONE item belonging."""
    today = date.today()
    week_start = get_week_start(today)
    year, month = today.year, today.month

    # TODAY
    t = (
        db.query(
            func.sum(SaleLog.quantity),
            func.sum(SaleLog.quantity * MenuItem.price)
        )
        .join(MenuItem)
        .filter(SaleLog.item_id == item_id)
        .filter(SaleLog.date == today)
        .first()
    )

    # WEEK
    w = (
        db.query(
            func.sum(SaleLog.quantity),
            func.sum(SaleLog.quantity * MenuItem.price)
        )
        .join(MenuItem)
        .filter(SaleLog.item_id == item_id)
        .filter(SaleLog.date >= week_start)
        .filter(SaleLog.date <= today)
        .first()
    )

    # MONTH
    m = (
        db.query(
            func.sum(SaleLog.quantity),
            func.sum(SaleLog.quantity * MenuItem.price)
        )
        .join(MenuItem)
        .filter(SaleLog.item_id == item_id)
        .filter(func.extract("year", SaleLog.date) == year)
        .filter(func.extract("month", SaleLog.date) == month)
        .first()
    )

    return {
        "today": {"qty": t[0] or 0, "earn": float(t[1] or 0)},
        "week": {"qty": w[0] or 0, "earn": float(w[1] or 0)},
        "month": {"qty": m[0] or 0, "earn": float(m[1] or 0)}
    }



def get_item_week_breakdown(db, item_id):
    """Return qty & earnings for each weekday (Mon–Sun)."""
    today = date.today()
    week_start = get_week_start(today)

    rows = (
        db.query(
            SaleLog.date,
            func.sum(SaleLog.quantity).label("qty"),
            func.sum(SaleLog.quantity * MenuItem.price).label("earn")
        )
        .join(MenuItem)
        .filter(SaleLog.item_id == item_id)
        .filter(SaleLog.date >= week_start)
        .filter(SaleLog.date <= today)
        .group_by(SaleLog.date)
        .all()
    )

    labels = []
    qty = []
    earn = []

    for i in range(7):
        d = week_start + timedelta(days=i)
        labels.append(d.strftime("%a"))

        match = next((r for r in rows if r.date == d), None)
        qty.append(match.qty if match else 0)
        earn.append(float(match.earn or 0) if match else 0)

    return {"labels": labels, "qty": qty, "earn": earn}



def get_item_month_breakdown(db, item_id):
    """Return qty & earnings per week of current month."""
    today = date.today()
    year, month = today.year, today.month

    rows = (
        db.query(
            func.strftime("%W", SaleLog.date).label("weeknum"),
            func.sum(SaleLog.quantity).label("qty"),
            func.sum(SaleLog.quantity * MenuItem.price).label("earn")
        )
        .join(MenuItem)
        .filter(SaleLog.item_id == item_id)
        .filter(func.extract("year", SaleLog.date) == year)
        .filter(func.extract("month", SaleLog.date) == month)
        .group_by(func.strftime("%W", SaleLog.date))
        .order_by(func.strftime("%W", SaleLog.date))
        .all()
    )

    labels = []
    qty_list = []
    earn_list = []

    for r in rows:
        labels.append(f"Week {int(r.weeknum)}")
        qty_list.append(r.qty)
        earn_list.append(float(r.earn))

    return {"labels": labels, "qty": qty_list, "earn": earn_list}
