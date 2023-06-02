from pathlib import Path
from llama_index import download_loader
from llama_index import GPTSimpleVectorIndex
import os

os.environ["OPENAI_API_KEY"] = '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'


def construct_index(directory_path):
  
  DocxReader = download_loader("DocxReader")
  loader = DocxReader()
  documents = loader.load_data(file=Path('C:\\Users\\phil.li\\Desktop\\JSB.docx'))
  index = GPTSimpleVectorIndex.from_documents(documents)  
  index.save_to_disk('index.json')  
  return index


if __name__ == "__main__":
    directory_path = "C:\\Users\\phil.li\\Desktop\\SFA"
    index = construct_index(directory_path)

 

