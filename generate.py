from PIL import Image, ImageDraw, ImageFont
import os

def create_icon(size, filename):
    # 1. Create an RGBA image (the 'A' allows for transparent corners)
    # Background is fully transparent (0, 0, 0, 0)
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # 2. Define a small border radius (15% of the size)
    radius = int(size * 0.15)
    
    # 3. Draw the Indigo background with the border radius
    # fill='#4f46e5' is your specific indigo color
    draw.rounded_rectangle(
        (0, 0, size, size), 
        radius=radius, 
        fill='#4f46e5'
    )
    
    # 4. Draw the 'N' in the center
    font_size = int(size * 0.6)
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        font = ImageFont.load_default()

    text = "N"
    bbox = draw.textbbox((0, 0), text, font=font)
    w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    
    # Centering the text
    draw.text(((size - w) / 2, (size - h) / 3), text, fill="white", font=font)
    
    # 5. Save the file
    os.makedirs("static/icons", exist_ok=True)
    img.save(f"static/icons/{filename}")
    print(f"Created {filename} with small border radius.")

# Generate both required sizes
create_icon(192, "icon-192.png")
create_icon(512, "icon-512.png")