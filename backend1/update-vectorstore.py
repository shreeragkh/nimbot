import os
import argparse
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma
from dotenv import load_dotenv


load_dotenv()

google_api_key = os.getenv("GOOGLE_API_KEY")
if not google_api_key:
    raise ValueError("GOOGLE_API_KEY environment variable is not set")
else:
    os.environ["GOOGLE_API_KEY"] = google_api_key


def update_vectorstore(docs_dir, db_dir="./chroma_db"):
    """
    Load all text files from a directory and update the vector store

    Args:
        docs_dir (str): Path to directory containing text files
        db_dir (str): Path to ChromaDB persistence directory
    """
    # Check if API key is set
    if not os.getenv("GOOGLE_API_KEY"):
        raise ValueError("GOOGLE_API_KEY environment variable is not set")

    # Create directory if it doesn't exist
    if not os.path.exists(docs_dir):
        os.makedirs(docs_dir)
        print(f"Created directory: {docs_dir}")
        print("Please add your text files to this directory and run the script again.")
        return

    # Load all text files from the directory
    loader = DirectoryLoader(docs_dir, glob="**/*.txt", loader_cls=TextLoader)
    documents = loader.load()

    if not documents:
        print(f"No text files found in {docs_dir}")
        return

    print(f"Loaded {len(documents)} documents")

    # Split text into chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    splits = text_splitter.split_documents(documents)

    print(f"Split into {len(splits)} chunks")

    # Create embeddings and store in ChromaDB
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

    # Use from_documents to recreate the database or add new documents
    vectorstore = Chroma.from_documents(
        documents=splits, embedding=embeddings, persist_directory=db_dir
    )

    # Persist the vectorstore
    vectorstore.persist()

    print(f"Vector store updated and saved to {db_dir}")
    print(f"Total documents in vector store: {vectorstore._collection.count()}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Update vector store with text files from a directory"
    )
    parser.add_argument(
        "--docs_dir",
        type=str,
        default="./documents",
        help="Directory containing text files",
    )
    parser.add_argument(
        "--db_dir",
        type=str,
        default="./chroma_db",
        help="ChromaDB persistence directory",
    )

    args = parser.parse_args()
    update_vectorstore(args.docs_dir, args.db_dir)