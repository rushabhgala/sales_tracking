from flask import Blueprint, jsonify, g
from datetime import date, timedelta
from sqlalchemy import func

from models import MenuItem, SaleLog

api = Blueprint("api", __name__)


# ---------------------------------------------------------
# DAILY SALES (user-scoped)
# ---------------------------------------------------------
@api.route("/daily")
def daily_sales_api():
    db = g.db
    today = date.today()

    rows = (
        db.query(
            MenuItem.name,
            func.sum(SaleLog.quantity).label("qty")
        )
        .join(SaleLog)
        .filter(SaleLog.date == today)
        .group_by(MenuItem.name)
        .all()
    )

    return jsonify({
        "labels": [r.name for r in rows],
        "values": [r.qty for r in rows]
    })


# ---------------------------------------------------------
# WEEKLY SALES (user-scoped)
# ---------------------------------------------------------
@api.route("/weekly")
def weekly_sales_api():
    db = g.db

    today = date.today()
    week_start = today - timedelta(days=today.weekday())

    rows = (
        db.query(
            MenuItem.name,
            func.sum(SaleLog.quantity * MenuItem.price).label("earnings")
        )
        .join(SaleLog)
        .filter(SaleLog.date >= week_start)
        .filter(SaleLog.date <= today)
        .group_by(MenuItem.name)
        .all()
    )

    return jsonify({
        "labels": [r.name for r in rows],
        "values": [r.earnings for r in rows]
    })


# ---------------------------------------------------------
# MONTHLY SALES (user-scoped)
# ---------------------------------------------------------
@api.route("/monthly")
def monthly_sales_api():
    db = g.db
    today = date.today()

    rows = (
        db.query(
            MenuItem.name,
            func.sum(SaleLog.quantity).label("qty")
        )
        .join(SaleLog)
        .filter(func.extract("year", SaleLog.date) == today.year)
        .filter(func.extract("month", SaleLog.date) == today.month)
        .group_by(MenuItem.name)
        .all()
    )

    return jsonify({
        "labels": [r.name for r in rows],
        "values": [r.qty for r in rows]
    })


# ---------------------------------------------------------
# ITEM SUMMARY (today, week, month — user-scoped)
# ---------------------------------------------------------
@api.route("/item_summary/<int:item_id>")
def item_summary(item_id):
    db = g.db

    today = date.today()
    week_start = today - timedelta(days=today.weekday())

    # --- TODAY ---
    t = (
        db.query(
            func.sum(SaleLog.quantity).label("qty"),
            func.sum(SaleLog.quantity * MenuItem.price).label("earn")
        )
        .join(MenuItem)
        .filter(SaleLog.item_id == item_id)
        .filter(SaleLog.date == today)
        .first()
    )

    # --- WEEK ---
    w = (
        db.query(
            func.sum(SaleLog.quantity).label("qty"),
            func.sum(SaleLog.quantity * MenuItem.price).label("earn")
        )
        .join(MenuItem)
        .filter(SaleLog.item_id == item_id)
        .filter(SaleLog.date >= week_start)
        .filter(SaleLog.date <= today)
        .first()
    )

    # --- MONTH ---
    m = (
        db.query(
            func.sum(SaleLog.quantity).label("qty"),
            func.sum(SaleLog.quantity * MenuItem.price).label("earn")
        )
        .join(MenuItem)
        .filter(SaleLog.item_id == item_id)
        .filter(func.extract("year", SaleLog.date) == today.year)
        .filter(func.extract("month", SaleLog.date) == today.month)
        .first()
    )

    return jsonify({
        "today": {"qty": t.qty or 0, "earn": float(t.earn or 0)},
        "week": {"qty": w.qty or 0, "earn": float(w.earn or 0)},
        "month": {"qty": m.qty or 0, "earn": float(m.earn or 0)},
    })


# ---------------------------------------------------------
# ITEM WEEK BREAKDOWN (Mon–Sun — user-scoped)
# ---------------------------------------------------------
@api.route("/item_week_breakdown/<int:item_id>")
def item_week_breakdown(item_id):
    db = g.db
    today = date.today()
    week_start = today - timedelta(days=today.weekday())

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
        .order_by(SaleLog.date)
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

    return jsonify({"labels": labels, "qty": qty, "earn": earn})


# ---------------------------------------------------------
# ITEM MONTH BREAKDOWN (week-by-week — user-scoped)
# ---------------------------------------------------------
@api.route("/item_month_breakdown/<int:item_id>")
def item_month_breakdown(item_id):
    db = g.db
    today = date.today()

    rows = (
        db.query(
            func.strftime("%W", SaleLog.date).label("weeknum"),
            func.sum(SaleLog.quantity).label("qty"),
            func.sum(SaleLog.quantity * MenuItem.price).label("earn")
        )
        .join(MenuItem)
        .filter(SaleLog.item_id == item_id)
        .filter(func.extract("year", SaleLog.date) == today.year)
        .filter(func.extract("month", SaleLog.date) == today.month)
        .group_by(func.strftime("%W", SaleLog.date))
        .order_by(func.strftime("%W", SaleLog.date))
        .all()
    )

    return jsonify({
        "labels": [f"Week {int(r.weeknum)}" for r in rows],
        "qty": [r.qty for r in rows],
        "earn": [float(r.earn) for r in rows]
    })
