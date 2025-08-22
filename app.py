import os
import logging
from flask import Flask, render_template, request, send_file, session, redirect, url_for, jsonify
from generator import generate_meme

# Configure logging for debugging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "fallback_secret_key_for_dev")

@app.route('/')
def index():
    return render_template("index.html")

@app.route("/generate", methods=["POST"])
def generate():
    template_name = request.form['template']
    
    texts = []
    text_list = request.form.getlist("text[]")
    x_list = request.form.getlist("x[]")
    y_list = request.form.getlist("y[]")

    for i in range(len(text_list)):
        text_content = text_list[i].strip()
        if text_content:  # skip empty text
            try:
                x = int(x_list[i])
                y = int(y_list[i])
            except ValueError:
                x, y = 10, 10  # fallback default
            texts.append({"text": text_content, "x": x, "y": y, "size": 36})

    if not texts:
        return render_template("index.html", error="❌ No text provided. Please add at least one text.")

    # Store meme data in session for preview page
    session['meme_data'] = {
        'template_name': template_name,
        'texts': texts
    }
    
    return redirect(url_for('preview'))

@app.route('/preview')
def preview():
    meme_data = session.get('meme_data')
    if not meme_data:
        return redirect(url_for('index'))
    
    # Generate initial preview meme
    try:
        meme_path = generate_meme(meme_data['template_name'], meme_data['texts'])
        meme_filename = os.path.basename(meme_path)
        return render_template('preview.html', 
                             meme_filename=meme_filename,
                             meme_data=meme_data)
    except Exception as e:
        app.logger.error(f"Error generating preview: {str(e)}")
        return redirect(url_for('index'))

@app.route('/update_meme', methods=['POST'])
def update_meme():
    meme_data = session.get('meme_data')
    if not meme_data:
        return jsonify({'error': 'No meme data found'}), 400
    
    # Update text parameters from request
    if request.json is None:
        return jsonify({'error': 'No JSON data provided'}), 400
    updated_texts = request.json.get('texts', [])
    meme_data['texts'] = updated_texts
    session['meme_data'] = meme_data
    
    try:
        meme_path = generate_meme(meme_data['template_name'], updated_texts)
        meme_filename = os.path.basename(meme_path)
        return jsonify({'meme_filename': meme_filename})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download')
def download():
    meme_data = session.get('meme_data')
    if not meme_data:
        return redirect(url_for('index'))
    
    try:
        meme_path = generate_meme(meme_data['template_name'], meme_data['texts'])
        template_name = meme_data['template_name']
        return send_file(meme_path, mimetype='image/jpeg', as_attachment=True, 
                        download_name=f"{os.path.splitext(template_name)[0]}_meme.jpg")
    except Exception as e:
        app.logger.error(f"Error downloading meme: {str(e)}")
        return redirect(url_for('preview'))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
