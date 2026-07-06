import os
import shutil
import subprocess
import webbrowser
import pandas as pd
from flask import Flask, request, jsonify, render_template, send_from_directory
from werkzeug.utils import secure_filename

app = Flask(__name__, template_folder="templates")
app.config['TEMPLATES_AUTO_RELOAD'] = True

CSV_FILE = "workout_data.csv"
IMAGE_DIR = "exercise_images"
PRINT_DIR = "print_ready_cards"

# Ensure directories exist
os.makedirs(IMAGE_DIR, exist_ok=True)
os.makedirs(PRINT_DIR, exist_ok=True)

def get_sanitized_base_name(exercise_name):
    """Matches the exact sanitization naming convention used in generate_cards.py"""
    sanitized = "".join([c if c.isalnum() or c in (" ", "_", "-") else "" for c in exercise_name]).strip()
    return sanitized.replace(" ", "_").lower()

def get_image_status(exercise_name):
    """Checks if Position 1 and Position 2 images exist for an exercise."""
    base_name = get_sanitized_base_name(exercise_name)
    extensions = [".jpg", ".jpeg", ".png", ".webp"]
    
    has_img1 = False
    has_img2 = False
    img1_path = ""
    img2_path = ""
    
    for ext in extensions:
        p1 = os.path.join(IMAGE_DIR, f"{base_name}_1{ext}")
        if os.path.exists(p1):
            has_img1 = True
            img1_path = f"/exercise_images/{base_name}_1{ext}"
        p2 = os.path.join(IMAGE_DIR, f"{base_name}_2{ext}")
        if os.path.exists(p2):
            has_img2 = True
            img2_path = f"/exercise_images/{base_name}_2{ext}"
            
    return has_img1, has_img2, img1_path, img2_path

def get_generated_card_path(exercise_name):
    """Gets the path to the generated print card if it exists."""
    base_name = get_sanitized_base_name(exercise_name)
    path = os.path.join(PRINT_DIR, f"{base_name}.jpg")
    if os.path.exists(path):
        return f"/print_ready_cards/{base_name}.jpg"
    return ""

def load_csv_data():
    """Loads CSV, ensuring required columns exist."""
    required_cols = [
        "ID", "Exercise_Name", "Print_Name", "Description", 
        "Form_Instructions", "Avoid_Mistake", "Video_URL", 
        "Primary_Muscles", "Secondary_Muscles"
    ]
    if not os.path.exists(CSV_FILE):
        df = pd.DataFrame(columns=required_cols)
        df.to_csv(CSV_FILE, index=False)
        return df
    
    df = pd.read_csv(CSV_FILE)
    
    # Standardize column casing
    col_mapping = {col.lower().strip(): col for col in required_cols}
    # Add backward compatibility mapping for old columns
    old_cols = ["Form_Instruction_1", "Form_Instruction_2", "Form_Instruction_3", "Form_Instruction_4"]
    for oc in old_cols:
        col_mapping[oc.lower().strip()] = oc
    
    df.columns = [col_mapping.get(c.lower().strip(), c) for c in df.columns]
    
    # Migrate old checklist columns if they exist and Form_Instructions is missing
    if "Form_Instructions" not in df.columns:
        instructions_col = []
        for idx, row in df.iterrows():
            steps = []
            for oc in old_cols:
                if oc in df.columns and not pd.isna(row[oc]):
                    val = str(row[oc]).strip()
                    if val:
                        steps.append(val)
            instructions_col.append("|".join(steps))
        df["Form_Instructions"] = instructions_col
        # Drop old columns
        df = df.drop(columns=[oc for oc in old_cols if oc in df.columns])
        df.to_csv(CSV_FILE, index=False)
        
    # Backfill missing columns
    for col in required_cols:
        if col not in df.columns:
            df[col] = ""
            
    # Auto-assign sequential IDs to empty/NaN/blank IDs
    df['ID'] = df['ID'].fillna("").astype(str).str.strip()
    assigned_any = False
    next_id = 1
    for val in df['ID']:
        if val.isdigit():
            next_id = max(next_id, int(val) + 1)
            
    for idx, row in df.iterrows():
        if not row['ID'] or row['ID'].lower() == "nan" or row['ID'] == "":
            df.at[idx, 'ID'] = str(next_id)
            next_id += 1
            assigned_any = True
            
    if assigned_any:
        # Reorder columns to put ID first
        cols = ["ID"] + [c for c in df.columns if c != "ID"]
        df = df[cols]
        df.to_csv(CSV_FILE, index=False)
            
    return df

@app.route("/")
def index():
    return render_template("index.html")

@app.after_request
def add_header(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

# Serve uploaded exercise images
@app.route("/exercise_images/<path:filename>")
def serve_exercise_image(filename):
    return send_from_directory(IMAGE_DIR, filename)

# Serve generated print ready cards
@app.route("/print_ready_cards/<path:filename>")
def serve_print_card(filename):
    return send_from_directory(PRINT_DIR, filename)

# Serve misc assets (e.g. brand logo)
@app.route("/misc/<path:filename>")
def serve_misc(filename):
    return send_from_directory("misc", filename)

# API: Get all exercises
@app.route("/api/exercises", methods=["GET"])
def get_exercises():
    try:
        df = load_csv_data()
        exercises = []
        for _, row in df.iterrows():
            name = str(row["Exercise_Name"]).strip()
            if not name or name.lower() == "nan":
                continue
                
            has_img1, has_img2, img1_path, img2_path = get_image_status(name)
            card_path = get_generated_card_path(name)
            
            exercises.append({
                "ID": str(row.get("ID", "")),
                "Exercise_Name": name,
                "Print_Name": str(row.get("Print_Name", name)) if not pd.isna(row.get("Print_Name")) else name,
                "Description": str(row["Description"]) if not pd.isna(row["Description"]) else "",
                "Form_Instructions": str(row["Form_Instructions"]) if not pd.isna(row["Form_Instructions"]) else "",
                "Avoid_Mistake": str(row.get("Avoid_Mistake", "")) if not pd.isna(row.get("Avoid_Mistake")) else "",
                "Video_URL": str(row["Video_URL"]) if not pd.isna(row["Video_URL"]) else "",
                "Primary_Muscles": str(row["Primary_Muscles"]) if not pd.isna(row["Primary_Muscles"]) else "",
                "Secondary_Muscles": str(row["Secondary_Muscles"]) if not pd.isna(row["Secondary_Muscles"]) else "",
                "has_img1": has_img1,
                "has_img2": has_img2,
                "img1_path": img1_path,
                "img2_path": img2_path,
                "card_path": card_path
            })
        return jsonify(exercises)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# API: Add or Update exercise
@app.route("/api/exercises", methods=["POST"])
def add_update_exercise():
    try:
        data = request.json
        name = data.get("Exercise_Name", "").strip()
        old_name = data.get("old_exercise_name", "").strip()
        id_val = data.get("ID", "").strip()
        
        if not name:
            return jsonify({"error": "Exercise Name is required."}), 400
            
        df = load_csv_data()
        
        # If id_val is empty, auto-generate sequential ID
        if not id_val:
            next_id = 1
            if "ID" in df.columns:
                df['ID'] = df['ID'].fillna("").astype(str).str.strip()
                for val in df['ID']:
                    if val.isdigit():
                        next_id = max(next_id, int(val) + 1)
            id_val = str(next_id)
            
        # If exercise renamed: update files in exercise_images/ and print_ready_cards/
        if old_name and old_name != name:
            # Rename images
            old_base = get_sanitized_base_name(old_name)
            new_base = get_sanitized_base_name(name)
            extensions = [".jpg", ".jpeg", ".png", ".webp"]
            for ext in extensions:
                p1_old = os.path.join(IMAGE_DIR, f"{old_base}_1{ext}")
                p1_new = os.path.join(IMAGE_DIR, f"{new_base}_1{ext}")
                if os.path.exists(p1_old):
                    os.rename(p1_old, p1_new)
                p2_old = os.path.join(IMAGE_DIR, f"{old_base}_2{ext}")
                p2_new = os.path.join(IMAGE_DIR, f"{new_base}_2{ext}")
                if os.path.exists(p2_old):
                    os.rename(p2_old, p2_new)
            # Rename compiled card if exists
            old_card = os.path.join(PRINT_DIR, f"{old_base}.jpg")
            new_card = os.path.join(PRINT_DIR, f"{new_base}.jpg")
            if os.path.exists(old_card):
                os.rename(old_card, new_card)
                
            # Drop old row from df to overwrite
            df = df[df["Exercise_Name"].str.lower() != old_name.lower()]
            
        # Check if updating existing
        df = df[df["Exercise_Name"].str.lower() != name.lower()]
        
        # Add new row
        new_row = {
            "ID": id_val,
            "Exercise_Name": name,
            "Print_Name": data.get("Print_Name", name).strip() or name,
            "Description": data.get("Description", "").strip(),
            "Form_Instructions": data.get("Form_Instructions", "").strip(),
            "Avoid_Mistake": data.get("Avoid_Mistake", "").strip(),
            "Video_URL": data.get("Video_URL", "").strip(),
            "Primary_Muscles": data.get("Primary_Muscles", "").strip(),
            "Secondary_Muscles": data.get("Secondary_Muscles", "").strip()
        }
        
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        
        # Reorder columns to put ID first
        cols = ["ID"] + [c for c in df.columns if c != "ID"]
        df = df[cols]
        
        df.to_csv(CSV_FILE, index=False)
        return jsonify({"message": "Exercise saved successfully."})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# API: Delete exercise
@app.route("/api/exercises/<name>", methods=["DELETE"])
def delete_exercise(name):
    try:
        df = load_csv_data()
        df = df[df["Exercise_Name"].str.lower() != name.lower()]
        df.to_csv(CSV_FILE, index=False)
        
        # Clean up images
        base_name = get_sanitized_base_name(name)
        extensions = [".jpg", ".jpeg", ".png", ".webp"]
        for ext in extensions:
            p1 = os.path.join(IMAGE_DIR, f"{base_name}_1{ext}")
            if os.path.exists(p1):
                os.unlink(p1)
            p2 = os.path.join(IMAGE_DIR, f"{base_name}_2{ext}")
            if os.path.exists(p2):
                os.unlink(p2)
                
        # Clean up card
        card_path = os.path.join(PRINT_DIR, f"{base_name}.jpg")
        if os.path.exists(card_path):
            os.unlink(card_path)
            
        return jsonify({"message": f"Exercise '{name}' and associated assets deleted successfully."})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# API: Upload image for an exercise
@app.route("/api/upload", methods=["POST"])
def upload_image():
    try:
        exercise_name = request.form.get("exercise_name")
        index = request.form.get("index") # 1 or 2
        
        if not exercise_name or not index:
            return jsonify({"error": "Missing exercise_name or index."}), 400
            
        if "image" not in request.files:
            return jsonify({"error": "No image file provided."}), 400
            
        file = request.files["image"]
        if file.filename == "":
            return jsonify({"error": "No file selected."}), 400
            
        # Secure filename and parse extension
        _, ext = os.path.splitext(file.filename)
        ext = ext.lower()
        if ext not in [".jpg", ".jpeg", ".png", ".webp"]:
            return jsonify({"error": "Invalid image extension. Only JPG, JPEG, PNG, WEBP allowed."}), 400
            
        base_name = get_sanitized_base_name(exercise_name)
        
        # Remove any existing files with different extension for the same index
        for old_ext in [".jpg", ".jpeg", ".png", ".webp"]:
            p = os.path.join(IMAGE_DIR, f"{base_name}_{index}{old_ext}")
            if os.path.exists(p):
                os.unlink(p)
                
        # Save new image
        target_path = os.path.join(IMAGE_DIR, f"{base_name}_{index}{ext}")
        file.save(target_path)
        
        return jsonify({"message": f"Position {index} image uploaded successfully.", "path": f"/exercise_images/{base_name}_{index}{ext}"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# API: Run card generator
@app.route("/api/generate", methods=["POST"])
def generate_cards():
    try:
        # Import and run the generator logic from generate_cards.py
        import importlib
        import generate_cards
        importlib.reload(generate_cards)
        generate_cards.main()
        return jsonify({"message": "Kaarten succesvol gegenereerd!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def start_server():
    # Automatically open browser after launching Flask
    webbrowser.open("http://localhost:5001")
    app.run(host="localhost", port=5001, debug=False)

if __name__ == "__main__":
    start_server()
