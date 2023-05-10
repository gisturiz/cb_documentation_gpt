from bs4 import BeautifulSoup
from pydantic import BaseModel, Field
from pathlib import Path
import re


class Document(BaseModel): 
    page_content: str
    metadata: dict = Field(default_factory=dict)

class ReadDocLoader():
    def __init__(self, path: str):
        self.file_path = path

    def load(self):
         #Load documents
        def _clean_data(data: str) -> str:
            soup = BeautifulSoup(data, "html.parser")
            text = soup.get_text().strip()
            # Remove extra spaces and newlines
            text = re.sub(r"\s+", " ", text)
            # Join sentences together
            sentences = re.split(r"(?<=[.!?]) +", text)
            text = " ".join(sentences).strip()
            return text
        
        docs = []
        for p in Path(self.file_path).rglob("*"):
            if p.is_dir():
                continue
            # Open the HTML file and read its contents
            with open(p, "r") as f:
                text = _clean_data(f.read())
            # Clean the HTML data and create an instance of the Document class
            metadata = {"source": str(p)}
            docs.append(Document(page_content=text, metadata=metadata))
        # Print the page content
        return docs

loader = ReadDocLoader("saved_pages")
docs = loader.load()
