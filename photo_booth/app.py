from flask import Flask, render_template, request, send_file
from PIL import Image, ImageDraw, ImageFont, ImageOps
import datetime
from io import BytesIO

app = Flask(__name__)

def process_image(img, effect):
    if img.mode == 'RGBA':
        img = img.convert('RGB')
    if effect == "NORMAL":
        return img
    elif effect == "POSTERIZE":
        return ImageOps.posterize(img, 2)
    elif effect == "GRAYSCALE":
        return ImageOps.grayscale(img)
    elif effect == "SEPIA":
        return ImageOps.colorize(ImageOps.grayscale(img), 'black', '#826c56')
    
def add_text(img, text, position):
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype('Arial.ttf', 150)
    draw.text(position, text, font=font, fill="black")
    return img

def create_strip(images, border_height=100, bottom_margin=600):
    widths, heights = zip(*(i.size for i in images))
    total_height = sum(heights) + (border_height * (len(images) - 1)) + bottom_margin
    max_width = max(widths)
    strip = Image.new('RGB', (max_width, total_height), 'white')
    y_offset = 0
    for img in images:
        strip.paste(img, (0, y_offset))
        y_offset += img.height + border_height

    title = "Photo Booth Strip"
    current_datetime = datetime.datetime.now()
    formatted_date = current_datetime.strftime('%Y-%m-%d')
    date = formatted_date
    add_text(strip, title, (200, y_offset))
    add_text(strip, date, (400, y_offset+200))

    return strip

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        images = [Image.open(request.files[f'image{i}']) for i in range(1, 4)]
        effects = [request.form[f'filter{i}'] for i in range(1, 4)]
        processed_images = [process_image(img, effect) for img, effect in zip(images, effects)]
        photo_strip = create_strip(processed_images)
        byte_io = BytesIO()
        photo_strip.save(byte_io, 'JPEG')
        byte_io.seek(0)
        return send_file(byte_io, as_attachment=True, download_name='photo_booth_strip.jpg')
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)