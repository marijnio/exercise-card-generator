import os
import shutil
import math
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import qrcode

# Color Palette Definitions (Premium Fitness Theme)
COLOR_BG = "#FAFAFA"          # Solid crisp light off-white
COLOR_PRIMARY = "#1E293B"     # Dark slate/charcoal for title and headers
COLOR_ACCENT = "#0D9488"      # Teal 600 accent color
COLOR_CARD_BG = "#F8FAFC"     # Slate 50 background
COLOR_CARD_BORDER = "#E2E8F0" # Slate 200 border for photos & QR
COLOR_TEXT_MUTED = "#64748B"  # Slate 500 for secondary labels
COLOR_BOX_BORDER = "#0D9488"  # Teal border for checkboxes
COLOR_TEXT_BODY = "#334155"   # Slate 700 for body text/cues

# Output Specs
IMAGE_WIDTH = 1800
IMAGE_HEIGHT = 1200
SAFE_MARGIN = 50
USABLE_WIDTH = IMAGE_WIDTH - 2 * SAFE_MARGIN # 1700px
OUTPUT_DIR = "print_ready_cards"

def clean_output_directory():
    """Removes all files from the output directory to ensure a clean run."""
    if os.path.exists(OUTPUT_DIR):
        print(f"Cleaning existing files in {OUTPUT_DIR}...")
        for filename in os.listdir(OUTPUT_DIR):
            file_path = os.path.join(OUTPUT_DIR, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f"Failed to delete {file_path}. Reason: {e}")
    else:
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        print(f"Created output directory: {OUTPUT_DIR}")

def load_system_font(font_name, size):
    """Loads a font from standard Mac paths, falling back to PIL default font if not found."""
    standard_paths = [
        f"/System/Library/Fonts/Supplemental/{font_name}",
        f"/System/Library/Fonts/{font_name}",
        f"/Library/Fonts/{font_name}",
        font_name
    ]
    for path in standard_paths:
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            continue
    # Fallback default if system loading fails
    try:
        return ImageFont.truetype("Arial.ttf", size)
    except Exception:
        print(f"Warning: Could not load {font_name}. Falling back to default bitmap font.")
        return ImageFont.load_default()

def get_text_width(text, font):
    """Helper to get text width safely across Pillow versions."""
    bbox = font.getbbox(text)
    return bbox[2] - bbox[0]

def get_text_height(text, font):
    """Helper to get text height safely across Pillow versions."""
    bbox = font.getbbox(text)
    return bbox[3] - bbox[1]

def wrap_text_by_pixels(text, font, max_width_px):
    """Wraps text into multiple lines so that no line exceeds max_width_px."""
    if not text:
        return []
    words = text.split(" ")
    lines = []
    current_line = []
    
    for word in words:
        test_line = " ".join(current_line + [word])
        w = get_text_width(test_line, font)
        if w <= max_width_px:
            current_line.append(word)
        else:
            if current_line:
                lines.append(" ".join(current_line))
                current_line = [word]
            else:
                # Individual word exceeds line width, force wrap it
                lines.append(word)
                current_line = []
    if current_line:
        lines.append(" ".join(current_line))
    return lines

def generate_qr_code(url, size=120):
    """Generates a QR code image resized to specified dimensions."""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=1,
    )
    qr.add_data(url)
    qr.make(fit=True)
    
    # Create QR image in black and white
    qr_img = qr.make_image(fill_color="black", back_color="white").convert("RGB")
    qr_img = qr_img.resize((size, size), Image.Resampling.LANCZOS)
    return qr_img

def load_and_crop_square(image_path, target_size=430):
    """Loads an image, crops it to 1:1 aspect ratio from center, and resizes to target_size."""
    if not image_path or not os.path.exists(image_path):
        return None
    try:
        with Image.open(image_path) as img:
            img = img.convert("RGB")
            width, height = img.size
            min_dim = min(width, height)
            
            # Crop from the center
            left = (width - min_dim) / 2
            top = (height - min_dim) / 2
            right = (width + min_dim) / 2
            bottom = (height + min_dim) / 2
            
            cropped = img.crop((left, top, right, bottom))
            resized = cropped.resize((target_size, target_size), Image.Resampling.LANCZOS)
            return resized
    except Exception as e:
        print(f"Error loading/cropping image {image_path}: {e}")
        return None

def create_rounded_mask(size, radius=16):
    """Creates a 1-channel 'L' mask image with rounded corners."""
    mask = Image.new("L", size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle([(0, 0), size], radius=radius, fill=255)
    return mask

def find_exercise_image(base_name, index, search_dir="exercise_images"):
    """Looks up an image file matching base_name_{index} with common image extensions."""
    extensions = [".jpg", ".jpeg", ".png", ".webp"]
    for ext in extensions:
        path = os.path.join(search_dir, f"{base_name}_{index}{ext}")
        if os.path.exists(path):
            return path
    return None

def draw_muscle_badges(draw, label, muscles, x_start, y_offset, bg_color, text_color, max_width):
    """Draws a label followed by rounded capsule badges for each muscle in the list, with wrapping."""
    label_font = load_system_font("Arial Bold.ttf", 22)
    badge_font = load_system_font("Arial Bold.ttf", 20)
    
    # Draw Row Label
    draw.text((x_start, y_offset + 5), label, fill=COLOR_TEXT_MUTED, font=label_font)
    
    # Starting coordinate for badges
    badge_x = x_start + 160
    badge_height = 34
    
    for muscle in muscles:
        muscle = muscle.strip()
        if not muscle:
            continue
            
        w = get_text_width(muscle, badge_font)
        badge_width = w + 24 # padding
        
        # Check if badge exceeds column bounds, wrap if it does
        if badge_x + badge_width > x_start + max_width:
            y_offset += 42
            badge_x = x_start + 160
            
        box_coords = [(badge_x, y_offset), (badge_x + badge_width, y_offset + badge_height)]
        
        # Draw background capsule
        draw.rounded_rectangle(box_coords, radius=8, fill=bg_color)
        
        # Draw text centered in the badge
        draw.text((badge_x + 12, y_offset + 5), muscle, fill=text_color, font=badge_font)
        
        badge_x += badge_width + 12
        
    return y_offset

def draw_card(row):
    """Renders a single physical workout card based on row data."""
    # Read row details safely checking for NaN or null values
    def clean_val(val):
        if pd.isna(val) or val is None:
            return ""
        return str(val).strip()

    exercise_name = clean_val(row.get("Exercise_Name"))
    if not exercise_name or exercise_name.lower() == "nan":
        exercise_name = "Unnamed Exercise"
        
    print_name = clean_val(row.get("Print_Name"))
    if not print_name or print_name.lower() == "nan":
        print_name = exercise_name
        
    description = clean_val(row.get("Description"))
    if description.lower() == "nan":
        description = ""
        
    instructions = [
        clean_val(row.get("Form_Instruction_1")),
        clean_val(row.get("Form_Instruction_2")),
        clean_val(row.get("Form_Instruction_3")),
        clean_val(row.get("Form_Instruction_4"))
    ]
    instructions = [i for i in instructions if i and i.lower() != "nan"]
    
    video_url = clean_val(row.get("Video_URL"))
    if video_url.lower() == "nan":
        video_url = ""
        
    # Sanitize exercise name to base folder naming convention (lowercase with underscores)
    sanitized = "".join([c if c.isalnum() or c in (" ", "_", "-") else "" for c in exercise_name]).strip()
    base_name = sanitized.replace(" ", "_").lower()
    
    # Check CSV override path first, fallback to automatic naming lookup in standard folder
    img1_path = clean_val(row.get("Image_1_Path"))
    if not img1_path or img1_path.lower() == "nan":
        img1_path = find_exercise_image(base_name, 1)
        
    img2_path = clean_val(row.get("Image_2_Path"))
    if not img2_path or img2_path.lower() == "nan":
        img2_path = find_exercise_image(base_name, 2)
        
    primary_muscles = clean_val(row.get("Primary_Muscles"))
    if primary_muscles.lower() == "nan":
        primary_muscles = ""
        
    secondary_muscles = clean_val(row.get("Secondary_Muscles"))
    if secondary_muscles.lower() == "nan":
        secondary_muscles = ""
        
    # Load and crop exercise images as raw squares
    img1 = load_and_crop_square(img1_path, target_size=430)
    img2 = load_and_crop_square(img2_path, target_size=430)
    has_images = img1 is not None or img2 is not None
    has_qr = bool(video_url)
    
    # Parse muscle strings
    prim_list = [m.strip() for m in primary_muscles.split(",") if m.strip()]
    sec_list = [m.strip() for m in secondary_muscles.split(",") if m.strip()]
    
    card_id = clean_val(row.get("ID"))
    id_display = ""
    if card_id:
        if card_id.isdigit():
            id_display = f"#{int(card_id):02d}"
        else:
            id_display = card_id

    # 1. Initialize canvas
    img = Image.new("RGB", (IMAGE_WIDTH, IMAGE_HEIGHT), color=COLOR_BG)
    draw = ImageDraw.Draw(img)
    
    # 2. Render Header Title (Exercise Name) & ID
    font_size = 72
    title_font = load_system_font("Arial Black.ttf", font_size)
    
    title_max_width = USABLE_WIDTH
    id_font = None
    id_w = 0
    id_h = 0
    if id_display:
        id_font = load_system_font("Arial Bold.ttf", 44)
        id_w = get_text_width(id_display, id_font)
        id_h = get_text_height(id_display, id_font)
        title_max_width = USABLE_WIDTH - id_w - 40 # 40px gap between title and ID
        
    while font_size > 24:
        title_width = get_text_width(print_name, title_font)
        if title_width <= title_max_width:
            break
        font_size -= 2
        title_font = load_system_font("Arial Black.ttf", font_size)
        
    # Draw Title
    title_y = SAFE_MARGIN
    draw.text((SAFE_MARGIN, title_y), print_name, fill=COLOR_PRIMARY, font=title_font)
    
    # Draw ID right-aligned if present
    if id_display and id_font:
        id_x = IMAGE_WIDTH - SAFE_MARGIN - id_w
        # Center vertically with respect to the title area (from y=50 to y=180, mid point is 115)
        id_y = 115 - id_h // 2
        draw.text((id_x, id_y), id_display, fill=COLOR_ACCENT, font=id_font)
    
    # 3. Draw Divider line (4px thick, Teal accent, spanning usable width)
    divider_y = 180
    draw.rectangle(
        [(SAFE_MARGIN, divider_y), (IMAGE_WIDTH - SAFE_MARGIN, divider_y + 4)],
        fill=COLOR_ACCENT
    )
    
    # 4. Determine Text wrapping column width
    if has_images:
        # Left column is constrained to leave a 50px gap before Column 2 (which starts at x=1320)
        cues_max_width = 1320 - SAFE_MARGIN - 50 # 1220px usable width
    else:
        cues_max_width = USABLE_WIDTH # 1700px usable width
        
    # 5. Render Description and Instructions dynamically
    y_offset = 230
    
    # Render Description Section inside a styled Slate Card
    if description:
        # Heading (30pt bold)
        desc_title_font = load_system_font("Arial Bold.ttf", 30)
        draw.text((SAFE_MARGIN, y_offset), "OVERZICHT", fill=COLOR_ACCENT, font=desc_title_font)
        y_offset += 46
        
        # Wrap Description Body text
        desc_body_font = load_system_font("Arial Italic.ttf", 28)
        # Indent text slightly inside the card container (padding = 24px)
        desc_lines = wrap_text_by_pixels(description, desc_body_font, cues_max_width - 48)
        
        # Calculate Card dimensions
        padding = 24
        line_h = 38
        box_height = padding * 2 + len(desc_lines) * line_h - 4
        box_coords = [(SAFE_MARGIN, y_offset), (SAFE_MARGIN + cues_max_width, y_offset + box_height)]
        
        # Draw background and border
        draw.rounded_rectangle(box_coords, radius=16, fill=COLOR_CARD_BG, outline=COLOR_CARD_BORDER, width=2)
        
        # Draw Description lines inside Card
        text_y = y_offset + padding
        for line in desc_lines:
            draw.text((SAFE_MARGIN + padding, text_y), line, fill=COLOR_TEXT_BODY, font=desc_body_font)
            text_y += line_h
            
        y_offset += box_height + 40 # spacer before instructions heading
        
    # Render Form Instructions Checklist
    if instructions:
        # Heading (30pt bold)
        inst_title_font = load_system_font("Arial Bold.ttf", 30)
        draw.text((SAFE_MARGIN, y_offset), "CORRECTE UITVOERING", fill=COLOR_ACCENT, font=inst_title_font)
        y_offset += 58
        
        # Body list (28pt regular)
        cue_font = load_system_font("Arial.ttf", 28)
        line_spacing = 38
        cue_gap = 25
        
        for item in instructions:
            # Draw modern checkbox [ ] as a rounded rectangle matching font height (28x28 px)
            box_size = 28
            box_y = y_offset + 4 # aligned vertically with 28pt text line
            draw.rounded_rectangle(
                [(SAFE_MARGIN, box_y), (SAFE_MARGIN + box_size, box_y + box_size)],
                radius=6,
                outline=COLOR_BOX_BORDER,
                width=3
            )
            
            # Wrap and draw lines
            item_lines = wrap_text_by_pixels(item, cue_font, cues_max_width - 55)
            for line in item_lines:
                draw.text((SAFE_MARGIN + 55, y_offset), line, fill=COLOR_TEXT_BODY, font=cue_font)
                y_offset += line_spacing
                
            y_offset += cue_gap
            
    # Render Bottom Section: Muscles Engaged (Left side) & QR code Card (Right side)
    if prim_list or sec_list or has_qr:
        # Allocate bottom grid widths
        if has_images:
            muscles_max_width = 720
            qr_card_x = SAFE_MARGIN + 760 # 810px
            qr_card_w = 460
        else:
            muscles_max_width = 1180
            qr_card_x = SAFE_MARGIN + 1240 # 1290px
            qr_card_w = 460
            
        # Draw Muscles Engaged Heading & Badges
        if prim_list or sec_list:
            y_offset += 15
            muscles_y = y_offset
            muscles_title_font = load_system_font("Arial Bold.ttf", 30)
            draw.text((SAFE_MARGIN, muscles_y), "BETROKKEN SPIEREN", fill=COLOR_ACCENT, font=muscles_title_font)
            
            badge_y = muscles_y + 40
            if prim_list:
                badge_y = draw_muscle_badges(
                    draw, "PRIMAIR", prim_list, SAFE_MARGIN, badge_y,
                    bg_color="#CCFBF1", text_color="#0F766E", max_width=muscles_max_width
                )
                badge_y += 42
                
            if sec_list:
                badge_y = draw_muscle_badges(
                    draw, "SECUNDAIR", sec_list, SAFE_MARGIN, badge_y,
                    bg_color="#F1F5F9", text_color="#475569", max_width=muscles_max_width
                )
                
        # Draw QR Code Card (aligned vertically with muscles section heading)
        if has_qr:
            qr_card_y = y_offset
            qr_card_h = 160
            
            # Draw QR Card Container
            draw.rounded_rectangle(
                [(qr_card_x, qr_card_y), (qr_card_x + qr_card_w, qr_card_y + qr_card_h)],
                radius=16,
                fill=COLOR_CARD_BG,
                outline=COLOR_CARD_BORDER,
                width=2
            )
            
            # Generate and paste QR code (120x120px)
            qr_inset_size = 120
            qr_img = generate_qr_code(video_url, size=qr_inset_size)
            img.paste(qr_img, (qr_card_x + 20, qr_card_y + 20))
            
            # Tiny border around the QR stamp
            draw.rectangle(
                [(qr_card_x + 19, qr_card_y + 19), (qr_card_x + 20 + qr_inset_size, qr_card_y + 20 + qr_inset_size)],
                outline=COLOR_CARD_BORDER,
                width=1
            )
            
            # Labels inside QR Card
            scan_title_font = load_system_font("Arial Bold.ttf", 20)
            scan_sub_font = load_system_font("Arial.ttf", 16)
            
            text_x = qr_card_x + 20 + qr_inset_size + 20
            draw.text((text_x, qr_card_y + 40), "SCAN VOOR VIDEO", fill=COLOR_PRIMARY, font=scan_title_font)
            draw.text((text_x, qr_card_y + 75), "Bekijk uitvoering", fill=COLOR_TEXT_MUTED, font=scan_sub_font)
            draw.text((text_x, qr_card_y + 98), "instructievideo", fill=COLOR_TEXT_MUTED, font=scan_sub_font)

    # 9. Render Stacked Demonstration Images (with rounded corners and rounded outlines)
    if has_images:
        img_x = 1320
        img_size = 430
        mask = create_rounded_mask((img_size, img_size), radius=16)
        
        # Image 1 (POSITION 1)
        if img1:
            img_y1 = 230
            img.paste(img1, (img_x, img_y1), mask=mask)
            draw.rounded_rectangle(
                [(img_x - 1, img_y1 - 1), (img_x + img_size, img_y1 + img_size)],
                radius=16,
                outline=COLOR_CARD_BORDER,
                width=2
            )
            
        # Image 2 (POSITION 2)
        if img2:
            img_y2 = 690
            img.paste(img2, (img_x, img_y2), mask=mask)
            draw.rounded_rectangle(
                [(img_x - 1, img_y2 - 1), (img_x + img_size, img_y2 + img_size)],
                radius=16,
                outline=COLOR_CARD_BORDER,
                width=2
            )

    # 10. Save image as high-quality JPEG
    sanitized_name = "".join([c if c.isalnum() or c in (" ", "_", "-") else "" for c in exercise_name]).strip()
    sanitized_name = sanitized_name.replace(" ", "_").lower()
    filename = f"{sanitized_name}.jpg"
    filepath = os.path.join(OUTPUT_DIR, filename)
    
    img.save(filepath, "JPEG", quality=95)
    print(f"Generated card: {filepath} (Dimensions: {img.size[0]}x{img.size[1]})")

def main():
    # Enforce input file check
    csv_file = "workout_data.csv"
    if not os.path.exists(csv_file):
        print(f"Error: Required spreadsheet '{csv_file}' was not found in the current directory.")
        return
        
    # Ingest data using pandas
    try:
        df = pd.read_csv(csv_file)
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return
        
    # Normalize column names to be case-insensitive
    df.columns = [col.strip().lower() for col in df.columns]
    
    # Verify required headers
    required_cols = [
        "exercise_name", 
        "description", 
        "form_instruction_1", 
        "form_instruction_2", 
        "form_instruction_3", 
        "form_instruction_4", 
        "video_url"
    ]
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        print(f"Error: The input CSV is missing columns: {missing}")
        return
        
    # Clean output directory
    clean_output_directory()
    
    # Process each row
    for index, row in df.iterrows():
        # Map back to original case for dictionary lookup ease
        mapped_row = {
            "ID": row["id"] if "id" in row else "",
            "Exercise_Name": row["exercise_name"],
            "Print_Name": row["print_name"] if "print_name" in row else row["exercise_name"],
            "Description": row["description"],
            "Form_Instruction_1": row["form_instruction_1"],
            "Form_Instruction_2": row["form_instruction_2"],
            "Form_Instruction_3": row["form_instruction_3"],
            "Form_Instruction_4": row["form_instruction_4"],
            "Video_URL": row["video_url"],
            "Image_1_Path": row["image_1_path"] if "image_1_path" in row else "",
            "Image_2_Path": row["image_2_path"] if "image_2_path" in row else "",
            "Primary_Muscles": row["primary_muscles"] if "primary_muscles" in row else "",
            "Secondary_Muscles": row["secondary_muscles"] if "secondary_muscles" in row else ""
        }
        draw_card(mapped_row)
        
    print("\nAll cards generated successfully in './print_ready_cards/'")

if __name__ == "__main__":
    main()
