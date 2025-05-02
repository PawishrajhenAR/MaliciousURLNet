from flask import Flask, request, jsonify, render_template, send_file
import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
import time
import json
import subprocess
import re
import os
from urllib.parse import urlparse
from collections import Counter
from models import load_models
import string
from llama_integration import OllamaClient
from fpdf import FPDF

app = Flask(__name__, template_folder='templates', static_folder='static', static_url_path='/static')

# Load the models
model_attention, model_no_attention = load_models()

# Initialize the Ollama client
ollama_client = OllamaClient()

# Character-level tokenization for URLs
class URLTokenizer:
    def __init__(self, max_length=200):
        self.max_length = max_length
        self.char_to_idx = {c: i+1 for i, c in enumerate(string.printable)}
        self.vocab_size = len(self.char_to_idx) + 1  # +1 for padding

    def tokenize(self, url):
        # Truncate or pad URL to max_length
        if len(url) > self.max_length:
            url = url[:self.max_length]

        # Convert characters to indices
        tokens = [self.char_to_idx.get(c, 0) for c in url]

        # Pad sequence
        tokens = tokens + [0] * (self.max_length - len(tokens))

        return torch.tensor(tokens, dtype=torch.long)

def classify_url(url):
    # Tokenize the URL
    tokenizer = URLTokenizer()
    tokenized_url = tokenizer.tokenize(url).unsqueeze(0).unsqueeze(0)  # Add batch and channel dimensions

    # Get predictions from both models
    with torch.no_grad():
        score_attention = torch.softmax(model_attention(tokenized_url.float()), dim=1).squeeze()
        score_no_attention = torch.softmax(model_no_attention(tokenized_url.float()), dim=1).squeeze()

    # Average the scores
    avg_score = (score_attention + score_no_attention) / 2

    # Determine classification
    classes = ["safe", "neutral", "malicious"]
    classification = classes[torch.argmax(avg_score).item()]

    return classification, avg_score.tolist()

def classify_url_with_model(url, use_attention):
    # Tokenize the URL
    tokenizer = URLTokenizer()
    tokenized_url = tokenizer.tokenize(url).unsqueeze(0).unsqueeze(0)  # Add batch and channel dimensions

    # Select the model based on user choice
    model = model_attention if use_attention else model_no_attention

    # Get predictions
    with torch.no_grad():
        scores = torch.softmax(model(tokenized_url.float()), dim=1).squeeze()

    # Map predictions to categories
    categories = ["benign", "defacement", "phishing", "malware"]
    classification = categories[torch.argmax(scores).item()]

    return classification, scores.tolist()

# Function to get AI analysis from LLaMA via Ollama
def get_ai_analysis(url, classification, threat_level):
    try:
        # Use the Ollama client to generate analysis
        analysis = ollama_client.generate_analysis(url, classification, threat_level)
        return analysis
    except Exception as e:
        return f"Error generating AI analysis: {str(e)}"

def create_pdf_report(report):
    pdf = FPDF()
    
    # Add metadata
    pdf.set_title("URL Threat Analysis Report")
    pdf.set_author("URL Threat Scanner")
    pdf.set_creator("URL Threat Scanner")
    
    # Set compression
    pdf.set_compression(True)
    
    # Add a page
    pdf.add_page()
    
    # Title
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "URL Threat Analysis Report", ln=True, align='C')
    pdf.ln(10)

    # URL
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "Analyzed URL:", ln=True)
    pdf.set_font("Arial", '', 12)
    pdf.multi_cell(0, 10, report['url'])
    pdf.ln(5)

    # Classification and Threat Level with color
    pdf.set_font("Arial", 'B', 12)
    
    # Set color based on classification
    if report['classification'] == 'benign':
        pdf.set_text_color(16, 185, 129)  # Green
    elif report['classification'] == 'defacement':
        pdf.set_text_color(245, 158, 11)  # Orange
    else:
        pdf.set_text_color(239, 68, 68)   # Red
        
    pdf.cell(0, 10, f"Classification: {report['classification'].upper()}", ln=True)
    
    # Reset text color
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, f"Threat Level: {report['threat_level']}/3", ln=True)
    pdf.ln(5)

    # Analysis
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "AI Analysis:", ln=True)
    pdf.set_font("Arial", '', 12)
    
    # Handle multiline analysis with proper encoding
    analysis_lines = report['analysis'].split('\n')
    for line in analysis_lines:
        if line.strip():
            # Replace emojis with their text equivalents
            line = (line.replace('✅', '[SAFE] ')
                       .replace('⚠️', '[WARNING] ')
                       .replace('❌', '[DANGER] ')
                       .replace('🔹', '- '))
            # Ensure proper encoding
            line = line.encode('latin-1', 'replace').decode('latin-1')
            pdf.multi_cell(0, 10, line)

    # Add footer
    pdf.set_y(-30)
    pdf.set_font("Arial", 'I', 8)
    pdf.set_text_color(128, 128, 128)
    pdf.cell(0, 10, f"Generated on {time.strftime('%Y-%m-%d %H:%M:%S')}", ln=True, align='C')

    return pdf

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/scan', methods=['POST'])
def scan_url():
    data = request.json
    url = data.get('url')
    use_attention = data.get('use_attention', True)
    format = data.get('format', 'json')

    if not url:
        return jsonify({"error": "URL is required"}), 400

    try:
        classification, scores = classify_url_with_model(url, use_attention)
        threat_level = torch.argmax(torch.tensor(scores)).item()
        analysis = get_ai_analysis(url, classification, threat_level)

        category_map = {
            0: "benign",
            1: "defacement",
            2: "phishing",
            3: "malware"
        }

        report = {
            "url": url,
            "classification": category_map[threat_level],
            "threat_level": threat_level,
            "scores": scores,
            "analysis": analysis
        }

        if format == 'pdf':
            try:
                pdf = create_pdf_report(report)
                timestamp = int(time.time())
                filename = f"threat_analysis_{timestamp}.pdf"
                temp_path = os.path.join(os.path.dirname(__file__), filename)
                
                # Save PDF with error checking
                pdf.output(temp_path)
                
                # Send file with explicit headers
                response = send_file(
                    temp_path,
                    mimetype='application/pdf',
                    as_attachment=True,
                    download_name=filename,
                    max_age=0
                )
                
                # Add headers to prevent caching
                response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
                response.headers["Pragma"] = "no-cache"
                response.headers["Expires"] = "0"
                response.headers["Content-Type"] = "application/pdf"
                
                return response
                
            except Exception as e:
                app.logger.error(f"PDF generation error: {str(e)}")
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                return jsonify({"error": "Failed to generate PDF report"}), 500
            finally:
                # Cleanup temp file
                if os.path.exists(temp_path):
                    try:
                        os.remove(temp_path)
                    except:
                        pass

        return jsonify(report)

    except Exception as e:
        app.logger.error(f"Scan error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/report.pdf', methods=['GET'])
def download_report():
    try:
        return send_file('report.pdf', as_attachment=False, mimetype='application/pdf')
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)