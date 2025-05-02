import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from urllib.parse import urlparse
import re
import string

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

# Define the CNN_BiLSTM model
class CNN_BiLSTM(nn.Module):
    def __init__(self, input_features, cnn_out_channels=32, hidden_size=64, num_classes=4):  # Adjusted num_classes to 4
        super(CNN_BiLSTM, self).__init__()
        self.conv1 = nn.Conv1d(in_channels=1, out_channels=cnn_out_channels, kernel_size=3, padding=1)
        self.bn1 = nn.BatchNorm1d(cnn_out_channels)  # Added BatchNorm1d layer
        self.relu = nn.ReLU()
        self.bilstm = nn.LSTM(input_size=cnn_out_channels, hidden_size=hidden_size, batch_first=True, bidirectional=True)
        self.fc1 = nn.Linear(hidden_size * 2, 64)
        self.fc2 = nn.Linear(64, num_classes)  # Adjusted num_classes to 4

    def forward(self, x):
        x = self.relu(self.bn1(self.conv1(x)))  # Added BatchNorm1d in the forward pass
        x = x.permute(0, 2, 1)
        lstm_out, _ = self.bilstm(x)
        x = self.relu(self.fc1(lstm_out[:, -1, :]))
        return self.fc2(x)

# Define the CNN_BiLSTM_Attention model
class CNN_BiLSTM_Attention(nn.Module):
    def __init__(self, input_features, cnn_out_channels=32, hidden_size=64, num_classes=4):  # Adjusted num_classes to 4
        super(CNN_BiLSTM_Attention, self).__init__()
        self.conv1 = nn.Conv1d(in_channels=1, out_channels=cnn_out_channels, kernel_size=3, padding=1)
        self.bn1 = nn.BatchNorm1d(cnn_out_channels)  # Added BatchNorm1d layer
        self.relu = nn.ReLU()
        self.bilstm = nn.LSTM(input_size=cnn_out_channels, hidden_size=hidden_size, batch_first=True, bidirectional=True)
        self.attn = nn.Linear(hidden_size * 2, 1)
        self.fc1 = nn.Linear(hidden_size * 2, 64)
        self.fc2 = nn.Linear(64, num_classes)  # Adjusted num_classes to 4

    def forward(self, x):
        x = self.relu(self.bn1(self.conv1(x)))  # Added BatchNorm1d in the forward pass
        x = x.permute(0, 2, 1)
        lstm_out, _ = self.bilstm(x)
        attn_weights = torch.softmax(self.attn(lstm_out), dim=1)
        context = torch.sum(attn_weights * lstm_out, dim=1)
        x = self.relu(self.fc1(context))
        return self.fc2(x)

# Load models

def load_models():
    input_features = 30  # Adjust based on your feature size
    model_attention = CNN_BiLSTM_Attention(input_features=input_features)
    model_no_attention = CNN_BiLSTM(input_features=input_features)

    model_attention.load_state_dict(torch.load(r'D:\KATALYZU PROJECTS\project\MALICIOUS WEB DEV\models\cnn_bilstm_attention.pt', map_location=torch.device('cpu')))
    model_no_attention.load_state_dict(torch.load(r'D:\KATALYZU PROJECTS\project\MALICIOUS WEB DEV\models\cnn_bilstm_no_attention.pt', map_location=torch.device('cpu')))

    model_attention.eval()
    model_no_attention.eval()

    return model_attention, model_no_attention