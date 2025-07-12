import os
from flask import Flask, render_template, request, jsonify
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.messages import HumanMessage
from typing import Dict, Optional
import base64
import fitz  # PyMuPDF

load_dotenv()

# --- Debugging ---
api_key = os.getenv("GOOGLE_API_KEY")
if api_key:
    print(f"Using Google API Key: {api_key[:5]}...{api_key[-5:]}")
else:
    print("Google API Key not found.")

# --- Configuration ---
VECTOR_STORE_PATH = "chroma_db"
EMBEDDING_MODEL = "sentence-transformers/all-mpnet-base-v2"

# --- LLM Configuration ---
llm_gemini_pro = ChatGoogleGenerativeAI(model="gemini-2.5-pro")
llm_gemini_flash = ChatGoogleGenerativeAI(model="gemini-2.5-flash")
llm_gemini_2_flash = ChatGoogleGenerativeAI(model="gemini-2.0-flash")
llm_gemini_2_flash_lite = ChatGoogleGenerativeAI(model="gemini-2.0-flash-lite")

# --- Fallback Chain ---
llm_fallback_chain = [
    llm_gemini_pro,
    llm_gemini_flash,
    llm_gemini_2_flash,
    llm_gemini_2_flash_lite
]

# --- App Setup ---
app = Flask(__name__)
# This will hold the content of the uploaded file for the user's session.
# In a real multi-user application, this should be handled by a proper session management system.
user_file_context: Dict[str, Optional[str]] = {
    "text": None,
    "filename": None
}

# --- RAG Setup ---
embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
# This is the main, persistent vector store for general knowledge.
main_vectorstore = Chroma(persist_directory=VECTOR_STORE_PATH, embedding_function=embeddings)
main_memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True, output_key='answer')
main_retriever = main_vectorstore.as_retriever(search_kwargs={"k": 5})

# This is the main QA chain that uses the persistent vector store.
qa_chain_gemini_pro = ConversationalRetrievalChain.from_llm(
    llm=llm_gemini_pro,
    retriever=main_retriever,
    memory=main_memory,
    return_source_documents=True
)

# --- Routes ---
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/ask", methods=["POST"])
def ask():
    user_message = request.form.get("message")
    if not user_message:
        return jsonify({"error": "No message provided"}), 400

    file_text = user_file_context.get("text")

    try:
        if file_text:
            # A file is in context, so we query against it directly.
            
            # 1. Create a temporary, in-memory vector store for the file.
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
            chunks = text_splitter.split_text(file_text)
            if not chunks:
                return jsonify({"error": "Could not process the file content."}), 500

            file_vectorstore = Chroma.from_texts(chunks, embeddings)
            file_retriever = file_vectorstore.as_retriever(search_kwargs={"k": 3})
            
            # 2. Create a dedicated, isolated memory for this file conversation.
            file_memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True, output_key='answer')

            # 3. Create a dedicated chain for this file.
            file_qa_chain = ConversationalRetrievalChain.from_llm(
                llm=llm_fallback_chain[0], # Start with the primary model
                retriever=file_retriever,
                memory=file_memory,
                return_source_documents=True
            )
            
            # 4. Invoke the file-specific chain with fallback logic.
            response = None
            for i, llm in enumerate(llm_fallback_chain):
                try:
                    print(f"Attempting to query with {llm.model}...")
                    file_qa_chain.llm = llm
                    response = file_qa_chain.invoke({"question": user_message})
                    break # Success, exit the loop
                except Exception as e:
                    if "429" in str(e) and i < len(llm_fallback_chain) - 1:
                        print(f"{llm.model} rate limit likely hit. Switching to next model.")
                        continue
                    else:
                        raise e
            if response is None:
                 return jsonify({"error": "All models in the fallback chain failed."}), 500
        else:
            # No file in context, use the main general-purpose chain with fallback.
            response = None
            for i, llm in enumerate(llm_fallback_chain):
                try:
                    print(f"Attempting to query with {llm.model}...")
                    qa_chain_gemini_pro.llm = llm
                    response = qa_chain_gemini_pro.invoke({"question": user_message})
                    break # Success, exit the loop
                except Exception as e:
                    if "429" in str(e) and i < len(llm_fallback_chain) - 1:
                        print(f"{llm.model} rate limit likely hit. Switching to next model.")
                        continue
                    else:
                        raise e
            if response is None:
                 return jsonify({"error": "All models in the fallback chain failed."}), 500
            
        return jsonify({"answer": response["answer"]})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/clear_context", methods=["POST"])
def clear_context():
    global user_file_context
    user_file_context = {"text": None, "filename": None}
    # Also clear the main conversation memory to avoid context bleed.
    main_memory.clear()
    return jsonify({"message": "File context and conversation history cleared."})

@app.route("/upload", methods=["POST"])
def upload():
    global user_file_context
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if not file or not file.filename:
        return jsonify({"error": "No selected file"}), 400

    try:
        text = ""
        filename_lower = file.filename.lower()

        if filename_lower.endswith('.pdf'):
            doc = fitz.open(stream=file.read(), filetype="pdf")
            for page_num in range(doc.page_count):
                page = doc[page_num]
                text += page.get_textpage().extractText()
            doc.close()
        elif filename_lower.endswith(('.png', '.jpg', '.jpeg')):
            image_data = base64.b64encode(file.read()).decode('utf-8')
            image_message = HumanMessage(
                content=[
                    {"type": "text", "text": "Describe this image in detail. This description will be used for a Retrieval-Augmented Generation system, so be comprehensive."},
                    {"type": "image_url", "image_url": f"data:image/jpeg;base64,{image_data}"},
                ]
            )
            response = None
            for i, llm in enumerate(llm_fallback_chain):
                try:
                    print(f"Attempting to query with {llm.model}...")
                    response = llm.invoke([image_message])
                    break # Success, exit the loop
                except Exception as e:
                    if "429" in str(e) and i < len(llm_fallback_chain) - 1:
                        print(f"{llm.model} rate limit likely hit. Switching to next model.")
                        continue
                    else:
                        raise e
            if response is None:
                    return jsonify({"error": "All models in the fallback chain failed to process the image."}), 500
            text = str(response.content)
        else:
            return jsonify({"error": "Unsupported file type. Please upload a PDF or image file (PNG, JPG, JPEG)."}), 400

        if not text:
            return jsonify({"error": "Could not extract text or description from the file."}), 400

        # Split the text into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
        chunks = text_splitter.split_text(text)

        # DO NOT add to the main vector store. Instead, hold it in our session context.
        if chunks:
            user_file_context["text"] = text
            user_file_context["filename"] = file.filename
            # Clear the main memory to signal a new conversational context.
            main_memory.clear()
            return jsonify({"message": f"File '{file.filename}' processed. You can now ask questions about it."})
        else:
            return jsonify({"error": "Could not process text into chunks."}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5001)
