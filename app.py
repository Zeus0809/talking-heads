import streamlit as st
from random import choice as randomize
import ollama_tools
import time

TITLE = "Welcome to Talking Heads AI"
CHAT_SPACE_HEIGHT = 660

def load_css(filename):
    with open(filename, "r") as f:
        css = f.read()
    st.markdown(f"""<style>{css}</style>""", unsafe_allow_html=True)

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
    elif input_b and not input_a: # model B was asked
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
    ollama_tools.start_ollama()
    time.sleep(0.5) # wait for ollama to start

    # Initialize params in session state
    if "model_names" not in st.session_state:
        st.session_state["model_names"] = ollama_tools.get_models()
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
        st.session_state["left_model"] = randomize(st.session_state["model_names"])
    if "right_model" not in st.session_state:
        st.session_state["right_model"] = randomize(st.session_state["model_names"])

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
        st.segmented_control("Pick a model:", st.session_state.model_names, selection_mode="single", key="left_model")
        st.markdown("</div>", unsafe_allow_html=True)
    with model_right:
        st.markdown('<div class="model-right">', unsafe_allow_html=True)
        st.segmented_control("Pick a model:", st.session_state.model_names, selection_mode="single", key="right_model")
        st.markdown("</div>", unsafe_allow_html=True)
    with chat_area:
        with st.container(height=CHAT_SPACE_HEIGHT, border=False):
            
            if st.session_state.talk_started:

                # initialize the conversation
                current_model = st.session_state.model_asked
                current_prompt = st.session_state.initial_prompt
                current_system_prompt = ""
                max_turns = 4

                for turn in range(max_turns):
                    # get the response from the current model and display it
                    model_reply = ollama_tools.get_llm_response(current_model, current_system_prompt, message=current_prompt)
                    model_reply = ollama_tools.remove_reasoning(model_reply)
                    
                    st.write(model_reply)
                   
                    # update the prompt for the next model
                    current_prompt = model_reply

                    # update the model for the next turn
                    current_model = st.session_state.right_model if current_model == st.session_state.left_model else st.session_state.left_model



    st.write(st.session_state)






if __name__ == "__main__":
    main()
