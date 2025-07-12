import os
from flask import Flask, render_template, request, jsonify
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

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

# --- App Setup ---
app = Flask(__name__)

# --- RAG Setup ---
embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
vectorstore = Chroma(persist_directory=VECTOR_STORE_PATH, embedding_function=embeddings)
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
retriever = vectorstore.as_retriever(search_kwargs={"k": 5})

qa_chain_gemini_pro = ConversationalRetrievalChain.from_llm(
    llm=llm_gemini_pro,
    retriever=retriever,
    memory=memory
)

qa_chain_gemini_flash = ConversationalRetrievalChain.from_llm(
    llm=llm_gemini_flash,
    retriever=retriever,
    memory=memory
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

    try:
        response = qa_chain_gemini_pro.invoke({"question": user_message})
        return jsonify({"answer": response["answer"]})
    except Exception as e:
        # Fallback mechanism
        try:
            response = qa_chain_gemini_flash.invoke({"question": user_message})
            return jsonify({"answer": response["answer"]})
        except Exception as e2:
            return jsonify({"error": str(e2)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5001)
