from flask import Flask, request, jsonify, render_template, session, redirect, url_for
import json
import os
from groq import Groq
from flask_cors import CORS

# Create Flask app
app = Flask(__name__)
app.secret_key = "tychi_wallet_secret_key"  # Change this to a random secret in production
CORS(app)

# Load knowledge base
try:
    with open('knowledge_base.json', 'r') as f:
        knowledge_base = json.load(f)
except FileNotFoundError:
    # Create an empty knowledge base if file doesn't exist
    knowledge_base = {"categories": []}

# Groq API client
client = Groq(api_key="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")  # Replace with your actual key

# Initial message history
messages = [
    {"role": "system", "content": "You are a helpful assistant for Tychi Wallet. Use the context to answer questions accurately."}
]

# In-memory user storage - in production, use a database
users = {}

# Search function
def search_kb(query, kb, max_results=3):
    results = []
    query = query.lower()
    for category in kb.get("categories", []):
        for entry in category.get("entries", []):
            title = entry.get("title", "").lower()
            content = entry.get("content", "").lower()
            if query in title or query in content:
                results.append(f"{entry['title']}: {entry['content']}")
            if len(results) >= max_results:
                return results
    return results

# Create templates directory and HTML templates
templates_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
os.makedirs(templates_dir, exist_ok=True)

# Login HTML template
login_html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Tychi Wallet Assistant - Login</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #f8f9fa;
            margin: 0;
            padding: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
        }
        .login-container {
            background-color: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            width: 100%;
            max-width: 400px;
        }
        h1 {
            text-align: center;
            color: #333;
            margin-bottom: 30px;
        }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 8px;
            font-weight: 500;
            color: #555;
        }
        input {
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 16px;
            box-sizing: border-box;
        }
        input:focus {
            outline: none;
            border-color: #2c7be5;
            box-shadow: 0 0 0 3px rgba(44, 123, 229, 0.2);
        }
        .btn {
            background-color: #2c7be5;
            color: white;
            border: none;
            border-radius: 5px;
            padding: 12px 20px;
            font-size: 16px;
            cursor: pointer;
            width: 100%;
            transition: background-color 0.2s;
        }
        .btn:hover {
            background-color: #1a68d1;
        }
        .error-message {
            color: #dc3545;
            margin-top: 5px;
            font-size: 14px;
            display: none;
        }
        .logo {
            text-align: center;
            margin-bottom: 20px;
        }
        .logo img {
            height: 60px;
        }
    </style>
</head>
<body>
    <div class="login-container">
        <div class="logo">
            <h2>Tychi Wallet</h2>
        </div>
        <h1>Welcome to Tychi Assistant</h1>
        <div id="login-form">
            <div class="form-group">
                <label for="name">Name</label>
                <input type="text" id="name" placeholder="Enter your name" required>
                <div class="error-message" id="name-error">Please enter your name</div>
            </div>
            <div class="form-group">
                <label for="email">Email</label>
                <input type="email" id="email" placeholder="Enter your email" required>
                <div class="error-message" id="email-error">Please enter a valid email</div>
            </div>
            <button class="btn" id="login-button">Start Chat</button>
        </div>
    </div>

    <script>
        document.addEventListener('DOMContentLoaded', function() {
            const loginButton = document.getElementById('login-button');
            const nameInput = document.getElementById('name');
            const emailInput = document.getElementById('email');
            const nameError = document.getElementById('name-error');
            const emailError = document.getElementById('email-error');

            loginButton.addEventListener('click', function() {
                // Reset error messages
                nameError.style.display = 'none';
                emailError.style.display = 'none';
                
                // Validate inputs
                let isValid = true;
                
                if (!nameInput.value.trim()) {
                    nameError.style.display = 'block';
                    isValid = false;
                }
                
                if (!emailInput.value.trim() || !isValidEmail(emailInput.value)) {
                    emailError.style.display = 'block';
                    isValid = false;
                }
                
                if (isValid) {
                    // Send login request
                    fetch('/login', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            name: nameInput.value.trim(),
                            email: emailInput.value.trim()
                        })
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            window.location.href = data.redirect;
                        } else {
                            alert(data.message || 'Login failed. Please try again.');
                        }
                    })
                    .catch(error => {
                        console.error('Error:', error);
                        alert('An error occurred. Please try again.');
                    });
                }
            });
            
            // Email validation function
            function isValidEmail(email) {
                const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                return emailRegex.test(email);
            }
        });
    </script>
</body>
</html>
"""

# Chat HTML template
chat_html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Tychi Wallet Assistant</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f8f9fa;
            display: flex;
            flex-direction: column;
            height: 100vh;
        }
        .header {
            background-color: #ffffff;
            padding: 15px 20px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .header h1 {
            margin: 0;
            font-size: 1.5rem;
            color: #333;
        }
        .user-info {
            display: flex;
            align-items: center;
        }
        .user-name {
            margin-right: 15px;
        }
        .logout-btn {
            background-color: #f1f1f1;
            border: none;
            padding: 8px 12px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
            transition: background-color 0.2s;
        }
        .logout-btn:hover {
            background-color: #e0e0e0;
        }
        .chat-container {
            flex: 1;
            display: flex;
            flex-direction: column;
            max-width: 800px;
            width: 100%;
            margin: 0 auto;
            padding: 20px;
            box-sizing: border-box;
            overflow: hidden;
        }
        .chat-box {
            flex: 1;
            overflow-y: auto;
            padding: 10px;
            background-color: #ffffff;
            border-radius: 8px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
            margin-bottom: 20px;
        }
        .message {
            margin-bottom: 15px;
            display: flex;
        }
        .user-message {
            justify-content: flex-end;
        }
        .message-content {
            padding: 10px 15px;
            border-radius: 18px;
            max-width: 70%;
        }
        .user-message .message-content {
            background-color: #2c7be5;
            color: white;
            border-bottom-right-radius: 5px;
        }
        .bot-message .message-content {
            background-color: #f1f3f5;
            border-bottom-left-radius: 5px;
        }
        .input-area {
            display: flex;
            padding: 10px;
            background-color: #ffffff;
            border-radius: 8px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        }
        #user-input {
            flex: 1;
            padding: 12px 15px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 16px;
            outline: none;
            transition: border-color 0.2s;
        }
        #user-input:focus {
            border-color: #2c7be5;
        }
        #send-button {
            margin-left: 10px;
            padding: 12px 20px;
            background-color: #2c7be5;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 16px;
            transition: background-color 0.2s;
        }
        #send-button:hover {
            background-color: #1a68d1;
        }
        .typing-indicator {
            display: none;
            padding: 10px 15px;
            background-color: #f1f3f5;
            border-radius: 18px;
            border-bottom-left-radius: 5px;
            margin-bottom: 15px;
            align-items: center;
            width: fit-content;
        }
        .typing-indicator span {
            height: 8px;
            width: 8px;
            margin: 0 2px;
            background-color: #aaa;
            display: inline-block;
            border-radius: 50%;
            animation: typing 1s infinite ease-in-out;
        }
        .typing-indicator span:nth-child(1) { animation-delay: 0s; }
        .typing-indicator span:nth-child(2) { animation-delay: 0.2s; }
        .typing-indicator span:nth-child(3) { animation-delay: 0.4s; }
        @keyframes typing {
            0% { transform: translateY(0px); }
            25% { transform: translateY(-5px); }
            50% { transform: translateY(0px); }
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>Tychi Wallet Assistant</h1>
        <div class="user-info">
            <span class="user-name" id="user-name">{{ username }}</span>
            <button class="logout-btn" id="logout-btn">Logout</button>
        </div>
    </div>

    <div class="chat-container">
        <div class="chat-box" id="chat-box">
            <div class="message bot-message">
                <div class="message-content">
                    Hello {{ username }}! I'm your Tychi Wallet assistant. How can I help you today?
                </div>
            </div>
            <div class="typing-indicator" id="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
            </div>
        </div>
        <div class="input-area">
            <input type="text" id="user-input" placeholder="Type your message here..." autocomplete="off">
            <button id="send-button">Send</button>
        </div>
    </div>

    <script>
        document.addEventListener('DOMContentLoaded', function() {
            const chatBox = document.getElementById('chat-box');
            const userInput = document.getElementById('user-input');
            const sendButton = document.getElementById('send-button');
            const typingIndicator = document.getElementById('typing-indicator');
            const logoutButton = document.getElementById('logout-btn');
            
            // Handle sending messages
            function sendMessage() {
                const message = userInput.value.trim();
                if (message) {
                    // Add user message to chat
                    addMessageToChat('user', message);
                    
                    // Clear input
                    userInput.value = '';
                    
                    // Show typing indicator
                    typingIndicator.style.display = 'flex';
                    
                    // Send to backend
                    fetch('/chat', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            message: message
                        })
                    })
                    .then(response => response.json())
                    .then(data => {
                        // Hide typing indicator
                        typingIndicator.style.display = 'none';
                        
                        // Add bot response
                        addMessageToChat('bot', data.reply);
                    })
                    .catch(error => {
                        console.error('Error:', error);
                        typingIndicator.style.display = 'none';
                        addMessageToChat('bot', 'Sorry, there was an error processing your request.');
                    });
                }
            }
            
            // Add message to chat
            function addMessageToChat(sender, message) {
                const messageDiv = document.createElement('div');
                messageDiv.classList.add('message');
                messageDiv.classList.add(sender === 'user' ? 'user-message' : 'bot-message');
                
                const contentDiv = document.createElement('div');
                contentDiv.classList.add('message-content');
                contentDiv.textContent = message;
                
                messageDiv.appendChild(contentDiv);
                chatBox.appendChild(messageDiv);
                
                // Scroll to bottom
                chatBox.scrollTop = chatBox.scrollHeight;
            }
            
            // Event listeners
            sendButton.addEventListener('click', sendMessage);
            
            userInput.addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    sendMessage();
                }
            });
            
            // Logout functionality
            logoutButton.addEventListener('click', function() {
                fetch('/logout', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    }
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        window.location.href = data.redirect;
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                });
            });
        });
    </script>
</body>
</html>
"""

# Write templates to files
with open(os.path.join(templates_dir, 'login.html'), 'w') as f:
    f.write(login_html)

with open(os.path.join(templates_dir, 'chat.html'), 'w') as f:
    f.write(chat_html)

# Routes
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('chat_page'))
    return render_template('login.html')

@app.route('/chat-page')
def chat_page():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    return render_template('chat.html', username=session.get('user_name', 'User'))

# Login endpoint
@app.route('/login', methods=['POST'])
def login():
    name = request.json.get("name", "")
    email = request.json.get("email", "")
    
    if not name or not email:
        return jsonify({"success": False, "message": "Name and email are required"}), 400
    
    # Create a simple user ID
    user_id = email
    
    # Store user info
    users[user_id] = {
        "name": name,
        "email": email,
        "chat_history": []
    }
    
    # Set session
    session['user_id'] = user_id
    session['user_name'] = name
    
    return jsonify({"success": True, "redirect": "/chat-page"})

# Chat endpoint
@app.route('/chat', methods=['POST'])
def chat():
    if 'user_id' not in session:
        return jsonify({"reply": "Please log in first"}), 401
    
    user_id = session['user_id']
    user_name = session['user_name']
    
    user_input = request.json.get("message", "")

    kb_matches = search_kb(user_input, knowledge_base)
    context = "\n\n".join(kb_matches) if kb_matches else "No related entries found."

    system_prompt = {
        "role": "system",
        "content": f"You are a Tychi Wallet assistant speaking with {user_name}. Use the following context:\n\n{context}"
    }

    # Get user-specific chat history
    if user_id not in users:
        users[user_id] = {"name": user_name, "email": user_id, "chat_history": []}
    
    user_messages = users[user_id].get("chat_history", [])
    
    conversation = [system_prompt] + user_messages
    conversation.append({"role": "user", "content": user_input})

    try:
        response = client.chat.completions.create(
            messages=conversation,
            model="llama3-70b-8192"
        )
        reply = response.choices[0].message.content

        # Save messages to user's chat history
        users[user_id]["chat_history"].append({"role": "user", "content": user_input})
        users[user_id]["chat_history"].append({"role": "assistant", "content": reply})

        return jsonify({"reply": reply})

    except Exception as e:
        return jsonify({"reply": f"Error: {str(e)}"}), 500

# Logout endpoint
@app.route('/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    session.pop('user_name', None)
    return jsonify({"success": True, "redirect": "/"})

if __name__ == '__main__':
    print(f"Templates directory: {templates_dir}")
    print(f"Templates exist: {os.path.exists(os.path.join(templates_dir, 'login.html'))} and {os.path.exists(os.path.join(templates_dir, 'chat.html'))}")
    app.run(debug=True)
