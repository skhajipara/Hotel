from flask import Flask, render_template, request, redirect, url_for, session # Importing the necessary libraries
import sqlite3 # Import for SQL
import smtplib # Import for email
from email.message import EmailMessage # Import for email
from datetime import datetime, timedelta # Import for date and time
from pathlib import Path # Import for file path
from dotenv import load_dotenv
import os
load_dotenv()
os.getenv("EMAIL_USER")
os.getenv("EMAIL_PASS")


app = Flask(__name__, template_folder='templates')

# Session config
app.secret_key = 'your_secret_key_here' 
app.permanent_session_lifetime = timedelta(hours=24)

# For pdf location
pdf_location = Path("Gujarati menu.pdf")

# Email send setup

def send_email_notification(to_email, customer_name, subject, body, attach_pdf=False):
    sender_email = os.getenv("EMAIL_USER") # email sender
    sender_password = os.getenv("EMAIL_PASS")

    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = to_email
    msg.set_content(body)

    # Attach pdf setup
    if attach_pdf and pdf_location.exists():
        with open(pdf_location, 'rb') as f:
            msg.add_attachment(f.read(), maintype='application', subtype='pdf', filename="S.K.Restaurant_Menu.pdf")

    # mail sending use smtplib
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(sender_email, sender_password)
        smtp.send_message(msg)


# for connect with html
@app.route('/')
def home():
    return render_template('Kathiyawad.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        Email = request.form.get('Email')
        Password = request.form.get('Password')
        if Email and Password:
            with sqlite3.connect('table.db') as conn: # Connect to the database
                cursor = conn.cursor()
                # Login table
                cursor.execute('''CREATE TABLE IF NOT EXISTS Login (
                    Customer_Name TEXT NOT NULL,
                    Email TEXT NOT NULL,
                    Mobile_No INTEGER NOT NULL,
                    Password TEXT NOT NULL);''')
                cursor.execute("SELECT Customer_Name, Password FROM Login WHERE Email = ?", (Email,))
                result = cursor.fetchone()

            if result: # Check if the user exists or not
                customer_name, stored_password = result
                if stored_password == Password:
                    # Set session on successful login
                    session.permanent = True
                    # mail send to customer for login time
                    session['user'] = customer_name
                    session['email'] = Email


                    subject = "🔐 Login Notification"
                    body = f"""\U0001f44b Hello {customer_name},

✅ You have successfully logged in to **S.K.Restaurant**!

Please enjoy your meal at our restaurant.

🍽️ Explore the Menu  
🛒 Place Your Order  
🪑   Book a Table  
🚚 Get Food Delivered  

🕰️ Login Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
❤️ Team S.K.Restaurant"""
                    send_email_notification(Email, customer_name, subject, body, attach_pdf=True)
                    return render_template('Kathiyawad.html', flash_message="✅ Login successful!")

                else:# Check if the password is correct or not
                    return render_template('login.html', flash_message="❌ Incorrect email or password. Please try again.")

            else:# Check if the user exists or not
                return render_template('signup.html', flash_message="⚠️ You don't have an account. Please sign up first.")

    return render_template('login.html') # Return the login page 

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        Customer_Name = request.form.get('Customer_Name')
        Email = request.form.get('Email')
        Mobile_No = request.form.get('Mobile_No')
        Password = request.form.get('Password')
        if Customer_Name and Email and Mobile_No and Password:
            with sqlite3.connect('table.db') as conn: # Connect to database. It will be created if it doesn't exist.
                cursor = conn.cursor()
                # Create table if it doesn't exist
                cursor.execute('''CREATE TABLE IF NOT EXISTS Login (
                    Customer_Name TEXT NOT NULL,
                    Email TEXT NOT NULL,
                    Mobile_No INTEGER NOT NULL,
                    Password TEXT NOT NULL);''')
                
                # Check if account already exists
                cursor.execute('SELECT * FROM Login WHERE Email = ?', (Email,))
                if cursor.fetchone():
                    return render_template('login.html', flash_message="⚠️ You already have an account. Please login.")


                cursor.execute('''INSERT INTO Login (Customer_Name, Email, Mobile_No, Password)
                                  VALUES (?, ?, ?, ?)''', (Customer_Name, Email, Mobile_No, Password))

            # mail send to customer for Account create at a time
            subject = "📝 Account Created Successfully"
            body = f"""\U0001f44b Hello {Customer_Name},

🎉 Your account has been created at **S.K.Restaurant**!


🍽️ Explore the Menu  
🛒 Place Your Order  
🪑 Book a Table  
🚚 Get Food Delivered  

❤️ Team S.K.Restaurant"""
            send_email_notification(Email, Customer_Name, subject, body)
            return render_template('login.html', flash_message="✅ Account created successfully!")

    return render_template('signup.html') # Return the signup page


@app.route('/forget', methods=['GET', 'POST'])
def forget_password():
    if request.method == 'POST':
        Email = request.form.get('Email')
        Mobile_No = request.form.get('Mobile_No')

        if Email and Mobile_No:
            with sqlite3.connect('table.db') as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT Customer_Name, Password FROM Login WHERE Email = ? AND Mobile_No = ?", (Email, Mobile_No))
                result = cursor.fetchone()

                if result:
                    customer_name, password = result
                    subject = "🔑 Password Recovery - S.K.Restaurant"
                    body = f"""\U0001f44b Hello {customer_name},

🛡️ You requested to recover your password from **S.K.Restaurant**.

📞 Contact: {Mobile_No}
🔐 Your Password: {password}


❤️ Team S.K.Restaurant"""
                    send_email_notification(Email, customer_name, subject, body)
                    return render_template('login.html', flash_message="✅ Password sent to your email.")
                else:
                    return render_template('signup.html', flash_message="⚠️ No account found. Please sign up first.")

    return render_template('forget.html')

# All route are link page with html file
@app.route('/booking')
def booking():
    return render_template('booking.html')

@app.route('/order')
def order():
    return render_template('order.html')

@app.route('/delivery')
def delivery():
    return render_template('delivery.html')

@app.route('/submit', methods=['POST'])
def submit():
    Customer_Name = request.form.get('Customer_Name')
    Email = request.form.get('Email')
    MO_Number = request.form.get('MO_Number')

    try:
        with sqlite3.connect('table.db', timeout=10) as conn: # Connect to database. It will be created if it doesn't exist.
            cursor = conn.cursor()


            # for table booking
            if Email and MO_Number and request.form.get('Table_No') and request.form.get('Date_Time'):
                Table_No = request.form.get('Table_No')
                Member = request.form.get('Member')
                Date_Time = request.form.get('Date_Time')

                cursor.execute('SELECT * FROM Login WHERE Customer_Name = ? AND Email = ? AND Mobile_No = ?', 
                               (Customer_Name, Email, MO_Number))
                if not cursor.fetchone(): # If customer is not in database
                    return render_template('login.html', flash_message="⚠️ Please login first (you are not registered).")

                # check date and time
                try:
                    booking_time = datetime.strptime(Date_Time, '%Y-%m-%dT%H:%M')
                    if booking_time < datetime.now():
                        return render_template('booking.html', flash_message="⚠️ You cannot book a table in the past. Please choose a future time.")

                except ValueError: # If date and time is not in correct format
                     
                     return render_template('booking.html',flash_message="⚠️ Invalid date/time format. Please select a valid date.")
    
                # Booing table database
                cursor.execute('''CREATE TABLE IF NOT EXISTS Booking (
                    Customer_Name TEXT, Email TEXT, MO_Number INTEGER,
                    Table_No INTEGER, Member INTEGER, Date_Time TEXT);''')
                cursor.execute("SELECT * FROM Booking WHERE Table_No = ? AND Date_Time = ?", (Table_No, Date_Time))
                if cursor.fetchone(): # check condition if table is already booked
                    return render_template('booking.html',flash_message="⚠️ Table already booked at that time.")
                else: # if table is not booked, insert data into database
                    cursor.execute('INSERT INTO Booking VALUES (?, ?, ?, ?, ?, ?)', 
                                   (Customer_Name, Email, MO_Number, Table_No, Member, Date_Time))

                    if Email:
                        # mail send to customer for Table booking time
                        subject = "🪑 Table Booking Confirmation"
                        body = f"""\U0001f44b Hello {Customer_Name},

✅ Your table has been booked at **S.K.Restaurant**!


🪑 Table No: {Table_No}  
👥 Members: {Member}  
📆 Date & Time: {Date_Time}


❤️ Team S.K.Restaurant"""
                        send_email_notification(Email, Customer_Name, subject, body, attach_pdf=True)
                    return render_template('Kathiyawad.html', flash_message="✅ Booking successful!")


            # for order page
            elif request.form.get('Table_No') and request.form.get('Order'):
                Table_No = request.form.get('Table_No')
                Order = request.form.get('Order')

                cursor.execute('SELECT * FROM Login WHERE Customer_Name = ?', (Customer_Name,))
                if not cursor.fetchone():
                    return render_template('login.html',flash_message="⚠️ Please login first.")

                # table order details
                cursor.execute('''CREATE TABLE IF NOT EXISTS Orders_Details (
                    Customer_Name TEXT,Email TEXT NOT NULL, Table_No INTEGER, "Order" TEXT);''')
                cursor.execute('SELECT * FROM Orders_Details WHERE Table_No = ? AND "Order" = ?', (Table_No, Order))
                if cursor.fetchone(): # check condition if order is already placed
                    return render_template('order.html',flash_message="⚠️ You gave this order already!")
                else: # if order is not placed, insert data into database
                    cursor.execute('INSERT INTO Orders_Details VALUES (?, ?, ?, ?)', (Customer_Name, Email, Table_No, Order))

                    if Email:
                        # mail send to customer for Order
                        subject = "🛒 Order Confirmation"
                        body = f"""\U0001f44b Hello {Customer_Name},

✅ Your order has been placed!


🪑 Table No: {Table_No}  
📝 Order: {Order}


Please wait a while.....

❤️ Team S.K.Restaurant"""
                        send_email_notification(Email, Customer_Name, subject, body)
                    return render_template('Kathiyawad.html', flash_message="✅ Your order has been placed successfully.")
    
            # Home Delivery page
            elif request.form.get('Address'):
                Mobile_Number = request.form.get('Mobile_Number')
                Order = request.form.get('Order')
                Address = request.form.get('Address')

                # check if customer is login or not
                cursor.execute('SELECT * FROM Login WHERE Customer_Name = ? AND Mobile_No = ?', (Customer_Name, Mobile_Number))
                if not cursor.fetchone():
                    return render_template('login.html', flash_message="⚠️ Please login first (you are not registered).")

                # home delivery order details
                cursor.execute('''CREATE TABLE IF NOT EXISTS Delivery (
                    Customer_Name TEXT, Mobile_Number INTEGER, "Order" TEXT, Address TEXT);''')
                cursor.execute('SELECT * FROM Delivery WHERE Mobile_Number = ? AND "Order" = ?', (Mobile_Number, Order))
                if cursor.fetchone(): # check condition if order is already placed
                    return render_template('order.html',flash_message="⚠️ You gave this order already!")
                else: # if order is not placed, insert data into database
                    cursor.execute('INSERT INTO Delivery VALUES (?, ?, ?, ?)', (Customer_Name, Mobile_Number, Order, Address))

                    if Email:
                        # mail send to customer for Delivery
                        subject = "🚚 Delivery Order Confirmation"
                        body = f"""\U0001f44b Hello {Customer_Name},

✅ Your delivery order has been placed!

Your order is our responsibility,

📦 Order: {Order}  
📍 Address: {Address}  
📞 Contact: {Mobile_Number}

Please wait a while.....


❤️ Team S.K.Restaurant"""
                        send_email_notification(Email, Customer_Name, subject, body)
                    return render_template('Kathiyawad.html',flash_message="✅ Your delivery order is confirmed.")

    
    except sqlite3.OperationalError as e: # if database is not created
        
        return render_template('Kathiyawad.html', flash_message=f"⚠️ Database Error: {str(e)}")

    return render_template(flash_message="⚠️ Invalid submission. Please try again.")


if __name__ == '__main__':
    app.run(debug=True)
