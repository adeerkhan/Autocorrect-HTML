import streamlit as st
import openai
import csv
import pandas as pd
from PIL import Image
import os

from langchain.chat_models import ChatOpenAI
from langchain.schema import (
    SystemMessage,
    HumanMessage,
    AIMessage
)

from langchain.callbacks.base import BaseCallbackHandler


class StreamHandler(BaseCallbackHandler):
    def __init__(self, container, initial_text=""):
        self.container = container
        self.text = initial_text

    def on_llm_new_token(self, token: str, **kwargs) -> None:
        self.text += token
        self.container.markdown(self.text)


def init_gpt(gpt_model, stream_handler):
    global chat
    chat = ChatOpenAI(
        temperature=0.3,
        model_name=gpt_model,
        streaming=True,
        callbacks=[stream_handler]
    )


def chatbot(query):
        system_prompt = """You are an experience developer in HTML. You will
        be given incorrect HTML code, and your job is to correct its mistakes. 
        The criteria that you will use to classify HTML problems is the following 10
        points:
1. Syntax errors: Missing closing tags, incorrect attribute values, or improper nesting can lead to syntax errors.
2. Cross-browser compatibility: Different browsers may interpret HTML code differently, leading to inconsistencies in rendering.
3. Responsive design: Ensuring that web pages are properly displayed on different screen sizes and devices can be challenging.
4. Accessibility: Ensuring that web content is accessible to users with disabilities, such as providing proper alt text for images.
5. Broken links: Links that are not properly formatted or lead to non-existent pages can frustrate users.
6. Slow loading times: Large file sizes, excessive use of external resources, or inefficient code can result in slow page loading.
7. Form validation: Validating user input in HTML forms to prevent incorrect or malicious data from being submitted.
8. SEO optimization: Structuring HTML content to improve search engine visibility and ranking.
9. CSS conflicts: CSS styles applied to HTML elements may conflict with each other, resulting in unexpected visual behavior.
10. Mobile optimization: Ensuring that web pages are optimized for mobile devices, including touch interactions and responsive layouts.

First you will identify the above problems in the given HTML code.
Then you will write the code fixing the mentioned issues.
If you see an issue that falls outside the range of the above 10 criteria, say 'Sorry this is outside the scope of my expertise.'
If you receive any query from the user that does not related to HTML or  HTML code, say 'Sorry I can not answer that, kindly 
provide me topics related to HTML"""
        messages = [SystemMessage(content=system_prompt)]
        for i in range(len(query)):
            if i % 2 == 0:
                temp_query = HumanMessage(content=query[i]['content'])
            else:
                temp_query = AIMessage(content=query[i]['content'])
            messages.append(temp_query)
        response = chat(messages)
        return response.content


def main():
    openai.api_key = st.secrets["OPENAI_API_KEY"]
    # chat = ChatOpenAI(temperature=0)
    st.set_page_config(
        page_title = "Autocorrect HTML",
        page_icon = "💻",
        layout = "centered",
        initial_sidebar_state="expanded",
        menu_items={
        'Get Help': 'https://github.com/adeerkhan/Autocorrect-HTML',
        'Report a bug': "mailto:adeer.khan@outlook.com",
        'About': " This application was created for GreenieWeb AI Intern Post."
    })

    st.title("Autocorrect HTML")
    st.subheader("Add your HTML code below, and then converse with the bot until your code is corrected")

    with st.sidebar:
        image_logo = Image.open('data/logo.png')
        st.image(image_logo)
        st.header("Want to know about HTML?")
        df = pd.read_csv('data/data.csv', index_col=False)
        image_history = Image.open('data/htm_history.png')
        if st.checkbox("History of HTML"):
            st.image(image_history, caption = "27 years history of HTML")

        if st.checkbox("Top 10 most-common HTML bad coding practices"):
            code_prac = df.reset_index(drop=True)
            st.caption("Double click the cell to view content fully.")
            st.dataframe(code_prac, hide_index=True)
        if st.button("Remove previous message"):
            if len(st.session_state.messages) >= 2:
                st.session_state.messages = st.session_state.messages[:-2]        
        image_info = Image.open('data/side_info.png')
        st.image(image_info)
        # remove last 2 messages

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


    # Accept user input
    if prompt := st.chat_input("What code would you like me to correct?"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)

        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            stream_handler = StreamHandler(st.empty())
            init_gpt('gpt-3.5-turbo', stream_handler)
            assistant_response = chatbot(st.session_state.messages)
        st.session_state.messages.append({"role": "assistant", "content": assistant_response})

        
if __name__ == "__main__":
    main()
