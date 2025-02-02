import pdfplumber
import os
from vectordb import Memory
from ollama import chat, ChatResponse

class Chunk:
    def __init__(self, id, pdf_name, text):
        self.metadata = {
            "id": id,
            "pdf_source": pdf_name
        }
        self.text = text

# mapping from each of the different sources to the files
pdf_folder_paths = {
    "all": "./demo-pdfs/",
    "primary": "./demo-pdfs/primary/",
    "protcols": "./demo-pdfs/protocols/",
    "safety": "./demo-pdfs/safety"
}

class VectorDB:
    # self.text_chunks: a list of Chunks()
    # self.folder_path: './demo-pdfs/' # TODO: in the future it should be in multiple folders
    # self.source: a string that can be: "all", "primary", "protocols", "safety"

    def __init__(self):
        folder_path = "./demo-pdfs/"

        # for every file in the folder name, parse the pdf

        pdfs = [
            os.path.join(root, file)
            for root, _, files in os.walk(folder_path)
            for file in files if file.endswith(".pdf")
        ]

        # list of Chunks
        self.text_chunks = []

        counter = 0

        for pdf_path in pdfs:
            with pdfplumber.open(pdf_path) as pdf:
                # remove the PDF extension to get the PDF name
                pdf_file_name = pdf_path.split("/")
                pdf_file_name = pdf_file_name[-1]
                pdf_name = pdf_file_name.rstrip(".pdf")
                # print(f"Parsing PDF name {pdf_name} right now.")
                for page in pdf.pages:
                    page_text = page.extract_text()
                    # split the page text into multiple chunks based on the \n line
                    page_chunks = page_text.split(sep='\n')
                    for chunk in page_chunks:
                        # add the chunk to text_chunks
                        new_chunk = Chunk(counter, pdf_name, chunk)
                        self.text_chunks.append(new_chunk)
                        counter += 1
                    # text_chunks.extend(page_chunks)
        # create the vector database
        self.memory = Memory()
        memory_texts = [text_chunk.text for text_chunk in self.text_chunks]
        memory_metadata = [text_chunk.metadata for text_chunk in self.text_chunks]
        self.memory.save(
            texts=memory_texts,
            metadata=memory_metadata
        )
        self.source = "all"
        print("Done with initializing DB.")


    def change_source(self, new_source):
        # if we already have this source, then don't recreate it
        if (self.source == new_source):
            return 0
        # if it's an invalid source, then don't do anything
        if (new_source != "all" and new_source != "primary" and new_source != "protocols" and new_source != "safety"):
            return -1
        
        # change the path
        folder_path = pdf_folder_paths[new_source]

        # for every file in the folder name, parse the pdf
        pdfs = [
            os.path.join(root, file)
            for root, _, files in os.walk(folder_path)
            for file in files if file.endswith(".pdf")
        ]

        # list of Chunks
        self.text_chunks = []

        counter = 0

        for pdf_path in pdfs:
            with pdfplumber.open(pdf_path) as pdf:
                # remove the PDF extension to get the PDF name
                pdf_file_name = pdf_path.split("/")
                pdf_file_name = pdf_file_name[-1]
                pdf_name = pdf_file_name.rstrip(".pdf")
                print(f"Parsing PDF name {pdf_name} right now.")
                for page in pdf.pages:
                    page_text = page.extract_text()
                    # split the page text into multiple chunks based on the \n line
                    page_chunks = page_text.split(sep='\n')
                    for chunk in page_chunks:
                        # add the chunk to text_chunks
                        new_chunk = Chunk(counter, pdf_name, chunk)
                        self.text_chunks.append(new_chunk)
                        counter += 1
                    # text_chunks.extend(page_chunks)
        # create the vector database
        self.memory = Memory()
        memory_texts = [text_chunk.text for text_chunk in self.text_chunks]
        memory_metadata = [text_chunk.metadata for text_chunk in self.text_chunks]
        self.memory.save(
            texts=memory_texts,
            metadata=memory_metadata
        )
        self.source = "all"
        print("Done with initializing DB.")
        return 0

    def run_query(self, query):
        results = self.memory.search(query, top_n = 100, unique=True)
        combined_context = ''.join([result['chunk'] for result in results])
        pdf_sources_used = set([ result['metadata']['pdf_source'] for result in results ])

        background_prompt = "You are a lab assistant and have read up research papers about the topic the researcher is asking you about. In particular, you recall the following information: " + combined_context + "\n\n"
        background_prompt += "Please respond the following user query in succint bullet points within 3-5 sentences. Also please limit the thinking phase to a few sentences, with a max of 10 sentences."

        response: ChatResponse = chat(model='deepseek-r1:1.5b', messages=[
            {
                'role': 'system',
                'content': background_prompt
            },
            {
                'role': 'user',
                'content': query
            },
        ])

        print(f"PDF sources used: {pdf_sources_used}")

        context = {
            'text': response.message.content,
            'sources': list(pdf_sources_used)
        }

        return context
