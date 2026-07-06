import os
import shutil
import math
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import qrcode

# Color Palette Definitions (Premium Fitness Theme)
COLOR_BG = "#FAFAFA"          # Solid crisp light off-white
COLOR_PRIMARY = "#1E293B"     # Dark slate/charcoal for title and headers
COLOR_ACCENT = "#FF7257"      # Cat orange accent color
COLOR_CARD_BG = "#F8FAFC"     # Slate 50 background
COLOR_CARD_BORDER = "#E2E8F0" # Slate 200 border for photos & QR
COLOR_TEXT_MUTED = "#64748B"  # Slate 500 for secondary labels
COLOR_BOX_BORDER = "#FF7257"  # Cat orange border for checkboxes
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

def load_and_crop_image(image_path, target_width=480, target_height=360):
    """Loads an image, crops it to target_width:target_height aspect ratio from center, and resizes it."""
    if not image_path or not os.path.exists(image_path):
        return None
    try:
        with Image.open(image_path) as img:
            img = img.convert("RGB")
            img_w, img_h = img.size
            
            # Calculate aspect ratios
            target_ratio = target_width / target_height
            img_ratio = img_w / img_h
            
            if img_ratio > target_ratio:
                # Image is wider than target ratio, crop horizontal sides
                crop_h = img_h
                crop_w = int(crop_h * target_ratio)
                left = (img_w - crop_w) / 2
                top = 0
                right = left + crop_w
                bottom = crop_h
            else:
                # Image is taller than target ratio, crop vertical sides
                crop_w = img_w
                crop_h = int(crop_w / target_ratio)
                left = 0
                top = (img_h - crop_h) / 2
                right = crop_w
                bottom = top + crop_h
                
            cropped = img.crop((left, top, right, bottom))
            resized = cropped.resize((target_width, target_height), Image.Resampling.LANCZOS)
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
    label_font = load_system_font("Arial Bold.ttf", 24)
    badge_font = load_system_font("Arial Bold.ttf", 22)
    
    # Draw Row Label
    draw.text((x_start, y_offset + 4), label, fill=COLOR_TEXT_MUTED, font=label_font)
    
    # Starting coordinate for badges
    badge_x = x_start + 180
    badge_height = 38
    
    for muscle in muscles:
        muscle = muscle.strip()
        if not muscle:
            continue
            
        w = get_text_width(muscle, badge_font)
        badge_width = w + 24 # padding
        
        # Check if badge exceeds column bounds, wrap if it does
        if badge_x + badge_width > x_start + max_width:
            y_offset += 48
            badge_x = x_start + 180
            
        box_coords = [(badge_x, y_offset), (badge_x + badge_width, y_offset + badge_height)]
        
        # Draw background capsule
        draw.rounded_rectangle(box_coords, radius=8, fill=bg_color)
        
        # Draw text centered in the badge
        draw.text((badge_x + 12, y_offset + 4), muscle, fill=text_color, font=badge_font)
        
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
        
    raw_instructions = clean_val(row.get("Form_Instructions"))
    instructions = []
    if raw_instructions:
        instructions = [i.strip() for i in raw_instructions.split("|") if i.strip() and i.strip().lower() != "nan"]
    
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
        
    # Load and crop exercise images, balancing dimensions
    img1 = load_and_crop_image(img1_path, target_width=610, target_height=430)
    img2 = load_and_crop_image(img2_path, target_width=610, target_height=430)
    has_images = img1 is not None or img2 is not None
    has_qr = bool(video_url)
    
    # Parse muscle strings
    prim_list = [m.strip() for m in primary_muscles.split(",") if m.strip()]
    sec_list = [m.strip() for m in secondary_muscles.split(",") if m.strip()]
    
    # 1. Initialize canvas
    img = Image.new("RGB", (IMAGE_WIDTH, IMAGE_HEIGHT), color=COLOR_BG)
    draw = ImageDraw.Draw(img)
    
    # 2. Render Header Title (Exercise Name)
    has_qr = bool(video_url)
    title_x = 180
    title_max_width = IMAGE_WIDTH - SAFE_MARGIN - title_x # 1800 - 50 - 180 = 1570px
    
    font_size = 72
    title_font = load_system_font("Arial Black.ttf", font_size)
    
    while font_size > 24:
        title_width = get_text_width(print_name, title_font)
        if title_width <= title_max_width:
            break
        font_size -= 2
        title_font = load_system_font("Arial Black.ttf", font_size)
        
    # Draw Title (shifted right to make room for the hole punch guide)
    title_y = SAFE_MARGIN
    draw.text((title_x, title_y), print_name, fill=COLOR_PRIMARY, font=title_font)
    
    # Draw faint punch hole guide in the top-left corner (centered at x=90, y=95, diameter=30px)
    hole_center_x = 90
    hole_center_y = 95
    hole_radius = 15
    draw.ellipse(
        [(hole_center_x - hole_radius, hole_center_y - hole_radius), 
         (hole_center_x + hole_radius, hole_center_y + hole_radius)],
        outline="#CBD5E1", # Slate 300 (faint gray)
        width=2
    )
    # Add a tiny center dot (crosshair style)
    draw.ellipse(
        [(hole_center_x - 2, hole_center_y - 2), (hole_center_x + 2, hole_center_y + 2)],
        fill="#CBD5E1"
    )
    
    # Draw Logo (Top Right)
    logo_path = "misc/cat.png"
    if os.path.exists(logo_path):
        try:
            with Image.open(logo_path) as logo_img:
                logo_img = logo_img.convert("RGBA")
                # Scale logo to height 120px
                logo_h = 120
                logo_w = int(logo_h * (logo_img.width / logo_img.height))
                logo_resized = logo_img.resize((logo_w, logo_h), Image.Resampling.LANCZOS)
                
                # Flip logo horizontally so the cat faces left
                logo_flipped = logo_resized.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
                
                logo_x = IMAGE_WIDTH - SAFE_MARGIN - logo_w
                logo_y = 50
                img.paste(logo_flipped, (logo_x, logo_y), mask=logo_flipped.split()[3])
        except Exception as e:
            print(f"Error loading logo {logo_path}: {e}")
    
    # 3. Draw Divider line (4px thick, Teal accent, spanning usable width)
    divider_y = 180
    draw.rectangle(
        [(SAFE_MARGIN, divider_y), (IMAGE_WIDTH - SAFE_MARGIN, divider_y + 4)],
        fill=COLOR_ACCENT
    )
    
    # 4. Determine Text wrapping column width
    if has_images:
        # Left column is constrained to leave a 50px gap before Column 2 (which starts at x=1140)
        cues_max_width = 1140 - SAFE_MARGIN - 50 # 1040px usable width
    else:
        cues_max_width = USABLE_WIDTH # 1700px usable width
        
    # 5. Render Description and Instructions dynamically
    y_offset = 220
    
    # Render Description Section inside a styled Slate Card
    if description:
        # Wrap Description Body text
        desc_body_font = load_system_font("Arial Italic.ttf", 28)
        # Indent text slightly inside the card container (padding = 24px)
        desc_lines = wrap_text_by_pixels(description, desc_body_font, cues_max_width - 48)
        
        # Calculate Card dimensions
        padding = 24
        line_h = 38
        box_height = padding * 2 + len(desc_lines) * line_h
        box_coords = [(SAFE_MARGIN, y_offset), (SAFE_MARGIN + cues_max_width, y_offset + box_height)]
        
        # Draw background and border
        draw.rounded_rectangle(box_coords, radius=16, fill=COLOR_CARD_BG, outline=COLOR_CARD_BORDER, width=2)
        
        # Draw Description lines inside Card
        text_y = y_offset + padding
        for line in desc_lines:
            draw.text((SAFE_MARGIN + padding, text_y), line, fill=COLOR_TEXT_BODY, font=desc_body_font)
            text_y += line_h
            
        y_offset += box_height + 40 # spacer before instructions list
        
    # Render Form Instructions Numbered List
    if instructions:
        # Body list (28pt regular)
        cue_font = load_system_font("Arial.ttf", 28)
        num_font = load_system_font("Arial Bold.ttf", 28)
        line_spacing = 38
        
        for idx, item in enumerate(instructions, start=1):
            # Draw step number (e.g. "1.") in accent color and bold font
            num_text = f"{idx}."
            draw.text((SAFE_MARGIN, y_offset), num_text, fill=COLOR_ACCENT, font=num_font)
            
            # Wrap and draw lines (indented 60px)
            item_lines = wrap_text_by_pixels(item, cue_font, cues_max_width - 60)
            for line in item_lines:
                draw.text((SAFE_MARGIN + 60, y_offset), line, fill=COLOR_TEXT_BODY, font=cue_font)
                y_offset += line_spacing
                
            y_offset += 16 # gap between steps
            
        y_offset += 20 # additional spacer after instructions list
            
    # Render Bottom Area (Mistake, Muscles & QR Code side-by-side)
    avoid_mistake = clean_val(row.get("Avoid_Mistake"))
    if avoid_mistake and avoid_mistake.lower() == "nan":
        avoid_mistake = ""
        
    if avoid_mistake or prim_list or sec_list or has_qr:
        # Anchor the bottom area to start at y = 810 to align with the bottom of the card,
        # but let it push down dynamically if instructions are very long
        y_start = max(y_offset + 20, 740)
        
        # Determine columns
        qr_card_w = 280
        qr_card_h = 320
        qr_card_x = SAFE_MARGIN + cues_max_width - qr_card_w # 50 + 1040 - 280 = 810px
        qr_card_y = y_start
        
        # Left columns width for mistake and muscles:
        bottom_left_max_width = cues_max_width - qr_card_w - 40 # 1040 - 280 - 40 = 720px
        
        # Draw on the left side:
        left_y = y_start
        
        # 1. Common Mistake Section
        if avoid_mistake:
            regular_font = load_system_font("Arial.ttf", 28)
            bold_font = load_system_font("Arial Bold.ttf", 28)
            
            full_mistake_text = f"Let op: {avoid_mistake}"
            mistake_lines = wrap_text_by_pixels(full_mistake_text, regular_font, bottom_left_max_width)
            
            line_h = 38
            for idx, line in enumerate(mistake_lines):
                if idx == 0 and line.startswith("Let op: "):
                    # Draw "Let op: " in bold
                    prefix = "Let op: "
                    suffix = line[len(prefix):]
                    draw.text((SAFE_MARGIN, left_y), prefix, fill=COLOR_TEXT_BODY, font=bold_font)
                    
                    bold_w = get_text_width(prefix, bold_font)
                    draw.text((SAFE_MARGIN + bold_w, left_y), suffix, fill=COLOR_TEXT_BODY, font=regular_font)
                else:
                    draw.text((SAFE_MARGIN, left_y), line, fill=COLOR_TEXT_BODY, font=regular_font)
                left_y += line_h
                
            left_y += 25 # spacer before muscles
            
        # 2. Muscles Engaged Section
        if prim_list or sec_list:
            muscles_title_font = load_system_font("Arial Bold.ttf", 30)
            draw.text((SAFE_MARGIN, left_y), "BETROKKEN SPIEREN", fill=COLOR_ACCENT, font=muscles_title_font)
            
            badge_y = left_y + 45
            if prim_list:
                badge_y = draw_muscle_badges(
                    draw, "PRIMAIR", prim_list, SAFE_MARGIN, badge_y,
                    bg_color="#FFEBE7", text_color="#C22E14", max_width=bottom_left_max_width
                )
                badge_y += 48
                
            if sec_list:
                badge_y = draw_muscle_badges(
                    draw, "SECUNDAIR", sec_list, SAFE_MARGIN, badge_y,
                    bg_color="#F1F5F9", text_color="#475569", max_width=bottom_left_max_width
                )
                
        # Draw QR Code Card (on the right of the bottom area)
        if has_qr:
            # Draw QR Card Container
            draw.rounded_rectangle(
                [(qr_card_x, qr_card_y), (qr_card_x + qr_card_w, qr_card_y + qr_card_h)],
                radius=16,
                fill=COLOR_CARD_BG,
                outline=COLOR_CARD_BORDER,
                width=2
            )
            
            # Generate and paste QR code (240x240px for maximum readability)
            qr_inset_size = 240
            qr_img = generate_qr_code(video_url, size=qr_inset_size)
            qr_x = qr_card_x + (qr_card_w - qr_inset_size) // 2 # Centered horizontally (qr_card_x + 20)
            img.paste(qr_img, (qr_x, qr_card_y + 20))
            
            # Tiny border around the QR stamp
            draw.rectangle(
                [(qr_x - 1, qr_card_y + 19), (qr_x + qr_inset_size, qr_card_y + 20 + qr_inset_size)],
                outline=COLOR_CARD_BORDER,
                width=1
            )
            
            # Label below QR Card (centered horizontally)
            scan_title_font = load_system_font("Arial Bold.ttf", 20)
            label_text = "SCAN VOOR VIDEO"
            label_w = get_text_width(label_text, scan_title_font)
            label_x = qr_card_x + (qr_card_w - label_w) // 2
            draw.text((label_x, qr_card_y + 20 + qr_inset_size + 15), label_text, fill=COLOR_PRIMARY, font=scan_title_font)

    # 9. Render Stacked Demonstration Images (with rounded corners and rounded outlines)
    if has_images:
        img_x = 1140
        img_w = 610
        img_h = 430
        mask = create_rounded_mask((img_w, img_h), radius=16)
        
        # Image 1 (POSITION 1)
        if img1:
            img_y1 = 230
            img.paste(img1, (img_x, img_y1), mask=mask)
            draw.rounded_rectangle(
                [(img_x - 1, img_y1 - 1), (img_x + img_w, img_y1 + img_h)],
                radius=16,
                outline=COLOR_CARD_BORDER,
                width=2
            )
            
        # Image 2 (POSITION 2)
        if img2:
            img_y2 = 710
            img.paste(img2, (img_x, img_y2), mask=mask)
            draw.rounded_rectangle(
                [(img_x - 1, img_y2 - 1), (img_x + img_w, img_y2 + img_h)],
                radius=16,
                outline=COLOR_CARD_BORDER,
                width=2
            )

    # 10. Save image as high-quality JPEG
    sanitized_name = "".join([c if c.isalnum() or c in (" ", "_", "-") else "" for c in exercise_name]).strip()
    sanitized_name = sanitized_name.replace(" ", "_").lower()
    filename = f"{sanitized_name}.jpg"
    filepath = os.path.join(OUTPUT_DIR, filename)
    
    img.save(filepath, "JPEG", quality=95, dpi=(300, 300))
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
        "form_instructions", 
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
            "Form_Instructions": row["form_instructions"],
            "Avoid_Mistake": row["avoid_mistake"] if "avoid_mistake" in row else "",
            "Video_URL": row["video_url"],
            "Image_1_Path": row["image_1_path"] if "image_1_path" in row else "",
            "Image_2_Path": row["image_2_path"] if "image_2_path" in row else "",
            "Primary_Muscles": row["primary_muscles"] if "primary_muscles" in row else "",
            "Secondary_Muscles": row["secondary_muscles"] if "secondary_muscles" in row else ""
        }
        draw_card(mapped_row)
        
    print("\nAll cards generated successfully in './print_ready_cards/'")
    
    # Auto-bundle all cards into a single PDF
    bundle_cards_to_pdf()

def bundle_cards_to_pdf(pdf_filename="kettlebell_kaarten.pdf"):
    """Bundles all generated JPEG cards in the output directory into a single PDF file."""
    if not os.path.exists(OUTPUT_DIR):
        print(f"Error: Output directory '{OUTPUT_DIR}' does not exist.")
        return None
        
    # Get all .jpg files in the directory
    jpg_files = [f for f in os.listdir(OUTPUT_DIR) if f.endswith(".jpg")]
    if not jpg_files:
        print("No JPEG cards found to bundle.")
        return None
        
    # Sort files alphabetically so they are ordered consistently in the PDF
    jpg_files.sort()
    
    images = []
    for f in jpg_files:
        path = os.path.join(OUTPUT_DIR, f)
        try:
            # Open image and convert to RGB (PDF format requires RGB)
            img = Image.open(path).convert("RGB")
            images.append(img)
        except Exception as e:
            print(f"Failed to open image {path} for PDF bundling: {e}")
            
    if not images:
        print("No valid images opened for PDF bundling.")
        return None
        
    pdf_path = os.path.join(OUTPUT_DIR, pdf_filename)
    try:
        # Save as a single multi-page PDF
        images[0].save(pdf_path, "PDF", resolution=300.0, save_all=True, append_images=images[1:])
        print(f"Successfully bundled all cards into: {pdf_path}")
        return pdf_path
    except Exception as e:
        print(f"Failed to save PDF: {e}")
        return None

if __name__ == "__main__":
    main()
