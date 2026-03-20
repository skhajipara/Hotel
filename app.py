from flask import Flask, render_template, request, redirect, session
import sqlite3
import smtplib
from email.message import EmailMessage
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv
from functools import wraps
import os

load_dotenv()
# Note: Ensure your .env file has valid credentials (use an App Password for Gmail!)

app = Flask(__name__, template_folder='templates')

# Session config
app.secret_key = 'your_secret_key_here' 
app.permanent_session_lifetime = timedelta(hours=24)

# For pdf location
pdf_location = Path("Gujarati menu.pdf")
pdf_location1= Path("English menu.pdf")


# ==========================================
# LUXURY CURVED HTML EMAIL TEMPLATE
# ==========================================
def get_html_email_template(title, content):
    """Wraps the email content in an elegant, seamlessly curved HTML design."""
    return f"""
    <!DOCTYPE html>
    <html>
      <head>
        <meta charset="utf-8">
      </head>
      <body style="font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; background-color: #F3F1EC; padding: 40px 10px; margin: 0;">
        
        <table align="center" border="0" cellpadding="0" cellspacing="0" width="100%" style="max-width: 600px; background-color: #ffffff; border-radius: 24px; box-shadow: 0 10px 30px rgba(0,0,0,0.08); overflow: hidden;">
          
          <tr>
            <td style="background-color: #192024; padding: 45px 20px; text-align: center;">
              <h1 style="color: #ffffff; margin: 0; font-size: 32px; letter-spacing: 1px; font-family: 'Georgia', serif;">S.K. Hotels</h1>
              <div style="margin: 15px auto 0; width: 50px; height: 3px; background-color: #095B19;"></div>
            </td>
          </tr>
          
          <tr>
            <td style="padding: 45px 35px; color: #444444; font-size: 16px; line-height: 1.8;">
              <h2 style="color: #095B19; margin-top: 0; font-size: 24px; text-align: center; font-family: 'Georgia', serif; margin-bottom: 25px;">
                {title}
              </h2>
              {content}
            </td>
          </tr>
          
          <tr>
            <td style="background-color: #fcfbf9; padding: 35px 30px; text-align: center; border-top: 1px solid #eeeeee;">
              <p style="margin: 0; font-size: 15px; color: #666666;">Warm Regards,</p>
              <p style="margin: 5px 0 20px 0; font-size: 18px; font-weight: bold; color: #095B19;">Team S.K. Hotels 🙏</p>
              
              <p style="margin: 0; font-size: 11px; color: #999999; line-height: 1.5;">You are receiving this email because of your recent activity with S.K. Hotels Group.</p>
              <p style="margin: 5px 0 0 0; font-size: 11px; color: #999999;">📍 S.K. Hotels Group, Kathiyawad, Gujarat, India</p>
            </td>
          </tr>
          
        </table>
      </body>
    </html>
    """

# ==========================================
# EMAIL SENDER FUNCTION (ANTI-SPAM FIXED)
# ==========================================
def send_email_notification(to_email, customer_name, subject, body_text, body_html=None, attach_pdf=False, attach_pdf1=False):
    sender_email = os.getenv("EMAIL_USER") 
    sender_password = os.getenv("EMAIL_PASS")

    if not sender_email or not sender_password:
        print("❌ CRITICAL ERROR: Email credentials not found in .env file!")
        return

    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = f"S.K. Hotels <{sender_email}>"
    msg['To'] = to_email
    msg['Reply-To'] = sender_email 
    
    # STRICT SPAM FIX: The plain text MUST have the exact same footer as the HTML version
    text_footer = "\n\nWarm Regards,\nTeam S.K. Hotels\n\n----------------------------------------\nYou are receiving this email because of your recent activity with S.K. Hotels Group.\nS.K. Hotels Group, Kathiyawad, Gujarat, India"
    msg.set_content(body_text + text_footer)
    
    if body_html:
        msg.add_alternative(body_html, subtype='html')

    if attach_pdf and pdf_location.exists():
        with open(pdf_location, 'rb') as f:
            msg.add_attachment(f.read(), maintype='application', subtype='pdf', filename="S.K.Hotels_Gujarati_Menu.pdf")

    if attach_pdf1 and pdf_location1.exists():
        with open(pdf_location1, 'rb') as f:
            msg.add_attachment(f.read(), maintype='application', subtype='pdf', filename="S.K.Hotels_English_Menu.pdf")

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(sender_email, sender_password)
            smtp.send_message(msg)
            print(f"✅ Email successfully sent to {to_email}")
    except Exception as e:
        print(f"❌ Email failed to send to {to_email}. Error: {e}")


# Login mandatory Decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session or 'email' not in session:
            return render_template('login.html', flash_message="⚠️ Please login first.")
        return f(*args, **kwargs)
    return decorated_function


# ==========================================
# AUTHENTICATION ROUTES
# ==========================================
@app.route('/')
def home():
    return render_template('Kathiyawad.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        Email = request.form.get('Email')
        Password = request.form.get('Password')
        
        if Email and Password:
            with sqlite3.connect('table.db') as conn:
                cursor = conn.cursor()
                cursor.execute('''CREATE TABLE IF NOT EXISTS Login (
                    Customer_Name TEXT NOT NULL,
                    Email TEXT NOT NULL,
                    Mobile_No INTEGER NOT NULL,
                    Password TEXT NOT NULL);''')
                cursor.execute("SELECT Customer_Name, Password FROM Login WHERE Email = ?", (Email,))
                result = cursor.fetchone()

            if result:
                customer_name, stored_password = result
                if stored_password == Password:
                    session.permanent = True
                    session['user'] = customer_name
                    session['email'] = Email

                    time_now = datetime.now().strftime('%d %b %Y, %I:%M %p')

                    subject = "S.K. Hotels - Login Notification"
                    title = "🔐 New Login Detected"
                    body_text = f"Hello {customer_name},\n\nYou have successfully logged in to your account at S.K. Hotels Group.\n\nPlease enjoy our services:\n- Explore the Menu\n- Place Your Order\n- Book a Table\n- Get Food Delivered\n- Book a Room\n\nLogin Time: {time_now}"
                    
                    html_content = f"""
                    <p>Hello <strong>{customer_name}</strong>,</p>
                    <p>You have successfully logged in to your account at S.K. Hotels Group.</p>
                    <p>We are ready to serve you. Please explore our services:</p>
                    <div style="background-color: #f8f9fa; border-radius: 25px; padding: 25px 30px; margin: 20px 0;">
                        <ul style="list-style-type: none; padding-left: 0; font-size: 15px; margin: 0;">
                            <li style="margin-bottom: 12px;">🍽️ Explore the Menu</li>
                            <li style="margin-bottom: 12px;">🛒 Place Your Order</li>
                            <li style="margin-bottom: 12px;">🪑 Book a Table</li>
                            <li style="margin-bottom: 12px;">🚚 Get Food Delivered</li>
                            <li style="margin-bottom: 0;">🛏️ Book a Room</li>
                        </ul>
                    </div>
                    <p style="color: #888; font-size: 13px; text-align: center;">🕰️ <strong>Login Time:</strong> {time_now}</p>
                    """
                    
                    body_html = get_html_email_template(title, html_content)
                    send_email_notification(Email, customer_name, subject, body_text, body_html=body_html, attach_pdf=True, attach_pdf1=True)
                    
                    return render_template('Kathiyawad.html', flash_message="✅ Login successful!")
                else:
                    return render_template('login.html', flash_message="❌ Incorrect email or password. Please try again.")
            else:
                return render_template('signup.html', flash_message="⚠️ You don't have an account. Please sign up first.")

    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        Customer_Name = request.form.get('Customer_Name')
        Email = request.form.get('Email')
        Mobile_No = request.form.get('Mobile_No')
        Password = request.form.get('Password')
        
        if Customer_Name and Email and Mobile_No and Password:
            with sqlite3.connect('table.db') as conn:
                cursor = conn.cursor()
                cursor.execute('''CREATE TABLE IF NOT EXISTS Login (
                    Customer_Name TEXT NOT NULL,
                    Email TEXT NOT NULL,
                    Mobile_No INTEGER NOT NULL,
                    Password TEXT NOT NULL);''')
                
                cursor.execute('SELECT * FROM Login WHERE Email = ?', (Email,))
                if cursor.fetchone():
                    return render_template('login.html', flash_message="⚠️ You already have an account. Please login.")

                cursor.execute('''INSERT INTO Login (Customer_Name, Email, Mobile_No, Password)
                                  VALUES (?, ?, ?, ?)''', (Customer_Name, Email, Mobile_No, Password))

            subject = "Account Created Successfully - S.K. Hotels"
            title = "🎉 Welcome to S.K. Hotels!"
            body_text = f"Hello {Customer_Name},\n\nWelcome to the family! Your account has been successfully created.\n\nYou can now seamlessly access all of our luxury services to book tables, reserve rooms, and order food straight to your door."
            
            html_content = f"""
            <p>Hello <strong>{Customer_Name}</strong>,</p>
            <p>Welcome to the family! ✅ Your account has been successfully created.</p>
            <p>You can now seamlessly access all of our luxury services:</p>
            <div style="background-color: #f8f9fa; border-radius: 25px; padding: 25px 30px; margin: 20px 0;">
                <ul style="list-style-type: none; padding-left: 0; font-size: 15px; margin: 0;">
                    <li style="margin-bottom: 12px;">🪑 Book a dining table</li>
                    <li style="margin-bottom: 12px;">🛏️ Reserve luxury rooms</li>
                    <li style="margin-bottom: 0;">🚚 Order fresh food to your door</li>
                </ul>
            </div>
            <div style="text-align: center; margin-top: 35px; margin-bottom: 10px;">
                <a href="https://yourwebsite.com" style="background-color: #095B19; color: #ffffff; text-decoration: none; padding: 16px 35px; border-radius: 40px; font-weight: bold; font-size: 16px; display: inline-block; box-shadow: 0 4px 10px rgba(9,91,25,0.3);">Explore Now</a>
            </div>
            """
            
            body_html = get_html_email_template(title, html_content)
            send_email_notification(Email, Customer_Name, subject, body_text, body_html=body_html)
            
            return render_template('login.html', flash_message="✅ Account created successfully! Please log in.")

    return render_template('signup.html')

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
                    
                    subject = "Password Recovery - S.K. Hotels Group"
                    title = "🛡️ Password Recovery"
                    body_text = f"Hello {customer_name},\n\nWe received a request to recover your password.\n\nYour Password: {password}\n\nIf you did not request this, please contact us immediately."
                    
                    html_content = f"""
                    <p>Hello <strong>{customer_name}</strong>,</p>
                    <p>We received a request to recover your password. Your secure details are below:</p>
                    
                    <div style="background-color: #f8f9fa; padding: 30px; border-radius: 40px; text-align: center; margin: 30px 0; border: 2px solid #eeeeee;">
                        <p style="margin: 0; font-size: 14px; color: #666; text-transform: uppercase; letter-spacing: 1px;">🔑 Your Password</p>
                        <h3 style="margin: 10px 0 0 0; color: #095B19; letter-spacing: 4px; font-size: 28px;">{password}</h3>
                    </div>
                    
                    <p style="font-size: 13px; color: #888; text-align: center;">📞 If you did not request this password recovery, please contact our support desk immediately.</p>
                    """
                    
                    body_html = get_html_email_template(title, html_content)
                    send_email_notification(Email, customer_name, subject, body_text, body_html=body_html)
                    
                    return render_template('login.html', flash_message="✅ Password sent to your email.")
                else:
                    return render_template('signup.html', flash_message="⚠️ No account found. Please sign up first.")

    return render_template('forget.html')

# ==========================================
# SERVICE ROUTES
# ==========================================
@app.route('/menu')
def menu():
    return render_template('menu.html')

@app.route('/booking')
@login_required
def booking():
    return render_template('booking.html')

@app.route('/order')
@login_required
def order():
    return render_template('order.html')

@app.route('/delivery')
@login_required
def delivery():
    return render_template('delivery.html')


# ==========================================
# THE FIX: ROOM BOOKING ROUTE
# ==========================================
@app.route('/room', methods=['GET', 'POST'])
@login_required
def room_booking():
    if request.method == 'POST':
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

                cursor.execute('SELECT * FROM Login WHERE Customer_Name = ? AND Email = ? AND Mobile_No = ?', 
                               (Customer_Name, Email, MO_Number))
                if not cursor.fetchone():
                   return render_template('login.html', flash_message="⚠️ Please login first (you are not registered).")

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

                cursor.execute('''CREATE TABLE IF NOT EXISTS RoomBooking (
                    Customer_Name TEXT, Email TEXT, Mobile_No TEXT,
                    Room_No INTEGER, Member INTEGER, Entry_Time TEXT, Exit_Time TEXT);''')

                cursor.execute('''SELECT * FROM RoomBooking WHERE Room_No = ? AND Exit_Time > ?''', (room_no, entry_time))
                if cursor.fetchone():
                    return render_template('room.html', flash_message="⚠️ This room is already booked for the selected time.")

                cursor.execute("INSERT INTO RoomBooking VALUES (?, ?, ?, ?, ?, ?, ?)",
                               (Customer_Name, Email, MO_Number, room_no, Member, entry_time, exit_time))

            # FIX: Format dates beautifully to prevent Spam Filters flagging raw "T" formats
            formatted_entry = entry.strftime("%d %b %Y, %I:%M %p")
            formatted_exit = exit.strftime("%d %b %Y, %I:%M %p")

            # --- HTML EMAIL SETUP ---
            subject = "Room Booking Confirmation - S.K. Hotels"
            title = "🛏️ Room Booking Confirmed"
            body_text = f"Hello {Customer_Name},\n\nYour stay has been successfully reserved. We can't wait to host you!\n\nRoom No: {room_no}\nGuests: {Member}\nCheck-in: {formatted_entry}\nCheck-out: {formatted_exit}\n\nIf you need any assistance prior to your arrival, feel free to contact the front desk."
            
            html_content = f"""
            <p>Hello <strong>{Customer_Name}</strong>,</p>
            <p>✅ Your stay has been successfully reserved. We can't wait to host you!</p>
            
            <table cellpadding="15" cellspacing="0" width="100%" style="border-radius: 25px; overflow: hidden; margin-top: 25px; background-color: #f8f9fa;">
                <tr>
                    <td style="border-bottom: 2px solid #ffffff; width: 40%;"><strong>🏨 Room No:</strong></td>
                    <td style="border-bottom: 2px solid #ffffff; color: #095B19; font-weight: bold;">{room_no}</td>
                </tr>
                <tr>
                    <td style="border-bottom: 2px solid #ffffff;"><strong>👥 Guests:</strong></td>
                    <td style="border-bottom: 2px solid #ffffff;">{Member}</td>
                </tr>
                <tr>
                    <td style="border-bottom: 2px solid #ffffff;"><strong>🕰️ Check-in:</strong></td>
                    <td style="border-bottom: 2px solid #ffffff;">{formatted_entry}</td>
                </tr>
                <tr>
                    <td><strong>⏳ Check-out:</strong></td>
                    <td>{formatted_exit}</td>
                </tr>
            </table>
            <p style="margin-top: 25px; text-align: center;">📞 If you need any assistance prior to your arrival, feel free to contact the front desk.</p>
            """
            
            body_html = get_html_email_template(title, html_content)
            send_email_notification(Email, Customer_Name, subject, body_text, body_html=body_html)
            
            return render_template('Kathiyawad.html', flash_message="✅ Room booked successfully!")

        except Exception as e:
            return render_template('room.html', flash_message=f"⚠️ Error: {str(e)}")

    return render_template('room.html')


@app.route('/submit', methods=['POST'])
@login_required
def submit():
    Customer_Name = request.form.get('Customer_Name')
    Email = request.form.get('Email')
    MO_Number = request.form.get('MO_Number')

    try:
        with sqlite3.connect('table.db', timeout=10) as conn:
            cursor = conn.cursor()

            # --- TABLE BOOKING ---
            if Email and MO_Number and request.form.get('Table_No') and request.form.get('Date_Time'):
                Table_No = request.form.get('Table_No')
                Member = request.form.get('Member')
                Date_Time = request.form.get('Date_Time')

                cursor.execute('SELECT * FROM Login WHERE Customer_Name = ? AND Email = ? AND Mobile_No = ?', 
                               (Customer_Name, Email, MO_Number))
                if not cursor.fetchone():
                    return render_template('login.html', flash_message="⚠️ Please login first (you are not registered).")

                try:
                    booking_time = datetime.strptime(Date_Time, '%Y-%m-%dT%H:%M')
                    if booking_time < datetime.now():
                        return render_template('booking.html', flash_message="⚠️ You cannot book a table in the past. Please choose a future time.")
                except ValueError:
                     return render_template('booking.html', flash_message="⚠️ Invalid date/time format. Please select a valid date.")
    
                cursor.execute('''CREATE TABLE IF NOT EXISTS Booking (
                    Customer_Name TEXT, Email TEXT, MO_Number INTEGER,
                    Table_No INTEGER, Member INTEGER, Date_Time TEXT);''')
                
                cursor.execute("SELECT * FROM Booking WHERE Table_No = ? AND Date_Time = ?", (Table_No, Date_Time))
                if cursor.fetchone():
                    return render_template('booking.html', flash_message="⚠️ Table already booked at that time.")
                else:
                    cursor.execute('INSERT INTO Booking VALUES (?, ?, ?, ?, ?, ?)', 
                                   (Customer_Name, Email, MO_Number, Table_No, Member, Date_Time))

                    # FIX: Format date
                    formatted_date = booking_time.strftime("%d %b %Y, %I:%M %p")

                    subject = "Table Booking Confirmation - S.K. Hotels"
                    title = "🪑 Table Reservation Confirmed"
                    body_text = f"Hello {Customer_Name},\n\nYour dining experience at S.K. Hotels is confirmed!\n\nTable No: {Table_No}\nGuests: {Member}\nDate & Time: {formatted_date}\n\nFor your convenience, we have attached our menus to this email."
                    
                    html_content = f"""
                    <p>Hello <strong>{Customer_Name}</strong>,</p>
                    <p>✅ Your dining experience at S.K. Hotels has been confirmed!</p>
                    
                    <table cellpadding="15" cellspacing="0" width="100%" style="border-radius: 25px; overflow: hidden; margin-top: 25px; background-color: #f8f9fa;">
                        <tr>
                            <td style="border-bottom: 2px solid #ffffff; width: 40%;"><strong>🪑 Table No:</strong></td>
                            <td style="border-bottom: 2px solid #ffffff; color: #095B19; font-weight: bold;">{Table_No}</td>
                        </tr>
                        <tr>
                            <td style="border-bottom: 2px solid #ffffff;"><strong>👥 Guests:</strong></td>
                            <td style="border-bottom: 2px solid #ffffff;">{Member}</td>
                        </tr>
                        <tr>
                            <td><strong>📆 Date & Time:</strong></td>
                            <td>{formatted_date}</td>
                        </tr>
                    </table>
                    
                    <div style="margin-top: 30px; text-align: center;">
                        <p style="background-color: #095B19; color: #ffffff; display: inline-block; padding: 10px 20px; border-radius: 20px; font-size: 13px;">
                            🍽️ We have attached our luxurious menus to this email.
                        </p>
                    </div>
                    """
                    body_html = get_html_email_template(title, html_content)
                    
                    send_email_notification(Email, Customer_Name, subject, body_text, body_html=body_html, attach_pdf=True, attach_pdf1=True)

                    return render_template('Kathiyawad.html', flash_message="✅ Booking successful!")

            # --- ORDER FOOD ---
            elif request.form.get('Table_No') and request.form.get('Order'):
                Table_No = request.form.get('Table_No')
                Order = request.form.get('Order')

                cursor.execute('SELECT * FROM Login WHERE Customer_Name = ?', (Customer_Name,))
                if not cursor.fetchone():
                    return render_template('login.html', flash_message="⚠️ Please login first.")

                cursor.execute('''CREATE TABLE IF NOT EXISTS Orders_Details (
                    Customer_Name TEXT,Email TEXT NOT NULL, Table_No INTEGER, "Order" TEXT);''')
                
                cursor.execute('SELECT * FROM Orders_Details WHERE Table_No = ? AND "Order" = ?', (Table_No, Order))
                if cursor.fetchone():
                    return render_template('order.html', flash_message="⚠️ You gave this order already!")
                else:
                    cursor.execute('INSERT INTO Orders_Details VALUES (?, ?, ?, ?)', (Customer_Name, Email, Table_No, Order))

                    subject = "Order Confirmation - S.K. Hotels"
                    title = "👨‍🍳 Kitchen Received Your Order"
                    body_text = f"Hello {Customer_Name},\n\nYour order has been placed and is currently being prepared by our chefs!\n\nTable: {Table_No}\nOrder: {Order}\n\nPlease wait a while, your food will arrive shortly!"
                    
                    html_content = f"""
                    <p>Hello <strong>{Customer_Name}</strong>,</p>
                    <p>✅ Your order has been placed and is currently being prepared by our expert chefs!</p>
                    
                    <div style="background-color: #f8f9fa; padding: 25px 30px; border-radius: 25px; margin: 25px 0;">
                        <p style="margin: 0 0 15px 0; font-size: 15px;"><strong>🪑 Table Number:</strong> <span style="color: #095B19; font-weight: bold;">{Table_No}</span></p>
                        <p style="margin: 0; font-size: 15px; line-height: 1.6; border-top: 1px dashed #ccc; padding-top: 15px;"><strong>📝 Your Order:</strong><br>{Order}</p>
                    </div>
                    
                    <p style="text-align: center;">⏳ Please wait a short while, your hot food will arrive at your table shortly!</p>
                    """
                    body_html = get_html_email_template(title, html_content)
                    send_email_notification(Email, Customer_Name, subject, body_text, body_html=body_html)
                    
                    return render_template('Kathiyawad.html', flash_message="✅ Your order has been placed successfully.")
    
            # --- HOME DELIVERY ---
            elif request.form.get('Address'):
                Mobile_Number = request.form.get('Mobile_Number')
                Order = request.form.get('Order')
                Address = request.form.get('Address')

                cursor.execute('SELECT * FROM Login WHERE Customer_Name = ? AND Mobile_No = ?', (Customer_Name, Mobile_Number))
                if not cursor.fetchone():
                    return render_template('login.html', flash_message="⚠️ Please login first (you are not registered).")

                cursor.execute('''CREATE TABLE IF NOT EXISTS Delivery (
                    Customer_Name TEXT, Mobile_Number INTEGER, "Order" TEXT, Address TEXT);''')
                
                cursor.execute('SELECT * FROM Delivery WHERE Mobile_Number = ? AND "Order" = ?', (Mobile_Number, Order))
                if cursor.fetchone():
                    return render_template('order.html', flash_message="⚠️ You gave this order already!")
                else:
                    cursor.execute('INSERT INTO Delivery VALUES (?, ?, ?, ?)', (Customer_Name, Mobile_Number, Order, Address))

                    subject = "Delivery Order Confirmation - S.K. Hotels"
                    title = "🚚 Your Delivery is Confirmed"
                    body_text = f"Hello {Customer_Name},\n\nYour delivery order is in the kitchen and will be dispatched soon.\n\nItems: {Order}\nDestination: {Address}\n\nOur delivery partner will contact you at {Mobile_Number} if needed."
                    
                    html_content = f"""
                    <p>Hello <strong>{Customer_Name}</strong>,</p>
                    <p>✅ Your delivery order is currently in the kitchen and will be dispatched to you very soon.</p>
                    
                    <div style="background-color: #f8f9fa; padding: 25px 30px; border-radius: 30px; margin: 25px 0;">
                        <p style="margin: 0 0 15px 0; font-size: 15px; line-height: 1.6; border-bottom: 1px dashed #ccc; padding-bottom: 15px;"><strong>📦 Items Ordered:</strong><br>{Order}</p>
                        <p style="margin: 0; font-size: 15px; line-height: 1.6;"><strong>📍 Delivery Destination:</strong><br>{Address}</p>
                    </div>
                    
                    <p style="text-align: center;">📞 Our delivery partner will contact you at <strong>{Mobile_Number}</strong> upon arrival.</p>
                    """
                    body_html = get_html_email_template(title, html_content)
                    send_email_notification(Email, Customer_Name, subject, body_text, body_html=body_html)
                    
                    return render_template('Kathiyawad.html', flash_message="✅ Your delivery order is confirmed.")

    except sqlite3.OperationalError as e:
        return render_template('Kathiyawad.html', flash_message=f"⚠️ Database Error: {str(e)}")

    return render_template('Kathiyawad.html', flash_message="⚠️ Invalid submission. Please fill all fields.")


if __name__ == '__main__':
    app.run(debug=True)