from flask import Flask, render_template, request
import requests
import time
import urllib.parse

app = Flask(__name__)

def mymemory_translate(text, target_lang, source_lang="en", retries=3):
    """Translate using MyMemory API with:
    - Rate limit handling
    - Fallback retries
    - Clean error messages
    """
    base_url = "https://api.mymemory.translated.net/get"
    
    for attempt in range(retries):
        try:
            # URL encode the text
            encoded_text = urllib.parse.quote(text)
            
            # Build the request URL
            # Add your email to get higher quota (replace 'youremail@example.com')
            url = f"{base_url}?q={encoded_text}&langpair={source_lang}|{target_lang}&de=jurassicdominion007@gmail.com"
            
            response = requests.get(url, timeout=10)
            
            # Handle rate limiting (429 status)
            if response.status_code == 429:
                time.sleep(2 ** attempt)  # Exponential backoff
                continue
                
            response.raise_for_status()
            
            data = response.json()
            
            if not data.get('responseData'):
                raise ValueError("Empty translation response")
            
            translated_text = data['responseData']['translatedText']
            
            # Handle quality warnings
            if data.get('quotaFinished'):
                return f"Translation warning: {translated_text} (Quota exceeded)"
                
            return translated_text
            
        except requests.exceptions.RequestException as e:
            if attempt == retries - 1:
                return f"Network error: {str(e)}"
            time.sleep(1)
        except (KeyError, ValueError) as e:
            return f"API error: {str(e)}"
    
    return "Translation failed after multiple attempts"

@app.route('/', methods=['GET', 'POST'])
def index():
    translated = ""
    input_text = ""
    if request.method == 'POST':
        input_text = request.form.get("input_text", "").strip()
        target_lang = request.form.get("target_lang", "es")  # Default to Spanish
        source_lang = request.form.get("source_lang", "en")  # MyMemory requires source lang
        
        if not input_text:
            translated = "Error: Please enter text to translate"
        elif len(input_text) > 500:
            translated = "Error: MyMemory limits to 500 characters per request"
        else:
            translated = mymemory_translate(input_text, target_lang, source_lang)
    
    return render_template("index.html", translated=translated, input_text=input_text)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)