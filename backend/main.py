import os

from dotenv import load_dotenv
from flask import Flask, jsonify, request

from langchain_google_genai import ChatGoogleGenerativeAI

# Set up Flask app
app = Flask(__name__)


# Load environment variables from .env
load_dotenv()


# Initialize the ChatGoogleGenerativeAI model
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash-lite-preview-02-05")


def generate_response(prompt):
    response = llm.invoke(prompt)
    # Convert the AIMessage object to a dictionary
    response_dict = {
        "content": response.content,
        "name": response.name,
    }
    return response_dict


# Endpoint to generate response from the model
@app.route("/generate", methods=["POST"])
def generate():
    data = request.json
    prompt = data.get("prompt")
    response = generate_response(prompt)
    return jsonify({"response": response})


# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True)
