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

# --- RAG Setup ---
embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
vectorstore = Chroma(persist_directory=VECTOR_STORE_PATH, embedding_function=embeddings)
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
retriever = vectorstore.as_retriever(search_kwargs={"k": 5})

# Create separate QA chains for each model
qa_chains = []
for llm in llm_fallback_chain:
    chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        memory=memory
    )
    qa_chains.append(chain)

# --- Routes ---
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/ask", methods=["POST"])
def ask():
    user_message = request.form.get("message")
    if not user_message:
        return jsonify({"error": "No message provided"}), 400

    # Try each model in the fallback chain
    response = None
    for i, (llm, qa_chain) in enumerate(zip(llm_fallback_chain, qa_chains)):
        try:
            print(f"Attempting to query with {llm.model}...")
            response = qa_chain.invoke({"question": user_message})
            print(f"Success with {llm.model}")
            break  # Success, exit the loop
        except Exception as e:
            print(f"{llm.model} failed: {e}")
            # Check if it's a rate limit error and we have more models to try
            if "429" in str(e) and i < len(llm_fallback_chain) - 1:
                print(f"Rate limit detected. Switching to next model...")
                continue
            elif i < len(llm_fallback_chain) - 1:
                print(f"Error with {llm.model}, trying next model...")
                continue
            else:
                # This was the last model in the chain
                print(f"All models in the fallback chain failed.")
                return jsonify({"error": f"All models failed. Last error: {str(e)}"}), 500
    
    if response is None:
        return jsonify({"error": "All models in the fallback chain failed."}), 500
        
    return jsonify({"answer": response["answer"]})

@app.route("/clear_chat", methods=["POST"])
def clear_chat():
    try:
        memory.clear()
        return jsonify({"message": "Chat history cleared successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5001)
