from backend.api._VectorCreator import VectorEmbedder
from backend.api._FunctionsToHelpBreakDownTextBook import pdf_To_String
from backend.api._FunctionsToHelpBreakDownTextBook import remove_Anything_Before_Content
from backend.api._FunctionsToHelpBreakDownTextBook import split_by_chapter
from backend.api._FunctionsToHelpBreakDownTextBook import splitIntoChunks_to_MapToChapter
from backend.api._FunctionsToHelpBreakDownTextBook import mapOfChapterWithChunks_to_DataFrame
from backend.api._FunctionsToHelpBreakDownTextBook import remove_Appendix_From_FinalChapter
import pandas as pd

def main():
    '''
    This is a script to create a CSV for the "ThinkPython2" textbook
    It is organized as:

    Columns: Chapter | Chunk Text | Chapter Name | Vector Embeddings      
    '''

    # title of text book
    textBookTitle = "thinkpython2"

    # these are the table of contents of the textbook
    tableOfContents = ["The Way of the Program", "Variables, expressions and statements", "Functions",
                        "Case study: interface design", "Conditionals and recursion", "Fruitful functions",
                          "Iteration", "Strings", "Case study: word play", "Lists", "Dictionaries", "Tuples",
                            "Case study: data structure selection", "Files", "Classes and object", "Classes and functions",
                              "Classes and methods", "Inheritance", "The Goodies"]

    # file of pdf
    pdfLocation = "./textbookPDFs/thinkpython2.pdf"

    # turning the pdf into string
    combinedText = pdf_To_String(pdfLocation)


    # remove any text before the table of contents
    removedContentText = remove_Anything_Before_Content(combinedText)

    # this function will split the text by chapters
    listSplitByChapters = split_by_chapter(removedContentText)


    # find the last chapter index
    finalChapter = len(listSplitByChapters)-1

    # removes the appendix from the last chapter
    listSplitByChapters = remove_Appendix_From_FinalChapter(listSplitByChapters, finalChapter)



    # make a make that key is chapter number and value is the text
    chapterMap = splitIntoChunks_to_MapToChapter(listSplitByChapters)

    # make data frame using the chapters map
    dataFrame = mapOfChapterWithChunks_to_DataFrame(chapterMap)

    # this named each chapter using the table of contents
    for chapter, chapter_name in enumerate(tableOfContents, start=1):
        dataFrame.loc[dataFrame['chapter'] == chapter, 'Chapter_Name'] = chapter_name

    

    # making embedding vectors using all-MiniLm-L6-v2 model
    embedder = VectorEmbedder("sentence-transformers/all-MiniLM-L6-v2", dataFrame)

    # create embeddings
    embedder.createEmbeddings()

    # print the embeddings
    embedder.printEmbeddings()

    # retireve the embeddings
    newFrame = embedder.getEmbeddingsDf()

    # turn the embeddings into csv
    newFrame.to_csv(f"./csv/{textBookTitle}.csv")

    

if __name__ == "__main__":
    main()
