import cv2
import numpy as np
import requests
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

def scan_barcode():
    cap = cv2.VideoCapture(0)
    detector = cv2.barcode_BarcodeDetector()
    last_barcode = None

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        retval, decoded_info, points, _ = detector.detectAndDecodeMulti(frame)
        if retval:
            for barcode in decoded_info:
                if barcode and barcode != last_barcode:
                    cap.release()
                    cv2.destroyAllWindows()
                    return barcode
        cv2.imshow('Barcode Scanner - Press Q to Quit', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    return None

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
        'blé', 'orge', 'seigle', 'grano', 'orzo',
        'segale', 'malto', 'glutine', 'weizen', 'gerste',
        'roggen', 'malz'
    ]
    if any(word in ingredients.lower() for word in gluten_keywords):
        return "Not Safe to Eat (Contains Gluten)"
    else:
        return "Safe to Eat (Gluten-Free)"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/scan', methods=['POST'])
def scan():
    barcode = scan_barcode()
    if barcode:
        name, ingredients = get_product_info(barcode)
        if name:
            result = check_gluten(ingredients)
            return jsonify({"product": name, "status": result})
        else:
            return jsonify({"error": "Product not found"})
    return jsonify({"error": "No barcode detected"})

if __name__ == "__main__":
    app.run(debug=True, port=5000)