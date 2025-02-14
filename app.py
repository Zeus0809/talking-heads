import streamlit as st
import requests

TITLE = "Welcome to Talking Heads AI"
CHAT_SPACE_HEIGHT = 800

API_URL_MODELS = "http://192.168.0.122:1234/v1/models"
API_URL_CHAT = "http://192.168.0.122:1234/v1/chat/completions"
model_name = ""
prompt = ""

def load_css(filename):
    with open(filename, "r") as f:
        css = f.read()
    st.markdown(f"""<style>{css}</style>""", unsafe_allow_html=True)

# retrieve LLM response
def get_llm_response(response):
    json = response.json()
    return json["choices"][0]["message"]["content"]

def main():
    st.set_page_config(layout="wide")
    load_css("styles.css")
    title = st.title(TITLE)

    col_left, col_chat, col_right = st.columns([1, 2, 1], border=True)
    
    with col_left:
        st.markdown('<div class="modelA">', unsafe_allow_html=True)
        first_prompt_A = st.text_input("Ask model A:")
        #print("prompt A is: ", first_prompt_A)
        model_asked = "model A" if first_prompt_A != "" else ""

        st.markdown("</div>", unsafe_allow_html=True)
    with col_right:
        st.markdown('<div class="modelB">', unsafe_allow_html=True)
        first_prompt_B = st.text_input("Ask model B:")
        #print("prompt B is: ", first_prompt_B)
        model_asked = "model B" if first_prompt_B != "" else ""
        
        st.markdown("</div>", unsafe_allow_html=True)

    with col_chat:
        st.markdown('<div class="chat-space">', unsafe_allow_html=True)

        st.write("Your initial prompt to " + model_asked)
        st.caption("[ " + first_prompt_A + " ]")

        st.markdown("</div>", unsafe_allow_html=True)

    


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
