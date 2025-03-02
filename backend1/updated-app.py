# app.py
import os
from flask import Flask, request, jsonify, render_template
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_community.vectorstores import Chroma
from langchain.prompts import ChatPromptTemplate
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain

# Initialize Flask app
app = Flask(__name__)

os.environ["GOOGLE_API_KEY"] = "AIzaSyDZAjtUHxJOa1Ga5dcaI04YQp6v27Q1EQI"
# Set your API key (you'll need to set this environment variable)
if not os.getenv("GOOGLE_API_KEY"):
    print("Warning: GOOGLE_API_KEY environment variable is not set")


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

    # Create a simple HTML template if it doesn't exist
    if not os.path.exists("templates/index.html"):
        with open("templates/index.html", "w") as f:
            f.write("""<!DOCTYPE html>
<html>
<head>
    <title>Simple RAG Chatbot</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
        #chat-container { height: 400px; overflow-y: auto; border: 1px solid #ccc; padding: 10px; margin-bottom: 10px; }
        #user-input { width: 80%; padding: 8px; }
        button { padding: 8px 15px; background: #4CAF50; color: white; border: none; cursor: pointer; }
        .user-message { text-align: right; margin: 5px; }
        .bot-message { text-align: left; margin: 5px; }
        .user-bubble { background-color: #dcf8c6; padding: 8px; border-radius: 10px; display: inline-block; max-width: 70%; }
        .bot-bubble { background-color: #f0f0f0; padding: 8px; border-radius: 10px; display: inline-block; max-width: 70%; }
        .source { font-size: 0.8em; color: #666; margin-top: 5px; }
    </style>
</head>
<body>
    <h1>Simple RAG Chatbot</h1>
    <div id="chat-container"></div>
    <div>
        <input type="text" id="user-input" placeholder="Ask a question...">
        <button onclick="sendMessage()">Send</button>
    </div>

    <script>
        const chatContainer = document.getElementById('chat-container');
        const userInput = document.getElementById('user-input');

        // Handle Enter key press
        userInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });

        function addMessage(text, isUser, sourceDocs = []) {
            const messageDiv = document.createElement('div');
            messageDiv.className = isUser ? 'user-message' : 'bot-message';
            
            const bubble = document.createElement('div');
            bubble.className = isUser ? 'user-bubble' : 'bot-bubble';
            bubble.innerText = text;
            messageDiv.appendChild(bubble);
            
            // Add source documents if available
            if (!isUser && sourceDocs && sourceDocs.length > 0) {
                const sourceDiv = document.createElement('div');
                sourceDiv.className = 'source';
                sourceDiv.innerHTML = '<strong>Sources:</strong><br>' + 
                    sourceDocs.map(doc => `- ${doc.substring(0, 100)}...`).join('<br>');
                messageDiv.appendChild(sourceDiv);
            }
            
            chatContainer.appendChild(messageDiv);
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }

        function sendMessage() {
            const message = userInput.value.trim();
            if (!message) return;
            
            // Add user message to chat
            addMessage(message, true);
            userInput.value = '';
            
            // Show loading message
            const loadingId = Date.now();
            const loadingDiv = document.createElement('div');
            loadingDiv.className = 'bot-message';
            loadingDiv.id = `loading-${loadingId}`;
            const loadingBubble = document.createElement('div');
            loadingBubble.className = 'bot-bubble';
            loadingBubble.innerText = 'Thinking...';
            loadingDiv.appendChild(loadingBubble);
            chatContainer.appendChild(loadingDiv);
            chatContainer.scrollTop = chatContainer.scrollHeight;
            
            // Send message to API
            fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ query: message }),
            })
            .then(response => response.json())
            .then(data => {
                // Remove loading message
                const loadingMessage = document.getElementById(`loading-${loadingId}`);
                if (loadingMessage) {
                    chatContainer.removeChild(loadingMessage);
                }
                
                // Add bot response
                if (data.error) {
                    addMessage(`Error: ${data.error}`, false);
                } else {
                    addMessage(data.answer, false, data.source_documents);
                }
            })
            .catch(error => {
                // Remove loading message
                const loadingMessage = document.getElementById(`loading-${loadingId}`);
                if (loadingMessage) {
                    chatContainer.removeChild(loadingMessage);
                }
                
                addMessage(`Error: ${error.message}`, false);
            });
        }
    </script>
</body>
</html>""")

    app.run(debug=True)
