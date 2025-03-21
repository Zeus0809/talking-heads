import streamlit as st
import random
import ollama_chat
import time

TITLE = "Welcome to Talking Heads AI"
CHAT_SPACE_HEIGHT = 660

API_URL_MODELS = "http://192.168.0.122:1234/v1/models"
API_URL_CHAT = "http://192.168.0.122:1234/v1/chat/completions"

model_names = []

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
    model_a = st.session_state.left_model or "model A"
    model_b = st.session_state.right_model or "model B"

    if input_a and not input_b: # model A was asked
        st.session_state.initial_prompt = input_a
        st.session_state.model_asked = model_a
        st.session_state.talk_started = True
    elif input_b and not input_a: # model A was asked
        st.session_state.initial_prompt = input_b
        st.session_state.model_asked = model_b
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

    # start ollama
    ollama_chat.start_ollama()
    time.sleep(1) # wait for ollama to start
    # fetch list of models
    global model_names
    model_names = ollama_chat.get_models()
    print(model_names)

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
    if "left_model" not in st.session_state:
        st.session_state["left_model"] = random.choice(model_names)
    if "right_model" not in st.session_state:
        st.session_state["right_model"] = random.choice(model_names)

    # Header (3 tiles)
    ask_left, initial_propmt_box, ask_right = st.columns([1, 2, 1], border=False)
    with ask_left:
        st.markdown('<div class="ask-left">', unsafe_allow_html=True)

        if st.session_state.left_model == None: # in case user deselects a model
            left_alias = "🤗"
        else:
            left_alias = st.session_state.left_model.split("-")[0]
        
        st.text_input(f"Ask {left_alias}:", key="input_a", on_change=begin_conversation)
        st.markdown("</div>", unsafe_allow_html=True)
    with ask_right:
        st.markdown('<div class="ask-right">', unsafe_allow_html=True)

        if st.session_state.right_model == None: # in case user deselects a model
            right_alias = "🤗"
        else:
            right_alias = st.session_state.right_model.split("-")[0]

        st.text_input(f"Ask {right_alias}:", key="input_b", on_change=begin_conversation)
        st.markdown("</div>", unsafe_allow_html=True)
    with initial_propmt_box:
        st.markdown('<div class="initial-prompt">', unsafe_allow_html=True)
        st.write("To begin this conversation, you asked `" + st.session_state.model_asked + "` :")
        st.caption("“ *" + st.session_state.initial_prompt + "* ”")
        st.markdown("</div>", unsafe_allow_html=True)

    # Body (3 tiles)
    model_left, chat_area, model_right = st.columns([1, 2, 1], border=True)
    with model_left:
        st.markdown('<div class="model-left">', unsafe_allow_html=True)
        st.segmented_control("Pick a model:", model_names, selection_mode="single", key="left_model")
        st.markdown("</div>", unsafe_allow_html=True)
    with model_right:
        st.markdown('<div class="model-right">', unsafe_allow_html=True)
        st.segmented_control("Pick a model:", model_names, selection_mode="single", key="right_model")
        st.markdown("</div>", unsafe_allow_html=True)
    with chat_area:
        st.markdown('<div class="chat-area">', unsafe_allow_html=True)
        st.container(height=CHAT_SPACE_HEIGHT, border=False)
        st.markdown("</div>", unsafe_allow_html=True)

    st.write(st.session_state)






if __name__ == "__main__":
    main()
