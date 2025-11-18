import os
from flask import Flask, request, jsonify
from sympy import sympify, solve, diff, integrate, latex
import pytesseract
from PIL import Image
import io

app = Flask(__name__)

def ocr_image(file_stream):
    try:
        image = Image.open(io.BytesIO(file_stream.read()))
        config = '--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789+-*/=()x[]{}.,^_ '
        text = pytesseract.image_to_string(image, config=config)
        return text.strip() or "x + 1"
    except:
        return "x + 1"

def get_solution_steps(expr_str):
    try:
        expr = sympify(expr_str.replace('^', '**'))
        steps = []
        result = None
        if 'integrate' in expr_str.lower():
            steps.append(f"चरण 1: ∫ {expr_str}")
            result = integrate(expr)
            steps.append(f"चरण 2: {latex(result)}")
        elif 'diff' in expr_str.lower():
            steps.append(f"चरण 1: {latex(expr)}")
            result = diff(expr)
            steps.append(f"चरण 2: {latex(result)}")
        else:
            steps.append(f"चरण 1: {latex(expr)}")
            result = solve(expr)
            steps.append(f"चरण 2: {latex(result)}")
        voice = " | ".join(steps) + f" | उत्तर: {str(result)}"
        return steps, str(result), voice
    except:
        return ["गलत फॉर्मूला!"], "Error", "समझ नहीं आया।"

@app.route('/', methods=['GET'])
def home():
    return "MathSnap.xyz - Flask App Running!"  # टेस्ट के लिए

@app.route('/solve', methods=['POST'])
def solve():
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
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
