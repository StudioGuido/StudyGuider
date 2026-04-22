import fitz  # PyMuPDF
import re
import os
import uuid
from api.auth import verify_jwt
from fastapi import Depends

def is_non_chapter_title(title_lower):
    NON_CHAPTER_KEYWORDS = [
    "preface", "introduction", "acknowledgments", "acknowledgements",
    "foreword", "contents", "table of contents", "appendix",
    "glossary", "index", "bibliography", "references", "about the author",
    "dedication", "copyright", "permissions", "answer key", "select bibliography",
    "book cover", "half title", "notational symbols", "title", "cover"
    ]
    # If it starts with a number or chapter keyword, it's a real chapter
    # regardless of other words in the title
    if re.match(r'^\d+[\.\)]?\s+', title_lower):
        return False
    if re.match(r'^(chapter|unit|ch\.?)\s+\d+', title_lower):
        return False
    if re.match(r'^table of\b', title_lower):
        return True
    return any(keyword in title_lower for keyword in NON_CHAPTER_KEYWORDS)


def extract_chapters_from_pdf_Updated_Better_Version(pdf_path, supabase_uid):
    doc = fitz.open(pdf_path)
    textbook_title = doc.metadata["title"]
    toc = doc.get_toc()

    if not toc:
        raise ValueError("No metadata Table of Contents found in this PDF.")

    mapOfChapters = []

    # Collect all level-1 TOC entries with their pages first
    level1_entries = [(re.sub(r'\s+', ' ', title).strip(), page) for level, title, page in toc if level == 1]
    # indexed to standard "0" start (TOC has 1 as start index)
    level1_entries = [(title, page - 1) for title, page in level1_entries]
    

    seen_pages = {}
    deduped_entries = []

    for title, page in level1_entries:
        title_lower = title.lower()
        is_bare_chapter = bool(re.match(r'^(chapter|unit|ch\.?)\s+\d+\s*$', title_lower))
        
        if page not in seen_pages:
            seen_pages[page] = len(deduped_entries)
            deduped_entries.append((title, page))
        else:
            existing_idx = seen_pages[page]
            existing_title = deduped_entries[existing_idx][0]
            existing_is_bare = bool(re.match(r'^(chapter|unit|ch\.?)\s+\d+\s*$', existing_title.lower()))
            
            if existing_is_bare and not is_bare_chapter:
                deduped_entries[existing_idx] = (title, page)

    level1_entries = deduped_entries

    # Find the page of the last numbered chapter in the TOC
    last_numbered_page = 0
    first_numbered_page = float('inf')

    for title, page in [(re.sub(r'\s+', ' ', t).strip(), p) for level, t, p in toc if level == 1]:
        if page < 1:
            continue
        title_lower = title.lower()
        if (re.match(r'^\d+[\.\)]?\s+', title_lower) or re.match(r'^(chapter|unit|ch\.?)\s+\d+', title_lower)):
            last_numbered_page = page
            if page < first_numbered_page:
                first_numbered_page = page
    # Only apply back-matter filtering if the book uses numbered chapters
    has_numbered_chapters = last_numbered_page > 0

    filtered_pages = set()
    for idx, (title, page) in enumerate(level1_entries):
        if page < 1:
            continue
        title_lower = title.lower()
        is_numbered = (re.match(r'^\d+[\.\)]?\s+', title_lower) or
                       re.match(r'^(chapter|unit|ch\.?)\s+\d+', title_lower))
        if has_numbered_chapters and not is_numbered:
            next_page = None
            for _, np in level1_entries[idx + 1:]:
                if np >= 1:
                    next_page = np
                    break
            if next_page is not None and (next_page - page) <= 2:
                for p in range(page, next_page):  # mark all divider pages
                    filtered_pages.add(p)
    
    for idx, (clean_title, page) in enumerate(level1_entries):
        if page < 1:
            continue

        clean_title_lower = clean_title.lower()

        if is_non_chapter_title(clean_title_lower):
            continue
        
        # For unnumbered books: skip known back-matter titles
        UNNUMBERED_BACKMATTER = [
            "debugging", "analysis of algorithms", "further reading",
            "afterword", "epilogue"
        ]
        if not has_numbered_chapters and clean_title_lower in UNNUMBERED_BACKMATTER:
            continue

        is_numbered = (re.match(r'^\d+[\.\)]?\s+', clean_title_lower) or re.match(r'^(chapter|unit|ch\.?)\s+\d+', clean_title_lower))

        if has_numbered_chapters and not is_numbered and page > last_numbered_page:
            continue
        if has_numbered_chapters and not is_numbered and page < first_numbered_page:
            continue

        if has_numbered_chapters and not is_numbered:
            next_page = None
            for _, np in level1_entries[idx + 1:]:
                if np >= 1:
                    next_page = np
                    break
            if next_page is not None and (next_page - page) <= 2:
                continue

        page_obj = doc[page - 1]

        if find_chapters_by_page(page_obj, clean_title):
            mapOfChapters.append([clean_title, [page]])

    # Build end pages: each chapter ends the page before the next begins
    for i in range(len(mapOfChapters) - 1):
        start_of_next = mapOfChapters[i + 1][1][0]
        chapter_end = start_of_next - 1

        while chapter_end in filtered_pages:
            chapter_end -= 1

        mapOfChapters[i][1].append(chapter_end)

    # Last chapter: end at the page before the first trailing non-chapter
    # level-1 TOC entry, not the end of the document
    if mapOfChapters:
        last_chapter_start = mapOfChapters[-1][1][0]
        end_page = len(doc)

        for title, page in level1_entries:
            if page < 1:
                continue
            if page > last_chapter_start:
                end_page = page - 1
                break

        mapOfChapters[-1][1].append(end_page)

    listOfChapters = []

    output_dir = os.path.join(os.path.dirname(__file__), "..", "bookadders", "textbookPDFs")
    os.makedirs(output_dir, exist_ok=True)

    run_id = str(uuid.uuid4())
    run_dir = os.path.join(output_dir, supabase_uid, run_id)
    os.makedirs(run_dir, exist_ok=True)

    # Saves each chapter as a separate PDF and adds the path to listOfChapters
    for i, (_, page_range) in enumerate(mapOfChapters):
        writer = fitz.open()
        writer.insert_pdf(doc, from_page=page_range[0], to_page=page_range[1])
        output_path = os.path.join(run_dir, f"chapter{i + 1}.pdf")
        writer.save(output_path)
        listOfChapters.append(output_path)
        writer.close()

    doc.close()

    return listOfChapters, textbook_title


def find_chapters_by_page(page, toc_title=""):
    data = page.get_text("dict")
    blocks = data["blocks"]
    body_size = body_font_size(page)
    height = page.rect.height

    # Find max font size on page
    max_size = 0
    for block in blocks:
        if block["type"] != 0:
            continue
        for line in block["lines"]:
            for span in line["spans"]:
                max_size = max(max_size, span["size"])

    # Normalize TOC title for cross-validation (bonus signal only)
    toc_title_normalized = re.sub(r'\s+', ' ', toc_title).strip().lower()

    for block in blocks:
        if block["type"] != 0:
            continue
        for line in block["lines"]:
            if not line["spans"]:
                continue

            line_text = " ".join(span["text"] for span in line["spans"]).strip()
            size = max(span["size"] for span in line["spans"])
            y_top = line["bbox"][1]
            words = line_text.split()
            word_count = len(words)

            # Basic filters
            if word_count < 1 or word_count > 15:
                continue
            if "..." in line_text:
                continue
            if re.match(r'^\s*\d+\s*$', line_text):
                continue
            if any(re.match(p, line_text, re.IGNORECASE) for p in [r'^\s*appendix\s+[a-z]', r'^\s*figure\s+\d+', r'^\s*table\s+\d+']):
                continue

            conditions = 0

            # Condition 1: explicit chapter/unit pattern (strong signal)
            if (re.match(r'^\s*(chapter|unit|ch\.?)\s+\d+', line_text, re.IGNORECASE) or
                    re.match(r'^\s*\d+[\.\)]?\s+[A-Z]', line_text)):
                conditions += 2

            # Condition 2: TOC title appears on the page (bonus, not required)
            if toc_title_normalized and toc_title_normalized in line_text.lower():
                conditions += 1

            # Condition 3: positioned in the top third of the page
            if y_top < height * 0.35:
                conditions += 1

            # Condition 4: significantly larger than body text
            if body_size and size >= body_size * 1.8:
                conditions += 1

            # Condition 5: close to the page's largest font
            if max_size and size >= max_size * 0.8:
                conditions += 1

            # Condition 6: short heading
            if word_count <= 10:
                conditions += 1

            if conditions >= 3:
                return True

    return False
    

def body_font_size(page):
    data = page.get_text("dict")
    freq = {}

    for block in data["blocks"]:
        if block["type"] != 0:
            continue

        for line in block["lines"]:
            for span in line["spans"]:
                size = round(span["size"])

                if 6 <= size <= 20:
                    if size in freq:
                        freq[size] += 1
                    else:
                        freq[size] = 1

    if not freq:
        return 12  # fallback

    # find most frequent
    max_size = None
    max_count = 0

    for size in freq:
        if freq[size] > max_count:
            max_count = freq[size]
            max_size = size

    return max_size

# branch name: frontend-dev

"""
Switch to the fronend branch
Merge this research branch into fronend
Then move your code into the new endpoint that is used for S3
Then test the new endpoint
"""