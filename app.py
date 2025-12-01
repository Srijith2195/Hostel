from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_pymongo import PyMongo
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import datetime, date, timedelta
import random
from bson.objectid import ObjectId
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'
app.config['MONGO_URI'] = 'mongodb://localhost:27017/hostel'
mongo = PyMongo(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'

# User class for Flask-Login
class User(UserMixin):
    def __init__(self, user_data=None):
        if user_data:
            self.id = str(user_data['_id'])
            self.username = user_data['username']
            self.email = user_data['email']
            self.role = user_data['role']
            # Set password if it exists in the data
            if 'password' in user_data:
                self.password = user_data['password']
    
    def save_to_db(self):
        user_data = {
            'username': self.username,
            'email': self.email,
            'password': self.password,
            'role': self.role
        }
        result = mongo.db.users.insert_one(user_data)
        self.id = str(result.inserted_id)
        return self.id
    
    def set_password(self, password):
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')
    
    def check_password(self, password):
        return bcrypt.check_password_hash(self.password, password)

@login_manager.user_loader
def load_user(user_id):
    user_data = mongo.db.users.find_one({'_id': ObjectId(user_id)})
    if user_data:
        return User(user_data)
    return None

# Custom decorators for role-based access control
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('admin_login'))
        if current_user.role != 'admin':
            flash('Access denied. Admin privileges required.')
            return redirect(url_for('resident_dashboard'))
        return f(*args, **kwargs)
    return decorated_function

def resident_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('resident_login'))
        if current_user.role != 'resident':
            flash('Access denied. Resident privileges required.')
            return redirect(url_for('admin_dashboard'))
        return f(*args, **kwargs)
    return decorated_function

# Routes
@app.route('/')
def index():
    # Check if user is logged in and redirect accordingly
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            return redirect(url_for('admin_dashboard'))
        elif current_user.role == 'resident':
            return redirect(url_for('resident_dashboard'))
    return redirect(url_for('login_options'))

@app.route('/login-options')
def login_options():
    return render_template('login_options.html')

@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user_data = mongo.db.users.find_one({'username': username, 'role': 'admin'})
        if user_data:
            user = User(user_data)
            if user.check_password(password):
                login_user(user)
                return redirect(url_for('admin_dashboard'))
        
        flash('Invalid admin credentials')
    
    return render_template('admin_login.html')

@app.route('/resident-login', methods=['GET', 'POST'])
def resident_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user_data = mongo.db.users.find_one({'username': username, 'role': 'resident'})
        if user_data:
            user = User(user_data)
            if user.check_password(password):
                login_user(user)
                return redirect(url_for('resident_dashboard'))
        
        flash('Invalid resident credentials')
    
    return render_template('resident_login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login_options'))

@app.route('/admin-dashboard')
@admin_required
def admin_dashboard():
    # Get dashboard statistics
    total_residents = mongo.db.residents.count_documents({'is_active': True})
    total_rooms = mongo.db.rooms.count_documents({})
    available_rooms = mongo.db.rooms.count_documents({'is_available': True})
    occupied_rooms = total_rooms - available_rooms
    
    # Get total complaints
    total_complaints = mongo.db.complaints.count_documents({})
    
    # Get recent complaints
    recent_complaints = list(mongo.db.complaints.find().sort('created_at', -1).limit(5))
    
    # Add resident data to complaints
    for complaint in recent_complaints:
        # Check if resident_id exists and is valid
        if 'resident_id' in complaint and complaint['resident_id']:
            try:
                resident = mongo.db.residents.find_one({'_id': complaint['resident_id']})
                if resident:
                    complaint['resident'] = resident
                else:
                    # Resident not found, set resident to None
                    complaint['resident'] = None
            except Exception as e:
                # Error occurred while fetching resident, set resident to None
                complaint['resident'] = None
                print(f"Error fetching resident for complaint {complaint['_id']}: {e}")
        else:
            # No resident_id in complaint, set resident to None
            complaint['resident'] = None
    
    # Get recent notices
    recent_notices = list(mongo.db.notices.find({'is_visible': True}).sort('created_at', -1).limit(5))
    
    return render_template('dashboard.html', 
                         total_residents=total_residents,
                         total_rooms=total_rooms,
                         available_rooms=available_rooms,
                         occupied_rooms=occupied_rooms,
                         total_complaints=total_complaints,
                         recent_complaints=recent_complaints,
                         recent_notices=recent_notices)

@app.route('/resident-dashboard')
@resident_required
def resident_dashboard():
    # Get resident-specific data
    resident = mongo.db.residents.find_one({'email': current_user.email})
    if not resident:
        flash('Resident not found!')
        return redirect(url_for('login'))
    
    # Get resident's room if assigned
    room = None
    if resident.get('room_id'):
        room = mongo.db.rooms.find_one({'_id': resident['room_id']})
    
    # Get resident's fees (both pending and paid)
    all_fees = list(mongo.db.fees.find({'resident_id': resident['_id']}).sort('due_date', -1))
    
    # Separate pending and paid fees
    pending_fees = [fee for fee in all_fees if fee.get('status') == 'Pending']
    paid_fees = [fee for fee in all_fees if fee.get('status') == 'Paid']
    
    # Calculate fee statistics
    total_pending_amount = sum([fee.get('amount', 0) for fee in pending_fees])
    total_paid_amount = sum([fee.get('amount', 0) for fee in paid_fees])
    
    # Get active notices
    active_notices = list(mongo.db.notices.find({'is_visible': True}).sort('created_at', -1).limit(5))
    
    # Get resident's complaints
    complaints = list(mongo.db.complaints.find({'resident_id': resident['_id']}).sort('created_at', -1))
    
    return render_template('resident_dashboard.html', 
                         resident=resident,
                         room=room,
                         all_fees=all_fees,
                         pending_fees=pending_fees,
                         paid_fees=paid_fees,
                         total_pending_amount=total_pending_amount,
                         total_paid_amount=total_paid_amount,
                         active_notices=active_notices,
                         complaints=complaints)

# Resident-specific routes
@app.route('/resident/pay-fee/<fee_id>', methods=['POST'])
@resident_required
def resident_pay_fee(fee_id):
    # Get resident
    resident = mongo.db.residents.find_one({'email': current_user.email})
    if not resident:
        return jsonify({'status': 'error', 'message': 'Resident not found'})
    
    # Update fee status to paid
    result = mongo.db.fees.update_one(
        {'_id': ObjectId(fee_id), 'resident_id': resident['_id']},
        {'$set': {
            'status': 'Paid',
            'paid_date': datetime.utcnow(),
            'payment_method': 'Online Payment'
        }}
    )
    
    if result.modified_count > 0:
        return jsonify({'status': 'success', 'message': 'Fee paid successfully'})
    else:
        return jsonify({'status': 'error', 'message': 'Failed to pay fee'})

@app.route('/resident/submit-complaint', methods=['POST'])
@resident_required
def resident_submit_complaint():
    # Get resident
    resident = mongo.db.residents.find_one({'email': current_user.email})
    if not resident:
        return jsonify({'status': 'error', 'message': 'Resident not found'})
    
    # Get form data
    subject = request.form.get('subject')
    description = request.form.get('description')
    category = request.form.get('category')
    priority = request.form.get('priority')
    
    # Validate required fields
    if not subject or not description or not category or not priority:
        return jsonify({'status': 'error', 'message': 'All fields are required'})
    
    # Create complaint
    complaint_data = {
        'resident_id': resident['_id'],
        'subject': subject,
        'description': description,
        'category': category,
        'priority': priority,
        'status': 'Open',
        'assigned_to': '',
        'resolved_at': None,
        'resolution_notes': '',
        'created_at': datetime.utcnow()
    }
    
    result = mongo.db.complaints.insert_one(complaint_data)
    
    if result.inserted_id:
        return jsonify({'status': 'success', 'message': 'Complaint submitted successfully'})
    else:
        return jsonify({'status': 'error', 'message': 'Failed to submit complaint'})

@app.route('/resident/select-room', methods=['GET', 'POST'])
@resident_required
def resident_select_room():
    # Get resident
    resident = mongo.db.residents.find_one({'email': current_user.email})
    if not resident:
        flash('Resident not found!')
        return redirect(url_for('login'))
    
    # If resident already has a room, redirect to dashboard
    if resident.get('room_id'):
        flash('You already have a room assigned.')
        return redirect(url_for('resident_dashboard'))
    
    if request.method == 'POST':
        room_id = request.form.get('room_id')
        if room_id:
            try:
                # Check if room is available
                room = mongo.db.rooms.find_one({'_id': ObjectId(room_id), 'is_available': True})
                if not room:
                    flash('Selected room is not available.')
                    return redirect(url_for('resident_select_room'))
                
                # Update resident with room
                mongo.db.residents.update_one(
                    {'_id': resident['_id']},
                    {'$set': {'room_id': ObjectId(room_id)}}
                )
                
                # Update room availability
                mongo.db.rooms.update_one(
                    {'_id': ObjectId(room_id)},
                    {'$set': {'is_available': False}}
                )
                
                flash('Room selected successfully!')
                return redirect(url_for('resident_dashboard'))
            except Exception as e:
                flash(f'Error selecting room: {str(e)}')
        else:
            flash('Please select a room.')
    
    # Get available rooms
    available_rooms = list(mongo.db.rooms.find({'is_available': True}))
    return render_template('resident_select_room.html', rooms=available_rooms)

@app.route('/resident/profile', methods=['GET', 'POST'])
@resident_required
def resident_profile():
    # Get resident
    resident = mongo.db.residents.find_one({'email': current_user.email})
    if not resident:
        flash('Resident not found!')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        try:
            # Process form data
            try:
                date_of_birth = datetime.strptime(request.form['date_of_birth'], '%Y-%m-%d')
            except ValueError:
                date_of_birth = resident.get('date_of_birth', datetime.utcnow())
                flash('Invalid date format for date of birth. Keeping current value.')
            
            resident_data = {
                'name': request.form['name'],
                'email': request.form['email'],
                'phone': request.form['phone'],
                'emergency_contact_name': request.form.get('emergency_contact_name', ''),
                'emergency_contact_phone': request.form.get('emergency_contact_phone', ''),
                'date_of_birth': date_of_birth,
                'street': request.form['street'],
                'city': request.form['city'],
                'state': request.form['state'],
                'zip_code': request.form['zip_code'],
                'dietary_preference': request.form.get('dietary_preference', 'Vegetarian')
            }
            
            mongo.db.residents.update_one(
                {'_id': resident['_id']},
                {'$set': resident_data}
            )
            
            flash('Profile updated successfully!')
            return redirect(url_for('resident_profile'))
        except Exception as e:
            flash(f'Error updating profile: {str(e)}')
    
    return render_template('resident_profile.html', resident=resident)

# API Routes for Dashboard Statistics
@app.route('/api/rooms/stats')
@admin_required
def api_room_stats():
    try:
        total_rooms = mongo.db.rooms.count_documents({})
        available_rooms = mongo.db.rooms.count_documents({'is_available': True})
        occupied_rooms = total_rooms - available_rooms
        
        # Calculate occupancy rate
        occupancy_rate = 0
        if total_rooms > 0:
            occupancy_rate = round((occupied_rooms / total_rooms) * 100, 2)
        
        return jsonify({
            'total_rooms': total_rooms,
            'available_rooms': available_rooms,
            'occupied_rooms': occupied_rooms,
            'occupancy_rate': occupancy_rate
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Rooms Routes
@app.route('/rooms')
@admin_required
def rooms():
    rooms = list(mongo.db.rooms.find())
    return render_template('rooms.html', rooms=rooms)

@app.route('/add-room', methods=['POST'])
@admin_required
def add_room():
    try:
        room_data = {
            'room_number': request.form['room_number'],
            'floor': int(request.form['floor']),
            'capacity': int(request.form['capacity']),
            'occupied_beds': 0,
            'amenities': request.form['amenities'],
            'monthly_rent': float(request.form['monthly_rent']),
            'is_available': True
        }
        
        result = mongo.db.rooms.insert_one(room_data)
        if result.inserted_id:
            return jsonify({'status': 'success', 'message': 'Room added successfully!'})
        else:
            return jsonify({'status': 'error', 'message': 'Failed to add room'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/update-room/<room_id>', methods=['POST'])
@admin_required
def update_room(room_id):
    try:
        room_data = {
            'room_number': request.form['room_number'],
            'floor': int(request.form['floor']),
            'capacity': int(request.form['capacity']),
            'amenities': request.form['amenities'],
            'monthly_rent': float(request.form['monthly_rent'])
        }
        
        result = mongo.db.rooms.update_one(
            {'_id': ObjectId(room_id)},
            {'$set': room_data}
        )
        
        if result.modified_count > 0:
            return jsonify({'status': 'success', 'message': 'Room updated successfully!'})
        else:
            return jsonify({'status': 'error', 'message': 'Failed to update room'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/delete-room/<room_id>', methods=['POST'])
@admin_required
def delete_room(room_id):
    try:
        # Check if room has residents
        resident_count = mongo.db.residents.count_documents({'room_id': ObjectId(room_id)})
        if resident_count > 0:
            return jsonify({'status': 'error', 'message': 'Cannot delete room with residents assigned'})
        
        result = mongo.db.rooms.delete_one({'_id': ObjectId(room_id)})
        if result.deleted_count > 0:
            return jsonify({'status': 'success', 'message': 'Room deleted successfully!'})
        else:
            return jsonify({'status': 'error', 'message': 'Failed to delete room'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

# Residents Routes
@app.route('/residents')
@admin_required
def residents():
    residents = list(mongo.db.residents.find({'is_active': True}))
    rooms = list(mongo.db.rooms.find())
    
    # Add room data to residents
    for resident in residents:
        if 'room_id' in resident and resident['room_id']:
            room = mongo.db.rooms.find_one({'_id': resident['room_id']})
            resident['room'] = room
    
    return render_template('residents.html', residents=residents, rooms=rooms)

@app.route('/add-resident', methods=['POST'])
@admin_required
def add_resident():
    try:
        # Parse date
        try:
            admission_date = datetime.strptime(request.form['admission_date'], '%Y-%m-%d')
        except ValueError:
            admission_date = datetime.utcnow()
        
        try:
            date_of_birth = datetime.strptime(request.form['date_of_birth'], '%Y-%m-%d')
        except ValueError:
            date_of_birth = datetime.utcnow()
        
        resident_data = {
            'name': request.form['name'],
            'email': request.form['email'],
            'phone': request.form['phone'],
            'emergency_contact_name': request.form.get('emergency_contact_name', ''),
            'emergency_contact_phone': request.form.get('emergency_contact_phone', ''),
            'date_of_birth': date_of_birth,
            'street': request.form['street'],
            'city': request.form['city'],
            'state': request.form['state'],
            'zip_code': request.form['zip_code'],
            'room_id': ObjectId(request.form['room_id']) if request.form['room_id'] else None,
            'admission_date': admission_date,
            'dietary_preference': request.form['dietary_preference'],
            'is_active': True
        }
        
        result = mongo.db.residents.insert_one(resident_data)
        if result.inserted_id:
            # Update room availability if room is assigned
            if resident_data['room_id']:
                mongo.db.rooms.update_one(
                    {'_id': resident_data['room_id']},
                    {'$inc': {'occupied_beds': 1}}
                )
                # Check if room is now full
                room = mongo.db.rooms.find_one({'_id': resident_data['room_id']})
                if room['occupied_beds'] >= room['capacity']:
                    mongo.db.rooms.update_one(
                        {'_id': resident_data['room_id']},
                        {'$set': {'is_available': False}}
                    )
            
            return jsonify({'status': 'success', 'message': 'Resident added successfully!'})
        else:
            return jsonify({'status': 'error', 'message': 'Failed to add resident'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/update-resident/<resident_id>', methods=['POST'])
@admin_required
def update_resident(resident_id):
    try:
        # Parse dates
        try:
            admission_date = datetime.strptime(request.form['admission_date'], '%Y-%m-%d')
        except ValueError:
            admission_date = datetime.utcnow()
        
        try:
            date_of_birth = datetime.strptime(request.form['date_of_birth'], '%Y-%m-%d')
        except ValueError:
            date_of_birth = datetime.utcnow()
        
        resident_data = {
            'name': request.form['name'],
            'email': request.form['email'],
            'phone': request.form['phone'],
            'emergency_contact_name': request.form.get('emergency_contact_name', ''),
            'emergency_contact_phone': request.form.get('emergency_contact_phone', ''),
            'date_of_birth': date_of_birth,
            'street': request.form['street'],
            'city': request.form['city'],
            'state': request.form['state'],
            'zip_code': request.form['zip_code'],
            'room_id': ObjectId(request.form['room_id']) if request.form['room_id'] else None,
            'admission_date': admission_date,
            'dietary_preference': request.form['dietary_preference']
        }
        
        result = mongo.db.residents.update_one(
            {'_id': ObjectId(resident_id)},
            {'$set': resident_data}
        )
        
        if result.modified_count > 0:
            return jsonify({'status': 'success', 'message': 'Resident updated successfully!'})
        else:
            return jsonify({'status': 'error', 'message': 'Failed to update resident'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/delete-resident/<resident_id>', methods=['POST'])
@admin_required
def delete_resident(resident_id):
    try:
        # Get resident to check room assignment
        resident = mongo.db.residents.find_one({'_id': ObjectId(resident_id)})
        if not resident:
            return jsonify({'status': 'error', 'message': 'Resident not found'})
        
        result = mongo.db.residents.update_one(
            {'_id': ObjectId(resident_id)},
            {'$set': {'is_active': False}}
        )
        
        if result.modified_count > 0:
            # Free up room if assigned
            if resident.get('room_id'):
                mongo.db.rooms.update_one(
                    {'_id': resident['room_id']},
                    {'$inc': {'occupied_beds': -1}, '$set': {'is_available': True}}
                )
            
            return jsonify({'status': 'success', 'message': 'Resident deleted successfully!'})
        else:
            return jsonify({'status': 'error', 'message': 'Failed to delete resident'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

# Attendance Routes
@app.route('/attendance')
@admin_required
def attendance():
    # Get date parameter or use today
    date_str = request.args.get('date')
    if date_str:
        try:
            today = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            today = date.today()
    else:
        today = date.today()
    
    # Get all residents
    residents = list(mongo.db.residents.find({'is_active': True}))
    
    # Get today's attendance records
    attendance_records = list(mongo.db.attendance.find({
        'date': datetime.combine(today, datetime.min.time())
    }))
    
    # Create a dictionary for quick lookup
    attendance_dict = {str(record['resident_id']): record for record in attendance_records}
    
    # Add attendance status to residents
    for resident in residents:
        resident_id_str = str(resident['_id'])
        if resident_id_str in attendance_dict:
            resident['attendance'] = attendance_dict[resident_id_str]
        else:
            resident['attendance'] = None
    
    # Add room data to residents
    for resident in residents:
        if 'room_id' in resident and resident['room_id']:
            room = mongo.db.rooms.find_one({'_id': resident['room_id']})
            resident['room'] = room
    
    # Add resident data to attendance records
    for record in attendance_records:
        resident = mongo.db.residents.find_one({'_id': record['resident_id']})
        if resident:
            # Add room data to resident
            if 'room_id' in resident and resident['room_id']:
                room = mongo.db.rooms.find_one({'_id': resident['room_id']})
                resident['room'] = room
            record['resident'] = resident

    # Calculate statistics
    total_residents = len(residents)
    present_count = len([r for r in attendance_records if r.get('status') == 'Present'])
    absent_count = len([r for r in attendance_records if r.get('status') == 'Absent'])
    leave_count = len([r for r in attendance_records if r.get('status') == 'Leave'])
    
    return render_template('attendance.html', 
                         residents=residents,
                         attendance_records=attendance_records,
                         today=today,
                         total_residents=total_residents,
                         present_count=present_count,
                         absent_count=absent_count,
                         leave_count=leave_count)

@app.route('/attendance/mark', methods=['POST'])
@admin_required
def mark_attendance():
    try:
        resident_id = request.form.get('resident_id')
        status = request.form.get('status')
        remarks = request.form.get('remarks', '')
        date_str = request.form.get('date')
        
        # Parse date
        attendance_date = datetime.strptime(date_str, '%Y-%m-%d') if date_str else datetime.combine(date.today(), datetime.min.time())
        
        # Check if attendance record already exists for this resident and date
        existing_record = mongo.db.attendance.find_one({
            'resident_id': ObjectId(resident_id),
            'date': attendance_date
        })
        
        if existing_record:
            # Update existing record
            result = mongo.db.attendance.update_one(
                {'_id': existing_record['_id']},
                {'$set': {
                    'status': status,
                    'remarks': remarks
                }}
            )
            message = 'Attendance updated successfully!'
        else:
            # Create new record
            attendance_record = {
                'resident_id': ObjectId(resident_id),
                'date': attendance_date,
                'status': status,
                'remarks': remarks
            }
            result = mongo.db.attendance.insert_one(attendance_record)
            message = 'Attendance marked successfully!'
        
        if result:
            return jsonify({'status': 'success', 'message': message})
        else:
            return jsonify({'status': 'error', 'message': 'Failed to save attendance'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/attendance/update/<attendance_id>', methods=['POST'])
@admin_required
def update_attendance(attendance_id):
    try:
        status = request.form.get('status')
        remarks = request.form.get('remarks', '')
        
        result = mongo.db.attendance.update_one(
            {'_id': ObjectId(attendance_id)},
            {'$set': {
                'status': status,
                'remarks': remarks
            }}
        )
        
        if result.modified_count > 0:
            return jsonify({'status': 'success', 'message': 'Attendance updated successfully!'})
        else:
            return jsonify({'status': 'error', 'message': 'Failed to update attendance'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

# Food Menu Routes
@app.route('/food-menu')
@login_required
def food_menu():
    # Get menu items for the current week
    menu_items_cursor = mongo.db.food_menu.find()
    menu_items = []
    for item in menu_items_cursor:
        # Convert ObjectId to string for template use
        item['id'] = str(item['_id'])
        menu_items.append(item)
    return render_template('food_menu.html', menu_items=menu_items)

# Fees Routes
@app.route('/fees')
@admin_required
def fees():
    fees = list(mongo.db.fees.find())
    residents = list(mongo.db.residents.find({'is_active': True}))
    
    # Add resident data to fees
    for fee in fees:
        # Check if resident_id exists and is valid
        if 'resident_id' in fee and fee['resident_id']:
            try:
                resident = mongo.db.residents.find_one({'_id': fee['resident_id']})
                if resident:
                    # Add room data to resident
                    if 'room_id' in resident and resident['room_id']:
                        room = mongo.db.rooms.find_one({'_id': resident['room_id']})
                        if room:
                            resident['room'] = room
                    fee['resident'] = resident
                else:
                    # Resident not found, set resident to None
                    fee['resident'] = None
            except Exception as e:
                # Error occurred while fetching resident, set resident to None
                fee['resident'] = None
                print(f"Error fetching resident for fee {fee['_id']}: {e}")
        else:
            # No resident_id in fee, set resident to None
            fee['resident'] = None
    
    # Calculate statistics
    total_amount = sum([f.get('amount', 0) for f in fees])
    paid_amount = sum([f.get('amount', 0) for f in fees if f.get('status') == 'Paid'])
    pending_amount = sum([f.get('amount', 0) for f in fees if f.get('status') == 'Pending'])
    overdue_amount = sum([f.get('amount', 0) for f in fees if f.get('status') == 'Overdue'])
    
    return render_template('fees.html', 
                         fees=fees,
                         residents=residents,
                         total_amount=total_amount,
                         paid_amount=paid_amount,
                         pending_amount=pending_amount,
                         overdue_amount=overdue_amount)

# Notices Routes
@app.route('/notices')
@login_required
def notices():
    notices = list(mongo.db.notices.find().sort('created_at', -1))
    return render_template('notices.html', notices=notices)

# Chats Routes
@app.route('/chats')
@admin_required
def chats():
    return render_template('chats.html')

# Complaints Routes
@app.route('/complaints')
@admin_required
def complaints():
    complaints = list(mongo.db.complaints.find().sort('created_at', -1))
    residents = list(mongo.db.residents.find({'is_active': True}))
    
    # Add resident data to complaints
    for complaint in complaints:
        # Check if resident_id exists and is valid
        if 'resident_id' in complaint and complaint['resident_id']:
            try:
                resident = mongo.db.residents.find_one({'_id': complaint['resident_id']})
                if resident:
                    # Add room data to resident
                    if 'room_id' in resident and resident['room_id']:
                        room = mongo.db.rooms.find_one({'_id': resident['room_id']})
                        if room:
                            resident['room'] = room
                    complaint['resident'] = resident
                else:
                    # Resident not found, set resident to None
                    complaint['resident'] = None
            except Exception as e:
                # Error occurred while fetching resident, set resident to None
                complaint['resident'] = None
                print(f"Error fetching resident for complaint {complaint['_id']}: {e}")
        else:
            # No resident_id in complaint, set resident to None
            complaint['resident'] = None
    
    # Calculate statistics
    total_complaints = len(complaints)
    open_complaints = len([c for c in complaints if c.get('status') == 'Open'])
    in_progress_complaints = len([c for c in complaints if c.get('status') == 'In Progress'])
    resolved_complaints = len([c for c in complaints if c.get('status') == 'Resolved'])
    
    return render_template('complaints.html', 
                         complaints=complaints,
                         residents=residents,
                         total_complaints=total_complaints,
                         open_complaints=open_complaints,
                         in_progress_complaints=in_progress_complaints,
                         resolved_complaints=resolved_complaints)

@app.route('/update-complaint-status/<complaint_id>', methods=['POST'])
@admin_required
def update_complaint_status(complaint_id):
    try:
        status = request.form.get('status')
        assigned_to = request.form.get('assigned_to', '')
        resolution_notes = request.form.get('resolution_notes', '')
        
        update_data = {
            'status': status,
            'assigned_to': assigned_to
        }
        
        if status == 'Resolved':
            update_data['resolved_at'] = datetime.utcnow()
            update_data['resolution_notes'] = resolution_notes
        
        result = mongo.db.complaints.update_one(
            {'_id': ObjectId(complaint_id)},
            {'$set': update_data}
        )
        
        if result.modified_count > 0:
            return jsonify({'status': 'success', 'message': 'Complaint status updated successfully!'})
        else:
            return jsonify({'status': 'error', 'message': 'Failed to update complaint status'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

def seed_database():
    """Seed the database with default data if it's empty"""
    try:
        # Check if we already have data
        if mongo.db.rooms.count_documents({}) > 0:
            print("Database already seeded, skipping...")
            return
        
        # Add sample rooms
        sample_rooms = [
            {'room_number': '101', 'floor': 1, 'capacity': 3, 'occupied_beds': 2, 'amenities': 'AC, WiFi, TV', 'monthly_rent': 8000.0, 'is_available': True},
            {'room_number': '102', 'floor': 1, 'capacity': 2, 'occupied_beds': 1, 'amenities': 'WiFi, TV', 'monthly_rent': 6000.0, 'is_available': True},
            {'room_number': '201', 'floor': 2, 'capacity': 4, 'occupied_beds': 4, 'amenities': 'AC, WiFi, TV, Geyser', 'monthly_rent': 10000.0, 'is_available': False},
            {'room_number': '202', 'floor': 2, 'capacity': 3, 'occupied_beds': 0, 'amenities': 'AC, WiFi', 'monthly_rent': 9000.0, 'is_available': True},
            {'room_number': '301', 'floor': 3, 'capacity': 2, 'occupied_beds': 0, 'amenities': 'AC, WiFi, TV, Geyser, Mini Fridge', 'monthly_rent': 12000.0, 'is_available': True},
            {'room_number': '302', 'floor': 3, 'capacity': 4, 'occupied_beds': 2, 'amenities': 'AC, WiFi, TV', 'monthly_rent': 10000.0, 'is_available': True},
            {'room_number': '401', 'floor': 4, 'capacity': 3, 'occupied_beds': 3, 'amenities': 'AC, WiFi, TV, Geyser', 'monthly_rent': 11000.0, 'is_available': False},
            {'room_number': '402', 'floor': 4, 'capacity': 2, 'occupied_beds': 0, 'amenities': 'AC, WiFi, TV', 'monthly_rent': 8500.0, 'is_available': True}
        ]
        
        room_ids = []
        for room in sample_rooms:
            result = mongo.db.rooms.insert_one(room)
            room_ids.append(result.inserted_id)
        
        print(f"Added {len(sample_rooms)} sample rooms")
        
        # Add sample residents
        sample_residents = [
            {
                'name': 'John Doe',
                'email': 'john.doe@example.com',
                'phone': '9876543210',
                'emergency_contact_name': 'Jane Doe',
                'emergency_contact_phone': '9876543211',
                'date_of_birth': datetime(1995, 5, 15),
                'street': '123 Main St',
                'city': 'Bangalore',
                'state': 'Karnataka',
                'zip_code': '560001',
                'room_id': room_ids[0],
                'admission_date': datetime(2023, 1, 15),
                'dietary_preference': 'Vegetarian',
                'is_active': True
            },
            {
                'name': 'Alice Smith',
                'email': 'alice.smith@example.com',
                'phone': '9876543212',
                'emergency_contact_name': 'Bob Smith',
                'emergency_contact_phone': '9876543213',
                'date_of_birth': datetime(1997, 8, 22),
                'street': '456 Park Ave',
                'city': 'Bangalore',
                'state': 'Karnataka',
                'zip_code': '560002',
                'room_id': room_ids[0],
                'admission_date': datetime(2023, 2, 10),
                'dietary_preference': 'Non-Vegetarian',
                'is_active': True
            },
            {
                'name': 'Robert Johnson',
                'email': 'robert.johnson@example.com',
                'phone': '9876543214',
                'emergency_contact_name': 'Mary Johnson',
                'emergency_contact_phone': '9876543215',
                'date_of_birth': datetime(1996, 12, 3),
                'street': '789 Elm St',
                'city': 'Bangalore',
                'state': 'Karnataka',
                'zip_code': '560003',
                'room_id': room_ids[1],
                'admission_date': datetime(2023, 3, 5),
                'dietary_preference': 'Vegetarian',
                'is_active': True
            },
            {
                'name': 'Emily Davis',
                'email': 'emily.davis@example.com',
                'phone': '9876543216',
                'emergency_contact_name': 'Michael Davis',
                'emergency_contact_phone': '9876543217',
                'date_of_birth': datetime(1998, 4, 18),
                'street': '101 Oak St',
                'city': 'Bangalore',
                'state': 'Karnataka',
                'zip_code': '560004',
                'room_id': room_ids[2],
                'admission_date': datetime(2023, 4, 20),
                'dietary_preference': 'Vegan',
                'is_active': True
            },
            {
                'name': 'Michael Wilson',
                'email': 'michael.wilson@example.com',
                'phone': '9876543218',
                'emergency_contact_name': 'Sarah Wilson',
                'emergency_contact_phone': '9876543219',
                'date_of_birth': datetime(1994, 11, 30),
                'street': '202 Pine St',
                'city': 'Bangalore',
                'state': 'Karnataka',
                'zip_code': '560005',
                'room_id': room_ids[2],
                'admission_date': datetime(2023, 5, 12),
                'dietary_preference': 'Non-Vegetarian',
                'is_active': True
            },
            {
                'name': 'Sophia Brown',
                'email': 'sophia.brown@example.com',
                'phone': '9876543220',
                'emergency_contact_name': 'David Brown',
                'emergency_contact_phone': '9876543221',
                'date_of_birth': datetime(1997, 7, 14),
                'street': '303 Maple St',
                'city': 'Bangalore',
                'state': 'Karnataka',
                'zip_code': '560006',
                'room_id': room_ids[2],
                'admission_date': datetime(2023, 6, 8),
                'dietary_preference': 'Vegetarian',
                'is_active': True
            },
            {
                'name': 'James Taylor',
                'email': 'james.taylor@example.com',
                'phone': '9876543222',
                'emergency_contact_name': 'Lisa Taylor',
                'emergency_contact_phone': '9876543223',
                'date_of_birth': datetime(1995, 9, 25),
                'street': '404 Cedar St',
                'city': 'Bangalore',
                'state': 'Karnataka',
                'zip_code': '560007',
                'room_id': room_ids[2],
                'admission_date': datetime(2023, 7, 3),
                'dietary_preference': 'Non-Vegetarian',
                'is_active': True
            },
            {
                'name': 'Emma Anderson',
                'email': 'emma.anderson@example.com',
                'phone': '9876543224',
                'emergency_contact_name': 'Peter Anderson',
                'emergency_contact_phone': '9876543225',
                'date_of_birth': datetime(1996, 3, 12),
                'street': '505 Walnut St',
                'city': 'Bangalore',
                'state': 'Karnataka',
                'zip_code': '560008',
                'room_id': room_ids[3],
                'admission_date': datetime(2023, 8, 15),
                'dietary_preference': 'Vegetarian',
                'is_active': True
            },
            {
                'name': 'William Thomas',
                'email': 'william.thomas@example.com',
                'phone': '9876543226',
                'emergency_contact_name': 'Jennifer Thomas',
                'emergency_contact_phone': '9876543227',
                'date_of_birth': datetime(1998, 1, 8),
                'street': '606 Birch St',
                'city': 'Bangalore',
                'state': 'Karnataka',
                'zip_code': '560009',
                'room_id': room_ids[5],
                'admission_date': datetime(2023, 9, 22),
                'dietary_preference': 'Non-Vegetarian',
                'is_active': True
            },
            {
                'name': 'Olivia Martinez',
                'email': 'olivia.martinez@example.com',
                'phone': '9876543228',
                'emergency_contact_name': 'Carlos Martinez',
                'emergency_contact_phone': '9876543229',
                'date_of_birth': datetime(1997, 11, 5),
                'street': '707 Spruce St',
                'city': 'Bangalore',
                'state': 'Karnataka',
                'zip_code': '560010',
                'room_id': room_ids[5],
                'admission_date': datetime(2023, 10, 30),
                'dietary_preference': 'Vegan',
                'is_active': True
            }
        ]
        
        resident_ids = []
        for resident in sample_residents:
            result = mongo.db.residents.insert_one(resident)
            resident_ids.append(result.inserted_id)
        
        print(f"Added {len(sample_residents)} sample residents")
        
        # Add sample attendance records
        today = date.today()
        sample_attendance = []
        statuses = ['Present', 'Absent', 'Leave']
        
        for resident_id in resident_ids:
            # Add attendance records for the last 30 days
            for i in range(30):
                attendance_date = today - timedelta(days=i)
                status = random.choice(statuses)
                sample_attendance.append({
                    'resident_id': resident_id,
                    'date': datetime.combine(attendance_date, datetime.min.time()),
                    'status': status,
                    'remarks': f'Auto-generated record for {attendance_date}'
                })
        
        if sample_attendance:
            mongo.db.attendance.insert_many(sample_attendance)
            print(f"Added {len(sample_attendance)} sample attendance records")
        
        # Add sample fees
        fee_types = ['Monthly Rent', 'Mess Fee', 'Maintenance', 'Electricity', 'Internet']
        sample_fees = []
        
        for resident_id in resident_ids:
            for i in range(6):  # 6 months of fees
                fee_month = today.replace(day=1) - timedelta(days=30*i)
                fee_type = random.choice(fee_types)
                amount = random.randint(3000, 12000)
                status = random.choice(['Pending', 'Paid', 'Overdue'])
                due_date = fee_month.replace(day=5)  # Due on 5th of month
                
                sample_fees.append({
                    'resident_id': resident_id,
                    'fee_type': fee_type,
                    'amount': amount,
                    'due_date': datetime.combine(due_date, datetime.min.time()),
                    'status': status,
                    'created_at': datetime.utcnow()
                })
        
        if sample_fees:
            mongo.db.fees.insert_many(sample_fees)
            print(f"Added {len(sample_fees)} sample fees")
        
        # Add sample notices
        sample_notices = [
            {
                'title': 'Maintenance Notice',
                'content': 'There will be maintenance work in the hostel premises on Sunday from 9 AM to 5 PM. We apologize for any inconvenience caused.',
                'is_visible': True,
                'created_at': datetime.utcnow()
            },
            {
                'title': 'New Security Protocol',
                'content': 'Starting next month, all residents must swipe their ID cards at the entrance gate. Please collect your ID cards from the admin office.',
                'is_visible': True,
                'created_at': datetime.utcnow()
            },
            {
                'title': 'Festivals Celebration',
                'content': 'The hostel will celebrate Diwali on November 12th. All residents are invited to participate in the cultural program.',
                'is_visible': True,
                'created_at': datetime.utcnow()
            }
        ]
        
        if sample_notices:
            mongo.db.notices.insert_many(sample_notices)
            print(f"Added {len(sample_notices)} sample notices")
        
        # Add sample complaints
        complaint_categories = ['Room Maintenance', 'Mess Issue', 'Water Supply', 'Electricity', 'Internet', 'Other']
        complaint_priorities = ['Low', 'Medium', 'High']
        complaint_statuses = ['Open', 'In Progress', 'Resolved']
        sample_complaints = []
        
        for i, resident_id in enumerate(resident_ids[:5]):  # Only first 5 residents
            sample_complaints.append({
                'resident_id': resident_id,
                'subject': f'Sample Complaint {i+1}',
                'description': f'This is a sample complaint description for complaint {i+1}.',
                'category': random.choice(complaint_categories),
                'priority': random.choice(complaint_priorities),
                'status': random.choice(complaint_statuses),
                'assigned_to': '',
                'resolved_at': None,
                'resolution_notes': '',
                'created_at': datetime.utcnow()
            })
        
        if sample_complaints:
            mongo.db.complaints.insert_many(sample_complaints)
            print(f"Added {len(sample_complaints)} sample complaints")
        
        # Add sample food menu
        # Clear existing menu items to avoid duplicates
        mongo.db.food_menu.delete_many({})
        
        # Sample food menu for all days of the week with both veg and non-veg options
        sample_food_menu = [
            # Monday
            {'day_of_week': 'Monday', 'meal_type': 'Breakfast', 'items': 'Idli, Dosa, Vada, Coconut Chutney, Sambar, Tea, Coffee', 'is_veg': True, 'effective_date': datetime(2023, 1, 1).date(), 'expiry_date': datetime(2023, 12, 31).date()},
            {'day_of_week': 'Monday', 'meal_type': 'Breakfast', 'items': 'Poha, Upma, Bread with Jam, Tea, Coffee, Milk', 'is_veg': False, 'effective_date': datetime(2023, 1, 1).date(), 'expiry_date': datetime(2023, 12, 31).date()},
            {'day_of_week': 'Monday', 'meal_type': 'Lunch', 'items': 'Rice, Dal Tadka, Seasonal Vegetable, Roti, Salad, Sweet', 'is_veg': True, 'effective_date': datetime(2023, 1, 1).date(), 'expiry_date': datetime(2023, 12, 31).date()},
            {'day_of_week': 'Monday', 'meal_type': 'Lunch', 'items': 'Rice, Chicken Curry, Roti, Salad, Sweet', 'is_veg': False, 'effective_date': datetime(2023, 1, 1).date(), 'expiry_date': datetime(2023, 12, 31).date()},
            {'day_of_week': 'Monday', 'meal_type': 'Dinner', 'items': 'Roti, Rice, Paneer Butter Masala, Dal Fry, Salad, Dessert', 'is_veg': True, 'effective_date': datetime(2023, 1, 1).date(), 'expiry_date': datetime(2023, 12, 31).date()},
            {'day_of_week': 'Monday', 'meal_type': 'Dinner', 'items': 'Roti, Rice, Mutton Curry, Dal Fry, Salad, Dessert', 'is_veg': False, 'effective_date': datetime(2023, 1, 1).date(), 'expiry_date': datetime(2023, 12, 31).date()},
            
            # Tuesday
            {'day_of_week': 'Tuesday', 'meal_type': 'Breakfast', 'items': 'Aloo Paratha, Curd, Tea, Coffee', 'is_veg': True, 'effective_date': datetime(2023, 1, 1).date(), 'expiry_date': datetime(2023, 12, 31).date()},
            {'day_of_week': 'Tuesday', 'meal_type': 'Breakfast', 'items': 'Egg Paratha, Tea, Coffee, Milk', 'is_veg': False, 'effective_date': datetime(2023, 1, 1).date(), 'expiry_date': datetime(2023, 12, 31).date()},
            {'day_of_week': 'Tuesday', 'meal_type': 'Lunch', 'items': 'Rice, Rajma, Seasonal Vegetable, Roti, Salad, Sweet', 'is_veg': True, 'effective_date': datetime(2023, 1, 1).date(), 'expiry_date': datetime(2023, 12, 31).date()},
            {'day_of_week': 'Tuesday', 'meal_type': 'Lunch', 'items': 'Rice, Fish Curry, Roti, Salad, Sweet', 'is_veg': False, 'effective_date': datetime(2023, 1, 1).date(), 'expiry_date': datetime(2023, 12, 31).date()},
            {'day_of_week': 'Tuesday', 'meal_type': 'Dinner', 'items': 'Roti, Rice, Palak Paneer, Dal Fry, Salad, Dessert', 'is_veg': True, 'effective_date': datetime(2023, 1, 1).date(), 'expiry_date': datetime(2023, 12, 31).date()},
            {'day_of_week': 'Tuesday', 'meal_type': 'Dinner', 'items': 'Roti, Rice, Egg Curry, Dal Fry, Salad, Dessert', 'is_veg': False, 'effective_date': datetime(2023, 1, 1).date(), 'expiry_date': datetime(2023, 12, 31).date()},
            
            # Wednesday
            {'day_of_week': 'Wednesday', 'meal_type': 'Breakfast', 'items': 'Puri, Aloo Sabzi, Tea, Coffee', 'is_veg': True, 'effective_date': datetime(2023, 1, 1).date(), 'expiry_date': datetime(2023, 12, 31).date()},
            {'day_of_week': 'Wednesday', 'meal_type': 'Breakfast', 'items': 'Puri, Egg Curry, Tea, Coffee, Milk', 'is_veg': False, 'effective_date': datetime(2023, 1, 1).date(), 'expiry_date': datetime(2023, 12, 31).date()},
            {'day_of_week': 'Wednesday', 'meal_type': 'Lunch', 'items': 'Rice, Chole, Seasonal Vegetable, Roti, Salad, Sweet', 'is_veg': True, 'effective_date': datetime(2023, 1, 1).date(), 'expiry_date': datetime(2023, 12, 31).date()},
            {'day_of_week': 'Wednesday', 'meal_type': 'Lunch', 'items': 'Rice, Chicken Biryani, Raita, Salad', 'is_veg': False, 'effective_date': datetime(2023, 1, 1).date(), 'expiry_date': datetime(2023, 12, 31).date()},
            {'day_of_week': 'Wednesday', 'meal_type': 'Dinner', 'items': 'Roti, Rice, Mix Veg, Dal Fry, Salad, Dessert', 'is_veg': True, 'effective_date': datetime(2023, 1, 1).date(), 'expiry_date': datetime(2023, 12, 31).date()},
            {'day_of_week': 'Wednesday', 'meal_type': 'Dinner', 'items': 'Roti, Rice, Fish Fry, Dal Fry, Salad, Dessert', 'is_veg': False, 'effective_date': datetime(2023, 1, 1).date(), 'expiry_date': datetime(2023, 12, 31).date()},
            
            # Thursday
            {'day_of_week': 'Thursday', 'meal_type': 'Breakfast', 'items': 'Semiya Upma, Tea, Coffee', 'is_veg': True, 'effective_date': datetime(2023, 1, 1).date(), 'expiry_date': datetime(2023, 12, 31).date()},
            {'day_of_week': 'Thursday', 'meal_type': 'Breakfast', 'items': 'Bread Omelette, Tea, Coffee, Milk', 'is_veg': False, 'effective_date': datetime(2023, 1, 1).date(), 'expiry_date': datetime(2023, 12, 31).date()},
            {'day_of_week': 'Thursday', 'meal_type': 'Lunch', 'items': 'Rice, Dal Tadka, Baigan Bharta, Roti, Salad, Sweet', 'is_veg': True, 'effective_date': datetime(2023, 1, 1).date(), 'expiry_date': datetime(2023, 12, 31).date()},
            {'day_of_week': 'Thursday', 'meal_type': 'Lunch', 'items': 'Rice, Mutton Curry, Roti, Salad, Sweet', 'is_veg': False, 'effective_date': datetime(2023, 1, 1).date(), 'expiry_date': datetime(2023, 12, 31).date()},
            {'day_of_week': 'Thursday', 'meal_type': 'Dinner', 'items': 'Roti, Rice, Kadhi Pakoda, Seasonal Vegetable, Salad, Dessert', 'is_veg': True, 'effective_date': datetime(2023, 1, 1).date(), 'expiry_date': datetime(2023, 12, 31).date()},
            {'day_of_week': 'Thursday', 'meal_type': 'Dinner', 'items': 'Roti, Rice, Chicken Curry, Dal Fry, Salad, Dessert', 'is_veg': False, 'effective_date': datetime(2023, 1, 1).date(), 'expiry_date': datetime(2023, 12, 31).date()},
            
            # Friday
            {'day_of_week': 'Friday', 'meal_type': 'Breakfast', 'items': 'Masala Dosa, Coconut Chutney, Sambar, Tea, Coffee', 'is_veg': True, 'effective_date': datetime(2023, 1, 1).date(), 'expiry_date': datetime(2023, 12, 31).date()},
            {'day_of_week': 'Friday', 'meal_type': 'Breakfast', 'items': 'Sandwich with Egg, Tea, Coffee, Milk', 'is_veg': False, 'effective_date': datetime(2023, 1, 1).date(), 'expiry_date': datetime(2023, 12, 31).date()},
            {'day_of_week': 'Friday', 'meal_type': 'Lunch', 'items': 'Rice, Dal Fry, Aloo Gobi, Roti, Salad, Sweet', 'is_veg': True, 'effective_date': datetime(2023, 1, 1).date(), 'expiry_date': datetime(2023, 12, 31).date()},
            {'day_of_week': 'Friday', 'meal_type': 'Lunch', 'items': 'Rice, Fish Curry, Roti, Salad, Sweet', 'is_veg': False, 'effective_date': datetime(2023, 1, 1).date(), 'expiry_date': datetime(2023, 12, 31).date()},
            {'day_of_week': 'Friday', 'meal_type': 'Dinner', 'items': 'Roti, Rice, Paneer Tikka Masala, Dal Fry, Salad, Dessert', 'is_veg': True, 'effective_date': datetime(2023, 1, 1).date(), 'expiry_date': datetime(2023, 12, 31).date()},
            {'day_of_week': 'Friday', 'meal_type': 'Dinner', 'items': 'Roti, Rice, Mutton Biryani, Raita, Salad, Dessert', 'is_veg': False, 'effective_date': datetime(2023, 1, 1).date(), 'expiry_date': datetime(2023, 12, 31).date()},
            
            # Saturday
            {'day_of_week': 'Saturday', 'meal_type': 'Breakfast', 'items': 'Poha, Jalebi, Tea, Coffee', 'is_veg': True, 'effective_date': datetime(2023, 1, 1).date(), 'expiry_date': datetime(2023, 12, 31).date()},
            {'day_of_week': 'Saturday', 'meal_type': 'Breakfast', 'items': 'Pancakes with Syrup, Tea, Coffee, Milk', 'is_veg': False, 'effective_date': datetime(2023, 1, 1).date(), 'expiry_date': datetime(2023, 12, 31).date()},
            {'day_of_week': 'Saturday', 'meal_type': 'Lunch', 'items': 'Rice, Dal Tadka, Mix Veg, Roti, Salad, Sweet', 'is_veg': True, 'effective_date': datetime(2023, 1, 1).date(), 'expiry_date': datetime(2023, 12, 31).date()},
            {'day_of_week': 'Saturday', 'meal_type': 'Lunch', 'items': 'Rice, Chicken Curry, Roti, Salad, Sweet', 'is_veg': False, 'effective_date': datetime(2023, 1, 1).date(), 'expiry_date': datetime(2023, 12, 31).date()},
            {'day_of_week': 'Saturday', 'meal_type': 'Dinner', 'items': 'Roti, Rice, Shahi Paneer, Dal Fry, Salad, Dessert', 'is_veg': True, 'effective_date': datetime(2023, 1, 1).date(), 'expiry_date': datetime(2023, 12, 31).date()},
            {'day_of_week': 'Saturday', 'meal_type': 'Dinner', 'items': 'Roti, Rice, Egg Curry, Dal Fry, Salad, Dessert', 'is_veg': False, 'effective_date': datetime(2023, 1, 1).date(), 'expiry_date': datetime(2023, 12, 31).date()},
            
            # Sunday
            {'day_of_week': 'Sunday', 'meal_type': 'Breakfast', 'items': 'Poori, Aloo Sabzi, Tea, Coffee', 'is_veg': True, 'effective_date': datetime(2023, 1, 1).date(), 'expiry_date': datetime(2023, 12, 31).date()},
            {'day_of_week': 'Sunday', 'meal_type': 'Breakfast', 'items': 'Poori, Egg Curry, Tea, Coffee, Milk', 'is_veg': False, 'effective_date': datetime(2023, 1, 1).date(), 'expiry_date': datetime(2023, 12, 31).date()},
            {'day_of_week': 'Sunday', 'meal_type': 'Lunch', 'items': 'Rice, Dal Fry, Seasonal Vegetable, Roti, Salad, Sweet', 'is_veg': True, 'effective_date': datetime(2023, 1, 1).date(), 'expiry_date': datetime(2023, 12, 31).date()},
            {'day_of_week': 'Sunday', 'meal_type': 'Lunch', 'items': 'Rice, Mutton Curry, Roti, Salad, Sweet', 'is_veg': False, 'effective_date': datetime(2023, 1, 1).date(), 'expiry_date': datetime(2023, 12, 31).date()},
            {'day_of_week': 'Sunday', 'meal_type': 'Dinner', 'items': 'Roti, Rice, Mix Veg, Dal Tadka, Salad, Dessert', 'is_veg': True, 'effective_date': datetime(2023, 1, 1).date(), 'expiry_date': datetime(2023, 12, 31).date()},
            {'day_of_week': 'Sunday', 'meal_type': 'Dinner', 'items': 'Roti, Rice, Fish Curry, Dal Fry, Salad, Dessert', 'is_veg': False, 'effective_date': datetime(2023, 1, 1).date(), 'expiry_date': datetime(2023, 12, 31).date()}
        ]
        
        for menu in sample_food_menu:
            # Convert date objects to datetime for MongoDB
            menu['effective_date'] = datetime.combine(menu['effective_date'], datetime.min.time())
            menu['expiry_date'] = datetime.combine(menu['expiry_date'], datetime.min.time())
            mongo.db.food_menu.insert_one(menu)
        
        print(f"Added {len(sample_food_menu)} sample food menu items")
        
        print("Database seeding completed successfully!")
        
    except Exception as e:
        print(f"Error seeding database: {str(e)}")

# Test MongoDB connection on startup
with app.app_context():
    try:
        # The ismaster command is cheap and does not require auth.
        mongo.db.command('ismaster')
        print("MongoDB connection successful!")
        
        # Initialize collections with indexes if they don't exist
        collections = ['users', 'residents', 'rooms', 'attendance', 'food_menu', 'complaints', 'fees', 'notices', 'chats']
        for collection_name in collections:
            # This will create the collection if it doesn't exist
            if collection_name not in mongo.db.list_collection_names():
                mongo.db.create_collection(collection_name)
                print(f"Created collection: {collection_name}")
        
        # Create indexes for better performance
        mongo.db.users.create_index('username', unique=True)
        mongo.db.users.create_index('email', unique=True)
        mongo.db.residents.create_index('email', unique=True)
        mongo.db.rooms.create_index('room_number', unique=True)
        print("Database indexes created successfully!")
        
        # Seed database with default data
        seed_database()
        
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")

def create_resident_users():
    """Create individual user accounts for all residents"""
    try:
        # Get all active residents
        residents = list(mongo.db.residents.find({'is_active': True}))
        
        for resident in residents:
            # Check if user already exists for this resident
            if mongo.db.users.find_one({'email': resident['email']}):
                continue
            
            # Create a username from the resident's name
            username = resident['name'].lower().replace(' ', '_')
            
            # Make sure username is unique
            original_username = username
            counter = 1
            while mongo.db.users.find_one({'username': username}):
                username = f"{original_username}_{counter}"
                counter += 1
            
            # Create user account
            user = User()
            user.username = username
            user.email = resident['email']
            user.role = 'resident'
            user.set_password('resident123')  # Default password
            user.save_to_db()
            
            print(f'Created user account for resident: {resident["name"]} with username: {username}')
        
        print(f'Created {len(residents)} resident user accounts')
        
    except Exception as e:
        print(f"Error creating resident users: {e}")

if __name__ == '__main__':
    # Create default users if they don't exist
    if not mongo.db.users.find_one({'username': 'admin'}):
        admin = User()
        admin.username = 'admin'
        admin.email = 'admin@example.com'
        admin.role = 'admin'
        admin.set_password('admin123')
        admin.save_to_db()
        print('Default admin user created')
    
    # Create individual user accounts for all residents
    create_resident_users()
    
    app.run(debug=True)
