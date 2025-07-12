import os
import json
import traceback
import PyPDF2
import re


def read_file(file):
    if file.name.endswith(".pdf"):
        try:
            pdf_reader=PyPDF2.PdfReader(file)
            text=""
            for page in pdf_reader.pages:
                text+=page.extract_text()
            return text
            
        except Exception as e:
            raise Exception("error reading the PDF file")
        
    elif file.name.endswith(".txt"):
        return file.read().decode("utf-8")
    
    else:
        raise Exception(
            "unsupported file format only pdf and text file suppoted"
            )

def get_table_data(quiz):
    """
    Always return a list-of-dicts so pd.DataFrame works.
    Accepts either a dict OR a string (even if the string is wrapped
    in ``` or ```json fences).
    """
    #normalise to a dict
    if isinstance(quiz, str):
        #strip ``` or ```json fences the LLM sometimes adds
        quiz = re.sub(r"```(?:json)?\s*|\s*```", "", quiz).strip()
        if not quiz:
            raise ValueError("Quiz string is empty after stripping code fences")

        quiz_dict = json.loads(quiz)   #will raise if still bad
    elif isinstance(quiz, dict):
        quiz_dict = quiz
    else:
        raise TypeError("`quiz` must be dict or JSON string")

    #2. build rows for the table
    table_rows = []
    for q_no, q in quiz_dict.items():
        row = {
            "MCQ": q.get("mcq", ""),
            "Choices": " || ".join(f"{opt} → {txt}"
                                   for opt, txt in q.get("options", {}).items()),
            "Correct": q.get("correct", ""),
        }
        table_rows.append(row)

    return table_rows