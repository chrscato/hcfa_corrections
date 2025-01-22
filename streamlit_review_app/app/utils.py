import os
import json
import shutil
from datetime import datetime

def list_files(folder):
    """List all JSON files in a folder."""
    if not os.path.exists(folder):
        return []
    return [f for f in os.listdir(folder) if f.endswith('.json')]

def load_file(filepath):
    """Load a JSON file."""
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading file {filepath}: {e}")
        return None

def save_file(data, filename, fails_folder, output_folder, originals_folder):
    """Save corrected JSON and move the original to backups."""
    output_path = os.path.join(output_folder, filename)
    original_path = os.path.join(originals_folder, filename)
    fail_path = os.path.join(fails_folder, filename)
    
    # Save the updated JSON to the output folder
    with open(output_path, 'w') as f:
        json.dump(data, f, indent=2)
    
    # Save the original JSON to the originals folder
    if os.path.exists(fail_path):
        shutil.move(fail_path, original_path)

def format_date(date_str):
    """Format a date string to YYYY-MM-DD."""
    try:
        date = datetime.strptime(date_str, '%Y-%m-%d')
        return date.strftime('%Y-%m-%d')
    except ValueError:
        return None

def process_files(INPUT_FOLDER, CLEANED_FOLDER):
    """Process files for final cleaning."""
    if not os.path.exists(CLEANED_FOLDER):
        os.makedirs(CLEANED_FOLDER)
    
    for filename in os.listdir(INPUT_FOLDER):
        if filename.endswith('.json'):
            input_path = os.path.join(INPUT_FOLDER, filename)
            cleaned_path = os.path.join(CLEANED_FOLDER, filename)
            
            # Load JSON
            with open(input_path, 'r') as f:
                data = json.load(f)
            
            # Validate and fix data
            if 'cleaned_total_charge' in data:
                try:
                    data['cleaned_total_charge'] = float(data['cleaned_total_charge'].replace(',', '').strip())
                except ValueError:
                    print(f"Invalid total charge in {filename}")
                    continue
            
            # Calculate totals and validate
            line_total = sum(
                float(item.get('cleaned_charge', '0').replace(',', '').strip()) 
                for item in data.get('line_items', [])
            )
            if abs(line_total - data.get('cleaned_total_charge', 0)) > 2:
                print(f"Warning: Total charge ({data.get('cleaned_total_charge')}) doesn't match line items total ({line_total})")
                continue
            
            # Format dates
            if 'cleaned_dos1' in data:
                data['cleaned_dos1'] = format_date(data['cleaned_dos1'])
            if 'cleaned_dos2' in data:
                data['cleaned_dos2'] = format_date(data['cleaned_dos2'])
            
            # Save cleaned JSON
            with open(cleaned_path, 'w') as f:
                json.dump(data, f, indent=2)
            
            print(f"Processed: {filename}")
