import streamlit as st
from random import choice as randomize
import ollama_tools
import time
import embedded_styles
import pprint

TITLE = "Welcome to Talking Heads AI"
CHAT_SPACE_HEIGHT = 510

def load_css(filename):
    with open(filename, "r") as f:
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

def update_conversation_log():
    # This is only meant to change model aliases on the change of the pills widget
    st.session_state.conversation_log = { st.session_state["left_model_alias"]: [], st.session_state["right_model_alias"]: [] }

def main():
    st.set_page_config(layout="wide", initial_sidebar_state="collapsed")
    load_css("styles.css")

    st.title(TITLE)

    # start ollama
    ollama_tools.start_ollama()
    time.sleep(0.5) # wait for ollama to start

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
        st.session_state["conversation_log"] = { st.session_state["left_model_alias"]: [], st.session_state["right_model_alias"]: [] }

    with st.sidebar:
        st.title("Conversation Settings")
        # Max turns slider
        st.slider("Messages to generate per conversation", min_value=2, max_value=50, step=1, key="max_turns")
        # Use context
        st.checkbox("Take context into account", key="use_context", help="If enabled, models will remember the context of the conversation.")
        # New conversation button
        if st.button("Reset Conversation"):
            st.session_state.talk_started = False
            st.session_state.initial_prompt = ""
            st.session_state.model_asked = ""
            st.session_state.left_model_alias = randomize(list(st.session_state["model_data"]["left_group"].keys()))
            st.session_state.right_model_alias = randomize(list(st.session_state["model_data"]["right_group"].keys()))
            st.session_state.conversation_log = { st.session_state["left_model_alias"]: [], st.session_state["right_model_alias"]: [] }
            st.rerun()

    # Header (3 tiles)
    ask_left, initial_propmt_box, ask_right = st.columns([1, 2, 1], border=False)
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
    with initial_propmt_box:
        st.markdown('<div class="initial-prompt">', unsafe_allow_html=True)
        st.write("To begin this conversation, you asked `" + st.session_state.model_asked + "` :")
        st.caption("“ *" + st.session_state.initial_prompt + "* ”")
        st.markdown("</div>", unsafe_allow_html=True)

    # Body (3 tiles)
    model_left, chat_area, model_right = st.columns([1, 2, 1], border=True)
    with model_left:
        st.markdown('<div class="model-left">', unsafe_allow_html=True)
        st.pills("Pick a model:", st.session_state.model_data["left_group"].keys(), selection_mode="single", key="left_model_alias", on_change=update_conversation_log)
        st.text_area("System prompt:", key="left_system_prompt", placeholder=f"Give a role to {st.session_state.left_model_alias}", height=300)
        st.markdown("</div>", unsafe_allow_html=True)
    with model_right:
        st.markdown('<div class="model-right">', unsafe_allow_html=True)
        st.pills("Pick a model:", st.session_state.model_data["right_group"].keys(), selection_mode="single", key="right_model_alias", on_change=update_conversation_log)
        st.text_area("System prompt:", key="right_system_prompt", placeholder=f"Give a role to {st.session_state.right_model_alias}", height=300)
        st.markdown("</div>", unsafe_allow_html=True)
    with chat_area:
        with st.container(height=CHAT_SPACE_HEIGHT, border=False):
            
            if st.session_state.talk_started:

                # initialize the conversation
                current_model_alias = st.session_state.model_asked
                current_prompt = st.session_state.initial_prompt
                current_system_prompt = st.session_state.left_system_prompt if current_model_alias == st.session_state.left_model_alias else st.session_state.right_system_prompt

                for turn in range(st.session_state.max_turns):
                    # get the response from the current model and display it
                    current_model_name = get_model_name_by_alias(current_model_alias)
                    model_side = "left" if current_model_alias == st.session_state.left_model_alias else "right"

                    model_reply_generator = ollama_tools.get_llm_response_streaming(current_model_name, current_system_prompt, chat_history=st.session_state.conversation_log.get(current_model_alias), prompt=current_prompt)

                    # Display model response
                    with st.empty():
                        model_full_message = ""
                        for chunk in model_reply_generator:
                            model_full_message += chunk['message']['content']
                            embedded_styles.render_model_response(model_full_message, model_side)
                            time.sleep(0.15)
                    
                    # update conversation log for the model we just ran inference on
                    if st.session_state.use_context:
                        #    1) set current_prompt as user's content
                        mcp_prompt = {"role": "user", "content": current_prompt}
                        st.session_state.conversation_log[current_model_alias].append(mcp_prompt)
                        #    2) set model_full_message as assistant's content
                        mcp_response = {"role": "assistant", "content": model_full_message}
                        st.session_state.conversation_log[current_model_alias].append(mcp_response)

                    # update the prompt for the next model
                    current_prompt = model_full_message
                    # update system prompt for next model
                    current_system_prompt = st.session_state.right_system_prompt if current_model_alias == st.session_state.left_model_alias else st.session_state.left_system_prompt
                    # update the model for the next turn
                    current_model_alias = st.session_state.right_model_alias if current_model_alias == st.session_state.left_model_alias else st.session_state.left_model_alias




    st.write(st.session_state)






if __name__ == "__main__":
    main()
