# RAG API - A Renaissance-Inspired Chatbot for Neo-Latin Studies

This is a sophisticated RAG (Retrieval-Augmented Generation) chatbot designed for Neo-Latin studies. It features a comprehensive 4-model fallback system using Google Gemini models and an elegant Renaissance-inspired user interface reminiscent of classical scholarly manuscripts.

## ✨ Features

- **Multi-Model Fallback System**: Automatically switches between 4 Google Gemini models (gemini-2.5-pro, gemini-2.5-flash, gemini-2.0-flash, gemini-2.0-flash-lite) for maximum reliability
- **Intelligent Source Detection**: Clearly distinguishes between handbook-sourced answers ("According to my handbooks") and general knowledge responses
- **Renaissance UI**: Beautiful classical interface inspired by scholarly engravings with ornate decorations and classical typography
- **Modern LangChain Architecture**: Uses the latest LangChain components without deprecated features
- **Chat History**: Maintains conversation context across interactions
- **Vector Store Integration**: ChromaDB with HuggingFace embeddings for semantic document retrieval

## 🛠️ Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment variables:**
   
   **⚠️ IMPORTANT: Never commit API keys to version control!**
   
   a. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```
   
   b. Get your Google Gemini API key:
   - Visit [Google AI Studio](https://aistudio.google.com/app/apikey)
   - Create a new API key
   - Copy the key
   
   c. Edit `.env` and replace `your_google_api_key_here` with your actual key:
   ```
   GOOGLE_API_KEY=your_actual_api_key_here
   ```
   
   **Note**: The `.env` file is automatically ignored by git and will not be committed.

3. **Vectorize your PDFs:**
   Place your OCRed PDF handbooks in the `my_pdfs` directory. Then run:
   ```bash
   python vectorize.py
   ```
   This creates a ChromaDB vector store in the `chroma_db` directory.

4. **Run the application:**
   ```bash
   python app.py
   ```
   The chatbot will be available at `http://127.0.0.1:5001`.

## 🏛️ Architecture

- **Backend**: Flask web server with modern LangChain retrieval chains
- **LLM**: Google Gemini models with intelligent fallback logic
- **Vector Store**: ChromaDB with sentence-transformers embeddings
- **Frontend**: Renaissance-themed HTML/CSS/JavaScript interface
- **Document Processing**: PyPDF and PyMuPDF for PDF handling

## 🎨 Interface

The user interface draws inspiration from classical Renaissance engravings and scholarly manuscripts, featuring:
- Classical typography (Cinzel, Cormorant Garamond)
- Ornate decorations and borders
- Gold and brass color palette
- Parchment-style textures
- Latin terminology for scholarly authenticity

## 📚 How It Works

1. **Document Retrieval**: Questions are semantically searched against your PDF handbook collection
2. **Context Assessment**: The system determines if retrieved documents are relevant
3. **Response Generation**: 
   - If relevant documents found → "According to my handbooks..."
   - If no relevant info → "There is no information about your question in my handbooks. [Various continuations]..."
4. **Model Fallback**: Automatically tries alternative models if the primary one fails
5. **Chat Memory**: Maintains conversation history for contextual responses

## 🔒 Security Notes

- **API Keys**: Never commit API keys to version control. Use the `.env.example` template.
- **Public Deployment**: If deploying publicly, consider implementing:
  - Rate limiting to prevent API abuse
  - User authentication
  - API key rotation
  - Usage monitoring and alerts
- **Cost Management**: Google Gemini API has usage-based pricing. Monitor your usage in the [Google Cloud Console](https://console.cloud.google.com/).

## 🚀 Deployment Options

For public deployment, consider these approaches:

1. **Personal Use**: Keep API keys in environment variables on your server
2. **Multi-User**: Implement user authentication and let users provide their own API keys
3. **SaaS Model**: Use server-side API keys with usage limits and billing
4. **Local-Only**: Distribute as a local application where users setup their own keys
