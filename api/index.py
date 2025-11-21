import os
from flask import Flask, request, jsonify
from flask_cors import CORS  # ← ये लाइन नई है
from sympy import sympify, solve, diff, integrate, latex
import pytesseract
from PIL import Image
import io

app = Flask(__name__)
CORS(app)  # ← ये लाइन CORS error को 100% खत्म कर देगी

def ocr_image(file_stream):
    try:
        image = Image.open(io.BytesIO(file_stream.read()))
        config = '--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789+-*/=()x[]{}.,^_ '
        text = pytesseract.image_to_string(image, config=config)
        return text.strip() or "x + 1"
    except Exception as e:
        return "x + 1"

def get_solution_steps(expr_str):
    try:
        expr = sympify(expr_str.replace('^', '**'))
        steps = []
        if 'integrate' in expr_str.lower():
            result = integrate(expr)
            steps = [f"∫ {expr_str}", f"{latex(result)}"]
        elif 'diff' in expr_str.lower():
            result = diff(expr)
            steps = [f"Derivative of {latex(expr)}", f"{latex(result)}"]
        else:
            result = solve(expr)
            steps = [f"Equation: {latex(expr)}", f"Solution: {latex(result)}"]
        voice = " | ".join(steps) + f" | Final answer {str(result)}"
        return steps, str(result), voice
    except:
        return ["समझ नहीं आया"], "Error", "गलत सवाल"

@app.route('/api/solve', methods=['POST', 'OPTIONS'])  # OPTIONS भी जरूरी
def solve():
    if request.method == 'OPTIONS':
        return '', 200
    text = request.form.get('text', '')
    image = request.files.get('image')
    if image:
        image.seek(0)
        latex_text = ocr_image(image)
    else:
        latex_text = text
    steps, answer, voice = get_solution_steps(latex_text)
    return jsonify({'steps': steps, 'answer': answer, 'voice': voice})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
