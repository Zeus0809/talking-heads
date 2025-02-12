import streamlit as st
import requests

TITLE = "Welcome to Talking Heads AI"

API_URL_MODELS = "http://192.168.0.122:1234/v1/models"
API_URL_CHAT = "http://192.168.0.122:1234/v1/chat/completions"
model_name = ""
prompt = ""

# retrieve LLM response
def get_llm_response(response):
    json = response.json()
    return json["choices"][0]["message"]["content"]

def main():
    st.set_page_config(layout="wide")
    st.title(TITLE)
    st.markdown("""
        <style>
        .block-container {
            padding-top: 2rem;
            padding-right: 0rem;
            padding-left: 0rem;
            padding-bottom: 0rem;
            text-align: center
        }
        </style>
    """,
    unsafe_allow_html=True
    )
    col_left, col_center, col_right = st.columns([1, 2, 1], border=True)

    





# Construct the message for LLM server
messages = [{"role" : "user", "content": prompt}]

# Construct the payload for LLM
payload = {
    "model" : model_name ,
    "messages" : messages ,
    "max_tokens" : 100
}


# API call to LLM
# response = requests.post(API_URL_CHAT, json=payload)
# if response.status_code == 200 :
#     print("AI: ", get_llm_response(response))
# else :
#     print("Error: ", response.status_code, response.text)




if __name__ == "__main__":
    main()
