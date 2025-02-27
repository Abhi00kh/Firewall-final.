# DO NOT CLONE THIS PROJECT 

#Neural Network-Based Web Application Firewall (WAF)

## Overview
This project implements a **Neural Network-Based Web Application Firewall (WAF)** designed to protect web applications from **SQL Injection, XSS, DDoS, OS Command Injection, and File Inclusion attacks**. The system uses **deep learning models** to classify incoming HTTP requests as legitimate or malicious in real-time, achieving **95% accuracy** in detection. 

## Features
- **Real-time attack detection** using Neural Networks
- **Protection against multiple cyber threats** (SQL Injection, XSS, DDoS, OS Command Injection, File Inclusion)
- **REST API support** for seamless integration with web applications
- **Logging & monitoring** with MongoDB for threat analysis
- **Scalable and adaptive** to new attack patterns

## Technology Stack
- **Programming Language:** Python
- **Machine Learning Framework:** TensorFlow, Keras
- **Web Framework:** Flask (for API & Web Interface)
- **Database:** MongoDB (for logging attack details)
- **Security Testing:** OWASP ZAP
- **Deployment:** WebSockets, REST API

## Machine Learning Model Details
The firewall utilizes different deep learning architectures for various attack types:
- **Convolutional Neural Networks (CNNs):** Used for analyzing structured HTTP request data (URLs, headers, payloads) to detect SQL Injection, XSS, OS Command Injection, and File Inclusion attacks.
- **Long Short-Term Memory (LSTM) Networks:** Used for detecting **DDoS attacks** by analyzing sequential traffic patterns and identifying sudden spikes or irregularities.

## Methodology
### 1. **Data Collection**
We gathered datasets from multiple sources:
- **SQL Injection & XSS Attacks:** Kaggle datasets
- **DDoS Attacks:** CIC-DDoS2019 dataset
- **OS Command Injection & File Inclusion:** Scripts and attack logs from GitHub, OWASP, and security forums

### 2. **Data Preprocessing**
- Removed **corrupted requests** and irrelevant features
- Tokenized and encoded categorical data (e.g., HTTP methods, status codes)
- Normalized numerical features (e.g., request size, response time)
- Split data into **training (70%), validation (15%), and test (15%) sets**

### 3. **Feature Engineering**
- Extracted **URL structure, headers, request parameters, payloads, and request frequency**
- Used **embedding layers** to represent text-based features (e.g., SQL payloads)
- Applied **feature scaling and dimensionality reduction**

### 4. **Model Training**
- CNN and LSTM models trained using **Adam Optimizer** with **ReLU/Softmax activation functions**
- Fine-tuned hyperparameters using **Grid Search**
- Handled class imbalance using **weighted loss functions**

### 5. **Model Evaluation**
Achieved high accuracy in detecting different attack types:
| Attack Type        | Accuracy | Precision | Recall | F1 Score |
|-------------------|----------|------------|--------|---------|
| DDoS            | 99%      | 1.00       | 1.00   | 1.00    |
| SQL Injection   | 99%      | 1.00       | 0.98   | 1.00    |
| XSS             | 99%      | 1.00       | 1.00   | 1.00    |
| File Inclusion  | 98%      | 0.97       | 0.99   | 0.98    |
| OS Command     | 98%      | 0.98       | 0.95   | 0.97    |

## Workflow
1. **Client Sends Request** → A web request is sent to the application.
2. **WAF Analyzes Request** → The firewall inspects the request and classifies it using a trained neural network model.
3. **Valid Request** → If the request is safe, it is forwarded to the web application.
4. **Malicious Request** → If an attack is detected, the request is blocked, and details are logged in MongoDB.
5. **Admin Dashboard** → Attack reports are visualized in a web-based dashboard.

## Setup Instructions
1. Clone the repository:
   ```bash
   git clone https://github.com/Abhi00kh/Firewall-final.git
   cd Firewall-final
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Start the application:
   ```bash
   python app.py
   ```
4. Access the API at `http://localhost:5000`

## Future Enhancements
- Implement **Autoencoder-based anomaly detection** for improved zero-day attack detection.
- Develop **real-time email/SMS alerts** for security teams.
- Enhance the **dashboard UI** with better analytics and visualization.

## License
This project is licensed under the **MIT License**.

## Contact
For queries, contact **[Your Email]** or visit **[Your GitHub Profile]**.
