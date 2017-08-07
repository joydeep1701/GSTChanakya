from flask import redirect, render_template, request, session, url_for
from functools import wraps
from sql import *
db = SQL("sqlite:///arthasastra.db")
def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/0.11/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("company_name") is None:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function
def get_ledger_id(ledger_name):
    table_name =  str(session["company_id"])+"_ledgers"
    rows = db.execute("SELECT * FROM :tbl WHERE ledger_name LIKE :lname",tbl=table_name,lname=ledger_name)
    if len(rows) == 1:
        return rows[0]["id"]
    else:
        return 0
def get_stock_item_id(stock_name):
    table_name =  str(session["company_id"])+"_stockitems"
    rows = db.execute("SELECT * FROM :table_name WHERE stock_item_name LIKE :s",table_name=table_name,s=stock_name)
    if len(rows) == 1:
        return rows[0]["id"]
    else:
        return 0
