import streamlit as st
import requests
import random
import pprint
import time

TITLE = "Welcome to Talking Heads AI"
CHAT_SPACE_HEIGHT = 660

# Configuration
DEFAULT_MAX_TOKENS = 50  # Default limit for responses
DEFAULT_MAX_TURNS = 10   # Maximum number of conversation turns (to prevent infinite loops)
MIN_TURNS = 2
MAX_TURNS = 30

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
        # Get the appropriate token limit based on which model is being used
        if model == st.session_state.left_model:
            max_tokens = st.session_state.left_max_tokens
        elif model == st.session_state.right_model:
            max_tokens = st.session_state.right_max_tokens
        else:
            max_tokens = DEFAULT_MAX_TOKENS  # Fallback to default
        
        # Prepare the request payload with the prompt and model
        payload = {
            "model": model,
            "messages": chat_history,
            "stream": False,
            "options": {
                "num_predict": max_tokens  # Use the model-specific token limit
            }
        }
        
        # Check if model is None before trying to use it
        if model is None:
            return "Error: No model selected"
            
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
    
    # Check if models are selected before starting conversation
    if st.session_state.left_model is None and input_a:
        st.error("Please select a model for the left side before asking a question.")
        st.session_state.input_a = ""
        return
        
    if st.session_state.right_model is None and input_b:
        st.error("Please select a model for the right side before asking a question.")
        st.session_state.input_b = ""
        return
    
    model_a = "model A" if st.session_state.left_model is None else st.session_state.left_model
    model_b = "model B" if st.session_state.right_model is None else st.session_state.right_model

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

def stop_conversation():
    """Stop the ongoing conversation and reset the conversation state."""
    st.session_state.conversation_active = False
    st.session_state.talk_started = False
    st.session_state.conversation_complete = True
    # We keep the conversation_log intact so the user can see the conversation history
    
    # Force a rerun to update the UI immediately
    st.rerun()

def run_conversation_turn(model, chat_history):
    """Run a single turn of the conversation with the specified model."""
    # Add a placeholder to show that the model is thinking
    with st.status(f"{model.split(':')[0]} is thinking...", expanded=True):
        # Get the model response
        response = get_model_response(model, chat_history)
    
    # Only proceed if we got a valid response
    if response and isinstance(response, str) and response.strip() and not response.startswith("Error:"):
        return response
    else:
        st.error(f"Failed to get a valid response from {model}: {response}")
        return None

def main():
    st.set_page_config(
        layout="wide",
        initial_sidebar_state="collapsed",  # Can be "auto", "expanded", or "collapsed"
        page_title="Talking Heads AI",
        page_icon="🤖"
    )
    load_css("styles.css")
    
    # Create a sidebar for general settings
    with st.sidebar:
        st.title("General Settings")
        
        # Add a note about collapsing the sidebar with better visibility
        st.markdown("<div style='background-color: #f0f7ff; padding: 10px; border-radius: 5px; border-left: 3px solid #4CAF50; margin-bottom: 15px;'><strong>💡 Tip:</strong> Click the arrow in the top right to collapse this sidebar</div>", unsafe_allow_html=True)
        
        # Custom increment/decrement control for maximum conversation turns
        st.markdown("### Maximum Turns")
        st.markdown("<span style='color: #333333;'>Set how many exchanges between models.</span>", unsafe_allow_html=True)
        
        # Initialize max_turns in session state if it doesn't exist
        if "max_turns" not in st.session_state:
            st.session_state.max_turns = DEFAULT_MAX_TURNS
        
        # Create three columns for the decrement button, value display, and increment button
        dec_col, val_col, inc_col = st.columns([1, 1, 1])
        
        # Decrement button
        with dec_col:
            if st.button("⬇️", key="decrement", help="Decrease maximum turns"):
                if st.session_state.max_turns > MIN_TURNS:  # Minimum value check
                    st.session_state.max_turns -= 1
        
        # Display current value
        with val_col:
            st.markdown(f"<div style='text-align: center; font-size: 1.8rem; font-weight: bold; color: #4CAF50; background-color: #f0f7f0; border: 2px solid #4CAF50; border-radius: 8px; padding: 0.3rem;'>{st.session_state.max_turns}</div>", unsafe_allow_html=True)
        
        # Increment button
        with inc_col:
            if st.button("⬆️", key="increment", help="Increase maximum turns"):
                if st.session_state.max_turns < MAX_TURNS:  # Maximum value check
                    st.session_state.max_turns += 1
        
        # Store the max_turns value for use in the app
        max_turns = st.session_state.max_turns
        
        # Add a divider
        st.divider()
        
        # Add some information about the app with explicit styling
        st.markdown("### About Talking Heads AI")
        st.markdown("<span style='color: #333333;'>This app allows two AI models to have a conversation with each other.</span>", unsafe_allow_html=True)
        st.markdown("<span style='color: #333333;'>Start by asking a question to one of the models, then watch them discuss!</span>", unsafe_allow_html=True)
        
        # Add a divider
        st.divider()
        
        # Add a link to reset the conversation
        if st.button("Reset Conversation", type="primary"):
            # Preserve important user settings
            preserved_settings = {
                "left_model": st.session_state.left_model,
                "right_model": st.session_state.right_model,
                "left_max_tokens": st.session_state.left_max_tokens,
                "right_max_tokens": st.session_state.right_max_tokens,
                "max_turns": st.session_state.max_turns
            }
            
            # Clear all conversation-related state
            keys_to_clear = [
                "conversation_log", "conversation_active", 
                "talk_started", "conversation_complete", "conversation_turn",
                "initial_prompt", "model_asked", "input_a", "input_b", "is_rerun"
            ]
            
            # Clear each key
            for key in keys_to_clear:
                if key in st.session_state:
                    if key == "conversation_log":
                        st.session_state[key] = []  # Initialize as empty list
                    else:
                        st.session_state[key] = False if key.endswith(("active", "started", "complete", "rerun")) else ""
            
            # Reset turn counter specifically
            st.session_state.conversation_turn = 0
            
            # Reset chat_history as an empty dictionary, not an empty list
            st.session_state.chat_history = {}
            
            # Restore preserved settings
            for key, value in preserved_settings.items():
                st.session_state[key] = value
            
            # Show a success message
            st.success("Conversation has been reset!")
            
            # Force a rerun to update the UI immediately
            st.rerun()
    
    # Always display the title
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
        "conversation_active": False,
        "conversation_turn": 0,  # Track the current turn number
        "conversation_complete": False,  # Flag to indicate if conversation processing is complete
        "is_rerun": False,  # Flag to track if we're in a conversation rerun
        "max_tokens": DEFAULT_MAX_TOKENS,  # Add max_tokens to session state
        "left_max_tokens": DEFAULT_MAX_TOKENS,  # Add separate token limits for each model
        "right_max_tokens": DEFAULT_MAX_TOKENS,
        "max_turns": DEFAULT_MAX_TURNS,  # Add max_turns to session state
    }
    
    # Initialize all session state variables if they don't exist
    for key, value in default_state.items():
        if key not in st.session_state:
            st.session_state[key] = value
    
    # Update max_turns from the sidebar number input
    st.session_state.max_turns = max_turns
    
    # Ensure models are always selected (prevent None values)
    if st.session_state.left_model is None and model_names:
        st.session_state.left_model = model_names[0] # default to the first model
    if st.session_state.right_model is None and model_names:
        st.session_state.right_model = model_names[1] # default to the second model 

    # Create placeholders for different parts of the UI
    if "header_placeholder" not in st.session_state:
        st.session_state.header_placeholder = st.empty()
    if "body_placeholder" not in st.session_state:
        st.session_state.body_placeholder = st.empty()
    if "debug_placeholder" not in st.session_state:
        st.session_state.debug_placeholder = st.empty()
    
    # Render the header
    with st.session_state.header_placeholder.container():
        # Header (3 tiles)
        ask_left, initial_propmt_box, ask_right = st.columns([1, 2, 1], border=False)
        with ask_left:
            st.markdown('<div class="ask-left">', unsafe_allow_html=True)

            if st.session_state.left_model is None: # in case user deselects a model
                left_alias = "🤗"
            else:
                left_alias = st.session_state.left_model.split(":")[0]
            
            st.text_input(f"Ask {left_alias}:", key="input_a", on_change=begin_conversation)
            st.markdown("</div>", unsafe_allow_html=True)
        with ask_right:
            st.markdown('<div class="ask-right">', unsafe_allow_html=True)

            if st.session_state.right_model is None: # in case user deselects a model
                right_alias = "🤗"
            else:
                right_alias = st.session_state.right_model.split(":")[0]

            st.text_input(f"Ask {right_alias}:", key="input_b", on_change=begin_conversation)
            st.markdown("</div>", unsafe_allow_html=True)
        with initial_propmt_box:
            st.markdown('<div class="initial-prompt">', unsafe_allow_html=True)
            st.write("To begin this conversation, you asked `" + st.session_state.model_asked + "` :")
            st.caption("*" + st.session_state.initial_prompt + "*")
            st.markdown("</div>", unsafe_allow_html=True)
    
    # Render the body
    with st.session_state.body_placeholder.container():
        # Body (3 tiles)
        model_left, chat_area, model_right = st.columns([1, 2, 1], border=True)
        with model_left:
            st.markdown('<div class="model-left">', unsafe_allow_html=True)
            st.segmented_control("Pick a model:", model_names, selection_mode="single", key="left_model")
            
            # Only show settings when conversation is not active
            if not st.session_state.conversation_active:
                st.markdown('<div class="model-settings">', unsafe_allow_html=True)
                # Check if left_model is None before trying to split
                model_name = "Model" if st.session_state.left_model is None else st.session_state.left_model.split(':')[0]
                st.markdown(f"<p style='text-align:center; margin-top:10px;'><strong>{model_name} Settings</strong></p>", unsafe_allow_html=True)
                # Add a slider to control left model's token limit
                st.slider(
                    "Max Word Count:",
                    min_value=10,
                    max_value=200,
                    value=st.session_state.left_max_tokens,
                    step=10,
                    key="left_max_tokens",
                    help="Adjust the length of this model's responses."
                )
                st.markdown("</div>", unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)
        with model_right:
            st.markdown('<div class="model-right">', unsafe_allow_html=True)
            st.segmented_control("Pick a model:", model_names, selection_mode="single", key="right_model")
            
            # Only show settings when conversation is not active
            if not st.session_state.conversation_active:
                st.markdown('<div class="model-settings">', unsafe_allow_html=True)
                # Check if right_model is None before trying to split
                model_name = "Model" if st.session_state.right_model is None else st.session_state.right_model.split(':')[0]
                st.markdown(f"<p style='text-align:center; margin-top:10px;'><strong>{model_name} Settings</strong></p>", unsafe_allow_html=True)
                # Add a slider to control right model's token limit
                st.slider(
                    "Max Word Count:",
                    min_value=10,
                    max_value=200,
                    value=st.session_state.right_max_tokens,
                    step=10,
                    key="right_max_tokens",
                    help="Adjust the length of this model's responses."
                )
                st.markdown("</div>", unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)
        with chat_area:
            st.markdown('<div class="chat-area">', unsafe_allow_html=True)
            
            # Move the STOP CONVERSATION button to the top of the chat area for better visibility
            if st.session_state.conversation_active:
                if st.button("STOP CONVERSATION", key="stop_button", icon="🔴"):
                    stop_conversation()
            
            with st.container(height=CHAT_SPACE_HEIGHT, border=False):
                # Display the conversation log with proper left/right justification
                for entry in st.session_state.conversation_log:
                    if entry["role"] == "system":
                        # Center system messages (like warnings)
                        st.markdown(f'<div class="system-message">{entry["content"]}</div>', unsafe_allow_html=True)
                    elif entry["model"] == st.session_state.left_model:
                        # Left-justify messages from the left model
                        cols = st.columns([5, 1])
                        with cols[0]:
                            st.markdown('<div class="left-message-container">', unsafe_allow_html=True)
                            with st.chat_message("assistant", avatar="🤖"):
                                st.write(entry['content'])
                            st.markdown('</div>', unsafe_allow_html=True)
                    elif entry["model"] == st.session_state.right_model:
                        # Right-justify messages from the right model
                        cols = st.columns([1, 5])
                        with cols[1]:
                            st.markdown('<div class="right-message-container">', unsafe_allow_html=True)
                            with st.chat_message("assistant", avatar="👽"):
                                st.write(entry['content'])
                            st.markdown('</div>', unsafe_allow_html=True)
                
                # Process the conversation if it's not complete yet
                if st.session_state.talk_started and not st.session_state.conversation_complete:
                    # Initialize the conversation if it's not active yet
                    if not st.session_state.conversation_active:
                        st.session_state.conversation_active = True
                        st.session_state.conversation_turn = 0
                        
                        # Ensure chat_history is initialized as a dictionary
                        if not isinstance(st.session_state.chat_history, dict):
                            st.session_state.chat_history = {}
                        
                        # Initialize chat history for both models with proper structure
                        st.session_state.chat_history[st.session_state.left_model] = []
                        st.session_state.chat_history[st.session_state.right_model] = []
                        
                        # Add the initial prompt to the chat history of the model being asked
                        st.session_state.chat_history[st.session_state.model_asked].append({
                            "role": "user",
                            "content": st.session_state.initial_prompt
                        })
                        
                        # Get the first model response
                        first_response = run_conversation_turn(
                            st.session_state.model_asked,
                            st.session_state["chat_history"][st.session_state.model_asked]
                        )
                        
                        if first_response:
                            # Add the response to the conversation log
                            st.session_state.conversation_log.append({
                                "role": "assistant",
                                "model": st.session_state.model_asked,
                                "content": first_response
                            })
                            
                            # Add the response to the chat history of the model asked
                            st.session_state["chat_history"][st.session_state.model_asked].append({
                                "role": "assistant",
                                "content": first_response
                            })
                            
                            # Add to the other model's history as a user message
                            other_model = st.session_state.right_model if st.session_state.model_asked == st.session_state.left_model else st.session_state.left_model
                            st.session_state["chat_history"][other_model].append({
                                "role": "user",
                                "content": first_response
                            })
                            
                            # Increment the turn counter
                            st.session_state.conversation_turn += 1
                            
                            # Set rerun flag
                            st.session_state.is_rerun = True
                            
                            # Rerun to update the UI
                            st.rerun()
                        else:
                            st.session_state.conversation_active = False
                            st.session_state.conversation_complete = True
                            st.session_state.is_rerun = False
                    
                    # Continue the conversation for subsequent turns
                    elif st.session_state.conversation_active and len(st.session_state.conversation_log) > 0:
                        # Check if we've reached the maximum number of turns
                        if st.session_state.conversation_turn >= st.session_state.max_turns:
                            warning_message = f"Reached the maximum number of turns ({st.session_state.max_turns}). Conversation stopped."
                            st.warning(warning_message)
                            
                            # Add the warning message to the conversation log as a system message
                            st.session_state.conversation_log.append({
                                "role": "system",
                                "model": "system",
                                "content": f"⚠️ **{warning_message}**"
                            })
                            
                            st.session_state.conversation_active = False
                            st.session_state.conversation_complete = True
                            st.session_state.is_rerun = False
                            st.rerun()
                        
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
                                # Get the next response
                                next_response = run_conversation_turn(
                                    next_model,
                                    st.session_state["chat_history"][next_model]
                                )
                                
                                if next_response:
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
                                    
                                    # Increment the turn counter
                                    st.session_state.conversation_turn += 1
                                    
                                    # Add a small delay to prevent too rapid reruns
                                    time.sleep(0.5)
                                    
                                    # Set rerun flag
                                    st.session_state.is_rerun = True
                                    
                                    # Rerun to update the UI
                                    st.rerun()
                                else:
                                    st.session_state.conversation_active = False
                                    st.session_state.conversation_complete = True
                                    st.session_state.is_rerun = False
                            else:
                                st.error(f"No valid chat history for {next_model}")
                                st.session_state.conversation_active = False
                                st.session_state.conversation_complete = True
                                st.session_state.is_rerun = False
                        else:
                            st.error("Last message is invalid or empty")
                            st.session_state.conversation_active = False
                            st.session_state.conversation_complete = True
                            st.session_state.is_rerun = False
            
            # Close the chat-area div properly
            st.markdown("</div>", unsafe_allow_html=True)

    # For debugging - only show when conversation is not active
    if not st.session_state.conversation_active:
        with st.session_state.debug_placeholder.container():
            with st.expander("Debug Information"):
                st.write("Session State:", st.session_state)
                st.session_state.is_rerun = False

if __name__ == "__main__":
    main()
