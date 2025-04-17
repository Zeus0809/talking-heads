import streamlit as st
from random import choice as randomize
import ollama_tools
import time
import embedded_styles
import pprint
import os
from datetime import datetime
import uuid

TITLE = "Welcome to Talking Heads AI"
CHAT_SPACE_HEIGHT = 510

def load_css(filename):
    # getting an absolute path to css
    css_path = os.path.join(os.path.dirname(__file__), filename)
    with open(css_path, "r") as f:
        css = f.read()
    st.markdown(f"""<style>{css}</style>""", unsafe_allow_html=True)

# Input callback method
def begin_conversation():

    input_a = st.session_state.input_a.strip()
    input_b = st.session_state.input_b.strip()
    model_a_alias = st.session_state.left_model_alias or "model A"
    model_b_alias = st.session_state.right_model_alias or "model B"

    # Note: model_asked uses aliases, not full model names

    if input_a and not input_b: # model A was asked
        st.session_state.initial_prompt = input_a
        st.session_state.model_asked = model_a_alias
        st.session_state.talk_started = True
    elif input_b and not input_a: # model B was asked
        st.session_state.initial_prompt = input_b
        st.session_state.model_asked = model_b_alias
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

def get_model_name_by_alias(alias: str) -> str:
    if not alias:
        raise ValueError("Can't get model name by alias because alias is None.")
    try:
        return st.session_state.model_data["all_models"].get(alias)
    except Exception as e:
        raise ValueError(e)

def clear_conversation_log() -> None:
    """Clear conversation history in case something gets reset. Used to reset the conversation."""
    st.session_state.conversation_log["left_model_log"].clear()
    st.session_state.conversation_log["right_model_log"].clear()
    st.session_state.show_clear_button = False

def update_system_prompts(new_prompt: str, side: str) -> None:
    """Update system prompts in session state to preserve them across different models."""
    st.session_state[f"{side}_system_prompt"] = new_prompt

def wait_for_ollama(timeout=30):
    """Keep sending requests to ollama every second until it responds"""
    import requests
    for _ in range(timeout):
        try:
            res = requests.get("http://localhost:11434/api/tags")
            if res.status_code == 200:
                return True
        except requests.exceptions.ConnectionError:
            pass
        time.sleep(1)
    raise RuntimeError(f"Ollama server did not become ready in {timeout} seconds.")

def get_country_code():
    lang = st.context.headers.get("Accept-Language", "")
    if "-" in lang:
        return lang.split(",")[0].split("-")[1].upper()
    return "UNK"

def get_log_file_path():
    if "log_file_path" not in st.session_state:
        country = get_country_code()
        session_id = str(uuid.uuid4())[:8]
        filename = f"logs/debug_{country}_{session_id}.log"
        full_path = os.path.join(os.path.dirname(__file__), filename)
        st.session_state["log_file_path"] = full_path
    return st.session_state.log_file_path

def main():
    st.set_page_config(layout="wide", initial_sidebar_state="collapsed")
    load_css("styles.css")

    st.title(TITLE)

    # start ollama
    ollama_tools.start_ollama()
    with st.spinner("Waiting for Ollama to wake up... 🦙🦙🦙"):
        try:
            wait_for_ollama()
        except RuntimeError:
            st.warning("The LLM server failed to start on time. Try again.")
            st.stop()

    # Initialize params in session state
    if "model_data" not in st.session_state:
        model_names = ollama_tools.get_models()
        model_data = ollama_tools.assign_model_aliases(model_names) # { "alias": "model_name" }
        left_group, right_group = ollama_tools.split_models_into_groups(model_data) # { "alias": "model_name" }
        st.session_state["model_data"] = {}
        st.session_state["model_data"]["all_models"] = model_data
        st.session_state["model_data"]["left_group"] = left_group
        st.session_state["model_data"]["right_group"] = right_group
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
    if "left_model_alias" not in st.session_state:
        st.session_state["left_model_alias"] = randomize(list(st.session_state["model_data"]["left_group"].keys()))
    if "right_model_alias" not in st.session_state:
        st.session_state["right_model_alias"] = randomize(list(st.session_state["model_data"]["right_group"].keys()))
    if "left_system_prompt" not in st.session_state:
        st.session_state["left_system_prompt"] = ollama_tools.DEFAULT_SYSTEM_PROMPT_LEFT
    if "right_system_prompt" not in st.session_state:
        st.session_state["right_system_prompt"] = ollama_tools.DEFAULT_SYSTEM_PROMPT_RIGHT
    if "max_turns" not in st.session_state:
        st.session_state["max_turns"] = 6 # default to 6 messages per conversation
    if "use_context" not in st.session_state:
        st.session_state["use_context"] = True
    if "conversation_log" not in st.session_state:
        st.session_state["conversation_log"] = { "left_model_log": [], "right_model_log": [] }
    if "show_clear_button" not in st.session_state:
        st.session_state["show_clear_button"] = False

    # Hide sidebar when conversation is ongoing
    if st.session_state.talk_started:
        st.markdown(
            """
            <style>
            [data-testid="stSidebar"] {
                display: none;
            }
            [data-testid="stSidebarNav"] {
                display: none;
            }
            </style>
            """,
            unsafe_allow_html=True,
    )

    with st.sidebar:
        st.title("Conversation Settings")
        # Max turns slider
        st.slider("Messages to generate per conversation", min_value=2, max_value=50, step=1, key="max_turns")
        # Use context
        st.checkbox("Take context into account", key="use_context", help="If enabled, models will remember the context of the conversation.")
        # New conversation button
        if st.button("Restart"):
            st.session_state.talk_started = False
            st.session_state.initial_prompt = ""
            st.session_state.model_asked = ""
            st.session_state.left_model_alias = randomize(list(st.session_state["model_data"]["left_group"].keys()))
            st.session_state.right_model_alias = randomize(list(st.session_state["model_data"]["right_group"].keys()))
            st.session_state.left_system_prompt = ollama_tools.DEFAULT_SYSTEM_PROMPT_LEFT
            st.session_state.right_system_prompt = ollama_tools.DEFAULT_SYSTEM_PROMPT_RIGHT
            clear_conversation_log()
            st.rerun()

    # Header (3 tiles)
    ask_left, initial_prompt_box, ask_right = st.columns([1, 2, 1], border=False)
    with ask_left:
        st.markdown('<div class="ask-left">', unsafe_allow_html=True)

        if st.session_state.left_model_alias == None: # in case user deselects a model
            left_alias = "🤗"
        else:
            left_alias = st.session_state.left_model_alias
        
        st.text_input(f"Ask `{left_alias}`:", placeholder="Hit ENTER when done", key="input_a", on_change=begin_conversation)
        st.markdown("</div>", unsafe_allow_html=True)
    with ask_right:
        st.markdown('<div class="ask-right">', unsafe_allow_html=True)

        if st.session_state.right_model_alias == None: # in case user deselects a model
            right_alias = "🤗"
        else:
            right_alias = st.session_state.right_model_alias

        st.text_input(f"Ask `{right_alias}`:", placeholder="Hit ENTER when done", key="input_b", on_change=begin_conversation)
        st.markdown("</div>", unsafe_allow_html=True)
    with initial_prompt_box:
        st.markdown('<div class="initial-prompt">', unsafe_allow_html=True)
        if st.session_state.model_asked and st.session_state.initial_prompt:
            st.write("To begin this conversation, you asked `" + st.session_state.model_asked + "` :")
            st.caption("“ *" + st.session_state.initial_prompt + "* ”")
        else:
            st.write(f"To start a conversation, ask or say something to one of the models: {st.session_state.left_model_alias} or {st.session_state.right_model_alias}.")
            st.caption("*[initial prompt goes here]*")
        st.markdown("</div>", unsafe_allow_html=True)

    # Body (3 tiles)
    model_left, chat_area, model_right = st.columns([1, 2, 1], border=True)
    with model_left:
        st.markdown('<div class="model-left">', unsafe_allow_html=True)
        st.pills("Pick a model:", st.session_state.model_data["left_group"].keys(), selection_mode="single", key="left_model_alias", on_change=clear_conversation_log)
        left_sys_prompt = st.text_area("System prompt:", value=st.session_state.left_system_prompt, placeholder=f"Give a role to {st.session_state.left_model_alias}", height=300)
        update_system_prompts(left_sys_prompt, "left")
        st.session_state.show_clear_button = False
        st.markdown("</div>", unsafe_allow_html=True)
    with model_right:
        st.markdown('<div class="model-right">', unsafe_allow_html=True)
        st.pills("Pick a model:", st.session_state.model_data["right_group"].keys(), selection_mode="single", key="right_model_alias", on_change=clear_conversation_log)
        right_sys_prompt = st.text_area("System prompt:", value=st.session_state.right_system_prompt, placeholder=f"Give a role to {st.session_state.right_model_alias}", height=300)
        update_system_prompts(right_sys_prompt, "right")
        st.session_state.show_clear_button = False
        st.markdown("</div>", unsafe_allow_html=True)
    with chat_area:
        with st.container(height=CHAT_SPACE_HEIGHT, border=False):
        
            if st.session_state.talk_started:
                # initialize the conversation
                current_model_alias = st.session_state.model_asked
                current_prompt = st.session_state.initial_prompt
                current_system_prompt = st.session_state.left_system_prompt if current_model_alias == st.session_state.left_model_alias else st.session_state.right_system_prompt

                for turn in range(st.session_state.max_turns): 

                    # get the response from the current model
                    current_model_name = get_model_name_by_alias(current_model_alias)
                    model_side = "left" if current_model_alias == st.session_state.left_model_alias else "right"
                    model_reply_generator = ollama_tools.get_llm_response_streaming(current_model_name, current_system_prompt, chat_history=st.session_state.conversation_log.get(f"{model_side}_model_log"), prompt=current_prompt)

                    # Display model response
                    placeholder = st.empty()
                    with st.spinner(f"{current_model_alias} is thinking..."):
                        # spin until the first chunk arrives
                        first_chunk = next(model_reply_generator)["message"]["content"]
                    # render first chunk
                    embedded_styles.render_model_response(first_chunk, placeholder, model_side)
                    time.sleep(0.15)
                    model_full_message = first_chunk
                    # keep iterating over the rest of the message
                    for chunk in model_reply_generator:
                        model_full_message += chunk['message']['content']
                        embedded_styles.render_model_response(model_full_message, placeholder, model_side)
                        time.sleep(0.15)
                    
                    # update conversation log for the model we just ran inference on
                    if st.session_state.use_context:
                        #    1) set current_prompt as user's content
                        mcp_prompt = {"role": "user", "content": current_prompt}
                        st.session_state.conversation_log[f"{model_side}_model_log"].append(mcp_prompt)
                        #    2) set model_full_message as assistant's content
                        mcp_response = {"role": "assistant", "content": model_full_message}
                        st.session_state.conversation_log[f"{model_side}_model_log"].append(mcp_response)

                    # update the prompt for the next model
                    current_prompt = model_full_message
                    # update system prompt for next model
                    current_system_prompt = st.session_state.right_system_prompt if current_model_alias == st.session_state.left_model_alias else st.session_state.left_system_prompt
                    # update the model for the next turn
                    current_model_alias = st.session_state.right_model_alias if current_model_alias == st.session_state.left_model_alias else st.session_state.left_model_alias
                
                st.session_state.talk_started = False
                st.session_state.show_clear_button = True

            # Clear Conversation button
            if st.session_state.show_clear_button:
                if st.button("CLEAR CONVERSATION", use_container_width=False):
                    st.session_state.initial_prompt = ""
                    st.session_state.model_asked = ""
                    clear_conversation_log()
                    st.rerun()

    if st.session_state.show_clear_button:
        # log only once after conversation is finished
        log_path = get_log_file_path()
        with open(log_path, 'a') as f:
            f.write("\n" + "="*50 + "\n")
            f.write(f"🕒 New session started: {datetime.now().isoformat()}\n")
            f.write("="*50 + "\n")
            pprint.pprint(dict(st.session_state.conversation_log), stream=f)
            pprint.pprint(dict(st.context.headers), stream=f)


if __name__ == "__main__":
    main()
