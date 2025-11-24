from flask import Flask, request, jsonify
from flask_cors import CORS
from sympy import sympify, solve, integrate, diff, latex
import io
from PIL import Image
import pytesseract

app = Flask(__name__)
CORS(app)

def ocr_image(file_stream):
    try:
        img = Image.open(io.BytesIO(file_stream.read()))
        text = pytesseract.image_to_string(img, config='--psm 6')
        return text.strip() or "x + 1"
    except:
        return "x + 1"

def get_solution(expr_str):
    try:
        expr = sympify(expr_str.replace('^', '**'))
        if 'integrate' in expr_str.lower():
            result = integrate(expr)
        elif 'diff' in expr_str.lower() or 'derivative' in expr_str.lower():
            result = diff(expr)
        else:
            result = solve(expr)
        return [f"सवाल: {expr_str}", f"जवाब: {latex(result)}"], str(result)
    except:
        return ["समझ नहीं आया"], "Error"

@app.route('/api/solve', methods=['POST'])
def solve():
    text = request.form.get('text', '')
    image = request.files.get('image')
    input_text = ocr_image(image) if image else text
    steps, answer = get_solution(input_text)
    return jsonify({"steps": steps, "answer": answer, "voice": " ".join(steps)})

# Vercel के लिए जरूरी
def handler(event, context):
    from mangum import Mangum
    return Mangum(app)(event, context)
