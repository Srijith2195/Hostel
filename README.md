# 🏨 Hostel/PG Management System

A comprehensive management system for hostels and paying guests (PG) built with Flask, MongoDB, and modern web technologies. This system provides automated features for attendance tracking, food menu scheduling, complaint management, room allocation, fee tracking, and communication tools.

## 📌 Problem Statement

Traditional hostel and PG management systems are manual, inefficient, and lack real-time monitoring. Conventional systems struggle with:

- Manual attendance tracking and record keeping
- Inefficient room allocation and management
- Poor communication between residents and administration
- Lack of centralized fee and payment tracking
- Time-consuming complaint resolution processes
- Inadequate food menu planning and management

## 💡 Solution

This project provides an intelligent hostel management system that:

- Automates daily attendance tracking with detailed reports
- Streamlines room allocation and availability management
- Enables real-time communication through chat and notice systems
- Centralizes fee collection and payment processing
- Simplifies complaint submission and resolution workflow
- Provides comprehensive food menu planning and scheduling

## 🧠 Key Features

### � Attendance Management System
- Automated daily attendance marking for residents
- Real-time attendance analytics and reporting
- Monthly attendance summaries and patterns
- Export attendance data for record keeping
- Attendance alerts for absent residents

### 🏠 Room Allocation & Management
- Intelligent room assignment based on availability
- Room capacity and occupancy tracking
- Room-wise resident management
- Availability status updates in real-time
- Room amenities and facilities management

### 💳 Fee & Payment Management
- Automated monthly fee calculation and billing
- Multiple payment method support
- Payment reminders and due date alerts
- Digital receipt generation and history
- Financial analytics and revenue tracking

### 🍽️ Food Menu Planning System
- Weekly and monthly meal planning
- Dietary preference management
- Meal scheduling (Breakfast, Lunch, Dinner)
- Menu calendar with nutritional information
- Feedback collection for meal improvement

### 🗨️ Complaint Resolution System
- Digital complaint submission platform
- Complaint categorization and priority levels
- Real-time status tracking and updates
- Resolution workflow management
- Complaint analytics and pattern analysis

### 📱 Communication & Notice Board
- Real-time chat between admin and residents
- Digital notice board for announcements
- Broadcast messaging capabilities
- Message notifications and alerts
- Communication history tracking

### 🔐 User Management & Security
- Multi-role authentication (Admin, Resident)
- Secure login system with role-based access
- Profile management for residents
- Activity logs and audit trails
- Data privacy and security measures

## 🛠️ Tech Stack

### Frontend
- **HTML5 & CSS3**: Modern semantic markup and styling
- **Bootstrap**: Responsive UI framework
- **JavaScript**: Interactive frontend functionality
- **Jinja Templates**: Server-side templating engine

### Backend
- **Python 3.8+**: Core programming language
- **Flask 2.3.2**: Web framework for API and routing
- **Flask-Login**: User session management
- **Flask-WTF**: Form handling and validation
- **Flask-Bcrypt**: Password hashing and security

### Database
- **MongoDB**: NoSQL database for flexible data storage
- **PyMongo**: Python driver for MongoDB
- **GridFS**: File storage for documents and images

### Additional Libraries
- **QR Code Generation**: qrcode[pil] for resident IDs
- **Image Processing**: Pillow for image manipulation
- **Environment Management**: python-dotenv
- **Data Validation**: WTForms for form validation

### Development Tools
- **Git & GitHub**: Version control and collaboration
- **VS Code / PyCharm**: Integrated development environments
- **Postman**: API testing and documentation
- **Docker**: Containerization for deployment

## 📁 Project Structure

```
hostel_management/
│
├── app.py                     # Main Flask application (1567 lines)
├── requirements.txt           # Python dependencies
├── README.md                 # This documentation
│
├── config/                   # Configuration files
│   ├── __init__.py
│   ├── config.py            # Application configuration
│   └── database.py          # Database connection settings
│
├── models/                   # Data models and schemas
│   ├── __init__.py
│   ├── user.py              # User and resident models
│   ├── room.py              # Room management models
│   ├── attendance.py        # Attendance tracking models
│   ├── complaint.py         # Complaint management models
│   ├── fee.py               # Fee and payment models
│   └── food_menu.py         # Food menu models
│
├── routes/                   # Application routes
│   ├── __init__.py
│   ├── main.py              # Main routes and dashboard
│   ├── auth.py              # Authentication routes
│   ├── api.py               # API endpoints
│   ├── residents.py         # Resident management routes
│   ├── rooms.py             # Room management routes
│   ├── attendance.py        # Attendance tracking routes
│   ├── complaints.py        # Complaint management routes
│   ├── fees.py              # Fee management routes
│   ├── food_menu.py         # Food menu routes
│   ├── notices.py           # Notice board routes
│   └── chats.py             # Chat system routes
│
├── services/                 # Business logic services
│   ├── __init__.py
│   ├── auth_service.py      # Authentication and authorization
│   ├── attendance_service.py # Attendance tracking logic
│   ├── room_service.py      # Room allocation and management
│   ├── fee_service.py       # Fee calculation and billing
│   ├── complaint_service.py # Complaint resolution workflow
│   ├── notification.py      # Email and SMS notifications
│   └── report_service.py    # Analytics and reporting
│
├── utils/                    # Utility functions
│   ├── __init__.py
│   ├── validators.py        # Input validation helpers
│   ├── helpers.py           # General utility functions
│   ├── decorators.py        # Custom decorators
│   ├── constants.py         # Application constants
│   └── qr_generator.py      # QR code generation utilities
│
├── templates/                # HTML templates (20 files)
│   ├── base.html            # Base template with navigation
│   ├── login_options.html   # Login selection page
│   ├── admin_login.html     # Admin login page
│   ├── resident_login.html  # Resident login page
│   ├── dashboard.html       # Admin dashboard
│   ├── resident_dashboard.html # Resident dashboard
│   ├── residents.html       # Residents management
│   ├── resident_form.html   # Add/Edit resident form
│   ├── resident_profile.html # Resident profile view
│   ├── resident_select_room.html # Room selection for residents
│   ├── rooms.html           # Rooms management
│   ├── room_form.html       # Add/Edit room form
│   ├── attendance.html      # Attendance management
│   ├── food_menu.html       # Food menu management
│   ├── complaints.html      # Complaints management
│   ├── fees.html            # Fee management (admin)
│   ├── resident_fees.html   # Fee view for residents
│   ├── notices.html         # Notice board management
│   ├── chats.html           # Chat system
│   └── components/
│       ├── navbar.html
│       ├── sidebar.html
│       └── footer.html
│
├── static/                   # Static assets
│   ├── css/
│   │   ├── main.css         # Main stylesheet
│   │   ├── dashboard.css    # Dashboard styles
│   │   └── responsive.css   # Mobile responsive styles
│   ├── js/
│   │   ├── main.js          # Main JavaScript
│   │   ├── dashboard.js     # Dashboard functionality
│   │   ├── attendance.js    # Attendance tracking scripts
│   │   ├── chat.js          # Real-time chat functionality
│   │   └── validation.js    # Form validation
│   ├── images/
│   │   ├── logo.png
│   │   ├── icons/
│   │   └── backgrounds/
│   └── uploads/
│       ├── resident_photos/ # Resident profile photos
│       └── documents/       # Uploaded documents
│
├── tests/                    # Test suite
│   ├── __init__.py
│   ├── test_app.py          # Application tests
│   ├── test_models.py       # Model tests
│   ├── test_services.py     # Service tests
│   ├── test_api.py          # API endpoint tests
│   └── fixtures/            # Test data and fixtures
│
├── scripts/                  # Utility scripts
│   ├── debug_users.py       # Debug user data
│   ├── reset_data.py        # Reset all application data
│   ├── reset_residents.py   # Reset resident data only
│   ├── reset_users.py       # Reset user data only
│   ├── setup_db.py          # Database initialization
│   ├── seed_data.py         # Sample data generation
│   └── backup_db.py         # Database backup
│
├── instance/                 # Instance-specific files
│   └── (database files)     # MongoDB data stored here
│
├── __pycache__/             # Python cache files
├── .git/                    # Git version control
├── .qoder/                  # IDE configuration
│
└── docs/                    # Documentation
    ├── api_documentation.md
    ├── deployment_guide.md
    ├── user_manual.md
    └── development_guide.md
```

## 🚀 Installation & Setup

### Prerequisites
- Python 3.8 or higher
- MongoDB installed and running
- Git (for cloning)

### Step-by-Step Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-username/hostel-management-system.git
   cd hostel-management-system
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up MongoDB**:
   ```bash
   # Ensure MongoDB is running
   sudo systemctl start mongod
   # Or use Docker:
   docker run -d -p 27017:27017 --name mongodb mongo
   ```

5. **Initialize the database**:
   ```bash
   python scripts/setup_db.py
   python scripts/seed_data.py
   ```

6. **Run the application**:
   ```bash
   python app.py
   ```

7. **Access the application**:
   - Open your browser and go to `http://localhost:5000`
   - Choose between Admin and Resident login

## 🔐 Configuration

### Environment Variables
Create a `.env` file in the root directory:
```bash
# Database Configuration
MONGO_URI=mongodb://localhost:27017/hostel_management
MONGO_DB_NAME=hostel_management

# Application Configuration
SECRET_KEY=your-secret-key-here
DEBUG=True
FLASK_ENV=development

# Email Configuration (for notifications)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password

# File Upload Configuration
UPLOAD_FOLDER=static/uploads
MAX_CONTENT_LENGTH=16777216  # 16MB max file size

# QR Code Configuration
QR_CODE_FOLDER=static/uploads/qrcodes
QR_CODE_SIZE=200
```

## 📖 Usage Guide

### For Administrators

1. **Dashboard Overview**
   - View total residents, rooms, complaints, and revenue
   - Monitor recent activities and system statistics
   - Quick access to all management modules
   - Real-time occupancy and attendance metrics

2. **Resident Management**
   - Add new residents with complete details
   - Edit existing resident information
   - Assign rooms to residents
   - View resident profiles and history
   - Generate resident ID cards with QR codes

3. **Room Management**
   - Create new rooms with specifications
   - Update room details and availability
   - Monitor room occupancy rates
   - Filter rooms by type/status
   - Room maintenance scheduling

4. **Attendance Tracking**
   - Mark daily attendance for residents
   - View attendance patterns and reports
   - Generate monthly attendance summaries
   - Export attendance data for records
   - Attendance alerts for absent residents

5. **Food Menu Planning**
   - Create weekly/monthly meal plans
   - Set menus for breakfast, lunch, and dinner
   - Update menu items and schedules
   - View menu calendar and nutritional info
   - Collect meal feedback from residents

6. **Complaint Resolution**
   - Review submitted complaints
   - Update complaint status and resolution
   - Categorize complaints by type and priority
   - Track resolution time and patterns
   - Generate complaint analytics reports

7. **Fee Management**
   - Generate monthly fee bills
   - Track payment status and history
   - Send payment reminders
   - Generate financial reports
   - Manage fee structures and discounts

8. **Communication**
   - Post important notices and announcements
   - Chat with residents in real-time
   - Send broadcast messages
   - Manage notice board categories
   - Schedule automated notifications

### For Residents

1. **Personal Dashboard**
   - View personal information and room details
   - Check fee status and payment history
   - View recent notices and messages
   - Track personal attendance record
   - Quick access to common services

2. **Profile Management**
   - Update personal information
   - Change password and security settings
   - View room allocation details
   - Upload profile photo
   - Manage emergency contacts

3. **Fee Management**
   - View current and past fees
   - Check payment status and due dates
   - Download fee receipts
   - Make online payments
   - View payment history and statements

4. **Communication**
   - Submit complaints and issues
   - Chat with administrator
   - View notices and announcements
   - Send messages to other residents
   - Participate in community discussions

5. **Services**
   - Request room maintenance
   - Provide meal feedback
   - Book common facilities
   - View food menu and schedules
   - Check attendance records

## 🧪 Testing

### Run Test Suite
```bash
# Run all tests
python -m pytest tests/

# Run specific test file
python -m pytest tests/test_app.py

# Run with coverage
python -m pytest --cov=app tests/
```

### Performance Testing
```bash
# Run performance benchmarks
python scripts/performance_test.py

# Load testing with multiple concurrent requests
python scripts/load_test.py
```

### Debug Scripts
```bash
# Debug user data
python debug_users.py

# Reset application data (use with caution)
python reset_data.py

# Reset only resident data
python reset_residents.py

# Reset only user data
python reset_users.py
```

## 🚀 Deployment

### Docker Deployment
```bash
# Build and run with Docker Compose
docker-compose up --build

# Or build individually
docker build -t hostel-management .
docker run -p 5000:5000 hostel-management
```

### Production Deployment
1. Set up production MongoDB cluster
2. Configure environment variables
3. Set up reverse proxy (nginx)
4. Configure SSL certificates
5. Set up monitoring and logging
6. Configure backup strategies

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📊 API Documentation

### Key Endpoints

#### Authentication
- `POST /api/auth/login` - User login
- `POST /api/auth/logout` - User logout
- `POST /api/auth/register` - User registration

#### Resident Management
- `GET /api/residents` - List all residents
- `POST /api/residents` - Add new resident
- `PUT /api/residents/{id}` - Update resident details
- `DELETE /api/residents/{id}` - Remove resident

#### Room Management
- `GET /api/rooms` - List all rooms
- `POST /api/rooms` - Add new room
- `PUT /api/rooms/{id}` - Update room details
- `GET /api/rooms/available` - Get available rooms

#### Attendance
- `POST /api/attendance/mark` - Mark attendance
- `GET /api/attendance/report` - Get attendance reports
- `GET /api/attendance/{resident_id}` - Get resident attendance

#### Fee Management
- `POST /api/fees/generate` - Generate fee bills
- `GET /api/fees/pending` - Get pending fees
- `POST /api/fees/pay` - Process payment

#### Complaints
- `POST /api/complaints` - Submit complaint
- `GET /api/complaints` - List complaints
- `PUT /api/complaints/{id}/status` - Update complaint status

## 🔧 Troubleshooting

### Common Issues

1. **Database Connection Issues**
   - Verify MongoDB is running
   - Check connection string
   - Ensure proper authentication

2. **Authentication Problems**
   - Check secret key configuration
   - Verify user roles and permissions
   - Clear browser cookies and cache

3. **File Upload Issues**
   - Check upload folder permissions
   - Verify file size limits
   - Ensure proper file formats

4. **Email Notification Issues**
   - Verify SMTP configuration
   - Check email credentials
   - Ensure proper network connectivity

## 📊 Data Models

### User Collection
```javascript
{
  "_id": ObjectId,
  "username": String,
  "email": String,
  "password": String (hashed),
  "role": String ("admin" or "resident"),
  "created_at": Date,
  "last_login": Date,
  "is_active": Boolean
}
```

### Resident Collection
```javascript
{
  "_id": ObjectId,
  "user_id": ObjectId,
  "name": String,
  "email": String,
  "phone": String,
  "address": String,
  "room_id": ObjectId,
  "join_date": Date,
  "status": String,
  "fees": Array,
  "complaints": Array,
  "attendance_records": Array,
  "emergency_contact": Object,
  "profile_photo": String
}
```

### Room Collection
```javascript
{
  "_id": ObjectId,
  "room_number": String,
  "capacity": Number,
  "type": String,
  "amenities": Array,
  "status": String,
  "current_occupants": Number,
  "occupants": Array,
  "rent_amount": Number,
  "floor": Number,
  "block": String
}
```

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Support

For support and questions:
- Create an issue on GitHub
- Email: support@hostelmanagement.com
- Documentation: [Project Wiki](https://github.com/your-username/hostel-management-system/wiki)

---

**Built with ❤️ using Python, Flask, MongoDB, and Modern Web Technologies**