from flask import Flask, render_template, request, redirect, make_response
from flask_sqlalchemy import SQLAlchemy
import datetime
import pdfkit
import os 
app = Flask(__name__)

# account login credentials
accountLoginCredentials = {"loginUserName" : "Laundry Room", "loginUserPassword" : "LaundryRoom@123", "alreadyLoggedIn" : False, "currentUserBills":"", "currentBillNo": ""}

# database configuration
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL") # "mysql://root:@localhost/billprinter"
# postgres://billingprinterdb_user:FYewCXPpkmL5rbXjOCh3ImcwPL9phQHI@dpg-cgbutf82qv267uahbl7g-a.oregon-postgres.render.com/billingprinterdb
db = SQLAlchemy(app)

class All_customers(db.Model):
    # sno, customer_name, phone_number, customer_address
    sno = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(225), nullable=False)
    phone_number = db.Column(db.String(225), nullable=False)
    customer_address = db.Column(db.String(500), nullable=True)

class List_of_bills(db.Model):
    # sno, date_time, phone_number, total_amount, payed_amount
    sno = db.Column(db.Integer, primary_key=True)
    date_time = db.Column(db.DateTime, nullable=False)
    phone_number = db.Column(db.String(225), nullable=False)
    total_amount = db.Column(db.Integer, nullable=False)  
    payed_amount = db.Column(db.Integer, nullable=False)

class List_of_items(db.Model):
    # sno, quantity, perticular, amount, billno
    sno = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)
    perticular = db.Column(db.String(500), nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    billno = db.Column(db.Integer, nullable=False)


# login and logout
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        userName = request.form.get("username")
        userPassword = request.form.get("password")
        if userName.lower() != accountLoginCredentials["loginUserName"].lower() or userPassword != accountLoginCredentials["loginUserPassword"]:
            return redirect("/")
        accountLoginCredentials["alreadyLoggedIn"] = True
        return redirect("/dashboard")
    return render_template("page not found.html")

@app.route("/logout", methods=["GET", "POST"])
def logout():
    if request.method == "POST":
        accountLoginCredentials["alreadyLoggedIn"] = False
        return redirect("/dashboard")
    return render_template("page not found.html")


# adding new customers
@app.route("/addnew", methods=["GET", "POST"])
def addNew():
    if request.method == "POST":
        customerName = request.form.get("customerName")
        customerPhone = request.form.get("customerPhone")
        customerAddress = request.form.get("customerAddress")
        
        if not (All_customers.query.filter_by(phone_number=customerPhone).all()):
            entry = All_customers(customer_name=customerName, phone_number=customerPhone, customer_address=customerAddress)
            db.session.add(entry)
            db.session.commit()

        listOfBills = List_of_bills.query.filter_by(phone_number=customerPhone).all()
        openCustomerName = All_customers.query.filter_by(phone_number=customerPhone).first().customer_name
        accountLoginCredentials["currentUserBills"] = customerPhone
        return render_template("User Dashboard.html", listOfBills=listOfBills, openCustomerName=openCustomerName, openCustomerNumber=customerPhone)
    return redirect("/listofbills")


# deleting the customer from the Dashboard
@app.route("/deletecustomer", methods=["GET", "POST"])
def deleteCustomer():
    # delete all the bills and the items perchased by this customer                     <---------------------------------
    if request.method == "POST":
        custmerNumber = request.form.get("deleteCustomerNumber")
        customer = All_customers.query.filter_by(phone_number=custmerNumber).first()
        db.session.delete(customer)
        db.session.commit()
        return redirect("/dashboard")
    return render_template("page not found.html")

# searching customer
@app.route("/searchedcustomer", methods=["GET", "POST"])
def searchCustomer():
    if request.method == "POST":
        customerNumber = request.form.get("numberToSearch")
        allCustomers = All_customers.query.filter_by(phone_number=customerNumber).all()
        return render_template("dashboard.html", allCustomers=allCustomers)
    return redirect("/dashboard")


# open customer
@app.route("/opencustomer", methods=["GET", "POST"])
def openCustomer():
    if request.method == "POST":
        openCustomerName = request.form.get("openCustomerName")
        openCustomerNumber = request.form.get("openCustomerNumber")
        listOfBills = List_of_bills.query.filter_by(phone_number=openCustomerNumber).all()
        accountLoginCredentials["currentUserBills"] = openCustomerNumber
        return render_template("User Dashboard.html", listOfBills=listOfBills, openCustomerName=openCustomerName, openCustomerNumber=openCustomerNumber)
    return redirect("/listofbills")

# delete bills
@app.route("/deletebill", methods=["GET", 'POST'])
def deleteBill():
    # delete all the items                                                          <-------------------------------------------------
    if request.method == "POST":
        deleteBillSno = request.form.get("deleteBillSno")
        bill = List_of_bills.query.filter_by(sno=deleteBillSno).first()
        db.session.delete(bill)
        db.session.commit()
        return redirect("/listofbills")
    return render_template("page not found.html")



# creating new bill
@app.route("/createbill", methods=["GET", "POST"])
def createbill():
    if request.method == "POST":
        dateTime = datetime.datetime.now()
        # dateTime = dateTime.strftime("%d, %a, %y, %I, %M, %S, %p")
        print(dateTime)
        customerPhone = request.form.get("createBillNumber")
        totalAmount = 0
        payedAmount = 0
        entry = List_of_bills(date_time=dateTime, phone_number=customerPhone, total_amount=totalAmount, payed_amount=payedAmount)
        # sno, date_time, phone_number, total_amount, payed_amount
        db.session.add(entry)
        db.session.commit()

        customer = All_customers.query.filter_by(phone_number=customerPhone).first()
        billNo = List_of_bills.query.all()[-1].sno
        accountLoginCredentials["currentBillNo"] = billNo
        bill = List_of_bills.query.filter_by(sno=billNo).first()
        billItems = List_of_items.query.filter_by(billno=billNo).all()
        return render_template("billing page.html", customerDetails=customer, billDetails=bill, billItems=billItems)
    return redirect("/billingpage")


# open bill
@app.route("/openbill", methods=["GET", 'POST'])
def openBill():
    if request.method == 'POST':
        openBillSno = request.form.get("openBillSno")
        accountLoginCredentials["currentBillNo"] = openBillSno
        bill = List_of_bills.query.filter_by(sno=openBillSno).first()
        customerNumber = bill.phone_number
        customer = All_customers.query.filter_by(phone_number=customerNumber).first()
        billItems = List_of_items.query.filter_by(billno=openBillSno).all()
        return render_template("billing page.html", customerDetails=customer, billDetails=bill, billItems=billItems)
    return redirect("/billingpage")

# add items in bill
@app.route("/additems", methods=["GET", "POST"])
def addItems():
    if request.method == "POST":
        addItemQyt = request.form.get("addItemQyt")
        addItemPerticular = request.form.get("addItemPerticular")
        addItemAmount = request.form.get('addItemAmount')
        addItemsBillSno = request.form.get("addItemsBillSno")
        # sno, quantity, perticular, amount, billno
        entry = List_of_items(quantity=addItemQyt, perticular=addItemPerticular, amount=addItemAmount, billno=addItemsBillSno)
        db.session.add(entry)
        db.session.commit()

        bill = List_of_bills.query.filter_by(sno=addItemsBillSno).first()
        # print(type(addItemAmount), type(bill.total_amount))
        bill.total_amount = bill.total_amount + int(addItemAmount)
        db.session.commit()
        customerNumber = bill.phone_number
        customer = All_customers.query.filter_by(phone_number=customerNumber).first()
        billItems = List_of_items.query.filter_by(billno=addItemsBillSno).all()
        return render_template("billing page.html", customerDetails=customer, billDetails=bill, billItems=billItems)
    return redirect("/billingpage")

# delete items form the bill
@app.route("/deleteitem", methods=["GET", "POST"])
def deleteItems():
    if request.method == "POST":
        deleteItemSno = request.form.get("deleteItemSno")
        updateBillSno = request.form.get("updateBillSno")
        item = List_of_items.query.filter_by(sno=deleteItemSno).first()
        db.session.delete(item)
        db.session.commit()
        bill = List_of_bills.query.filter_by(sno=updateBillSno).first()
        print(updateBillSno, bill)
        bill.total_amount = bill.total_amount - int(item.amount)
        db.session.commit()
        return redirect("/billingpage")
    return render_template("page not found.html")

# making payment
@app.route("/payamount", methods={"GET", "POST"})
def payAmount():
    if request.method == "POST":
        payingBillSno = request.form.get("payingBillSno")
        currentPayment = request.form.get("currentpayment")

        bill = List_of_bills.query.filter_by(sno=payingBillSno).first()
        bill.payed_amount = bill.payed_amount + int(currentPayment)
        bill.date_time  = datetime.datetime.now()
        db.session.commit()
        return redirect("/billingpage")
    return render_template("page not found.html")



# app pages
@app.route("/")
def loginPage():
    if accountLoginCredentials["alreadyLoggedIn"]:
        return redirect("/dashboard")
    return render_template("login.html")

@app.route("/dashboard", methods=["GET", "POST"])
def dashboardPage():
    if accountLoginCredentials["alreadyLoggedIn"]:
        allCustomers = All_customers.query.all()
        accountLoginCredentials["currentUserBills"] = ""
        return render_template("dashboard.html", allCustomers=allCustomers)
    return redirect("/")

@app.route("/listofbills")
def allListOfBills():
    if accountLoginCredentials["alreadyLoggedIn"] and accountLoginCredentials["currentUserBills"] != "":
        accountLoginCredentials["currentBillNo"] = ""
        currentUserBills = List_of_bills.query.filter_by(phone_number=accountLoginCredentials["currentUserBills"]).all()
        openCustomerName = All_customers.query.filter_by(phone_number=accountLoginCredentials["currentUserBills"]).first().customer_name
        return render_template("User Dashboard.html", listOfBills=currentUserBills, openCustomerName=openCustomerName, openCustomerNumber=accountLoginCredentials["currentUserBills"])
    return redirect("/dashboard")

@app.route("/billingpage")
def billingPage():
    if accountLoginCredentials["alreadyLoggedIn"] and accountLoginCredentials["currentBillNo"]:
        bill = List_of_bills.query.filter_by(sno=accountLoginCredentials["currentBillNo"]).first()
        customerNumber = bill.phone_number
        customer = All_customers.query.filter_by(phone_number=customerNumber).first()
        billItems = List_of_items.query.filter_by(billno=accountLoginCredentials["currentBillNo"]).all()
        return render_template("billing page.html", customerDetails=customer, billDetails=bill, billItems=billItems)
    return redirect("/listofbills")

# printing bill
@app.route("/print_pdf", methods=["POST", "GET"])  
def print_pdf():
    if request.method == "POST":
        # printBillSno = request.form.get("printBillSno")
        bill = List_of_bills.query.filter_by(sno=accountLoginCredentials["currentBillNo"]).first()
        customerNumber = bill.phone_number
        customer = All_customers.query.filter_by(phone_number=customerNumber).first()
        billItems = List_of_items.query.filter_by(billno=accountLoginCredentials["currentBillNo"]).all()
        rendered = render_template("bill.html",  customerDetails=customer, billDetails=bill, billItems=billItems)
        pdf = pdfkit.from_string(rendered, False)

        response = make_response(pdf)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = 'inline; filename=recipt.pdf'
        return response
    return render_template("page not found.html")



        






if __name__=="__main__":
    app.run(debug=True)