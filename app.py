import streamlit as st
import requests
import random
import pprint

TITLE = "Welcome to Talking Heads AI"
CHAT_SPACE_HEIGHT = 660

# Configuration
MAX_TOKENS = 50  # Limit responses to this many tokens

# Ollama API endpoints
OLLAMA_API_MODELS = "http://localhost:11434/api/tags"
OLLAMA_API_CHAT = "http://localhost:11434/api/chat"
OLLAMA_API_GENERATE = "http://localhost:11434/api/generate"

def load_css(filename):
    with open(filename, "r") as f:
        css = f.read()
    st.markdown(f"""<style>{css}</style>""", unsafe_allow_html=True)

# Fetch available Ollama models
def fetch_ollama_models():
    try:
        response = requests.get(OLLAMA_API_MODELS)
        if response.status_code == 200:
            models = response.json()
            model_names = [model['name'] for model in models['models']]
            return model_names
        else:
            st.write(f"\nError fetching models: {response.status_code}")
            return []
    except Exception as e:
        st.write(f"\nError connecting to Ollama API: {e}")
        return []
    
def get_model_response(model, chat_history):
    try:
        # Prepare the request payload with the prompt and model
        payload = {
            "model": model,
            "messages": chat_history,
            "stream": False,
            "options": {
                "num_predict": MAX_TOKENS  # Limit the response length
            }
        }
        
        print(f"Sending request to {model} with payload:")
        pprint.pprint(payload)
        
        # Send the request to the Ollama API
        response = requests.post(OLLAMA_API_CHAT, json=payload)
        
        # Check if the request was successful
        if response.status_code == 200:
            result = response.json()
            print("API response:")
            pprint.pprint(result)
            
            # Extract the response content based on the response format
            if 'message' in result and 'content' in result['message']:
                return result['message']['content']
            elif 'response' in result:
                return result['response']
            else:
                st.error(f"Unexpected response format: {result}")
                return "Error: Unexpected response format from API"
        else:
            st.error(f"API Error: {response.status_code} - {response.text[:200]}")
            return f"Error: Received status code {response.status_code} from API"
    except Exception as e:
        st.error(f"Exception: {str(e)}")
        return f"Error communicating with the model: {str(e)}"

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

    # Fetch available Ollama models
    model_names = fetch_ollama_models()

    # Initialize params in session state with default values
    default_state = {
        "input_a": "",
        "input_b": "",
        "talk_started": False,
        "initial_prompt": "",
        "model_asked": "",
        "left_model": random.choice(model_names) if model_names else "No models available",
        "right_model": random.choice(model_names) if model_names else "No models available",
        "chat_history": {},
        "conversation_log": [],  # this log is for UI display of the conversation
        "conversation_active": False
    }
    
    # Initialize all session state variables if they don't exist
    for key, value in default_state.items():
        if key not in st.session_state:
            st.session_state[key] = value

    # Header (3 tiles)
    ask_left, initial_propmt_box, ask_right = st.columns([1, 2, 1], border=False)
    with ask_left:
        st.markdown('<div class="ask-left">', unsafe_allow_html=True)

        if st.session_state.left_model == None: # in case user deselects a model
            left_alias = "🤗"
        else:
            left_alias = st.session_state.left_model.split(":")[0]
        
        st.text_input(f"Ask {left_alias}:", key="input_a", on_change=begin_conversation)
        st.markdown("</div>", unsafe_allow_html=True)
    with ask_right:
        st.markdown('<div class="ask-right">', unsafe_allow_html=True)

        if st.session_state.right_model == None: # in case user deselects a model
            right_alias = "🤗"
        else:
            right_alias = st.session_state.right_model.split(":")[0]

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
        
        # Move the STOP CONVERSATION button to the top of the chat area for better visibility
        if st.session_state.conversation_active:
            st.button("STOP CONVERSATION", key="stop_button", icon="🔴", use_container_width=True, 
                      on_click=lambda: setattr(st.session_state, "conversation_active", False))
        
        with st.container(height=CHAT_SPACE_HEIGHT, border=False):
            # Display the conversation log with proper left/right justification
            for entry in st.session_state.conversation_log:
                if entry["model"] == st.session_state.left_model:
                    # Left-justify messages from the left model
                    cols = st.columns([3, 2])
                    with cols[0]:
                        st.markdown('<div class="left-message-container">', unsafe_allow_html=True)
                        with st.chat_message("assistant", avatar="🤖"):
                            st.write(entry['content'])
                        st.markdown('</div>', unsafe_allow_html=True)
                elif entry["model"] == st.session_state.right_model:
                    # Right-justify messages from the right model
                    cols = st.columns([2, 3])
                    with cols[1]:
                        st.markdown('<div class="right-message-container">', unsafe_allow_html=True)
                        with st.chat_message("assistant", avatar="👽"):
                            st.write(entry['content'])
                        st.markdown('</div>', unsafe_allow_html=True)
            
            # On user input + Enter, start the conversation
            if st.session_state.talk_started and not st.session_state.conversation_active:
                
                # No need to explicitly load models - Ollama API handles this automatically
                
                st.session_state.conversation_active = True
                
                # Initialize chat history for both models with proper structure
                st.session_state["chat_history"][st.session_state.left_model] = []
                st.session_state["chat_history"][st.session_state.right_model] = []
                
                # Add the initial prompt to the chat history of the model being asked
                st.session_state["chat_history"][st.session_state.model_asked].append({
                    "role": "user",
                    "content": st.session_state.initial_prompt
                })
                
                # Add a placeholder to show that the model is thinking
                with st.status(f"{st.session_state.model_asked.split(':')[0]} is thinking...", expanded=True):
                    # Get the first model response
                    model_response = get_model_response(
                        st.session_state.model_asked, 
                        st.session_state["chat_history"][st.session_state.model_asked]
                    )
                
                # Only proceed if we got a valid response
                if model_response and isinstance(model_response, str) and model_response.strip() and not model_response.startswith("Error:"):
                    # Add the response to the conversation log
                    st.session_state.conversation_log.append({
                        "role": "assistant",
                        "model": st.session_state.model_asked,
                        "content": model_response
                    })
                    
                    # Add the response to the chat history of the model asked
                    st.session_state["chat_history"][st.session_state.model_asked].append({
                        "role": "assistant",
                        "content": model_response
                    })
                    
                    # Add to the other model's history as a user message
                    other_model = st.session_state.right_model if st.session_state.model_asked == st.session_state.left_model else st.session_state.left_model
                    st.session_state["chat_history"][other_model].append({
                        "role": "user",
                        "content": model_response
                    })
                    
                    # Rerun to update the UI
                    st.rerun()
                else:
                    st.error(f"Failed to get a valid response from {st.session_state.model_asked}: {model_response}")
                    st.session_state.conversation_active = False
            
            # Continue the conversation if it's active
            if st.session_state.conversation_active and len(st.session_state.conversation_log) > 0:
                # Determine which model should respond next
                last_assistant = st.session_state.conversation_log[-1]
                
                # Only proceed if we have a valid last message
                if "model" in last_assistant and "content" in last_assistant and last_assistant["content"].strip():
                    if last_assistant["model"] == st.session_state.left_model:
                        next_model = st.session_state.right_model
                    else:
                        next_model = st.session_state.left_model
                    
                    # Make sure we have valid chat history
                    if next_model in st.session_state["chat_history"] and st.session_state["chat_history"][next_model]:
                        # Add a placeholder to show that the model is thinking
                        with st.status(f"{next_model.split(':')[0]} is thinking...", expanded=True):
                            # Get the next response
                            next_response = get_model_response(
                                next_model,
                                st.session_state["chat_history"][next_model]
                            )
                        
                        # Only proceed if we got a valid response
                        if next_response and isinstance(next_response, str) and next_response.strip() and not next_response.startswith("Error:"):
                            # Add the response to the conversation log
                            st.session_state.conversation_log.append({
                                "role": "assistant",
                                "model": next_model,
                                "content": next_response
                            })
                            
                            # Add the response to this model's chat history
                            st.session_state["chat_history"][next_model].append({
                                "role": "assistant",
                                "content": next_response
                            })
                            
                            # Add to the other model's history as a user message
                            other_model = st.session_state.left_model if next_model == st.session_state.right_model else st.session_state.right_model
                            st.session_state["chat_history"][other_model].append({
                                "role": "user",
                                "content": next_response
                            })
                            
                            # Rerun to update the UI
                            st.rerun()
                        else:
                            st.error(f"Failed to get a valid response from {next_model}: {next_response}")
                            st.session_state.conversation_active = False
                    else:
                        st.error(f"No valid chat history for {next_model}")
                        st.session_state.conversation_active = False
                else:
                    st.error("Last message is invalid or empty")
                    st.session_state.conversation_active = False
        
        # Close the chat-area div properly
        st.markdown("</div>", unsafe_allow_html=True)

    # For debugging - comment out in production
    with st.expander("Debug Information"):
        st.write("Session State:", st.session_state)

if __name__ == "__main__":
    main()
