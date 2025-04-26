# -*- coding: utf-8 -*-
import cv2
import numpy as np
import requests
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

def get_product_info(barcode):
    url = f"https://world.openfoodfacts.org/api/v0/product/{barcode}.json"
    response = requests.get(url)
    data = response.json()
    if data.get('status') == 1:
        product = data['product']
        name = product.get('product_name', 'Unknown Product')
        ingredients = product.get('ingredients_text', None)
        return name, ingredients
    else:
        return None, None

def check_gluten(ingredients):
    if not ingredients or ingredients.strip() == "":
        return "Unknown: Check product details on the package"

    gluten_keywords = [
        'wheat', 'barley', 'rye', 'malt', 'gluten',
        'bl�', 'orge', 'seigle', 'grano', 'orzo',
        'segale', 'malto', 'glutine', 'weizen', 'gerste',
        'roggen', 'malz'
    ]
    if any(word in ingredients.lower() for word in gluten_keywords):
        return "Not Safe to Eat (Contains Gluten)"
    else:
        return "Safe to Eat (Gluten-Free)"

@app.route('/')
def home():
    return render_template('upload.html')  # New HTML page for uploads

@app.route('/scan', methods=['POST'])
def scan():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"})
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "Empty filename"})
    
    # Read the uploaded image
    img_bytes = file.read()
    img = cv2.imdecode(np.frombuffer(img_bytes, np.uint8), cv2.IMREAD_COLOR)
    
    # Detect barcode
    detector = cv2.barcode_BarcodeDetector()
    retval, decoded_info, _, _ = detector.detectAndDecodeMulti(img)
    
    if retval and decoded_info[0]:
        barcode = decoded_info[0]
        name, ingredients = get_product_info(barcode)
        if name:
            return jsonify({
                "product": name,
                "status": check_gluten(ingredients),
                "barcode": barcode
            })
    
    return jsonify({"error": "No barcode detected"})

if __name__ == '__main__':
    app.run(debug=True)
