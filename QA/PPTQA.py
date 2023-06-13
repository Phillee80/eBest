import os
from langchain import OpenAI
from dotenv import load_dotenv
from langchain.document_loaders import PyPDFLoader
from langchain.document_loaders import UnstructuredPowerPointLoader
from langchain.document_loaders import UnstructuredWordDocumentLoader
from langchain.embeddings import OpenAIEmbeddings
from langchain.chains import RetrievalQA
from langchain.vectorstores import Chroma
from langchain.text_splitter import CharacterTextSplitter
from langchain.prompts import PromptTemplate
from langchain.text_splitter import RecursiveCharacterTextSplitter

load_dotenv()
os.environ['OPENAI_API_KEY'] = "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"

def chat(qa):
    while True:
        question = input("请输入你的问题：")

        if question.lower() == "stop":
            break
        
        result = qa({"query": question})
        print (result)
        

def main():
    # loader = PyPDFLoader("C:/Python/FAQ.pdf")
    # loader = UnstructuredPowerPointLoader("C:/Users/phil.li/Desktop/Product.pptx")
    loader = UnstructuredWordDocumentLoader("C:/Users/phil.li/Desktop/产品手册_脆脆鲨.docx")
    # load document
    documents = loader.load()
    # split the documents into chunks
    text_splitter = CharacterTextSplitter(separator = "[/END]", chunk_size=5, chunk_overlap=0)
    texts = text_splitter.split_documents(documents)
    print ("拆分的文档数量:", len(texts) ) 
    
    # select which embeddings we want to use
    embeddings = OpenAIEmbeddings()
    # create the vectorestore to use as the index
    db = Chroma.from_documents(texts, embeddings)
    # expose this index in a retriever interface
    retriever = db.as_retriever(search_type="similarity", search_kwargs={"k":1})

    prompt_template = """请根据以下信息：
                        {context}
                        回答问题: {question} 
                        在每次回答的结尾添加文档中提到的图文链接"""
    PROMPT = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
    chain_type_kwargs = {"prompt": PROMPT}
    # create a chain to answer questions 
    qa = RetrievalQA.from_chain_type(
        llm=OpenAI(), chain_type="stuff", retriever=retriever, return_source_documents=False,chain_type_kwargs=chain_type_kwargs)
    chat (qa)
    
if __name__ == "__main__":
    main()