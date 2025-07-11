# Jozef - A RAG Chatbot for Neo-Latin Studies

This is a RAG (Retrieval-Augmented Generation) chatbot for Neo-Latin studies. It uses a variety of large language models and a vector store of Neo-Latin handbooks to answer questions.

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
2. **Set up environment variables:**
   Create a `.env` file and add your API keys for Google Gemini and other services:
   ```
   GOOGLE_API_KEY=your_google_api_key
   ```
3. **Vectorize the PDFs:**
   Place your OCRed PDF handbooks in the `my_pdfs` directory. Then, run the vectorization script:
   ```bash
   python vectorize.py
   ```
   This will create a ChromaDB vector store in the `chroma_db` directory.

4. **Run the chatbot:**
   ```bash
   python app.py
   ```
   The chatbot will be available at `http://127.0.0.1:5000`.
