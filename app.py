from flask import Flask, render_template, request, redirect, url_for, session # Importing the necessary libraries
import sqlite3 # Import for SQL
import smtplib # Import for email
from email.message import EmailMessage # Import for email
from datetime import datetime, timedelta # Import for date and time
from pathlib import Path # Import for file path
from dotenv import load_dotenv
from functools import wraps
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
pdf_location1= Path("English menu.pdf")

# Email send setup

def send_email_notification(to_email, customer_name, subject, body, attach_pdf=False,attach_pdf1=False):
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
            msg.add_attachment(f.read(), maintype='application', subtype='pdf', filename="S.K.Hostels_Gujarati_Menu.pdf")

    if attach_pdf1 and pdf_location1.exists():
        with open(pdf_location1, 'rb') as f:
            msg.add_attachment(f.read(), maintype='application', subtype='pdf', filename="S.K.Hotels_English_Menu.pdf")

    # mail sending use smtplib
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(sender_email, sender_password)
        smtp.send_message(msg)

# Login mandatory
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session or 'email' not in session:
            return redirect(url_for('login', flash_message="⚠️ Please login first."))
        return f(*args, **kwargs)
    return decorated_function
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

✅ You have successfully logged in to **S.K.Hotels Group**!

Please enjoy your meal at our Hotel.

🍽️ Explore the Menu  
🛒 Place Your Order  
🪑  Book a Table  
🚚 Get Food Delivered  
🛏️ Room Book

🕰️ Login Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}



Warm Regards,
❤️ Team S.K.Hotels"""
                    send_email_notification(Email, customer_name, subject, body, attach_pdf=True,attach_pdf1=True)
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

🎉 Your account has been created at **S.K.Hotels Group**!


🍽️ Explore the Menu  
🛒 Place Your Order  
🪑 Book a Table  
🚚 Get Food Delivered
🛏️ Room Book  



Warm Regards,
❤️ Team S.K.Hotels"""
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
                    subject = "🔑 Password Recovery - S.K.Hotels Group"
                    body = f"""\U0001f44b Hello {customer_name},

🛡️ You requested to recover your password from **S.K.Hotels Group**.

📞 Contact: {Mobile_No}
🔐 Your Password: {password}



Warm Regards,
❤️ Team S.K.Hotels"""
                    send_email_notification(Email, customer_name, subject, body)
                    return render_template('login.html', flash_message="✅ Password sent to your email.")
                else:
                    return render_template('signup.html', flash_message="⚠️ No account found. Please sign up first.")

    return render_template('forget.html')

# All route are link page with html file
@app.route('/menu')
def menu():
    return render_template('menu.html')

@app.route('/booking')
def booking():
    return render_template('booking.html')

@app.route('/order')
def order():
    return render_template('order.html')

@app.route('/delivery')
def delivery():
    return render_template('delivery.html')

@app.route('/room', methods=['GET', 'POST'])
def room_booking():
    if request.method == 'POST':
        # ✅ Check login session
        if 'user' not in session or 'email' not in session:
            return redirect(url_for('login', flash_message="⚠️ Please login first to book a room."))

        Customer_Name = request.form.get('Customer_Name')
        Email = request.form.get('Email')
        MO_Number = request.form.get('MO_Number')
        room_no = request.form.get('Room_No')
        Member = request.form.get('Member')
        entry_time = request.form.get('Entry_Time')
        exit_time = request.form.get('Exit_Time')

        try:
            Customer_Name = Customer_Name.strip()
            Email = Email.strip()
            MO_Number = MO_Number.strip()
            room_no = room_no.strip()
            Member = Member.strip()
            entry_time = entry_time.strip()
            exit_time = exit_time.strip()

            if not all([Customer_Name, Email, MO_Number, room_no, Member, entry_time, exit_time]):
                return render_template('room.html', flash_message="⚠️ All fields are required.")

            with sqlite3.connect('table.db') as conn:
                cursor = conn.cursor()

                # Check if user is registered
                cursor.execute('SELECT * FROM Login WHERE Customer_Name = ? AND Email = ? AND Mobile_No = ?', 
                               (Customer_Name, Email, MO_Number))
                if not cursor.fetchone():
                    return redirect(url_for('login', flash_message="⚠️ Please login first (you are not registered)."))

                # Convert time to datetime
                entry = datetime.strptime(entry_time, "%Y-%m-%dT%H:%M")
                exit = datetime.strptime(exit_time, "%Y-%m-%dT%H:%M")

                if exit <= entry or (exit - entry).total_seconds() < 3600:
                    return render_template('room.html', flash_message="⚠️ You must book the room for a minimum of 1 hour.")

                if entry < datetime.now():
                    return render_template('room.html', flash_message="⚠️ You cannot book a room in the past.")

                room = int(room_no)
                valid_ranges = list(range(101, 131)) + list(range(201, 231)) + list(range(301, 331)) + list(range(401, 441))
                if room not in valid_ranges:
                    return render_template('room.html', flash_message="⚠️ Room number must be between 101-130, 201-230, 301-330, 401-440")

                # Create table if not exists
                cursor.execute('''CREATE TABLE IF NOT EXISTS RoomBooking (
                    Customer_Name TEXT, Email TEXT, Mobile_No TEXT,
                    Room_No INTEGER, Member INTEGER, Entry_Time TEXT, Exit_Time TEXT);''')

                # Check if room is already booked (not yet exited)
                cursor.execute('''
                    SELECT * FROM RoomBooking 
                    WHERE Room_No = ? AND Exit_Time > ?
                ''', (room_no, entry_time))

                if cursor.fetchone():
                    return render_template('room.html', flash_message="⚠️ This room is already booked for the selected time.")

                # Book room
                cursor.execute("INSERT INTO RoomBooking VALUES (?, ?, ?, ?, ?, ?, ?)",
                               (Customer_Name, Email, MO_Number, room_no, Member, entry_time, exit_time))

            # Send confirmation email
            subject = "🛏️ Room Booking Confirmation"
            body = f"""👋 Hello {Customer_Name},

✅ Your room has been booked successfully!

🏨 Room No: {room_no}  
👥 Members: {Member}  
🕰️ From: {entry_time}  
⏳ To: {exit_time}
📞 Contact: {MO_Number}



Warm Regards,  
❤️ Team S.K.Hotels"""

            send_email_notification(Email, Customer_Name, subject, body)

            return render_template('Kathiyawad.html', flash_message="✅ Room booked successfully!")

        except Exception as e:
            return render_template('room.html', flash_message=f"⚠️ Error: {str(e)}")

    return render_template('room.html')  # GET method returns booking page



@app.route('/submit', methods=['POST'])

def submit():
    Customer_Name = request.form.get('Customer_Name')
    Email = request.form.get('Email')
    MO_Number = request.form.get('MO_Number')

    if 'user' not in session or 'email' not in session:
        return redirect(url_for('login', flash_message="⚠️ Please login first."))
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

✅ Your table has been booked at **S.K.Hotel Group**!


🪑 Table No: {Table_No}  
👥 Members: {Member}  
📆 Date & Time: {Date_Time}



Warm Regards,
❤️ Team S.K.Hotels"""
                        send_email_notification(Email, Customer_Name, subject, body, attach_pdf=True,attach_pdf1=True)
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



Warm Regards,
❤️ Team S.K.Hotels"""
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



Warm Regards,
❤️ Team S.K.Hotels"""
                        send_email_notification(Email, Customer_Name, subject, body)
                    return render_template('Kathiyawad.html',flash_message="✅ Your delivery order is confirmed.")

    
    except sqlite3.OperationalError as e: # if database is not created
        
        return render_template('Kathiyawad.html', flash_message=f"⚠️ Database Error Read: {str(e)}")

    return render_template(flash_message="⚠️ Invalid submission. Please try again.")


if __name__ == '__main__':
    app.run(debug=True)
