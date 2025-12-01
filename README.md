# Hostel/PG Management System

A comprehensive management system for hostels and paying guests (PG) built with Flask, HTML, CSS, and JavaScript. This system provides automated features for attendance tracking, food menu scheduling, complaint management, room allocation, fee tracking, and communication tools.

## Features

1. **Attendance Tracking**
   - Daily attendance marking for residents
   - Attendance reports and analytics

2. **Food Menu Scheduling**
   - Weekly/monthly menu planning
   - Dietary preference management

3. **Complaint Management**
   - Resident complaint submission
   - Status tracking and resolution

4. **Room Allocation**
   - Room assignment and management
   - Availability tracking

5. **Monthly Fee Tracking**
   - Automated fee calculation
   - Payment reminders and history

6. **Notice Board & Chat System**
   - Announcements and notifications
   - Inter-resident messaging

## Tech Stack

- **Backend**: Flask (Python)
- **Frontend**: HTML, CSS, JavaScript with Bootstrap
- **Database**: SQLite
- **Authentication**: Flask-Login

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd hostel
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**:
   ```bash
   python app.py
   ```

5. **Access the application**:
   Open your browser and go to `http://localhost:5000`

## Default Login Credentials

- **Username**: admin
- **Password**: admin123

## Project Structure

```
hostel/
│
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── README.md             # This file
│
├── templates/            # HTML templates
│   ├── base.html         # Base template
│   ├── login.html        # Login page
│   ├── dashboard.html    # Dashboard page
│   ├── residents.html    # Residents management
│   ├── resident_form.html # Resident form
│   ├── rooms.html        # Rooms management
│   ├── room_form.html    # Room form
│   ├── attendance.html   # Attendance management
│   ├── food_menu.html    # Food menu management
│   ├── complaints.html   # Complaints management
│   ├── fees.html         # Fees management
│   ├── notices.html      # Notices management
│   └── chats.html        # Chat system
│
├── static/               # Static files
│   ├── css/
│   │   └── style.css     # Custom styles
│   └── js/
│       └── script.js     # Custom JavaScript
│
└── hostel.db             # SQLite database (created automatically)
```

## Usage

1. **Login**: Use the default admin credentials to log in
2. **Dashboard**: View overall statistics and recent activities
3. **Residents**: Manage resident information and room assignments
4. **Rooms**: Manage room details and availability
5. **Attendance**: Track daily attendance of residents
6. **Food Menu**: Plan and manage weekly food menus
7. **Complaints**: Handle resident complaints and issues
8. **Fees**: Manage fee collection and payment status
9. **Notices**: Post announcements and important notices
10. **Chats**: Communicate with residents through the messaging system

## Customization

You can customize the application by modifying:
- Templates in the `templates/` directory
- Styles in `static/css/style.css`
- JavaScript functionality in `static/js/script.js`
- Backend logic in `app.py`

## Contributing

This project is designed as a portfolio piece for data science students. Feel free to fork and modify it for your own use.

## License

This project is open source and available under the MIT License.