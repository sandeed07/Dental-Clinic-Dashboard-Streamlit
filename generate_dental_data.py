import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# --- Configuration for Dataset Generation ---
NUM_ROWS = 250 # Total rows in the dataset (appointments)
OUTPUT_FILE = 'dental_data.csv' # Output CSV file name

# Lists for realistic data generation
PATIENT_NAMES = [
    'Ali Khan', 'Fatima Ahmed', 'Usman Butt', 'Sana Tariq', 'Imran Malik',
    'Ayesha Zafar', 'Bilal Hussain', 'Zara Nadeem', 'Omer Farooq', 'Hina Javed',
    'Kamran Ali', 'Maryam Raza', 'Asad Mehmood', 'Nazia Saleem', 'Faisal Shah',
    'Sara Khan', 'Junaid Anwar', 'Mehwish Iqbal', 'Adnan Siddiqui', 'Nida Fatima'
]

DOCTOR_NAMES = ['Dr. Ayesha', 'Dr. Bilal', 'Dr. Zara']

PROCEDURE_TYPES = {
    'Cleaning': {'duration': (30, 45), 'billing': (50, 100)},
    'Filling': {'duration': (45, 75), 'billing': (100, 250)},
    'Root Canal': {'duration': (60, 120), 'billing': (300, 800)},
    'Whitening': {'duration': (60, 90), 'billing': (250, 500)},
    'Extraction': {'duration': (30, 60), 'billing': (150, 350)},
    'Check-up': {'duration': (15, 30), 'billing': (30, 70)},
    'Braces Consultation': {'duration': (45, 60), 'billing': (80, 150)}
}

APPOINTMENT_STATUS = ['Completed', 'Cancelled', 'No-show']
PAYMENT_STATUS = ['Paid', 'Pending']

# --- Data Generation Logic ---
def generate_dental_data(num_rows):
    data = []
    
    # Define start and end date for data generation (last 6 months)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=180) # Approximately 6 months

    for i in range(num_rows):
        # Generate random date within the last 6 months
        random_days = random.randint(0, (end_date - start_date).days)
        appointment_date = start_date + timedelta(days=random_days)
        
        # Random Patient Data
        patient_name = random.choice(PATIENT_NAMES)
        patient_age = random.randint(5, 80)
        gender = random.choice(['Male', 'Female']) # Simpler for demo

        # Random Doctor and Procedure
        doctor_name = random.choice(DOCTOR_NAMES)
        procedure_type = random.choice(list(PROCEDURE_TYPES.keys()))
        proc_details = PROCEDURE_TYPES[procedure_type]

        # Get duration and billing based on procedure type
        duration = random.randint(proc_details['duration'][0], proc_details['duration'][1])
        billing_amount = round(random.uniform(proc_details['billing'][0], proc_details['billing'][1]), 2)
        
        # Random Appointment Status (adjust probabilities for realism)
        status_choice = random.choices(APPOINTMENT_STATUS, weights=[0.85, 0.10, 0.05], k=1)[0] # 85% Completed, 10% Cancelled, 5% No-show
        
        # Payment Status (mostly paid for completed, some pending for all)
        payment_status = random.choices(PAYMENT_STATUS, weights=[0.90, 0.10], k=1)[0] if status_choice == 'Completed' else random.choice(PAYMENT_STATUS)

        data.append({
            'Appointment ID': 1000 + i + 1,
            'Date': appointment_date.strftime('%Y-%m-%d'), # Format date as YYYY-MM-DD
            'Patient Name': patient_name,
            'Patient Age': patient_age,
            'Gender': gender,
            'Doctor Name': doctor_name,
            'Procedure Type': procedure_type,
            'Appointment Status': status_choice,
            'Duration (minutes)': duration,
            'Billing Amount ($)': billing_amount,
            'Payment Status': payment_status
        })

    df = pd.DataFrame(data)
    return df

# --- Main Execution ---
if __name__ == "__main__":
    print(f"Generating {NUM_ROWS} rows of fake dental clinic data...")
    dental_df = generate_dental_data(NUM_ROWS)
    dental_df.to_csv(OUTPUT_FILE, index=False)
    print(f"Data generation complete. Saved to '{OUTPUT_FILE}'.")
    print("\nFirst 5 rows of the generated data:")
    print(dental_df.head())
