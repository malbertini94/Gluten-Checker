# -*- coding: utf-8 -*-
import cv2
import numpy as np
import requests
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# New route to serve the scanner page
@app.route('/')
def home():
    return render_template('index.html')  # Sends index.html to the user's browser

# Keep your existing /scan API route
@app.route('/scan', methods=['POST'])
def scan():
    barcode = request.json.get('barcode')

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
    return render_template('index.html')

@app.route('/scan', methods=['POST'])
def scan():
    barcode = request.json.get('barcode')  # Expects {"barcode": "123456789"}
    if barcode:
        name, ingredients = get_product_info(barcode)
        if name:
            result = check_gluten(ingredients)
            return jsonify({"product": name, "status": result})
    return jsonify({"error": "No barcode provided"})