# URL Threat Scanner

A sophisticated web application that analyzes URLs for potential security threats using deep learning models with and without attention mechanisms.

## Features

- **Dual Model Analysis**: Choose between two deep learning models:
  - CNN-BiLSTM with Attention
  - CNN-BiLSTM without Attention

- **Threat Categories**:
  - Benign (Level 0)
  - Defacement (Level 1)
  - Phishing (Level 2)
  - Malware (Level 3)

- **Real-time Analysis**:
  - Instant URL scanning
  - Dynamic threat level indicators
  - Detailed AI-powered security analysis

- **AI-Powered Analysis**:
  - Ollama integration with llama3.2
  - Real-time threat assessment
  - Detailed security recommendations
  - Context-aware analysis

- **Interactive UI**:
  - Dark/Light mode toggle
  - Modern model selection interface
  - Visual threat level indicators
  - Loading animations

- **Export Functionality**:
  - PDF report generation
  - Detailed threat analysis
  - Downloadable reports

## Technical Stack

- **Frontend**:
  - HTML5/CSS3
  - JavaScript (Vanilla)
  - Modern UI components
  - Responsive design

- **Backend**:
  - Python
  - Flask web framework
  - PyTorch for deep learning
  - Ollama with Llama3.2 for AI analysis
  - FPDF for report generation

- **Models**:
  - CNN-BiLSTM architecture
  - Attention mechanism implementation
  - Character-level URL tokenization
  - Llama3.2 for contextual threat analysis

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/url-threat-scanner.git
cd url-threat-scanner
```

2. Install Ollama and Llama3.2:
   - Follow instructions at https://ollama.ai to install Ollama
   - Pull the Llama3.2 model: `ollama pull llama3.2`

3. Install Python dependencies:
```bash
pip install -r requirements.txt
```

4. Run the application:
```bash
python app.py
```

## Usage

1. Access the web interface at `http://localhost:5000`
2. Paste a URL in the input field
3. Select preferred model (With/Without Attention)
4. Click "Check URL Now"
5. View analysis results and export if needed

## Project Structure

```
malicious_checker/
├── app.py                 # Flask application with main routing logic
├── models.py             # Neural network models (CNN-BiLSTM)
├── llama_integration.py  # Ollama/Llama3.2 integration for AI analysis
├── static/
│   ├── styles.css       # Styling
│   └── script.js        # Frontend logic
├── templates/
│   └── index.html       # Main interface
└── models/              # Trained model weights
    ├── cnn_bilstm_attention.pt
    └── cnn_bilstm_no_attention.pt
```

## How It Works

1. **URL Analysis**:
   - Input URLs are processed through character-level tokenization
   - Deep learning models (CNN-BiLSTM) analyze URL patterns
   - Threat levels are determined based on model predictions

2. **AI-Powered Assessment**:
   - Ollama with Llama3.2 provides detailed threat analysis
   - Context-aware security recommendations
   - Classification-specific insights and warnings
   - Real-time threat level assessment

3. **Report Generation**:
   - Comprehensive PDF reports including:
     - URL analysis results
     - AI-generated security assessment
     - Specific threat indicators
     - Actionable recommendations

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Deep learning implementation inspired by modern URL classification techniques
- UI/UX design following modern web development practices
- Integration with LLaMA for detailed threat analysis