from fastapi import FastAPI, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from sympy import sympify, solve, integrate, diff, latex
from PIL import Image
import pytesseract
import io

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def ocr_image(file):
    try:
        img = Image.open(io.BytesIO(file))
        text = pytesseract.image_to_string(img, config="--psm 6")
        return text.strip() or "x + 1"
    except:
        return "x + 1"

def get_solution(expr_str):
    try:
        expr = sympify(expr_str.replace("^", "**"))
        if "integrate" in expr_str.lower():
            result = integrate(expr)
        elif "diff" in expr_str.lower() or "derivative" in expr_str.lower():
            result = diff(expr)
        else:
            result = solve(expr)

        return [f"सवाल: {expr_str}", f"जवाब: {latex(result)}"], str(result)
    except:
        return ["समझ नहीं आया"], "Error"

@app.post("/api/solve")
async def solve_api(text: str = Form(None), image: UploadFile = None):
    if image:
        file_bytes = await image.read()
        input_text = ocr_image(file_bytes)
    else:
        input_text = text

    steps, answer = get_solution(input_text)
    return {"steps": steps, "answer": answer, "voice": " ".join(steps)}

# Vercel handler
from mangum import Mangum
handler = Mangum(app)
