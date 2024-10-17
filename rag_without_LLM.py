import os
import json
import requests
from dotenv import load_dotenv
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.language_models.llms import LLM
from langchain_core.runnables import Runnable
from langchain.chains import RetrievalQA, LLMChain
from langchain_core.prompts import PromptTemplate
from langchain_core.tools import Tool
from langchain_google_community import GoogleSearchAPIWrapper
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain import hub
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans



# Load environment variables from .env file
load_dotenv()

# Access API keys from environment variables
serper_api_key = os.getenv('SERPER_API_KEY')
google_cse_id = os.getenv('GOOGLE_CSE_ID')
google_api_key = os.getenv('GOOGLE_API_KEY')



# Configuration
KRYPTOMIND_API_URL = "https://llm.kryptomind.net/api/generate"
EMBEDDING_MODEL = 'BAAI/bge-small-en-v1.5'
LLM_MODEL = "llama3"
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 150


class CustomLLM(Runnable):
    def __init__(self):
        self.url = "https://llm.kryptomind.net/api/generate"

    def invoke(self, inputs, context=None):
        if isinstance(inputs, dict):
            prompt = f"Context: {inputs.get('context', '')}\nQuery: {inputs.get('query', '')}"
        else:
            prompt = str(inputs)

        data = {
            "model": "llama3",
            "prompt": prompt
        }
        response = requests.post(self.url, json=data)
        response_text = response.content.decode("utf-8")

        full_response = ""
        for line in response_text.splitlines():
            try:
                json_line = json.loads(line)
                if 'response' in json_line:
                    full_response += json_line['response']
            except json.JSONDecodeError:
                pass

        return full_response  # Return the string directly, not a dict

custom_llm = CustomLLM()

# Load and process the document
loader = TextLoader("knowledge_base.txt")
documents = loader.load()
text_splitter = RecursiveCharacterTextSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
texts = text_splitter.split_documents(documents)

embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
db = Chroma.from_documents(texts, embeddings)

# Create the retriever from your database
retriever = db.as_retriever(search_kwargs={"k": 1})

def retrieve_documents(query):
    results = retriever.invoke(query)
    if results:
        docs = results
        similarity_score = calculate_similarity_score(query, docs[0].page_content)
        print(f"Retrieved {len(docs)} documents with similarity score: {similarity_score}")
        return docs, similarity_score
    else:
        print("No documents found")
        return [], 0

def calculate_similarity_score(query, document_content):
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform([query, document_content])
    cosine_sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
    return float(cosine_sim[0][0])

search = GoogleSearchAPIWrapper()

tool = Tool(
    name="google_search",
    description="Search Google for recent results.",
    func=search.run,
)

format_template = """
Given the following context:
Context: {context}

Question: {query}

Instructions: Based on the given context, please provide a precise, relevant answer to the question. Avoid unnecessary details or unrelated information. If the context doesn't contain enough information, respond with "No relevant information found in the provided context." Ensure the response is clear and concise.

Source: {source}
"""

format_prompt = PromptTemplate(
    input_variables=["context", "query", "source"],
    template=format_template
)

format_chain = format_prompt | custom_llm | StrOutputParser()





# Main RAG chain function without passing to LLM
def rag_chain(query):
    print(f"RAG chain query: {query}")
    try:
        # Retrieve documents from the local knowledge base
        docs, similarity_score = retrieve_documents(query)
        
        if docs and similarity_score >= 0.3:  # Adjust this threshold as needed
            print("Information found in local knowledge base")
            # Return document content directly without sending it to the LLM
            documents_content = "\n".join([doc.page_content for doc in docs])
            source = "Local Knowledge Base"
            final_result = f"{documents_content}\n\nSource: {source}"
        else:
            print("Information not found in local knowledge base or similarity score too low. Searching the internet...")
            # If no relevant documents, search the internet
            internet_result = tool.run(query)
            source = "Internet Search"
            final_result = f"{internet_result}\n\nSource: {source}"

        # Store query and response in MongoDB
        # collection.insert_one({"query": query, "response": final_result})

        return final_result

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        import traceback
        traceback.print_exc()
        return "I'm sorry, but I encountered an error while processing your query. Please try again later."

