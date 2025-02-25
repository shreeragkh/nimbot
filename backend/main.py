import os
from flask_cors import CORS
from dotenv import load_dotenv
from flask import Flask, jsonify, request

from langchain_google_genai import ChatGoogleGenerativeAI

# Set up Flask app
app = Flask(__name__)
CORS(app)


# Load environment variables from .env
load_dotenv()


# Initialize the ChatGoogleGenerativeAI model
llm = ChatGoogleGenerativeAI(model="gemini-pro",timeout=1600)


def generate_response(prompt):
    try:
        print("generating response")
        response = llm.invoke(prompt)
        print("response",response.content)
    except Exception as e:
        print('error occured',e)
    # Convert the AIMessage object to a dictionary
    response_dict = {
        "content": response.content,
    }
    return response_dict


# Endpoint to generate response from the model
@app.route("/generate", methods=["POST"])
def generate():
    data = request.json
    print("data from frontend",data)
    prompt = data.get("prompt")
    print(prompt)
    response = generate_response(prompt)
    return jsonify({"response": response})



# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True, port=8000)
