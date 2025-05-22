# Tychi Wallet Assistant

A Flask-based chatbot application for Tychi Wallet with user authentication features.

## Overview

This application provides a conversational AI assistant for Tychi Wallet users. It features:

- User authentication with name and email
- Personalized chat experience
- Knowledge base integration for accurate responses
- Integration with Groq LLM API (llama3-70b-8192)
- Session management for persistent user data

## Features

- **User Authentication**: Requires users to register with name and email before accessing the chat
- **Personalized Experience**: Addresses users by name and maintains user-specific chat history
- **Responsive UI**: Clean, modern interface that works across devices
- **Knowledge Base Integration**: Searches through a structured knowledge base to provide accurate answers
- **LLM Integration**: Uses the Groq API to generate human-like conversational responses
- **Session Management**: Maintains user sessions for a seamless experience

## Installation

### Prerequisites

- Python 3.8+
- Flask
- Groq API key

### Setup

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/tychi-wallet-assistant.git
   cd tychi-wallet-assistant
   ```

2. Install dependencies:
   ```
   pip install flask flask-cors groq
   ```

3. Set up your Groq API key:
   - Sign up at [groq.com](https://groq.com) to get an API key
   - Replace the placeholder API key in the code with your actual key:
     ```python
     client = Groq(api_key="YOUR_API_KEY_HERE")
     ```

4. Create a knowledge base file:
   - Create a file named `knowledge_base.json` in the project root with your content
   - Follow the structure in the example below

5. Run the application:
   ```
   python app.py
   ```

6. Open your browser and navigate to:
   ```
   http://127.0.0.1:5000/
   ```

## Knowledge Base Structure

The knowledge base should be structured as follows:

```json
{
  "categories": [
    {
      "name": "General Information",
      "entries": [
        {
          "title": "What is Tychi Wallet?",
          "content": "Tychi Wallet is a digital wallet platform that allows users to manage crypto assets securely."
        }
      ]
    },
    {
      "name": "Troubleshooting",
      "entries": [
        {
          "title": "Login Issues",
          "content": "If you're having trouble logging in, try resetting your password through the 'Forgot Password' link."
        }
      ]
    }
  ]
}
```

## Usage

1. When a user first visits the site, they'll be prompted to enter their name and email
2. After registration, they'll be redirected to the chat interface
3. Users can ask questions about Tychi Wallet, and the assistant will provide relevant responses
4. The assistant searches the knowledge base for context before generating responses
5. User chat history is maintained for a personalized experience
6. Users can log out when finished, which clears their session

## File Structure

```
tychi-wallet-assistant/
├── app.py                  # Main Flask application
├── knowledge_base.json     # Structured knowledge for the assistant
└── templates/              # Auto-generated HTML templates
    ├── login.html          # Login page
    └── chat.html           # Chat interface
```

## Security Notes

This application is for demonstration purposes and includes several simplifications:

- User data is stored in memory (not persistent)
- Session secret is hardcoded (should be environment variable)
- No password protection for user accounts
- No HTTPS configuration

For production use, consider:
- Adding proper user authentication with passwords
- Using a database for persistent storage
- Setting up HTTPS
- Configuring proper session management
- Protecting your API key with environment variables

