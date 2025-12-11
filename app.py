from datetime import date, datetime, timedelta

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    g,
)

from api import api
from database import Base, engine, SessionLocal
from models import MenuItem, SaleLog

# -----------------------------
# APP CONFIG
# -----------------------------
app = Flask(__name__)
app.secret_key = "development-secret"

app.register_blueprint(api, url_prefix="/api")

# Create all tables
Base.metadata.create_all(bind=engine)


# -----------------------------
# DB SESSION HANDLING
# -----------------------------
@app.before_request
def create_db_session():
    g.db = SessionLocal()


@app.teardown_request
def close_db_session(exception):
    db = getattr(g, "db", None)
    if db:
        try:
            if exception is None:
                db.commit()
            else:
                db.rollback()
        finally:
            db.close()

# -----------------------------
# MAIN PAGE (Add Items + Log Sales)
# -----------------------------
@app.route("/", methods=["GET", "POST"])
def index():
    db = g.db

    if request.method == "POST":
        form_type = request.form.get("form_type")

        # ADD ITEM
        if form_type == "add_item":
            name = request.form.get("name", "").strip()
            price_str = request.form.get("price", "").strip()

            if not name or not price_str:
                flash("Name and price are required.", "error")
                return redirect(url_for("index"))

            try:
                price = float(price_str)
            except ValueError:
                flash("Price must be a number.", "error")
                return redirect(url_for("index"))

            existing = db.query(MenuItem).filter_by(name=name).first()
            if existing:
                flash("Item already exists.", "error")
            else:
                db.add(MenuItem(name=name, price=price))
                flash("Menu item added!", "success")

            return redirect(url_for("index"))

        # LOG SALE
        elif form_type == "log_sale":
            item_id = request.form.get("item_id")
            date_str = request.form.get("date")
            qty_str = request.form.get("quantity")

            if not item_id or not date_str or not qty_str:
                flash("All fields are required.", "error")
                return redirect(url_for("index"))

            try:
                quantity = int(qty_str)
            except ValueError:
                flash("Quantity must be an integer.", "error")
                return redirect(url_for("index"))

            try:
                sale_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            except ValueError:
                flash("Invalid date format.", "error")
                return redirect(url_for("index"))

            item = db.query(MenuItem).get(int(item_id))
            if not item:
                flash("Menu item not found.", "error")
            else:
                db.add(SaleLog(
                    item_id=item.id,
                    date=sale_date,
                    quantity=quantity
                ))
                flash("Sale logged!", "success")

            return redirect(url_for("index"))

    items = db.query(MenuItem).order_by(MenuItem.name).all()
    today = date.today().isoformat()

    return render_template("index.html", items=items, today=today)



# -----------------------------
# STATS PAGE
# -----------------------------
from stats import get_daily_sales, get_monthly_sales, get_weekly_sales

@app.route("/stats")
def stats_page():
    db = g.db

    today = date.today()
    week_start = today - timedelta(days=today.weekday())

    daily_rows, daily_total, daily_earnings = get_daily_sales(db, today)
    weekly_rows, weekly_total, weekly_earnings = get_weekly_sales(db, week_start)
    monthly_rows, monthly_total, monthly_earnings = get_monthly_sales(db, today.year, today.month)

    all_items = db.query(MenuItem).order_by(MenuItem.name).all()

    return render_template(
        "stats.html",
        today=today,
        daily_rows=daily_rows, daily_total=daily_total, daily_earnings=daily_earnings,
        weekly_rows=weekly_rows, weekly_total=weekly_total, weekly_earnings=weekly_earnings,
        monthly_rows=monthly_rows, monthly_total=monthly_total, monthly_earnings=monthly_earnings,
        all_items=all_items
    )



# -----------------------------
# ITEMS PAGE
# -----------------------------
@app.route("/items")
def items_page():
    db = g.db
    items = db.query(MenuItem).order_by(MenuItem.name).all()
    return render_template("items.html", items=items)



# -----------------------------
# EDIT ITEM
# -----------------------------
@app.route("/edit_item/<int:item_id>", methods=["GET", "POST"])
def edit_item(item_id):
    db = g.db
    item = db.query(MenuItem).get(item_id)

    if not item:
        flash("Item not found.","error")
        return redirect(url_for("items_page"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        price_str = request.form.get("price", "").strip()

        if not name or not price_str:
            flash("Name and price required", "error")
            return redirect(url_for("edit_item", item_id=item_id))

        try:
            price = float(price_str)
        except ValueError:
            flash("Price must be a number", "error")
            return redirect(url_for("edit_item", item_id=item_id))

        existing = db.query(MenuItem).filter(
            MenuItem.name == name,
            MenuItem.id != item_id
        ).first()

        if existing:
            flash("Another item already has that name", "error")
            return redirect(url_for("edit_item", item_id=item_id))

        item.name = name
        item.price = price

        flash("Item updated!", "success")
        return redirect(url_for("items_page"))

    return render_template("edit_item.html", item=item)



# -----------------------------
# DELETE ITEM
# -----------------------------
@app.route("/delete_item/<int:item_id>")
def delete_item(item_id):
    db = g.db
    item = db.query(MenuItem).get(item_id)

    if not item:
        flash("Item not found", "error")
        return redirect(url_for("items_page"))

    db.delete(item)
    flash("Item and related sales deleted", "success")
    return redirect(url_for("items_page"))



# -----------------------------
# DASHBOARD
# -----------------------------
@app.route("/dashboard")
def dashboard():
    db = g.db
    today = date.today()

    daily_rows, daily_total, daily_earnings = get_daily_sales(db, today)
    weekly_rows, weekly_total, weekly_earnings = get_weekly_sales(db, today - timedelta(days=today.weekday()))
    monthly_rows, monthly_total, monthly_earnings = get_monthly_sales(db, today.year, today.month)

    best_today = max(daily_rows, key=lambda r: r.qty, default=None)
    best_week = max(weekly_rows, key=lambda r: r.qty, default=None)
    best_month = max(monthly_rows, key=lambda r: r.qty, default=None)

    total_items = db.query(MenuItem).count()
    total_sales_logs = db.query(SaleLog).count()

    return render_template(
        "dashboard.html",
        today=today,
        daily_total=daily_total, daily_earnings=daily_earnings,
        weekly_earnings=weekly_earnings,
        monthly_earnings=monthly_earnings,
        best_today=best_today, best_week=best_week, best_month=best_month,
        total_items=total_items, total_sales_logs=total_sales_logs,
    )


# -----------------------------
# START SERVER
# -----------------------------
if __name__ == "__main__":
    app.run(debug=True)
