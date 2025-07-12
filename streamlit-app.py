import os
import json
import pandas as pd
import traceback
from dotenv import load_dotenv
import streamlit as st
from src.mcqgenerator.utils import read_file, get_table_data
from src.mcqgenerator.logger import logging
from src.mcqgenerator.MCQGenerator import gen_eval_chain
from langchain_community.callbacks.manager import get_openai_callback


with open('/workspaces/mcqgen/response.json', 'r') as file:
    RESPONSE_JSON = json.load(file)

st.title("MCQs Application with LangChain")

with st.form("user_inputs"):
    uploaded_file = st.file_uploader("Upload a PDF or txt file")

    mcq_count = st.number_input("No. of MCQs", min_value=3, max_value=50)

    subject = st.text_input("Insert Subject", max_chars=20)

    tone = st.text_input("Complexity Level Of Questions", max_chars=20, placeholder="Simple")

    button = st.form_submit_button("Create MCQs")


    if button and uploaded_file is not None and mcq_count and subject and tone:
        with st.spinner("loading..."):

            try:
                text = read_file(uploaded_file)

                with get_openai_callback() as cb:
                    response = gen_eval_chain(
                        {
                            "text": text,
                            "number": mcq_count,
                            "subject": subject,
                            "tone": tone,
                            "response_json": json.dumps(RESPONSE_JSON)

                        }
                        )
                # st.write(response)


            except Exception as e:
                traceback.print_exception(type(e), e, e.__traceback__)
                st.error("Error")

            
            else:
                print(f"Total tokens used: {cb.total_tokens}")
                print(f"Prompt tokens: {cb.prompt_tokens}")
                print(f"Completion tokens: {cb.completion_tokens}")
                print(f"Total cost: {cb.total_cost}")

                if isinstance(response, dict):

                    quiz = response.get("quiz", None)
                    if quiz is not None:
                        table_data = get_table_data(quiz)
                        if table_data is not None:
                            print("==== DEBUG ====")
                            print("type:", type(table_data))
                            print("value:", table_data)
                            print("================")

                            df = pd.DataFrame(table_data)
                            df.index = df.index + 1
                            st.table(df)
                            st.text_area(label="Review", value=response["review"])

                        else:
                            st.error("Error in the table data")

                    else:
                        st.write(response)
