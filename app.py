import os
import requests
import warnings
import base64
from flask import Flask, render_template, request, jsonify

# --- 1. SETUP ---
warnings.filterwarnings("ignore")

try:
    import google.generativeai as genai
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("\n❌ MISSING LIBRARIES! Run: pip install --upgrade flask requests google-generativeai python-dotenv")
    exit(1)

app = Flask(__name__)

# --- 2. CONFIGURATION ---
GOOGLE_KEY = os.getenv("GEMINI_API_KEY")

print("--- SYSTEM CHECK ---")
if not GOOGLE_KEY:
    print("❌ ERROR: GEMINI_API_KEY is missing from .env file!")
else:
    # Print first 4 chars to verify it's reading the right key (safety check)
    print(f"✅ Google Key Loaded (Starts with: {GOOGLE_KEY[:4]}...)")
    genai.configure(api_key=GOOGLE_KEY)

# --- 3. AI LOGIC ---
def generate_caption_logic(product, tone):
    print(f"   ↳ Text Gen: {product}...")
    
    if not GOOGLE_KEY: return "Error: Missing Google API Key."

    # Try standard stable models first
    models_to_try = [
        'gemini-1.5-flash',       # Newest Fast Model
        'gemini-pro',             # Classic Stable Model (Most likely to work for you)
        'gemini-1.5-pro-latest'   # Backup
    ]

    for model_name in models_to_try:
        try:
            print(f"     Attempting model: {model_name}...")
            model = genai.GenerativeModel(model_name)
            prompt = f"Write a viral Instagram caption for {product}. Tone: {tone}. Include 3 hashtags."
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"     ❌ {model_name} Error: {e}")
            continue # Try next model
            
    return "Error: Could not generate text. Please check your API key permissions."

def generate_image_logic(prompt):
    print(f"   ↳ Image Gen: {prompt}...")
    
    # Pollinations.ai (Keyless & Free)
    safe_prompt = prompt.replace(" ", "%20")
    image_url = f"https://image.pollinations.ai/prompt/{safe_prompt}?nologo=true&private=true&model=flux"
    
    try:
        response = requests.get(image_url)
        if response.status_code == 200:
            return base64.b64encode(response.content).decode("utf-8")
        else:
            return None
    except Exception as e:
        print(f"     ❌ Image Failed: {e}")
        return None

# --- 4. ROUTES ---
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    print("\n📩 BUTTON CLICKED!")
    
    try:
        caption_guidance = request.form.get('caption_guidance', 'Product')
        image_guidance = request.form.get('image_guidance', '')
        tone = request.form.get('tone', 'Neutral')
        
        # 1. Text
        caption_result = generate_caption_logic(caption_guidance, tone)
        
        # 2. Image
        full_image_prompt = f"professional product photo of {caption_guidance} {image_guidance}, studio lighting, 8k"
        image_result = generate_image_logic(full_image_prompt)

        return jsonify({
            "status": "success",
            "caption": caption_result,
            "image": image_result
        })

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

if __name__ == '__main__':
    print("🚀 Server Online. Ready for requests.")
    app.run(debug=True, port=5000)