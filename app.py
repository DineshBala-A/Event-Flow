import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import Flask, request, render_template, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
from flask_cors import CORS
import os

# Load environment variables from .env file
load_dotenv()

# Initialize the Flask application
app = Flask(__name__)

CORS(app)

app.secret_key = os.getenv("SECRET_KEY", "your_default_secret_key")  # Use environment variable for better security

# Path to the JSON database
USER_DB = "users.json"
DATA_FILE = 'data.json'
BOOKING_DB = "bookings.json"

# SMTP credentials loaded from environment variables
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = os.getenv("SMTP_USER")  # Load SMTP_USER from .env
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")  # Load SMTP_PASSWORD from .env

# Load users from the JSON file
def load_users():
    try:
        with open(USER_DB, "r") as file:
            users = json.load(file)
    except FileNotFoundError:
        users = []

    # Check if the admin user exists; if not, create the admin user with password '1234'
    if not any(u["username"] == "admin" for u in users):
        # Hash password '1234' for admin user
        admin_password = generate_password_hash("1234")
        users.append({"username": "admin", "password": admin_password, "email": "admin@example.com", "role": "admin"})
        save_users(users)

    return users

def load_bookings():
    try:
        with open(BOOKING_DB, "r") as file:
            bookings = json.load(file)
    except FileNotFoundError:
        bookings = []

# Save users to the JSON file
def save_users(users):
    with open(USER_DB, "w") as file:
        json.dump(users, file, indent=4)

# Function to send the email
def send_email_immediately(to_email, subject, date, time_input):
    # Create the email content
    email_content = f"""
    Dear Recipient,

    We hope you are doing well. This is a notification from **Event Flow**, your go-to platform for managing event bookings.

    We are looking to schedule an appointment with you regarding your recent event inquiry. The proposed appointment is set for **{date}** at **{time_input}**. Kindly confirm if this time works for you, or feel free to suggest an alternative.

    Thank you for using **Event Flow**. We look forward to your confirmation and to assisting you with your event needs.

    Best regards,
    The **Event Flow** Team
    """

    # Set up the MIME
    msg = MIMEMultipart()
    msg['From'] = SMTP_USER
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(email_content, 'plain'))

    # Send the email using SMTP server
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()  # Secure the connection
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(SMTP_USER, to_email, msg.as_string())
    except Exception as e:
        raise Exception(f"Failed to send email: {e}")

# Route for sending email
@app.route('/send-email', methods=['POST'])
def send_email():
    """Handle sending an email immediately with time and description."""
    if request.method == 'POST':
        # Capture the form data
        to_email = request.json.get('to_email')
        subject = "Appointment Confirmation Request from Event Flow"  # Predefined subject
        date = request.json.get('date')
        time_input = request.json.get('time')

        # Simply send the email immediately
        try:
            send_email_immediately(to_email, subject, date, time_input)
            return jsonify({
                "message": f"Email sent successfully to {to_email}!",
                "status_code": 200
            }), 200
        except Exception as e:
            return jsonify({
                "message": f"Failed to send email: {str(e)}",
                "status_code": 500
            }), 500
# # Function to send the email
# def send_email_immediately(to_email, subject, description, date, time_input):
#     """Function to send an email with the given details."""
#     try:
#         # Create email content
#         email_body = f"""
#         Subject: {subject}
        
#         Description: {description}
        
#         Date: {date}
        
#         Time: {time_input}
#         """
        
#         msg = MIMEText(email_body)
#         msg['Subject'] = "Scheduled Email"
#         msg['From'] = SMTP_USER
#         msg['To'] = to_email

#         # Send email via SMTP server
#         with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
#             server.starttls()  # Secure the connection
#             server.login(SMTP_USER, SMTP_PASSWORD)
#             server.sendmail(SMTP_USER, to_email, msg.as_string())

#         return f"Email sent successfully to {to_email}!"

#     except Exception as e:
#         return f"Failed to send email: {str(e)}"

# Route for the home page (index). This will be the first page users see.
@app.route('/')
def home():
    """Render the home page."""
    return render_template('home.html')

# Route for login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handle login."""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Load users from JSON
        users = load_users()

        # Login logic
        user = next((u for u in users if u["username"] == username), None)
        if user and check_password_hash(user["password"], password):
            session['user'] = username
            session['role'] = user.get('role', 'user')  # Default role is 'user'
            session['email'] = user.get('email')
            flash("Login successful!", "success")
            if session['role'] == 'admin':
                return redirect(url_for('admin'))
            return redirect(url_for('index'))
        else:
            flash("Invalid username or password.", "danger")

    return render_template('login.html')

# Route for admin login page
@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    """Handle admin login."""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Load users from JSON
        users = load_users()

        # Admin login logic
        user = next((u for u in users if u["username"] == username), None)
        if user and check_password_hash(user["password"], password) and user.get('role') == 'admin':
            session['user'] = username
            session['role'] = 'admin'
            session['email'] = user.get('email','')
            flash("Admin login successful!", "success")
            return redirect(url_for('admin'))
        else:
            flash("Invalid admin credentials or you are not an admin.", "danger")

    return render_template('admin_index.html')
    # return render_template('admin.html')

# Route for register page
@app.route('/register', methods=['GET', 'POST'])
def register():
    """Handle registration."""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')

        # Load users from JSON
        users = load_users()

        # Registration logic
        if any(u["username"] == username for u in users):
            flash("Username already exists. Please choose a different one.", "danger")
        else:
            hashed_password = generate_password_hash(password)
            users.append({"username": username, "password": hashed_password, "email": email, "role": "user"})
            save_users(users)
            flash("Registration successful! You can now log in.", "success")
            return redirect(url_for('login'))

    return render_template('register.html')

# Route for the home page (index) when logged in (only accessible when logged in)
@app.route('/index')
def index():
    """Render the home page (index). Only accessible when logged in."""
    if 'user' not in session:
        return redirect(url_for('login'))
    
    return render_template('index.html', user=session['user'])

# # Route for sending email
# @app.route('/send-email', methods=['GET', 'POST'])
# def send_email():
#     """Handle sending an email immediately with time and description."""
#     message = None

#     if request.method == 'POST':
#         # Capture the form data
#         to_email = request.form.get('to_email')
#         subject = request.form.get('subject')
#         description = request.form.get('description')
#         date = request.form.get('date')
#         time_input = request.form.get('time')

#         # Simply send the email immediately
#         try:
#             send_email_immediately(to_email, subject, description, date, time_input)
#             message = f"Email sent successfully to {to_email}!"
#         except Exception as e:
#             message = f"Failed to send email: {str(e)}"

#     return render_template('send_email.html', message=message)

# Route for logout
@app.route('/logout')
def logout():
    """Logout the user and clear the session."""
    session.pop('user', None)
    session.pop('role', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

# Route for admin dashboard
@app.route('/admin', methods=['GET', 'POST'])
def admin_dashboard():
    """Admin dashboard, accessible only by admins."""
    if 'user' not in session or session.get('role') != 'admin':
        flash("Access denied. Admins only.", "danger")
        return redirect(url_for('login'))
    
    users = load_users()

    if request.method == 'POST':  
        # Admin actions: delete, promote, or add user
        action = request.form.get('action')
        username = request.form.get('username')

        if action == "delete":
            # Remove user from the database
            users = [user for user in users if user["username"] != username]
            save_users(users)
            flash(f"User '{username}' has been deleted.", "success")

        elif action == "promote":
            # Promote user to admin
            for user in users:
                if user["username"] == username:
                    user["role"] = "admin"
            save_users(users)
            flash(f"User '{username}' has been promoted to admin.", "success")

        elif action == "add":
            # Add a new user (admin only)
            new_username = request.form.get('new_username')
            new_password = request.form.get('new_password')
            new_email = request.form.get('new_email')

            # Check if the username already exists
            if any(u["username"] == new_username for u in users):
                flash("Username already exists. Please choose a different one.", "danger")
            else:
                hashed_password = generate_password_hash(new_password)
                users.append({"username": new_username, "password": hashed_password, "email": new_email, "role": "user"})
                save_users(users)
                flash(f"User '{new_username}' has been added.", "success")
    
    return render_template('admin.html', users=users)

def add_event_to_file(event_data, file_path='events.json'):
    try:
        # Read the existing data from the file
        try:
            with open(file_path, 'r') as file:
                data = json.load(file)
        except FileNotFoundError:
            # If file doesn't exist, initialize with an empty list
            data = []

        # Ensure the data in the file is a list
        if not isinstance(data, list):
            raise ValueError("The JSON file should contain an array.")
        # Calculate the index
        index = len(data)

        # Add the index to the event_data
        event_data['event_id'] = index+1  # Assuming event_data is a dictionary

        # Append the new event to the list
        data.append(event_data)

        # Write the updated data back to the file
        with open(file_path, 'w') as file:
            json.dump(data, file, indent=4)

        return {"message": "Event added successfully"}, 200

    except Exception as e:
        return {"message": f"An error occurred: {e}"}, 500

@app.route('/add_event', methods=['POST'])
def add_event():
    try:
        event_data = request.json  # Get the JSON data from the request
        if not event_data:
            return {"message": "No JSON data received."}, 400

        # Validate required fields
        required_fields = [
            "title", 
            "description",
              "image",
            #     "amountStandard",
            # "amountPremium", 
            # "amountDeluxe",
              "date", "time"
        ]
        missing_fields = [field for field in required_fields if field not in event_data]

        if missing_fields:
            return {"message": f"Missing required fields: {', '.join(missing_fields)}"}, 400

        # Add the event to the file
        response, status_code = add_event_to_file(event_data)
        return (response), status_code

    except Exception as e:
        return ({"message": f"An error occurred: {e}"}), 500


@app.route('/get_events', methods=['GET'])
def get_events():
    try:
        # Read the existing data from the file
        try:
            with open('events.json', 'r') as file:
                data = json.load(file)
        except FileNotFoundError:
            # If file doesn't exist, return an empty list
            return jsonify([])

        # Ensure the data in the file is a list
        if not isinstance(data, list):
            raise ValueError("The JSON file should contain an array.")

        return jsonify(data),200
    except Exception as e:
        return jsonify({"message": f"An error occurred: {e}"}), 500
    
def book_event_to_file(event_id, file_path='booking.json'):
    try:
        # Read the existing data from the file
        try:
            with open(file_path, 'r') as file:
                data = json.load(file)
        except FileNotFoundError:
            # If file doesn't exist, initialize with an empty list
            data = []

        # Ensure the data in the file is a list
        if not isinstance(data, list):
            raise ValueError("The JSON file should contain an array.")
        # Calculate the index
        index = len(data)

        booking_data = {"event_id": event_id, "booking_id": index+1, "user_email": session.get('email')}

        # Append the new event to the list
        data.append(booking_data)

        # Write the updated data back to the file
        with open(file_path, 'w') as file:
            json.dump(data, file, indent=4)

        return {"message": "Event added successfully"}, 200

    except Exception as e:
        return {"message": f"An error occurred: {e}"}, 500

@app.route('/book_event', methods=['POST'])
def book_event():
    event_id = request.json.get('event_id')
    print("session ",session.get('email'))
    response, status_code = book_event_to_file(event_id)
    return (response), status_code

def get_events_for_user(user_email, events_file='events.json', bookings_file='booking.json'):
    try:
        # Read events.json file
        with open(events_file, 'r') as events_file:
            events = json.load(events_file)

        # Read booking.json file
        with open(bookings_file, 'r') as bookings_file:
            bookings = json.load(bookings_file)

        # Filter the booking records for the given user_email
        user_bookings = [booking for booking in bookings if booking['user_email'] == user_email]

        # Extract event_ids from the user bookings
        user_event_ids = {booking['event_id'] for booking in user_bookings}

        # Filter the events.json data to get only the events corresponding to the user's bookings
        filtered_events = [event for event in events if event['event_id'] in user_event_ids]

        return filtered_events, 200  # Returning both events and status code

    except FileNotFoundError as e:
        return {"message": f"File not found: {e}"}, 404
    except json.JSONDecodeError:
        return {"message": "Error decoding JSON from one of the files."}, 400
    except Exception as e:
        return {"message": f"An error occurred: {e}"}, 500
    
@app.route('/get_user_events', methods=['GET'])
def get_user_events():
    user_email = session.get('email')
    if not user_email:
        return {"message": "User not logged in."}, 401

    events, status_code = get_events_for_user(user_email)  # This will now work properly
    return jsonify(events), status_code


def cancelRegistration(event_id, user_email, bookings_file='booking.json'):
    try:
        # Read the booking.json file
        with open(bookings_file, 'r') as file:
            bookings = json.load(file)

        print("Original Bookings:", bookings)

        # Filter the bookings, keeping those that don't match the specified event_id and user_email
        updated_bookings = []
        for booking in bookings:
            try:
                # Check if both event_id and user_email match the specified values
                if booking.get('event_id') and booking.get('user_email'):
                    if int(booking['event_id']) == int(event_id) and booking['user_email'] == user_email:
                        continue  # Skip this booking as it matches
                updated_bookings.append(booking)
            except (ValueError, TypeError) as e:
                print(f"Error with booking {booking}: {e}")
                updated_bookings.append(booking)

        print("Updated Bookings:", updated_bookings)

        # If no changes were made, return a message indicating no such booking was found
        if len(updated_bookings) == len(bookings):
            return {"message": "No matching booking found to cancel."}, 404

        # Write the updated list back to the file
        with open(bookings_file, 'w') as file:
            json.dump(updated_bookings, file, indent=4)

        return {"message": "Booking canceled successfully."}, 200

    except FileNotFoundError:
        return {"message": "File not found."}, 404
    except json.JSONDecodeError:
        return {"message": "Error decoding JSON."}, 400
    except Exception as e:
        return {"message": f"An error occurred: {e}"}, 500

@app.route('/cancel_registration', methods=['POST'])
def cancel_registration():
    event_id = request.json.get('event_id')
    print("session ",session.get('email'))
    response, status_code = cancelRegistration(event_id, session.get('email'))
    return (response), status_code

def fetch_all_user_events(events_file='events.json', bookings_file='booking.json', users_file='users.json'):
    try:
        # Read events.json file
        with open(events_file, 'r') as events_file:
            events = json.load(events_file)

        # Read booking.json file
        with open(bookings_file, 'r') as bookings_file:
            bookings = json.load(bookings_file)

        # Read user.json file to get user details
        with open(users_file, 'r') as users_file:
            users = json.load(users_file)

        # Initialize an empty list to hold the user events
        user_events = []

        # Iterate through all the users
        for user in users:
            # Get the user email for the current user
            user_email = user['email']

            # Find all bookings for the current user where user_email matches booking's user_email
            user_bookings = [booking for booking in bookings if booking['user_email'] == user_email]

            # Extract event_ids from the user's bookings
            user_event_ids = {booking['event_id'] for booking in user_bookings}

            # Filter the events to get only the events corresponding to the user's bookings
            filtered_events = [event for event in events if event['event_id'] in user_event_ids]

            # Merge the user data with the event data into a single object
            for event in filtered_events:
                user_event = user.copy()  # Create a copy of the user data to avoid modifying the original
                user_event.update(event)  # Merge the event data into the user data
                user_events.append(user_event)  # Add the combined data to the list
                # user_events.pop("password")
                # user_events.pop("role")
                # user_events.pop("image")



        return user_events, 200  # Return the grouped data and status code

    except FileNotFoundError as e:
        print(e)
        return {"message": f"File not found: {e}"}, 404
    except json.JSONDecodeError:
        return {"message": "Error decoding JSON from one of the files."}, 400
    except Exception as e:
        print(e)
        return {"message": f"An error occurred: {e}"}, 500

# The route handler function should now call the `fetch_all_user_events` function
@app.route('/get_all_user_events', methods=['GET'])
def get_all_user_events_handler():
    user_events, status_code = fetch_all_user_events()  # Call the function that fetches user events
    return jsonify(user_events), status_code

def add_notification_to_file(email, text, file_path='notifications.json'):
    try:
        # Read the existing data from the file
        try:
            with open(file_path, 'r') as file:
                data = json.load(file)
        except FileNotFoundError:
            # If file doesn't exist, initialize with an empty list
            data = []

        # Ensure the data in the file is a list
        if not isinstance(data, list):
            raise ValueError("The JSON file should contain an array.")
        # Calculate the index
        index = len(data)

        notification = {"user_email": email, "notification_id": index+1, "text": text}

        # Append the new event to the list
        data.append(notification)

        # Write the updated data back to the file
        with open(file_path, 'w') as file:
            json.dump(data, file, indent=4)

        return {"message": "Notification sent successfully"}, 200

    except Exception as e:
        return {"message": f"An error occurred: {e}"}, 500

@app.route('/add_notification', methods=['POST'])
def add_notification():
    email = request.json.get('email')
    text = request.json.get('text')
    print("session ",session.get('email'))
    response, status_code = add_notification_to_file(email, text)
    return (response), status_code



def get_user_notification_from_the_file(user_email, notification_file='notifications.json'):
    try:
        # Open the notifications file
        with open(notification_file, 'r') as file:
            notifications = json.load(file)

        # Filter the notifications for the given user_email
        user_notifications = [notification for notification in notifications if notification['user_email'] == user_email]

        return user_notifications, 200  # Return notifications and status code

    except FileNotFoundError as e:
        return {"message": f"File not found: {e}"}, 404
    except json.JSONDecodeError:
        return {"message": "Error decoding JSON from the notifications file."}, 400
    except Exception as e:
        return {"message": f"An error occurred: {e}"}, 500
    
@app.route('/get_user_notifications', methods=['GET'])
def get_user_notifications():
    user_email = session.get('email')

    notifications, status_code = get_user_notification_from_the_file(user_email)  # This will now work properly
    return jsonify(notifications), status_code

@app.route('/about')
def about():
    """Render the booking page."""
    return render_template('about.html')

@app.route('/event')
def event():
    """Render the booking page."""
    return render_template('event.html')

@app.route('/my_event')
def my_event():
    """Render the booking page."""
    return render_template('my_event.html')

@app.route('/contact')
def contact():
    """Render the booking page."""
    return render_template('contact.html')

@app.route('/booking')
def booking():
    """Render the booking page."""
    return render_template('booking.html')
@app.route('/viewbook')
def viewbooking():
    """Render the viewbooking page."""
    return render_template('viewbooking.html')
@app.route('/payment')
def payment():
    """Render the payment page."""
    return render_template('payment.html')

@app.route('/notifications')
def notifications():
    """Render the notifications page."""
    return render_template('notification.html')

@app.route('/admin_event')
def admin_event():
    """Render the notifications page."""
    return render_template('admin_event.html')

@app.route('/admin_index')
def admin_index():
    """Render the notifications page."""
    return render_template('admin_index.html')

@app.route('/add_event_admin')
def add_event_admin():
    """Render the notifications page."""
    return render_template('add_event_admin.html')

@app.route('/create_notification')
def create_notification():
    """Render the notifications page."""
    return render_template('create_notification.html')

@app.route('/generate_pwd')
def generate_pwd():
    return generate_password_hash(request.args.get('password'))

if __name__ == '__main__':
    app.run(debug=True)
