import os
from flask import Flask, request, jsonify, send_from_directory
import shutil
from wand.image import Image as im
import re
import threading
import time

app = Flask(__name__)

# Define directories for uploads and outputs
UPLOAD_FOLDER = './uploads'
OUTPUT_FOLDER = './downloads'  # Make sure it's the same folder for download
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def is_arabic(text):
    return bool(re.fullmatch(r'[\u0600-\u06FF\s]+', text))

def delete_file_after_timeout(file_path):
    time.sleep(600)  # Sleep for 10 minutes (600 seconds)
    if os.path.exists(file_path):
        os.remove(file_path)
        print(f"File {file_path} has been deleted after 10 minutes.")
@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

# Process form and handle name input
@app.route('/process', methods=['POST'])
def process_file():
    name = request.form.get('name')

    # Check if name is provided
    if not name:
        return jsonify({"error": "Name is required"}), 400

    # Sanitize the name to avoid file system issues (optional)
    sanitized_name = name.replace(" ", "_").replace("/", "_")

    # Path to the template SVG file
    svg_file_path = os.path.join(UPLOAD_FOLDER, 'template.svg')

    # Check if the template SVG file exists
    if not os.path.exists(svg_file_path):
        return jsonify({"error": "SVG template file not found"}), 400

    # Path for the new modified SVG in the output folder
    output_svg_path = os.path.join(OUTPUT_FOLDER, f'{sanitized_name}_template.svg')

    # Copy the template SVG to the outputs folder with a new name
    shutil.copy(svg_file_path, output_svg_path)

    with open(output_svg_path, 'r', encoding='utf-8') as f:
        svg_content = f.read()




    with open(output_svg_path, 'w', encoding='utf-8') as f:
            f.write(svg_content)
# Replace placeholder text with a properly positioned tspan


    with open(output_svg_path, 'r', encoding='utf-8') as f:
        svg_content = f.read()
    # Replace placeholder text with the user's n
    #
    newtext="" 
    name=name.split()
    for x,i in enumerate(name):
        if not is_arabic(i):
            i =i.capitalize()
        newtext+=f'<text x="50%" y="{19.5+(x*4)}%" dominant-baseline="middle" text-anchor="middle" font-size="45px" style="text-transform: capitalize;" fill="white">{i}</text>'
    svg_content = re.sub(r'<text[^>]*>.*?</text>', newtext, svg_content, flags=re.DOTALL)
    # Save the modified SVG with UTF-8 encoding
    with open(output_svg_path, 'w', encoding='utf-8') as f:
        f.write(svg_content)

    # Convert the modified SVG to PNG using wand
    png_path = os.path.join(OUTPUT_FOLDER, f"{sanitized_name}.png")
    png_path=png_path.replace('\\','/')
    print(png_path)
    if os.path.exists(png_path):
        os.remove(png_path)
    with im(filename=output_svg_path) as img:
        img.format = 'png'
        img.save(filename=png_path)

    deletion_thread = threading.Thread(target=delete_file_after_timeout, args=(png_path,))
    deletion_thread.start()
    deletion_thread1 = threading.Thread(target=delete_file_after_timeout, args=(output_svg_path,))
    deletion_thread1.start()
    return jsonify({"download": f"/downloads/{sanitized_name}.png"})

# Serve the generated PNG file
@app.route('/downloads/<filename>')
def download_file(filename):
    # Ensure the file exists before serving
    file_path = os.path.join(OUTPUT_FOLDER, filename)
    if os.path.exists(file_path):
        return send_from_directory(OUTPUT_FOLDER, filename)
    return jsonify({"error": "File not found"}), 404

if __name__ == '__main__':
    app.run(debug=True, port=5000)
