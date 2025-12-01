import os
import sys
from datetime import datetime, timedelta
from pymongo import MongoClient
from bson import ObjectId

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the app to get the mongo connection
try:
    from app import mongo
except ImportError:
    # If we can't import, create a direct connection
    client = MongoClient('mongodb://localhost:27017/')
    db = client['hostel_management']
    mongo = type('Mongo', (), {'db': db})()

def reset_complaints_and_fees():
    """Reset complaints and fees data and add new sample data"""
    
    # Remove all current complaints and fees
    mongo.db.complaints.delete_many({})
    mongo.db.fees.delete_many({})
    
    print("Removed all existing complaints and fees")
    
    # Get some residents to assign complaints and fees to
    residents = list(mongo.db.residents.find({'is_active': True}).limit(10))
    
    if not residents:
        print("No active residents found. Please add residents first.")
        return
    
    # Add sample fees for residents (mix of paid and pending)
    sample_fees = []
    fee_types = ['Monthly Rent', 'Mess Fee', 'Maintenance', 'Electricity', 'Internet']
    
    for i, resident in enumerate(residents):
        # Add 3 months of fees for each resident
        for month_offset in range(3):
            fee_date = datetime.now() - timedelta(days=30 * month_offset)
            
            # Alternate between paid and pending status
            status = 'Paid' if (i + month_offset) % 2 == 0 else 'Pending'
            paid_date = datetime.now() if status == 'Paid' else None
            
            sample_fees.append({
                'resident_id': resident['_id'],
                'fee_type': fee_types[(i + month_offset) % len(fee_types)],
                'amount': float(5000 + (i * 1000)),
                'due_date': fee_date.replace(day=5),  # Due on 5th of month
                'status': status,
                'paid_date': paid_date,
                'created_at': datetime.utcnow()
            })
    
    if sample_fees:
        mongo.db.fees.insert_many(sample_fees)
        print(f"Added {len(sample_fees)} sample fees")
    
    # Add sample complaints from random residents
    complaint_categories = ['Room Maintenance', 'Mess Issue', 'Water Supply', 'Electricity', 'Internet', 'Other']
    complaint_priorities = ['Low', 'Medium', 'High', 'Critical']
    complaint_statuses = ['Open', 'In Progress', 'Resolved']
    
    sample_complaints = []
    
    # Add 2 complaints from random residents
    for i in range(min(2, len(residents))):
        resident = residents[i]
        sample_complaints.append({
            'resident_id': resident['_id'],
            'subject': f'Complaint about {complaint_categories[i % len(complaint_categories)]}',
            'description': f'This is a sample complaint description from {resident["name"]} regarding {complaint_categories[i % len(complaint_categories)].lower()}.',
            'category': complaint_categories[i % len(complaint_categories)],
            'priority': complaint_priorities[i % len(complaint_priorities)],
            'status': complaint_statuses[i % len(complaint_statuses)],
            'assigned_to': '',
            'resolved_at': None,
            'resolution_notes': '',
            'created_at': datetime.utcnow()
        })
    
    if sample_complaints:
        mongo.db.complaints.insert_many(sample_complaints)
        print(f"Added {len(sample_complaints)} sample complaints")
    
    print("Data reset completed successfully!")

if __name__ == "__main__":
    reset_complaints_and_fees()