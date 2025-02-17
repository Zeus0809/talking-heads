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

def get_llm_response(response):
    json = response.json()
    return json["choices"][0]["message"]["content"]

# Input callback method
def begin_conversation():

    input_a = st.session_state.input_a.strip()
    input_b = st.session_state.input_b.strip()

    if input_a and not input_b: # model A was asked
        st.session_state.initial_prompt = input_a
        st.session_state.model_asked = "model A"
        st.session_state.talk_started = True
    elif input_b and not input_a: # model A was asked
        st.session_state.initial_prompt = input_b
        st.session_state.model_asked = "model B"
        st.session_state.talk_started = True
    else: # both inputs left blank
        st.session_state.initial_prompt = ""
        st.session_state.model_asked = ""
        st.session_state.talk_started = False

    # clear inputs
    st.session_state.input_a = ""
    st.session_state.input_b = ""

    # blur focus with JS
    st.markdown("<script>document.activeElement.blur()</script>", unsafe_allow_html=True)

def main():
    st.set_page_config(layout="wide")
    load_css("styles.css")
    st.title(TITLE)

    # Initialize params in session state
    if "input_a" not in st.session_state:
        st.session_state["input_a"] = ""
    if "input_b" not in st.session_state:
        st.session_state["input_b"] = ""
    if "talk_started" not in st.session_state:
        st.session_state["talk_started"] = False
    if "initial_prompt" not in st.session_state:
        st.session_state["initial_prompt"] = ""
    if "model_asked" not in st.session_state:
        st.session_state["model_asked"] = ""

    col_left, col_chat, col_right = st.columns([1, 2, 1], border=True)
    
    with col_left:
        st.markdown('<div class="modelA">', unsafe_allow_html=True)
        st.text_input("Ask model A:", key="input_a", on_change=begin_conversation)
        st.markdown("</div>", unsafe_allow_html=True)

    with col_right:
        st.markdown('<div class="modelB">', unsafe_allow_html=True)
        st.text_input("Ask model B:", key="input_b", on_change=begin_conversation)
        st.markdown("</div>", unsafe_allow_html=True)

    with col_chat:
        st.markdown('<div class="chat-space">', unsafe_allow_html=True)

        st.write("To begin this conversation, you asked " + st.session_state.model_asked + ":")
        st.caption("“ *" + st.session_state.initial_prompt + "* ”")

        st.markdown("</div>", unsafe_allow_html=True)

    # st.write(st.session_state)


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
