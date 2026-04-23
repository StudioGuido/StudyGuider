import pandas as pd
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import fitz
import re




def pdf_To_String(pathToPdf:str):
    '''
    This function leverage langchains pdf loader to turn the
    pdf text into string format
    '''

    # path to pdf
    loader = PyPDFLoader(pathToPdf)

    # turning to text
    documents = loader.load()

    # joining seperate pages into 1 document split by a new line character
    combined_text = "\n".join([doc.page_content for doc in documents])

    return combined_text

    

def split_by_chapter(text, pattern=r'\nChapter\s+\d+\s*[:.-]?\s*\n'):
    '''
    This function splits the texts into chapters. The chapter patterns
    works by looking at

    1: Starts with a new line
    2: Matches the word chapter
    3: Any number of white space after the word chapter
    4: Any Digit after the white space
    5: If there is anything after the number like :, ., - or nothing
    6: Any optional spaces after the possible character from pattern 5
    7: A new line after pattern 6

    '''

    # Split text by chapters
    parts = re.split(pattern, text)

    return parts[1:]
    

def remove_Anything_Before_Content(text:str):
    '''
    This function searches for the first instance of the word content
    and then removes any text prior to that word
    '''

    index = text.lower().find("contents")

    if index != -1:
        # Slice the text starting from the word "contents"
        cleaned_text = text[index:]
    else:
        # If the word "contents" is not found, use the original text
        cleaned_text = text
    
    return cleaned_text


def splitIntoChunks_to_MapToChapter(pdf_paths: list[str]):
    '''
    This function will split each chapters text into chunks.
    It then creates a hashmap with format:

    {1: [text], 2: [text], ....}
    '''
    chapterChunksMap = {}

    # Create a text splitter instance with desired chunk size and overlap
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    for i, pdf_path in enumerate(pdf_paths, start=1):
        reader = fitz.open(pdf_path)
        
        chapter_text = " ".join(page.get_text() for page in reader if page.get_text())

        chunks = text_splitter.split_text(chapter_text)
        
        chapterChunksMap[i] = chunks

    return chapterChunksMap


def mapOfChapterWithChunks_to_DataFrame(map_of_chapter_with_chunks:dict):
    '''
    This function makes turns the map of chapter with chunks into a dataframe 
    with columns:
    
    Columns: | Chapter | Chunk Text |
    '''

    data = []

    # Iterate over the chapters and their chunks
    for chapter, chunks in map_of_chapter_with_chunks.items():
        for chunk in chunks:
            data.append({
                'chapter': chapter,
                'chunk_text': chunk
            })

    df = pd.DataFrame(data)

    return df

def remove_Appendix_From_FinalChapter(chapters, finalChapterIndex):
    '''
    This will search for the word appendix that is attached to the 
    last chapter and then remove appendix
    '''
    index1 = chapters[finalChapterIndex].lower().find("appendix")
    chapters[finalChapterIndex] = chapters[finalChapterIndex][:index1]

    return chapters
