import os
from langchain import OpenAI
from dotenv import load_dotenv
from langchain.document_loaders import PyPDFLoader
from langchain.document_loaders import UnstructuredPowerPointLoader
from langchain.embeddings import OpenAIEmbeddings
from langchain.chains import RetrievalQA
from langchain.vectorstores import Chroma
from langchain.text_splitter import CharacterTextSplitter


load_dotenv()

# Get the Variables from the .env file
OPENAI_API_KEY = os.getenv('OPEN_AI_KEY')

def chat(qa):
    while True:
        question = input("请输入你的问题：")

        if question.lower() == "stop":
            break
        
        result = qa({"query": question})
        print (result)      

def main():
    # loader = PyPDFLoader("C:/Python/FAQ.pdf")
    loader = UnstructuredPowerPointLoader("C:/Users/Phil/Desktop/Test.pptx")
    # load document
    documents = loader.load()
    # split the documents into chunks
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    texts = text_splitter.split_documents(documents)
    # select which embeddings we want to use
    embeddings = OpenAIEmbeddings()
    # create the vectorestore to use as the index
    db = Chroma.from_documents(texts, embeddings)
    # expose this index in a retriever interface
    retriever = db.as_retriever(search_type="similarity", search_kwargs={"k":2})
    # create a chain to answer questions 
    qa = RetrievalQA.from_chain_type(
        llm=OpenAI(), chain_type="stuff", retriever=retriever, return_source_documents=False)
    chat (qa)
    
    


if __name__ == "__main__":
    main()