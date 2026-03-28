import fitz  # PyMuPDF
import re

# doc = fitz.open("./textbooks/Biology2e-OP_aHSFm3Y.pdf")
# doc = fitz.open("./Textbooks/thinkpython2.pdf")

def extract_chapters_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)

    toc = doc.get_toc()


    mapOfChapters = []

    lastPage = 0
    for i, item in enumerate(toc):
        level, title, page = item
        # print(f"Level: {level}, Title: {title}, Page: {page}")

        # # Only top-level chapters
        if level == 1:
            # Keep only titles starting with 'Chapter' followed by a number
            if re.match(r'^Appendix', title.strip(), re.IGNORECASE) or re.match(r'^Solutions', title.strip(), re.IGNORECASE) or re.match(r'^Preface', title.strip(), re.IGNORECASE):
                continue
            clean_title = re.sub(r'\s+', ' ', title).strip()
            mapOfChapters.append([clean_title, [page]])
            lastIndex = i
        
        # elif level == 2:
        #     if re.match(r'^Glossary', title.strip(), re.IGNORECASE):
        #         mapOfChapters[len(mapOfChapters)-1][1].append(page)
        
        lastPage = page

    mapOfChapters[len(mapOfChapters)-1][1].append(lastPage)



    # assumption: The a textbook chapter end a page before the next one start
    for i, chapter in enumerate(mapOfChapters):
        if i+1 < len(mapOfChapters):
            mapOfChapters[i][1].append(mapOfChapters[i+1][1][0]-1)

    # Returns mapOfChapters array to access in test file
    return mapOfChapters

    # Print only real chapters
    # for chapter in mapOfChapters:
    #     print(chapter)

    # Print all chapters
    # print(mapOfChapters)

    # Print first chapter and pages of map of chapters
    # print(mapOfChapters[0])

    # Print pages of first chapter
    # print(mapOfChapters[0][1])




"""
TODOs:

1. Find 5 textbook pdfs online
2. Turn this into a function that will take the pdf location
3. In another file import this function and write test to see if retrievals are correct
4. If solution is mid then figure out otherways to make it better

Tips: Look into previous test in the project to set up test to learn how things
work

Note: Something weird I found is that page number on the table of contents don't
actually match the correct page that it is on the pdf. Make sure to check how the
page jumps works

Note: Due to the problem above, we currently have bad embeddings
"""

