#!c:/Python34/python.exe -u
from sql import *
from flask import Flask, flash, redirect, render_template, request, session, url_for, Response, make_response
from flask_session import Session
from tempfile import gettempdir
import json
from helpers import *

db = SQL("sqlite:///arthasastra.db")
hsn = SQL("sqlite:///hsn.db")

app = Flask(__name__)
app.config["SESSION_FILE_DIR"] = gettempdir()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

"""
Group: Master
"""
# --------------Ledger--------------
# --------------Ledger----ADD----------
@app.route('/master/ledger/add/<group>',methods=["GET","POST"])
def add_ledger_master(group):
    if request.method == "GET":
        return render_template("add_ledger.html",under_group=group)
    else:
        #return str(request.form)
        table_name =  str(session["company_id"])+"_ledgers"
        rows = db.execute("SELECT * FROM :tbl WHERE ledger_name = :ldgr_name AND ledger_group = :ldgr_grp",tbl=table_name,ldgr_name=request.form.get("name"),ldgr_grp=request.form.get("group"))
        if len(rows) > 0:
            flash("Duplicate Entry","error")
            return render_template("add_ledger.html",under_group=request.form.get("group"))
        else:
            rows = db.execute("SELECT * FROM ledger_groups WHERE group_name=:group",group=request.form.get("group"))
            if len(rows) == 0:
                flash("Invalid Group Name","warning")
                return render_template("add_ledger.html",under_group=request.form.get("group"))
            else:
                db.execute("INSERT INTO :tbl (ledger_name,ledger_group,opening_balance,address,gstin) VALUES (:lname,:lg,:ob,:add,:gstin)",tbl=table_name,lname=request.form.get("name"),lg=request.form.get("group"),ob=request.form.get("balance"),add=request.form.get("address"),gstin=request.form.get("gstin"))
                flash("Ledger Created: "+request.form.get("name"),"success")
                return render_template("add_ledger.html",under_group=request.form.get("group"))
        return str(rows)
# --------------Ledger----ADD-------END---
# --------------Ledger----DISPLAY----------
@app.route("/master/ledger/display")
def display_ledger_master():
    return render_template("display_ledger.html")
# --------------Ledger----DISPLAY-----END-----
# --------------Ledger----EDIT----------
@app.route('/master/ledger/edit/<id>',methods=["GET","POST"])
def edit_ledger_master(id):
    table_name =  str(session["company_id"])+"_ledgers"
    if request.method == "GET":
        rows = db.execute("SELECT * FROM :tbl WHERE id = :id",tbl=table_name,id=id)
        if len(rows) == 1:
            return render_template("edit_ledger.html",row=rows[0])
        else:
            return "Server Fault"
    else:
        db.execute("UPDATE :tbl SET ledger_name=:lname,ledger_group=:lg,opening_balance=:ob,address=:add,gstin=:gstin WHERE id=:id",tbl=table_name,lname=request.form.get("name"),lg=request.form.get("group"),ob=request.form.get("balance"),add=request.form.get("address"),gstin=request.form.get("gstin"),id=id)
        flash("Ledger updated: "+request.form.get("name"),"success")
        return redirect(url_for('display_ledger_master'))
# --------------Ledger----EDIT-------END---
# --------------Ledger----SEARCH----------
@app.route('/master/ledger/getgroups/<grp>')
def getgroups_ledger_master(grp):
    grp = "%"+grp+"%"
    rows = db.execute("SELECT * FROM ledger_groups WHERE group_name LIKE :group",group=grp)
    return json.dumps(rows)
@app.route("/master/ledger/getledgers/byname/<ledger_name>")
def getledgers_ledger_master(ledger_name):
    ledger_name = "%"+ledger_name+"%"
    table_name =  str(session["company_id"])+"_ledgers"
    rows = db.execute("SELECT * FROM :tbl WHERE ledger_name LIKE :lname",tbl=table_name,lname=ledger_name)
    return json.dumps(rows)
# --------------Ledger------SEARCH-----END---
# --------------Ledger--------------END
# --------------Inventory--------------
# --------------Inventory----STOCK----ITEM----ADD--
@app.route('/master/inventory/add/stock/item',methods=["GET","POST"])
def add_stock_item_inventory_master():
    if request.method == "GET":
        return render_template("add_stock_item.html")
    else:
        #return str(request.form)
        table_name =  str(session["company_id"])+"_stockitems"
        rows = db.execute("SELECT * FROM :table WHERE stock_item_name=:itm_name",table=table_name,itm_name=request.form.get("stock_name"))
        if len(rows) > 0:
            flash("Duplicate Entry","error")
            return render_template("add_stock_item.html")
        else:
            table_name =  str(session["company_id"])+"_stockgroup"
            rows = db.execute("SELECT * FROM :tbl WHERE group_name=:id",tbl=table_name,id=request.form.get("under_group"))
            if len(rows) < 1:
                flash("Given Stock Group Not Found","warning")
                return render_template("add_stock_item.html")
            else:
                hsns = hsn.execute("SELECT * FROM hsn_codes WHERE HSN=:hsn",hsn=request.form.get('hsn'))
                if len(hsns) == 0:
                    flash("Invalid HSN code","warning")
                    return render_template("add_stock_item.html")
                else:
                    table_name =  str(session["company_id"])+"_stockitems"
                    db.execute("""INSERT INTO :table_name (stock_item_name,stock_item_group,
                    stock_item_hsn,stock_item_taxrate,stock_item_uom,rate)
                    VALUES (:name,:group,:hsn,:taxrate,:uom,:rate)"""
                    ,table_name=table_name,name=request.form.get('stock_name'),
                    group=request.form.get('under_group'),hsn=request.form.get('hsn'),
                    taxrate=request.form.get('taxrate'),uom=request.form.get('units_om'),
                    rate=request.form.get('rate'))
                    flash("Stock Item Added","success")
                    return render_template("add_stock_item.html")
# --------------Inventory----STOCK----ITEM----ADD--END-
# --------------Inventory----STOCK----ITEM----DISPLAY--
@app.route("/master/inventory/display/stock/item")
def display_stock_item_iventory_master():
    return render_template("display_stock_items.html")
# --------------Inventory----STOCK----ITEM----DUSPLAY--END-
# --------------Inventory----STOCK----ITEM----EDIT--
@app.route("/master/inventory/edit/stock/item/<id>",methods=["GET","POST"])
def edit_stock_item_iventory_master(id):
    table_name =  str(session["company_id"])+"_stockitems"
    if request.method == "GET":
        rows = db.execute("SELECT * FROM :table_name WHERE id=:id",table_name=table_name,id=id)
        if len(rows) == 1:
            return render_template("edit_stock_item.html",data=rows[0])
        else:
            return "Server Fault"
    else:
        #return str(request.form)
        table_name =  str(session["company_id"])+"_stockgroup"
        rows = db.execute("SELECT * FROM :tbl WHERE group_name=:id",tbl=table_name,id=request.form.get("under_group"))
        if len(rows) < 1:
            flash("Given Stock Group Not Found","warning")
            return redirect(url_for("edit_stock_item_iventory_master",id=id))
        else:
            hsns = hsn.execute("SELECT * FROM hsn_codes WHERE HSN=:hsn",hsn=request.form.get('hsn'))
            if len(hsns) == 0:
                flash("Invalid HSN code","warning")
                return redirect(url_for("edit_stock_item_iventory_master",id=id))
            else:
                table_name =  str(session["company_id"])+"_stockitems"
                db.execute("""UPDATE :table_name SET stock_item_name=:name,
                stock_item_group=:group,stock_item_hsn=:hsn,stock_item_taxrate=:taxrate,
                stock_item_uom=:uom,rate=:rate WHERE id=:id""",id=id,table_name=table_name,
                name=request.form.get('stock_name'),group=request.form.get('under_group')
                ,hsn=request.form.get('hsn'),taxrate=request.form.get('taxrate')
                ,uom=request.form.get('units_om'),rate=request.form.get('rate'))
                flash("Stock Item Altered: "+request.form.get('stock_name'),"success")
                return redirect(url_for("display_stock_item_iventory_master"))
# --------------Inventory----STOCK----ITEM----EDIT--END-
# --------------Inventory----STOCK----ITEM----SEARCH--
@app.route("/master/inventory/stock/getitems/<s>")
def search_stock_items_inventory_master(s):
    table_name =  str(session["company_id"])+"_stockitems"
    s = "%"+s+"%"
    rows = db.execute("SELECT * FROM :table_name WHERE stock_item_name LIKE :s",table_name=table_name,s=s)
    return json.dumps(rows)
# --------------Inventory----STOCK----ITEM----SEARCH--END-
# --------------Inventory----STOCK----GROUP-----ADD-
@app.route('/master/inventory/add/stock/group',methods=["GET","POST"])
def add_stock_group_inventory_master():
    table_name =  str(session["company_id"])+"_stockgroup"
    if request.method == "GET":
        return render_template("add_stock_group.html")
    else:
        rows = db.execute("SELECT * FROM :tbl WHERE group_name=:group_name",tbl=table_name,group_name=request.form.get("group_name"))
        if len(rows) > 0:
            flash("Duplicate Entry","error")
        else:
            db.execute("""INSERT INTO :tbl
            (group_name,hsn,taxrate,uom)
            VALUES (:group_name,:hsn,:taxrate,:uom)""",
            tbl=table_name,group_name=request.form.get("group_name"),
            hsn=request.form.get("hsn"),taxrate=request.form.get("taxrate"),
            uom=request.form.get("uom"))
            flash("Stock Created: "+request.form.get("group_name"),"success")
        return render_template("add_stock_group.html")
# --------------Inventory----STOCK----GROUP-----ADD----END-
# --------------Inventory----STOCK----GROUP-----DISPLAY-
@app.route("/master/inventory/display/stock/group")
def display_stockgroup_inventory_master():
    return render_template("display_stock_group.html")
# --------------Inventory----STOCK----GROUP-----DISPLAY--END-
@app.route("/master/inventory/edit/stock/group/<id>",methods=["GET","POST"])
def edit_stock_group_inventory_master(id):
    table_name =  str(session["company_id"])+"_stockgroup"
    if request.method == "GET":
        rows = db.execute("SELECT * FROM :tbl WHERE id=:id",tbl=table_name,id=id)
        if len(rows) == 1:
            return render_template("add_stock_group.html",row=rows[0])
        else:
            return "Server Fault"
    else:
        db.execute("""UPDATE :tbl SET group_name=:group_name,
        hsn=:hsn,taxrate=:taxrate,uom=:uom WHERE id=:id"""
        ,tbl=table_name,id=id,group_name=request.form.get("group_name"),
        hsn=request.form.get("hsn"),taxrate=request.form.get("taxrate"),
        uom=request.form.get("uom"))
        flash("Stock Group Updated:"+request.form.get("group_name"),"success")
        return redirect(url_for("display_stockgroup_inventory_master"))
# --------------Inventory----STOCK----GROUP-----SEARCH-
@app.route("/master/inventory/stock/getgroups/<grp>")
def getstock_groups_inventory_master(grp):
    grp = "%"+grp+"%"
    table_name =  str(session["company_id"])+"_stockgroup"
    rows = db.execute("SELECT * FROM :tbl WHERE group_name LIKE :group",tbl=table_name,group=grp)
    return json.dumps(rows)
# --------------Inventory----STOCK----GROUP-----SEARCH--END-
# --------------Inventory----STOCK----GROUP-------END-
@app.route('/master/inventory/add/stock/uom')
def add_stock_uom_inventory_master():
    if request.method == "GET":
        return render_template("add_stock_uom.html")
@app.route('/master/inventory/add')
@app.route('/master/inventory/edit')
def master():
    return render_template("add_ledger.html")


@app.route('/')
@login_required
def index():
    company = db.execute("SELECT * FROM master WHERE company_id=:id",id=session["company_id"])

    return render_template('dash.html',company=company[0])
"""
END Group: Master
"""
# ------------------------------
"""
Group: Vouchers
"""
@app.route('/voucher/purchase/add',methods=["GET","POST"])
def add_purchase_voucher():
    if request.method == "GET":
        return render_template('add_purchase_voucher.html')
    else:
        s = dict(request.form)
        if s['date'][0] == '':
            flash("No Date Selected","error")
            return render_template('add_payment_voucher.html')
        pur_date = str(request.form.get("date")).split("-")[0]
        pur_month = str(request.form.get("date")).split("-")[1]
        pur_year = str(request.form.get("date")).split("-")[2]
        si_no = request.form.get("sino")
        sup_date = str(request.form.get("sup_date")).split("-")[0]
        sup_month = str(request.form.get("sup_date")).split("-")[1]
        sup_year = str(request.form.get("sup_date")).split("-")[2]
        #return pur_date+pur_month+pur_year
        #return str(request.form)
        pur_ac_id =  get_ledger_id(request.form.get("purchaseacname"))
        if pur_ac_id == 0:
            flash("Invalid Purchase A/C Name","error")
            return render_template("add_purchase_voucher.html",date=pur_date,month=pur_month,year=pur_year)
        par_ac_id =  get_ledger_id(request.form.get("partyacname"))
        if par_ac_id == 0:
            flash("Invalid Party A/C Name","error")
            return render_template("add_purchase_voucher.html",date=pur_date,month=pur_month,year=pur_year)
        s = dict(request.form)
        if s["itm_id"] == ['']:
            flash("Empty Voucher","error")
            return render_template("add_purchase_voucher.html",date=pur_date,month=pur_month,year=pur_year)
        for name,id in zip(s['itm_name'],s['itm_id']):
            if int(id) != int(get_stock_item_id(name)):
                flash("Voucher name NOT given","error")
                return render_template("add_purchase_voucher.html",date=pur_date,month=pur_month,year=pur_year)
                #return str(id)+" "+str(get_stock_item_id(name)) + " "+name
        #check Duplicates
        table_name =  str(session["company_id"])+"_master_purchase"
        voucher_rows = db.execute("""SELECT id FROM :table_name
        WHERE pur_date=:voucher_date AND pur_month=:voucher_month
        AND supplier_inv_no=:inv AND creditor_id=:cid""",
        table_name=table_name,voucher_date=pur_date,voucher_month=pur_month,inv=si_no,cid=par_ac_id)
        if len(voucher_rows) > 0:
            flash("Duplicate Entry","error")
            return render_template("add_purchase_voucher.html",date=pur_date,month=pur_month,year=pur_year)
        db.execute("""
        INSERT INTO :table_name (supplier_inv_no,debtor_id,creditor_id,pur_date,
        pur_month,pur_year,supplier_date,supplier_month,supplier_year)
        VALUES (:invc_n,:did,:cid,:pur_date,:pur_month,:pur_year,
        :sup_date,:sup_month,:sup_year)""",table_name=table_name,invc_n=si_no,
        did=pur_ac_id,cid=par_ac_id,pur_date=pur_date,pur_month=pur_month,
        pur_year=pur_year,sup_date=sup_date,sup_month=sup_month,sup_year=sup_year)
        voucher_rows = db.execute("""SELECT id FROM :table_name
        WHERE pur_date=:voucher_date AND pur_month=:voucher_month
        AND supplier_inv_no=:inv AND creditor_id=:cid""",
        table_name=table_name,voucher_date=pur_date,voucher_month=pur_month,inv=si_no,cid=par_ac_id)
        master_id=voucher_rows[0]['id']
        table_name =  str(session["company_id"])+"_purchase"
        for id,qty,rate,disc,am in zip(s['itm_id'],s['qty'],s['rate'],s['discount'],s['amount']):
            db.execute("""
            INSERT INTO :table_name (bill_id,item_id,qty,rate,amount,disc)
            VALUES (:mid,:iid,:qty,:rate,:amount,:disc)""",table_name=table_name,
            mid=master_id,iid=id,qty=qty,rate=rate,amount=am,disc=disc)
        flash("Voucher Added Successfully","success")
        return render_template("add_purchase_voucher.html",date=pur_date,month=pur_month,year=pur_year)
        return str(s)
        return str(request.form)
# ----- END -------PURCHASE VOUCHER -- add
# -----  -------PURCHASE VOUCHER -- edit
@app.route("/voucher/purchase/edit/<id>")
def edit_purchase_voucher(id):
    table_name =  str(session["company_id"])+"_master_purchase"
    items =  str(session["company_id"])+"_stockitems"
    main_details = db.execute("""SELECT * FROM :table_name
        WHERE id=:id""",table_name=table_name,id=id)
    #debtor = db.execute("SELECT ledger_name FROM :ledger_table WHERE id=:id",ledger_table=,id=)
    table_name =  str(session["company_id"])+"_purchase"
    items = db.execute("""SELECT * FROM :table_name
        INNER JOIN :items ON :items.id = :table_name.item_id
        WHERE bill_id=:id""",items=items,table_name=table_name,id=id)
    return render_template("edit_purchase_voucher.html",main=main_details[0],items=items)
# ----- END -------PURCHASE VOUCHER -- add
# -----  -------PURCHASE VOUCHER -- search
@app.route("/voucher/purchase/get/<id>")
def get_purchase_vouchers_by_ledger_id(id):
    master =  str(session["company_id"])+"_master_purchase"
    main =  str(session["company_id"])+"_purchase"
    items =  str(session["company_id"])+"_stockitems"
    paid = str(session["company_id"])+"_payment"
    rows = db.execute("""
    SELECT bill_id,
    :master.supplier_inv_no AS inv_no,
    SUM(amount) AS amount,
    SUM(amount*stock_item_taxrate)/100 AS tax,
    paid_amount
    FROM :main
    INNER JOIN (
        SELECT SUM(amount) AS paid_amount,
        voucher_no AS paid_bill_no
        FROM :paid
        WHERE debtor_id=:id
        GROUP BY voucher_no
    ) ON paid_bill_no = :main.bill_id
    INNER JOIN :master ON :master.id = :main.bill_id
    INNER JOIN :items ON :items.id = :main.item_id
    WHERE :master.creditor_id = :id
    GROUP BY bill_id""",
    main=main,master=master,items=items,id=id,paid=paid)
    return json.dumps(rows)
# ----- END -------PURCHASE VOUCHER -- add
# -----  -------SALE VOUCHER -- add
@app.route('/voucher/sale/add',methods=["GET","POST"])
def add_sale_voucher():
    if request.method == "GET":
        return render_template('add_sale_voucher.html')
    else:
        s = dict(request.form)
        #return str(request.form)
        if s['date'][0] == '':
            flash("No Date Selected","error")
            return render_template('add_sale_voucher.html')
        date = s['date'][0].split("-")[0]
        month = s['date'][0].split("-")[1]
        year = s['date'][0].split("-")[2]
        inv_no = s['sino'][0]

        debtor_id = get_ledger_id(s['partyacname'][0])
        if debtor_id == 0:
            flash("Invalid  Reciever A/C Name","error")
            return render_template("add_sale_voucher.html",date=s['date'][0])

        creditor_id = get_ledger_id(s['saleacname'][0])
        if debtor_id == 0:
            flash("Invalid Sales A/C Name","error")
            return render_template("add_sale_voucher.html",date=s['date'][0])
        if s["itm_id"] == ['']:
            flash("Empty Voucher","error")
            return render_template("add_sale_voucher.html",date=s['date'][0])
        for name,id in zip(s['itm_name'],s['itm_id']):
            if int(id) != int(get_stock_item_id(name)):
                flash("Voucher name NOT given","error")
                return render_template("add_sale_voucher.html",date=s['date'][0])

        table_name =  str(session["company_id"])+"_master_sales"
        voucher_rows = db.execute("""SELECT id FROM :table_name
        WHERE date=:voucher_date AND month=:voucher_month
        AND inv_no=:inv AND debtor_id=:did""",
        table_name=table_name,
        voucher_date=date,voucher_month=month,inv=inv_no,did=debtor_id)
        if len(voucher_rows) > 0:
            flash("Duplicate Entry","error")
            return render_template("add_sale_voucher.html",date=s['date'][0])
        db.execute("""
            INSERT INTO :table_name (debtor_id,creditor_id,inv_no,date,
            month,year,place_of_supply,roundoff)
            VALUES (:did,:cid,:invc_n,:date,:month,:year,:place_of_supply,:roundoff)""",
            table_name=table_name,invc_n=inv_no,
            did=debtor_id,cid=creditor_id,place_of_supply=request.form.get("pos"),
            date=date,month=month,year=year,roundoff=request.form.get("roundoff"))
        voucher_rows = db.execute("""SELECT id FROM :table_name
            WHERE date=:voucher_date AND month=:voucher_month
            AND inv_no=:inv AND debtor_id=:did""",
            table_name=table_name,
            voucher_date=date,voucher_month=month,inv=inv_no,did=debtor_id)
        master_id=voucher_rows[0]['id']
        table_name =  str(session["company_id"])+"_sales"
        for id,qty,rate,disc,am in zip(s['itm_id'],s['qty'],s['rate'],s['discount'],s['amount']):
            db.execute("""
                INSERT INTO :table_name (bill_id,item_id,qty,rate,amount,disc)
                VALUES (:mid,:iid,:qty,:rate,:amount,:disc)""",
                table_name=table_name,mid=master_id,iid=id,qty=qty,rate=rate,amount=am,disc=disc)
        flash("Voucher Added Successfully","success")
        return render_template("add_sale_voucher.html",date=s['date'][0])
        return str(s)
# ----- END -------SALE VOUCHER -- add

@app.route("/voucher/sale/edit/<master_bill_id>",methods=["GET","POST"])
def edit_sale_voucher(master_bill_id):
    if request.method == "GET":
        table_name =  str(session["company_id"])+"_master_sales"
        items =  str(session["company_id"])+"_stockitems"
        main_details = db.execute("""SELECT * FROM :table_name
            WHERE id=:id""",table_name=table_name,id=master_bill_id)
        #debtor = db.execute("SELECT ledger_name FROM :ledger_table WHERE id=:id",ledger_table=,id=)
        table_name =  str(session["company_id"])+"_sales"
        items = db.execute("""SELECT :table_name.id AS salesrow_id,
            bill_id,item_id,qty,
            :table_name.rate,amount,disc,
            :items.stock_item_name,:items.stock_item_hsn,:items.stock_item_taxrate
            FROM :table_name
            INNER JOIN :items ON :items.id = :table_name.item_id
            WHERE bill_id=:id""",items=items,table_name=table_name,id=master_bill_id)
        table = str(session["company_id"])+"_ledgers"
        debtor = db.execute("SELECT ledger_name FROM :table WHERE id=:id",table=table,id=main_details[0]["debtor_id"])
        creditor = db.execute("SELECT ledger_name FROM :table WHERE id=:id",table=table,id=main_details[0]["creditor_id"])
        return render_template("edit_sale_voucher.html",main=main_details[0],items=items,debtor=debtor[0],creditor=creditor[0])
    else:
        s = dict(request.form)
        #return str(dict(request.form))
        delete_type = 0
        for v in s['delete']:
            delete_type -= int(v)
        if (delete_type) == (len(s['amount'])):
            table =  str(session["company_id"])+"_sales"
            db.execute("DELETE FROM :table WHERE bill_id=:bill_id",table=table,bill_id=master_bill_id)
            table = str(session["company_id"])+"_master_sales"
            db.execute("DELETE FROM :table WHERE id=:bill_id",table=table,bill_id=master_bill_id)
            return redirect(url_for('gstr1_main'))
        else:
            if s['date'][0] == '':
                flash("No Date Selected","error")
                return redirect(url_for("edit_sale_voucher"),id=master_bill_id)
            date = s['date'][0].split("-")[0]
            month = s['date'][0].split("-")[1]
            year = s['date'][0].split("-")[2]
            inv_no = s['sino'][0]

            debtor_id = get_ledger_id(s['partyacname'][0])
            if debtor_id == 0:
                flash("Invalid  Reciever A/C Name","error")
                return redirect(url_for("edit_sale_voucher"),id=master_bill_id)

            creditor_id = get_ledger_id(s['saleacname'][0])
            if debtor_id == 0:
                flash("Invalid Sales A/C Name","error")
                return redirect(url_for("edit_sale_voucher"),id=master_bill_id)
            if s["itm_id"] == ['']:
                flash("Empty Voucher","error")
                return redirect(url_for("edit_sale_voucher"),id=master_bill_id)
            for name,id in zip(s['itm_name'],s['itm_id']):
                if int(id) != int(get_stock_item_id(name)):
                    flash("Voucher name NOT given","error")
                    return redirect(url_for("edit_sale_voucher"),id=master_bill_id)
            table = str(session["company_id"])+"_master_sales"
            db.execute("""
                UPDATE :table_name SET
                debtor_id=:did,creditor_id=:cid,inv_no=:invc_n,
                date=:date,month=:month,year=:year,place_of_supply=:place_of_supply,
                roundoff=:roundoff WHERE id=:id""",
                table_name=table,invc_n=inv_no,
                did=debtor_id,cid=creditor_id,place_of_supply=request.form.get("pos"),
                date=date,month=month,year=year,roundoff=request.form.get("roundoff"),id=master_bill_id)

            if delete_type != 0:
                log = "Delete Called\n"
                for delete,row_id in zip(s["delete"],s["row_id"]):
                    log += "\nrow_id:"+str(row_id)+"delete:"+str(delete)
                    if delete == "-1":
                        log += " Inside Delete If"
                        table =  str(session["company_id"])+"_sales"
                        db.execute("DELETE FROM :table WHERE id=:row_id",table=table,row_id=row_id)
            #return str(log)
            for row_id,itm_id,qty,rate,disc,am,delete in zip(s['row_id'],s['itm_id'],s['qty'],s['rate'],s['discount'],s['amount'],s['delete']):
                if delete == "-1":
                    pass
                if row_id == "N":
                    table =  str(session["company_id"])+"_sales"
                    db.execute("""
                        INSERT INTO :table_name (bill_id,item_id,qty,rate,amount,disc)
                        VALUES (:mid,:iid,:qty,:rate,:amount,:disc)""",
                        table_name=table,mid=master_bill_id,iid=itm_id,qty=qty,rate=rate,amount=am,disc=disc)
                else:
                    table =  str(session["company_id"])+"_sales"
                    db.execute("""
                    UPDATE :table_name SET
                    bill_id=:bill_id,item_id=:item_id,qty=:qty,
                    rate=:rate,amount=:amount,disc=:disc WHERE id=:master_id
                    """,table_name=table,bill_id=master_bill_id,item_id=itm_id,master_id=row_id,
                    qty=qty,rate=rate,amount=am,disc=disc)
            return redirect(url_for('gstr1_main'))

# ----- END -------SALE VOUCHER -- edit

@app.route('/voucher/payment/add',methods=["GET","POST"])
def add_payment_voucher():
    if request.method == "GET":
        return render_template('add_payment_voucher.html')
    else:
        s = dict(request.form)
        if s['date'][0] == '':
            flash("No Date Selected","error")
            return render_template('add_payment_voucher.html')
        date = str(request.form.get("date")).split("-")[0]
        month = str(request.form.get("date")).split("-")[1]
        year = str(request.form.get("date")).split("-")[2]
        table_name = str(session["company_id"])+"_master_payment"
        nar =  str()
        #return nar
        #return str(dict(request.form))
        db.execute("""INSERT INTO :table_name
        (creditor_id,date,month,year,narration)
        VALUES (:cid,:date,:month,:year,:nar)""",
        cid=s['saleacname'][0],table_name=table_name,date=date,
        month=month,year=year,nar=s['narration'][0])
        rows = db.execute("SELECT id FROM :table_name",table_name=table_name)
        master_id = rows[-1]['id']
        table_name = str(session["company_id"])+"_payment"
        for debtor_id,bill_no,bill_amount in zip(s['debtor_id'],s['bill_no'],s['bill_amount']):
            db.execute("""INSERT INTO :table_name
            (master_id,debtor_id,voucher_no,amount)
            VALUES (:master_id,:debtor_id,:voucher_no,:amount)""",
            table_name=table_name,master_id=master_id,debtor_id=debtor_id,
            voucher_no=bill_no,amount=bill_amount)

        flash("Payment Added","success")
        return render_template('add_payment_voucher.html')

@app.route('/voucher/reciept/add')
def add_reciept_voucher():
    if request.method == "GET":
        return render_template('add_reciept_voucher.html')
    else:
        return str(request.form)
        if s['date'][0] == '':
            flash("No Date Selected","error")
            return render_template('add_payment_voucher.html')
@app.route('/voucher/contra/add')
@app.route('/voucher/journal/add')
def voucher():
    return "Hello"
"""
END Group: Vouchers
"""
"""
Group: GST RETURNS
"""
@app.route('/gstr1',methods=["GET","POST"])
def gstr1_main():
    if request.method == "POST":
        if request.form.get("category") == "b2b":
            return redirect(url_for('gstr1_b2b',m=request.form.get('month')))
        if request.form.get("category") == "b2cl":
            return redirect(url_for('gstr1_b2cl',m=request.form.get('month')))
        if request.form.get("category") == "b2cs":
            return redirect(url_for('gstr1_b2cs',m=request.form.get('month')))
    return render_template('gstr1.html')
@app.route('/gstr1/b2b/<m>',methods=["GET","POST"])
def gstr1_b2b(m):
    b2b = str(session["company_id"])+"_gstr1_sales"
    ur_id = get_ledger_id("Unregistered Sale")
    rows = db.execute("SELECT * FROM :table WHERE month=:month AND debtor_id != :ur_id",table=b2b,month=m,ur_id=ur_id)

    state_codes = {"35":"35-Andaman and Nicobar Islands","37":"37-Andhra Pradesh","12":"12-Arunachal Pradesh","18":"18-Assam","10":"10-Bihar","04":"04-Chandigarh","22":"22-Chhattisgarh","26":"26-Dadra and Nagar Haveli","25":"25-Daman and Diu","07":"07-Delhi","30":"30-Goa","24":"24-Gujarat","06":"06-Haryana","02":"02-Himachal Pradesh","01":"01-Jammu and Kashmir","20":"20-Jharkhand","29":"29-Karnataka","32":"32-Kerala","31":"31-Lakshadweep","23":"23-Madhya Pradesh","27":"27-Maharashtra","14":"14-Manipur","17":"17-Meghalaya","15":"15-Mizoram","13":"13-Nagaland","21":"21-Odisha","34":"34-Puducherry","03":"03-Punjab","08":"08-Rajasthan","11":"11-Sikkim","33":"33-Tamil Nadu","36":"36-Telangana","16":"16-Tripura","09":"09-Uttar Pradesh","05":"05-Uttarakhand","97":"97-Other Territory","19":"19-West Bengal"}
    return render_template("gstr1_b2b.html",data=rows,month=m,state_codes=state_codes)
@app.route('/gstr1/b2cl/<m>')
def gstr1_b2cl(m):
    b2cl = str(session["company_id"])+"_gstr1_sales"
    ur_id = get_ledger_id("Unregistered Sale")
    home_state = '19'
    rows = db.execute("""SELECT * FROM :table WHERE month=:month
    AND debtor_id = :ur_id AND invoice_value > 250000 AND place_of_supply!=:hs""",
    table=b2cl,month=m,ur_id=ur_id,hs=home_state)

    state_codes = {"35":"35-Andaman and Nicobar Islands","37":"37-Andhra Pradesh","12":"12-Arunachal Pradesh","18":"18-Assam","10":"10-Bihar","04":"04-Chandigarh","22":"22-Chhattisgarh","26":"26-Dadra and Nagar Haveli","25":"25-Daman and Diu","07":"07-Delhi","30":"30-Goa","24":"24-Gujarat","06":"06-Haryana","02":"02-Himachal Pradesh","01":"01-Jammu and Kashmir","20":"20-Jharkhand","29":"29-Karnataka","32":"32-Kerala","31":"31-Lakshadweep","23":"23-Madhya Pradesh","27":"27-Maharashtra","14":"14-Manipur","17":"17-Meghalaya","15":"15-Mizoram","13":"13-Nagaland","21":"21-Odisha","34":"34-Puducherry","03":"03-Punjab","08":"08-Rajasthan","11":"11-Sikkim","33":"33-Tamil Nadu","36":"36-Telangana","16":"16-Tripura","09":"09-Uttar Pradesh","05":"05-Uttarakhand","97":"97-Other Territory","19":"19-West Bengal"}
    return render_template("gstr1_b2cl.html",data=rows,month=m,state_codes=state_codes)
@app.route('/gstr1/b2cs/<m>')
def gstr1_b2cs(m):
    b2cs = str(session["company_id"])+"_gstr1_sales"
    home_state = '19'
    ur_id = get_ledger_id("Unregistered Sale")
    rows = db.execute("""SELECT * FROM :table WHERE month=:month
    AND debtor_id = :ur_id AND
    ((place_of_supply = :hs)
      OR (place_of_supply != :hs AND invoice_value < 250001))
    """,table=b2cs,month=m,ur_id=ur_id,hs=home_state)
    state_codes = {"35":"35-Andaman and Nicobar Islands","37":"37-Andhra Pradesh","12":"12-Arunachal Pradesh","18":"18-Assam","10":"10-Bihar","04":"04-Chandigarh","22":"22-Chhattisgarh","26":"26-Dadra and Nagar Haveli","25":"25-Daman and Diu","07":"07-Delhi","30":"30-Goa","24":"24-Gujarat","06":"06-Haryana","02":"02-Himachal Pradesh","01":"01-Jammu and Kashmir","20":"20-Jharkhand","29":"29-Karnataka","32":"32-Kerala","31":"31-Lakshadweep","23":"23-Madhya Pradesh","27":"27-Maharashtra","14":"14-Manipur","17":"17-Meghalaya","15":"15-Mizoram","13":"13-Nagaland","21":"21-Odisha","34":"34-Puducherry","03":"03-Punjab","08":"08-Rajasthan","11":"11-Sikkim","33":"33-Tamil Nadu","36":"36-Telangana","16":"16-Tripura","09":"09-Uttar Pradesh","05":"05-Uttarakhand","97":"97-Other Territory","19":"19-West Bengal"}
    return render_template("gstr1_b2cs.html",data=rows,month=m,state_codes=state_codes)
@app.route('/gstr1/download/<t>/<m>')
def gstr1_download(t,m):
    company = db.execute("SELECT * FROM master WHERE company_id=:id",id=session["company_id"])
    filename = company[0]["company_name"].strip()
    state_codes = {"35":"35-Andaman and Nicobar Islands","37":"37-Andhra Pradesh","12":"12-Arunachal Pradesh","18":"18-Assam","10":"10-Bihar","04":"04-Chandigarh","22":"22-Chhattisgarh","26":"26-Dadra and Nagar Haveli","25":"25-Daman and Diu","07":"07-Delhi","30":"30-Goa","24":"24-Gujarat","06":"06-Haryana","02":"02-Himachal Pradesh","01":"01-Jammu and Kashmir","20":"20-Jharkhand","29":"29-Karnataka","32":"32-Kerala","31":"31-Lakshadweep","23":"23-Madhya Pradesh","27":"27-Maharashtra","14":"14-Manipur","17":"17-Meghalaya","15":"15-Mizoram","13":"13-Nagaland","21":"21-Odisha","34":"34-Puducherry","03":"03-Punjab","08":"08-Rajasthan","11":"11-Sikkim","33":"33-Tamil Nadu","36":"36-Telangana","16":"16-Tripura","09":"09-Uttar Pradesh","05":"05-Uttarakhand","97":"97-Other Territory","19":"19-West Bengal"}

    if t == "b2b":
        csv = "GSTIN/UIN of Recipient,Invoice Number,Invoice date,Invoice Value,Place Of Supply,Reverse Charge,Invoice Type,E-Commerce GSTIN,Rate,Taxable Value,Cess Amount"
        b2b = str(session["company_id"])+"_gstr1_sales"
        ur_id = get_ledger_id("Unregistered Sale")
        rows = db.execute("SELECT * FROM :table WHERE month=:month AND debtor_id != :ur_id",table=b2b,month=m,ur_id=ur_id)
        for row in rows:
            csv += "\n"
            if len(str(row["date"])) == 1:
                row["date"] = "0"+str(row["date"])
            csv += row["gstin"]+","
            csv += row["inv_no"]+","
            csv += str(row["date"]) + "-" + row["month"] + "-20" + str(row["year"])+","
            csv += str("%0.2f"%round(row["invoice_value"]+row["roundoff"]))+","
            csv += state_codes[row["place_of_supply"]]+","
            csv += "N," #Reverse Charge
            csv += "Regular,," #Invoice Type,E-Commerce
            csv += str(row["stock_item_taxrate"])+","
            csv += str("%0.2f"%row["amount"])+","
    if t == "b2cs":
        csv = "Type,Place Of Supply,Rate,Taxable Value,Cess Amount,E-Commerce GSTIN"
        b2cs = str(session["company_id"])+"_gstr1_sales"
        home_state = '19'
        ur_id = get_ledger_id("Unregistered Sale")
        rows = db.execute("""SELECT * FROM :table WHERE month=:month
        AND debtor_id = :ur_id AND
        ((place_of_supply = :hs)
          OR (place_of_supply != :hs AND invoice_value < 250001))
        """,table=b2cs,month=m,ur_id=ur_id,hs=home_state)
        for row in rows:
            csv += "\nOE,"
            csv += state_codes[row["place_of_supply"]]+","
            csv += str(row["stock_item_taxrate"])+","
            csv += str("%0.2f"%round(row["invoice_value"]+row["roundoff"]))+","
            csv += ","
    if t == "b2cl":
        csv = "Invoice Number,Invoice date,Invoice Value,Place Of Supply,Rate,Taxable Value,Cess Amount,E-Commerce GSTIN"
        b2cl = str(session["company_id"])+"_gstr1_sales"
        ur_id = get_ledger_id("Unregistered Sale")
        home_state = '19'
        rows = db.execute("""SELECT * FROM :table WHERE month=:month
        AND debtor_id = :ur_id AND invoice_value > 250000 AND place_of_supply!=:hs""",
        table=b2cl,month=m,ur_id=ur_id,hs=home_state)
        for row in rows:
            csv += "\n"
            if len(str(row["date"])) == 1:
                row["date"] = "0"+str(row["date"])
            csv += row["inv_no"]+","
            csv += str(row["date"]) + "-" + row["month"] + "-20" + str(row["year"])+","
            csv += str("%0.2f"%round(row["invoice_value"]+row["roundoff"]))+","
            csv += state_codes[row["place_of_supply"]]+","
            csv += str(row["stock_item_taxrate"])+","
            csv += str("%0.2f"%row["amount"])+","
            csv += ""
    # We need to modify the response, so the first thing we
    # need to do is create a response out of the CSV string
    response = make_response(csv)
    # This is the key: Set the right header for the response
    # to be downloaded, instead of just printed on the browser
    response.headers["Content-Disposition"] = "attachment;filename="+filename+" "+m+"_"+t+".csv"
    return response
"""
END Group: GST RETURNS
"""
# ------------------------------
"""
GROUP: Login & register
"""
@app.route('/login',methods=["GET","POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    else:
        #return str(request.form)
        rows = db.execute("SELECT * FROM login WHERE userid=:userid AND password=:password",userid=request.form.get('userid'),password=request.form.get('password'))
        if len(rows) != 1:
            flash("Invalid Userid/Password","error")
            return render_template("login.html")
        else:
            company = db.execute("SELECT * FROM master WHERE company_id=:id",id=rows[0]["company_id"])
            session["company_name"] = company[0]["company_name"]
            session["company_id"] = company[0]["company_id"]
            flash("Welcome","info")
            return redirect(url_for('index'))
        #return str(request.form)
@app.route('/register',methods=["GET","POST"])
def register():
    #return str(Session)
    if request.method == "GET":
        return render_template("register.html")
    else:
        #ImmutableMultiDict([('gstin', '19AAAAA1234E1ZT'), ('repassword', 'admin'),
        # ('company_name', 'A1 CLAMPS INDIA PVT LTD'), ('userid', 'klipco'), ('address', '1A BONFIELD LANE KOL-1'), ('password', 'admin')])
        s = dict(request.form)
        rows = db.execute("SELECT * FROM master WHERE company_name=:name OR company_gstin=:gstin",name=s["company_name"][0],gstin=s["gstin"][0])
        if len(rows) > 0:
            flash("Duplicate Entry","error")
            return render_template("register.html")
        if s["password"][0] != s["repassword"][0]:
            flash("Passwords Don't Match","error")
            return render_template("register.html")
        rows = db.execute("SELECT * FROM login WHERE userid=:uid",uid=s["userid"][0])
        if len(rows) > 0:
            flash("User-ID already taken","error")
            return render_template("register.html")
        row = db.execute("""
        INSERT INTO master (company_name,company_gstin,company_address)
        VALUES (:cname,:cgstin,:cadd)
        """,cname=s["company_name"][0],cgstin=s["gstin"][0],cadd=s["address"][0])
        company_id = row
        #return str(row)
        db.execute("""INSERT INTO login
            (userid,password,company_name,company_id)
            VALUES (:uid,:passw,:cname,:cid)""",uid=s["userid"][0],
            passw=s["password"][0],cname=s["company_name"][0],cid=company_id)

        #Ledgers table
        table = str(company_id)+"_ledgers"
        db.execute("""
        CREATE TABLE :table
        ('id' INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, 'ledger_name' TEXT,
        'ledger_group' TEXT, 'opening_balance' REAL, 'address' TEXT, 'gstin' TEXT)
        """,table=table)

        #Master Payment table
        table = str(company_id)+"_master_payment"
        db.execute("""
        CREATE TABLE :table
         ('id' INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
         'creditor_id' INTEGER, 'date' INTEGER, 'month' TEXT, 'year' INTEGER,
         'narration' TEXT)
        """,table=table)
        #Master Purchase table
        table = str(company_id)+"_master_purchase"
        db.execute("""
        CREATE TABLE :table ('id' INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
        'supplier_inv_no' TEXT, 'debtor_id' TEXT, 'creditor_id' TEXT,'pur_date' INTEGER,
         'supplier_date' INTEGER, 'pur_month' TEXT, 'pur_year' TEXT, 'supplier_month' TEXT, 'supplier_year' TEXT)
        """,table=table)
        #Master Sales table
        table = str(company_id)+"_master_sales"
        db.execute("""
        CREATE TABLE :table ('id' INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
         'debtor_id' INTEGER, 'creditor_id' INTEGER, 'inv_no' TEXT, 'date' INTEGER,
         'month' INTEGER, 'year' INTEGER, 'place_of_supply' TEXT DEFAULT '19',
         'roundoff' REAL DEFAULT 0.00)
        """,table=table)
        #Payments table
        table = str(company_id)+"_payment"
        db.execute("""
        CREATE TABLE :table ('id' INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
        'master_id' INTEGER, 'debtor_id' INTEGER, 'voucher_no' INTEGER, 'amount' REAL)
        """,table=table)
        #Purchase table
        table = str(company_id)+"_purchase"
        db.execute("""
        CREATE TABLE :table ('id' INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
        'bill_id' INTEGER, 'item_id' INTEGER, 'qty' REAL, 'rate' REAL,
        'amount' REAL, 'disc' REAL)
        """,table=table)
        #Sales table
        table = str(company_id)+"_sales"
        db.execute("""
        CREATE TABLE :table ('id' INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
        'bill_id' INTEGER, 'item_id' INTEGER, 'qty' REAL, 'rate' REAL,
        'amount' REAL, 'disc' REAL)
        """,table=table)
        #Stock Group table
        table = str(company_id)+"_stockgroup"
        db.execute("""
        CREATE TABLE :table ('id' INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
        'group_name' TEXT, 'hsn' TEXT, 'taxrate' TEXT, 'uom' TEXT)
        """,table=table)
        #Stock Items table
        table = str(company_id)+"_stock_items"
        db.execute("""
        CREATE TABLE :table ('id' INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
        'stock_item_name' TEXT, 'stock_item_group' TEXT, 'stock_item_hsn' TEXT,
        'stock_item_taxrate' REAL, 'stock_item_uom' TEXT, 'rate' REAL DEFAULT 0.00)
        """,table=table)
        #Sales View table
        table = str(company_id)+"_gstr1_sales"
        db.execute("""
        CREATE VIEW :table AS SELECT * FROM '1_sales'
        INNER JOIN '1_master_sales' ON '1_master_sales'.id = bill_id
        INNER JOIN '1_stockitems' ON '1_stockitems'.id = item_id
        INNER JOIN '1_ledgers' ON '1_ledgers'.id = debtor_id
        INNER JOIN (
                    SELECT bill_id AS invoice_number,
                    SUM(amount + (amount*'1_stockitems'.stock_item_taxrate)/100)
                    AS invoice_value
                    FROM '1_sales'
                    INNER JOIN '1_stockitems' ON '1_stockitems'.id = item_id
                    GROUP BY bill_id
                    ) ON invoice_number = bill_id
        """,table=table)
        # INSERT Purchase,Sales,Unregistered
        table = str(company_id)+"_ledgers"
        db.execute("INSERT INTO :table (ledger_name,ledger_group) VALUES ('Purchase','Purchase')",table=table)
        db.execute("INSERT INTO :table (ledger_name,ledger_group) VALUES ('Sales Acc','Sales')",table=table)
        db.execute("INSERT INTO :table (ledger_name,ledger_group) VALUES ('Unregistered Sale','Sundry Debtors')",table=table)
        return redirect(url_for('logout'))
@app.route('/logout')
def logout():
    session.clear()
    flash("Successfully Logged out","info")
    return redirect(url_for('index'))
"""
END GROUP: Login & register
"""
# ------------------------------
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
