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
   Create a `.env` file and add your Google API key:
   ```
   GOOGLE_API_KEY=your_google_api_key
   ```

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
