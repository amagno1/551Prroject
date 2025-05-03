from PIL import Image

def remove_whitespace(image_path, save_path):
    """Remove whitespace and transparent pixels around a PNG image"""

    img = Image.open(image_path)
    img = img.convert("RGBA")
    data = img.getdata()

    threshold = (200, 200, 200, 255)  # White color threshold to ignore
    
    # List to store the non-white and non-transparent pixels
    non_background_pixels = []
    
    # Loop through each pixel and check if it's not white or transparent
    for pixel in data:
        if pixel[0] < threshold[0] or pixel[1] < threshold[1] or pixel[2] < threshold[2] or pixel[3] < threshold[3]:
            non_background_pixels.append(pixel)
        else:
            non_background_pixels.append((255, 255, 255, 0))  

    img.putdata(non_background_pixels)

    bbox = img.getbbox()
    cropped_img = img.crop(bbox)

    cropped_img.save(save_path, "PNG")

remove_whitespace('resized_wall.png', 'wall.png')
