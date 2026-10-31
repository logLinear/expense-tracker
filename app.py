
import sqlite3
import os
from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import date

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "expense-tracker-local-key")

DATABASE = os.environ.get("DATABASE_PATH", "database.db")


# Connect to SQLite database
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# Create database and expenses table
def init_db():
    os.makedirs(
        os.path.dirname(os.path.abspath(DATABASE)),
        exist_ok=True
    )

    conn = get_db_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            expense_date TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


# Display all expenses and total expenditure
@app.route("/")
def index():
    conn = get_db_connection()

    expenses = conn.execute(
        "SELECT * FROM expenses ORDER BY expense_date DESC, id DESC"
    ).fetchall()

    total = conn.execute(
        "SELECT COALESCE(SUM(amount), 0) FROM expenses"
    ).fetchone()[0]

    category_totals = conn.execute("""
        SELECT category, SUM(amount) AS total
        FROM expenses
        GROUP BY category
        ORDER BY total DESC
    """).fetchall()

    conn.close()

    return render_template(
        "index.html",
        expenses=expenses,
        total=total,
        category_totals=category_totals,
        today=date.today().isoformat()
    )


# Add a new expense
@app.route("/add", methods=["POST"])
def add_expense():
    amount = request.form.get("amount", "").strip()
    category = request.form.get("category", "").strip()
    expense_date = request.form.get("expense_date", "").strip()

    try:
        amount = float(amount)
        if amount <= 0:
            raise ValueError()
    except (ValueError, TypeError):
        flash("Please enter a valid positive amount.", "error")
        return redirect(url_for("index"))

    if not category or not expense_date:
        flash("Please enter category and date.", "error")
        return redirect(url_for("index"))

    conn = get_db_connection()

    conn.execute(
        """
        INSERT INTO expenses (amount, category, expense_date)
        VALUES (?, ?, ?)
        """,
        (amount, category, expense_date)
    )

    conn.commit()
    conn.close()

    flash("Expense added successfully!", "success")
    return redirect(url_for("index"))


# Edit an existing expense
@app.route("/edit/<int:expense_id>", methods=["POST"])
def edit_expense(expense_id):
    amount = request.form.get("amount", "").strip()
    category = request.form.get("category", "").strip()
    expense_date = request.form.get("expense_date", "").strip()

    try:
        amount = float(amount)
        if amount <= 0:
            raise ValueError()
    except (ValueError, TypeError):
        flash("Please enter a valid positive amount.", "error")
        return redirect(url_for("index"))

    if not category or not expense_date:
        flash("Please enter category and date.", "error")
        return redirect(url_for("index"))

    conn = get_db_connection()

    conn.execute(
        """
        UPDATE expenses
        SET amount = ?, category = ?, expense_date = ?
        WHERE id = ?
        """,
        (amount, category, expense_date, expense_id)
    )

    conn.commit()
    conn.close()

    flash("Expense updated successfully!", "success")
    return redirect(url_for("index"))


# Delete an expense
@app.route("/delete/<int:expense_id>", methods=["POST"])
def delete_expense(expense_id):
    conn = get_db_connection()

    conn.execute(
        "DELETE FROM expenses WHERE id = ?",
        (expense_id,)
    )

    conn.commit()
    conn.close()

    flash("Expense deleted successfully!", "success")
    return redirect(url_for("index"))


# Initialize database and start application
if __name__ == "__main__":
    init_db()

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=os.environ.get("FLASK_DEBUG") == "1"
    )
