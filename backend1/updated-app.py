# app.py
import os
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_community.vectorstores import Chroma
from langchain.prompts import ChatPromptTemplate
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from dotenv import load_dotenv 


# Load environment variables from .env
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app, origins=["http://localhost:3000"])

google_api_key = os.getenv("GOOGLE_API_KEY")
if not google_api_key:
    raise ValueError("GOOGLE_API_KEY environment variable is not set")
else:
    os.environ["GOOGLE_API_KEY"] = google_api_key


# Initialize the vector store and retriever
def init_retriever(persist_directory="./chroma_db"):
    try:
        # Create embeddings
        embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

        # Load existing vector store
        vectorstore = Chroma(
            persist_directory=persist_directory, embedding_function=embeddings
        )

        # Check if the vectorstore is empty
        if vectorstore._collection.count() == 0:
            print(
                "Warning: Vector store is empty. Please run update_vectorstore.py to add documents."
            )
        else:
            print(
                f"Vector store loaded with {vectorstore._collection.count()} documents"
            )

        # Create retriever
        return vectorstore.as_retriever(
            search_type="similarity", search_kwargs={"k": 3}
        )

    except Exception as e:
        print(f"Error initializing retriever: {e}")
        print("Please make sure to run update_vectorstore.py first")
        return None


# Initialize components
retriever = init_retriever()
llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro")
# Create prompt template
prompt = ChatPromptTemplate.from_template("""

Answer the following question based only on the provided context:

<context>
You are naipunnya's beloved polite youre trained on data about the college and is able to answer anything about it 

{context}
</context>

Question: {input}

If the answer cannot be found in the context, say "I don't have enough information to answer that question."
""")
print(prompt)
# Create document chain
document_chain = create_stuff_documents_chain(llm, prompt)

# Create retrieval chain
retrieval_chain = create_retrieval_chain(retriever, document_chain)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.json
    query = data.get("query", "")

    if not query:
        return jsonify({"error": "Query is required"}), 400

    if retriever is None:
        return jsonify(
            {
                "answer": "The knowledge base has not been initialized. Please run update_vectorstore.py first."
            }
        )

    # Get response from RAG
    try:
        response = retrieval_chain.invoke({"input": query})

        # Extract source documents if available
        source_docs = []
        if "context" in response and response["context"]:
            source_docs = [doc.page_content for doc in response["context"]]

        return jsonify(
            {
                "question": query,
                "answer": response["answer"],
                "source_documents": source_docs,
            }
        )
    except Exception as e:
        return jsonify({"error": f"Error processing query: {str(e)}"}), 500


if __name__ == "__main__":
    # Create templates directory if it doesn't exist
    os.makedirs("templates", exist_ok=True)
    app.run(debug=True, port=5000)