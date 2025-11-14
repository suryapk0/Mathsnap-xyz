from flask import Flask, request, jsonify
from sympy import sympify, solve, diff, integrate, latex
import json, requests

app = Flask(__name__)

# Mathpix API (फ्री: mathpix.com → Dashboard से ID/Key लो)
MATHPIX_ID = "YOUR_MATHPIX_APP_ID"
MATHPIX_KEY = "YOUR_MATHPIX_APP_KEY"

def ocr_image(file_stream):
    try:
        r = requests.post("https://api.mathpix.com/v3/text",
            files={"file": file_stream},
            data={"options_json": json.dumps({"math_inline_delimiters": ["$", "$"]})},
            headers={"app_id": MATHPIX_ID, "app_key": MATHPIX_KEY})
        return r.json().get("text", "")
    except:
        return "x + 1"

def get_solution_steps(expr_str):
    try:
        expr = sympify(expr_str.replace('^', '**'))
        steps = []
        result = None
        if 'integrate' in expr_str.lower():
            steps.append(f"∫ {expr_str}")
            result = integrate(expr)
            steps.append(f"हल → {latex(result)}")
        elif 'diff' in expr_str.lower():
            steps.append(f"फंक्शन → {latex(expr)}")
            result = diff(expr)
            steps.append(f"अवकलन → {latex(result)}")
        else:
            steps.append(f"समीकरण → {latex(expr)}")
            result = solve(expr)
            steps.append(f"हल → {latex(result)}")
        voice = " | ".join(steps) + f" | अंतिम उत्तर: {str(result)}"
        return steps, str(result), voice
    except:
        return ["समझ नहीं आया!"], "Error", "गलत इनपुट।"

@app.route('/solve', methods=['POST'])
def solve():
    text = request.form.get('text', '')
    image = request.files.get('image')
    latex_text = ocr_image(image) if image else text
    steps, answer, voice = get_solution_steps(latex_text)
    return jsonify({'steps': steps, 'answer': answer, 'voice': voice})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
