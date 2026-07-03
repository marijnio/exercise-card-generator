# Kettlebell Workout Card Generator & Manager

A lightweight, beautiful, and local system for managing a fitness exercise database and generating high-resolution, print-ready workout cards. The cards are compiled into a premium landscape design (1800x1200 px, 3:2 aspect ratio) featuring description cues, step-by-step form instructions, movement execution images, and dynamic video lookup QR codes.

---

## 📋 Features

- **Interactive Database Manager GUI**: A local Flask-based web application to add, edit, and delete exercises, upload photos, filter/search by ID or name, and view generation status.
- **Interactive List Sorting & IDs**: Sort the list of exercises by ID (ascending/descending) or Name (A-Z/Z-A) directly from the sidebar. Each card receives a unique, customizable ID.
- **Card Generator**: A Pillow-powered rendering engine that draws high-quality cards with card IDs rendered at the top-right, precise text wrapping, structured layouts, and fallback support for missing assets.
- **macOS Shortcut Scripts**: Double-clickable executable `.command` files to launch the database GUI or compile cards directly from Finder.
- **Dynamic QR Code Integration**: Automatically generates and embeds a QR code for each exercise's video URL.

---

## 🛠️ Installation & Setup

### Prerequisites
- **Python 3.x** must be installed on your system.
- macOS is fully supported out of the box with the double-clickable `.command` launchers.

### Step 1: Install Dependencies
Open your terminal, navigate to the project directory, and install the required Python packages:

```bash
pip install -r requirements.txt
```

> [!NOTE]
> The dependencies include:
> - `pandas`: For managing the CSV exercise database.
> - `Pillow`: For high-performance image processing and card rendering.
> - `qrcode`: For dynamic QR code generation.
> - `flask`: For hosting the local database manager web GUI.

### Step 2: Generate Sample Data (Optional)
If you want to start with a predefined set of kettlebell exercises (e.g., Goblet Squats, swings, Turkish Get-Ups), you can generate a sample `workout_data.csv`:

```bash
python3 generate_sample_csv.py
```

---

## 🚀 How to Launch the GUI

The Kettlebell Cards Manager web GUI allows you to manage your exercise list, upload demonstration images, and trigger card generation directly from your web browser.

### Method 1: Double-Click Launcher (macOS)
1. Find the [run_gui.command](file:///Users/273974/Developer/exercise-card-generator/run_gui.command) file in your project folder.
2. Double-click it.
3. A terminal window will open, start the local Flask server, and automatically open your default browser to:
   ```
   http://localhost:5001
   ```

*Note: If macOS prevents the file from running due to permissions, open your terminal and run:*
```bash
chmod +x run_gui.command
```

### Method 2: Terminal Command
If you prefer using the terminal directly:
1. Open your terminal in the project directory.
2. Execute the Flask app script:
   ```bash
   python3 gui.py
   ```
3. Open your web browser and go to [http://localhost:5001](http://localhost:5001).

---

## 🖨️ How to Generate Workout Cards

Once your exercise database is set up and images are uploaded, you can generate print-ready JPEG cards.

### Method 1: From the Web GUI (Recommended)
1. Launch the GUI and look at the bottom of the sidebar or the main dashboard.
2. Click the **"Generate Cards"** button.
3. The server will run the rendering engine and save the output in the `print_ready_cards` folder.

### Method 2: Double-Click Launcher (macOS)
- Double-click the [run_generator.command](file:///Users/273974/Developer/exercise-card-generator/run_generator.command) file. This will automatically clean the output directory and generate cards for all exercises in the database.

### Method 3: Terminal Command
- Run the generator script directly:
  ```bash
  python3 generate_cards.py
  ```

---

## 📁 Directory Structure

- [gui.py](file:///Users/273974/Developer/exercise-card-generator/gui.py): Entry point for the local Flask web GUI application.
- [generate_cards.py](file:///Users/273974/Developer/exercise-card-generator/generate_cards.py): Rendering script that compiles CSV rows and images into 1800x1200 JPEGs.
- [workout_data.csv](file:///Users/273974/Developer/exercise-card-generator/workout_data.csv): The CSV database holding exercise descriptions, cues, and muscle details.
- `exercise_images/`: Contains exercise execution photos (e.g., `<exercise_name>_1.jpg` and `<exercise_name>_2.jpg`).
- `print_ready_cards/`: The output folder where completed high-resolution JPEG workout cards are saved.
- `templates/`: HTML templates containing the front-end interface for the Flask application.
