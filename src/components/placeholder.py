from PIL import Image, ImageDraw, ImageFont
import os

def create_placeholder_image(output_path, size=(32, 32)):
    """Create a simple placeholder image"""
    # Create a blank image with a transparent background
    img = Image.new('RGBA', size, color=(0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Draw a rectangle with a border
    draw.rectangle(
        [(0, 0), (size[0] - 1, size[1] - 1)],
        outline=(100, 100, 100, 255),
        fill=(50, 50, 50, 128)
    )
    
    # Draw an X across the image
    draw.line([(0, 0), (size[0] - 1, size[1] - 1)], fill=(150, 150, 150, 200), width=1)
    draw.line([(0, size[1] - 1), (size[0] - 1, 0)], fill=(150, 150, 150, 200), width=1)
    
    # Ensure the directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Save the image
    img.save(output_path)
    print(f"Placeholder image created at: {output_path}")

if __name__ == "__main__":
    # Get the base directory (src folder)
    base_dir = os.path.dirname(os.path.abspath(__file__))
    src_dir = os.path.dirname(base_dir)
    
    # Create placeholder images for all required icons
    icons = [
        "home.png", "cleaner.png", "gpu.png", "repair.png", "dism.png",
        "network.png", "disk.png", "boot.png", "virus.png", "settings.png",
        "icon.png", "arrow.png", "optimize.png", "clean.png", "cpu.png",
        "memory.png", "temperature.png", "info.png", "placeholder.png"
    ]
    
    for icon in icons:
        output_path = os.path.join(src_dir, "assets", "images", icon)
        create_placeholder_image(output_path) 