import subprocess
import json
import time

def format_points(text):
    # Split into lines and format as points
    lines = text.strip().split('\n')
    formatted_lines = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Determine the appropriate emoji based on content
        if any(word in line.lower() for word in ['benign', 'safe', 'secure']):
            emoji = '✅'
        elif any(word in line.lower() for word in ['defacement', 'warning', 'caution']):
            emoji = '⚠️'
        elif any(word in line.lower() for word in ['phishing', 'malware', 'danger', 'threat']):
            emoji = '❌'
        else:
            emoji = '🔹'
            
        formatted_lines.append(f"{emoji} {line}")
    
    return '\n'.join(formatted_lines)

class OllamaClient:
    def __init__(self, model_name="llama3.2"):
        self.model_name = model_name
    
    def generate_analysis(self, url, classification, threat_level):
        # Create a prompt based on the classification
        category_map = {
            0: "benign",
            1: "defacement",
            2: "phishing",
            3: "malware"
        }
        
        classification = category_map.get(threat_level, classification)
        
        prompt = f"""Analyze this URL: {url}
        Classification: {classification}
        Threat Level: {threat_level}/3
        
        Provide a detailed security analysis in clear, separate points covering:
        1. URL characteristics and patterns
        2. Potential security implications
        3. Specific recommendations
        
        Format the response in clear, separate points."""
        
        # Simulate LLaMA response for demonstration
        if classification == "benign":
            analysis = f"""URL Analysis for {url}:

Safe URL Characteristics:
- Domain structure follows standard patterns
- No suspicious patterns or obfuscation detected
- Regular URL length and character distribution

Security Assessment:
- Low risk profile based on structural analysis
- No known malicious patterns identified
- Clean reputation in security databases

Recommendations:
- Safe to proceed with normal browsing
- Standard security practices apply
- Monitor for any unusual behavior"""

        elif classification == "defacement":
            analysis = f"""URL Analysis for {url}:

Suspicious Patterns Detected:
- Unusual URL structure raises concerns
- Potential attempts at visual deception
- Abnormal character patterns observed

Risk Assessment:
- Moderate risk of website manipulation
- Possible unauthorized content modification
- Visual elements may be compromised

Security Recommendations:
- Exercise caution when accessing
- Verify website authenticity
- Report suspicious behavior"""

        elif classification == "phishing":
            analysis = f"""URL Analysis for {url}:

Critical Warning Signs:
- Suspicious URL masquerading patterns
- Potential credential harvesting attempt
- Deceptive domain structure detected

Threat Assessment:
- High risk of credential theft
- Social engineering tactics likely
- Data security compromise possible

Urgent Recommendations:
- Do not enter any personal information
- Avoid downloading any content
- Report to security authorities"""

        else:  # malware
            analysis = f"""URL Analysis for {url}:

Severe Threat Indicators:
- Malicious code deployment likely
- System compromise attempts detected
- Known malware patterns present

Risk Analysis:
- Critical threat to system security
- Potential for data theft or encryption
- System integrity at risk

Emergency Actions Required:
- Do not access this URL
- Block at network level
- Update security protocols"""
        
        return format_points(analysis)

# Example usage
if __name__ == "__main__":
    client = OllamaClient()
    analysis = client.generate_analysis(
        "https://example-suspicious-site.com/login/verify",
        "malicious",
        4
    )
    print(analysis)