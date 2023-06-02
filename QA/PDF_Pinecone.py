import os
import pinecone
import requests
import mimetypes
import os
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlsplit
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Pinecone
from langchain.chat_models import ChatOpenAI
from langchain.schema import (
    AIMessage,
    HumanMessage,
    SystemMessage
)
from langchain.document_loaders import (
    PyPDFLoader,
    CSVLoader,
    UnstructuredWordDocumentLoader,
    WebBaseLoader,
)

load_dotenv()



# Get the Variables from the .env file
OPENAI_API_KEY = os.getenv('OPEN_AI_KEY')
PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
PINECONE_ENVIRONMENT = os.getenv('PINECONE_ENVIRONMENT')
PINECONE_INDEX_NAME = os.getenv('PINECONE_INDEX_NAME')


embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
chat = ChatOpenAI(temperature=0.1, openai_api_key=OPENAI_API_KEY)


class PineconeManager:
    def __init__(self, api_key, environment):
        pinecone.init(
            api_key=api_key,
            environment=environment
        )

    def list_indexes(self):
        return pinecone.list_indexes()

    def create_index(self, index_name, dimension, metric):
        pinecone.create_index(name=index_name, dimension=dimension, metric=metric)

    def delete_index(self, index_name):
        pinecone.deinit()


class DocumentLoaderFactory:
    @staticmethod
    def get_loader(file_path_or_url):
        
        
        mime_type, _ = mimetypes.guess_type(file_path_or_url)
        ext_name = os.path.splitext(file_path_or_url)[1]

        if mime_type == 'application/pdf':
            return PyPDFLoader(file_path_or_url)
        elif mime_type == 'text/csv':
            return CSVLoader(file_path_or_url)
        elif ext_name == ".docx":
            return UnstructuredWordDocumentLoader(file_path_or_url)
        elif mime_type in ['application/msword',
                            'application/vnd.openxmlformats-officedocument.wordprocessingml.document']:
            return UnstructuredWordDocumentLoader(file_path_or_url)
        else:
            raise ValueError(f"Unsupported file type: {mime_type}")


class PineconeIndexManager:
    def __init__(self, pinecone_manager, index_name):
        self.pinecone_manager = pinecone_manager
        self.index_name = index_name

    def index_exists(self):
        active_indexes = self.pinecone_manager.list_indexes()
        return self.index_name in active_indexes

    def create_index(self, dimension, metric):
        self.pinecone_manager.create_index(self.index_name, dimension, metric)

    def delete_index(self):
        self.pinecone_manager.delete_index(self.index_name)


def train_or_load_model(train, pinecone_index_manager, file_path, name_space):
    if train:
        loader = DocumentLoaderFactory.get_loader(file_path)
        pages = loader.load_and_split()

        if pinecone_index_manager.index_exists():
            print("Updating the model")
            pinecone_index = Pinecone.from_documents(pages, embeddings, index_name=pinecone_index_manager.index_name,
                                                     namespace=name_space)

        else:
            print("Training the model")
            pinecone_index_manager.create_index(dimension=1536, metric="cosine")
            pinecone_index = Pinecone.from_documents(documents=pages, embedding=embeddings,
                                                     index_name=pinecone_index_manager.index_name,
                                                     namespace=name_space)
        return pinecone_index
    else:
        pinecone_index = Pinecone.from_existing_index(index_name=pinecone_index_manager.index_name,
                                                      namespace=name_space, embedding=embeddings)
        return pinecone_index





def answer_questions(pinecone_index):
    messages = [
        SystemMessage(
            content='I want you to act as a document that I am having a conversation with. Your name is "AI '
                    'Assistant". You will provide me with answers from the given info. If the answer is not included, '
                    'say exactly "Hmm, I am not sure." and stop after that. Refuse to answer any question not about '
                    'the info. Never break character.')
    ]
    while True:
        question = input("Ask a question (type 'stop' to end): ")

        if question.lower() == "stop":
            break      
        
        docs = pinecone_index.similarity_search(query=question, k=1)
        
        main_content = question + "\n\n"
        for doc in docs:
            main_content += doc.page_content + "\n\n"

        messages.append(HumanMessage(content=main_content))
        print ("Ready to ask")
        ai_response = chat(messages).content
        messages.pop()
        messages.append(HumanMessage(content=question))
        messages.append(AIMessage(content=ai_response))

        print(ai_response)


def main():
    pinecone_manager = PineconeManager(PINECONE_API_KEY, PINECONE_ENVIRONMENT)
    pinecone_index_manager = PineconeIndexManager(pinecone_manager, PINECONE_INDEX_NAME)
    file_path = "D:/Python/eBest/FAQ.docx"
    name_space = "insurance"

    train = int(input("Do you want to train the model? (1 for yes, 0 for no): "))
    pinecone_index = train_or_load_model(train, pinecone_index_manager, file_path, name_space)
    answer_questions(pinecone_index)


if __name__ == "__main__":
    main()