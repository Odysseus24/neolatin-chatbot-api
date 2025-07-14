import os
from flask import Flask, render_template, request, jsonify
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

load_dotenv()

# --- Debugging ---
api_key = os.getenv("GOOGLE_API_KEY")
if api_key:
    print(f"Using Google API Key: {api_key[:5]}...{api_key[-5:]}")
else:
    print("❌ Google API Key not found!")
    print("Please ensure you have:")
    print("1. Created a .env file (copy from .env.example)")
    print("2. Added your Google API key to the .env file")
    print("3. Get your API key from: https://aistudio.google.com/app/apikey")
    exit(1)

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
retriever = vectorstore.as_retriever(search_kwargs={"k": 5})

# Chat history storage (in-memory for this example)
chat_history = []

# Create prompt template for RAG with chat history
system_prompt = (
    "You are a knowledgeable assistant for question-answering tasks. "
    "First, check if the retrieved context below contains relevant information "
    "to answer the question. If the context is relevant and helpful, use it "
    "as your primary source and start your response with 'According to my handbooks' "
    "instead of phrases like 'Based on the provided context' or 'The context shows'. "
    "If the context is not relevant or doesn't contain useful information "
    "for the question, rely on your general knowledge to provide a helpful answer. "
    "In this case, start with one of these phrases (choose randomly): "
    "'There is no information about your question in my handbooks. Relying on my general knowledge, I can tell you that', "
    "'There is no information about your question in my handbooks. From what I know generally', "
    "'There is no information about your question in my handbooks. Drawing from my broader knowledge', "
    "'There is no information about your question in my handbooks. Based on my general understanding', "
    "'There is no information about your question in my handbooks. What I can share from my general knowledge is that'. "
    "Keep your answer informative but concise."
    "\n\n"
    "Retrieved context: {context}"
)

prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    MessagesPlaceholder("chat_history"),
    ("human", "{input}"),
])

# Create separate chains for each model
rag_chains = []
for llm in llm_fallback_chain:
    question_answer_chain = create_stuff_documents_chain(llm, prompt)
    rag_chain = create_retrieval_chain(retriever, question_answer_chain)
    rag_chains.append(rag_chain)

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
    for i, (llm, rag_chain) in enumerate(zip(llm_fallback_chain, rag_chains)):
        try:
            print(f"Attempting to query with {llm.model}...")
            response = rag_chain.invoke({
                "input": user_message,
                "chat_history": chat_history
            })
            print(f"Success with {llm.model}")
            
            # Add to chat history
            chat_history.extend([
                HumanMessage(content=user_message),
                AIMessage(content=response["answer"])
            ])
            
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
        global chat_history
        chat_history = []
        return jsonify({"message": "Chat history cleared successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5001)
