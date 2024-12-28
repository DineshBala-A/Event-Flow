Event Flow

Event Flow is a comprehensive event booking application designed to simplify the process of scheduling and managing events. This application is ideal for event organizers and participants, offering an intuitive interface, robust features, and seamless communication.

Features

Event Creation and Management: Easily create and manage events with detailed descriptions, dates, and times.

User Notifications: Notify users about events, updates, or cancellations via email.

Appointment Scheduling: Set and manage appointments effortlessly.

Responsive Design: Fully responsive UI for an optimal experience on desktop and mobile devices.

User-Friendly Interface: Simple and intuitive design for hassle-free navigation.

Installation

Clone the Repository:

git clone <repository-url>
cd event-flow

Set Up Virtual Environment:

python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

Install Dependencies:

pip install -r requirements.txt

Set Up Environment Variables:
Create a .env file and add the following variables:

SMTP_USER=<your-smtp-email>
SMTP_PASSWORD=<your-smtp-password>

Run the Application:

flask run

Access the application at http://localhost:5000.
