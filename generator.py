from PIL import Image, ImageDraw, ImageFont
import os

def generate_meme(template_name, texts, font_size=36):
    """
    Generate a meme by overlaying text on a template image.
    
    Args:
        template_name: Name of the template file
        texts: List of dictionaries with text, x, and y coordinates
               Example: [{"text": "Hello World", "x": 50, "y": 100}]
    
    Returns:
        Path to the generated meme file
    """
    template_path = f"static/templates/{template_name}"
    
    try:
        img = Image.open(template_path)
    except FileNotFoundError:
        raise Exception(f"Template not found at {template_path}")
    except Exception as e:
        raise Exception(f"Could not open template image: {str(e)}")
    
    # Convert to RGB if necessary (for JPEG output)
    if img.mode != 'RGB':
        img = img.convert('RGB')
    
    draw = ImageDraw.Draw(img)

    # Try to load a better font, fall back to default
    font = None
    font_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/System/Library/Fonts/Arial.ttf",
        "arial.ttf"
    ]
    
    for font_path in font_paths:
        try:
            font = ImageFont.truetype(font_path, font_size)
            break
        except Exception:
            continue
    
    if font is None:
        try:
            font = ImageFont.load_default()
            print("Using default font as fallback")
        except Exception as e:
            print(f"Could not load any font: {e}")
            font = None

    # Place each text at given coordinates with outline for better visibility
    for t in texts:
        text = t["text"]
        x, y = t["x"], t["y"]
        text_font_size = t.get("size", font_size)
        
        # Load font with specific size for this text
        text_font = None
        for font_path in font_paths:
            try:
                text_font = ImageFont.truetype(font_path, text_font_size)
                break
            except Exception:
                continue
        
        if text_font is None:
            text_font = font  # fallback to default font
        
        if text_font:
            # Add black outline for better text visibility
            outline_width = 2
            for adj_x in range(-outline_width, outline_width + 1):
                for adj_y in range(-outline_width, outline_width + 1):
                    draw.text((x + adj_x, y + adj_y), text, font=text_font, fill="black")
            
            # Draw main text in white
            draw.text((x, y), text, font=text_font, fill="white")
        else:
            # Fallback without font
            draw.text((x, y), text, fill="white")

    # Ensure output directory exists
    os.makedirs("static/memes", exist_ok=True)

    # Generate unique filename
    base_name = os.path.splitext(template_name)[0]
    output_path = f"static/memes/{base_name}_meme.jpg"
    
    # Handle duplicate filenames
    counter = 1
    while os.path.exists(output_path):
        output_path = f"static/memes/{base_name}_meme_{counter}.jpg"
        counter += 1

    try:
        img.save(output_path, "JPEG", quality=95)
        return output_path
    except Exception as e:
        raise Exception(f"Could not save meme: {str(e)}")
