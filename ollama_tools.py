import ollama
import requests
import subprocess
import random
import pprint
import re
import json

ollama_process = None
SYSTEM_CONCISE = "Keep your responses no more than 50 words."
DEFAULT_SYSTEM_PROMPT_LEFT = "You are an absolute coffee fanatic. You advocate for everyone to drink coffee."
DEFAULT_SYSTEM_PROMPT_RIGHT = "You are an absolute tea fanatic. You advocate for everyone to drink tea."

def start_ollama():
    global ollama_process
    if ollama_process is None:
        ollama_process = subprocess.Popen(["/Applications/Ollama.app/Contents/MacOS/ollama", "serve"])

def stop_ollama():
    global ollama_process
    if ollama_process:
        ollama_process.terminate()
        ollama_process = None

def get_models():
    response = requests.get("http://localhost:11434/api/tags").json()
    models = [model["name"] for model in response["models"]]
    return models

def assign_model_aliases(model_names: list[str]) -> dict[str, str]:
    model_data = {}
    for model in model_names:
        if "phi" in model:
            model_data["Phi 3"] = model
        elif "qwen" in model:
            model_data["Qwen 2.5"] = model
        elif "gemma" in model:
            model_data["Gemma 3"] = model
        elif "uncensored" in model:
            model_data["Unhinged llama"] = model
        elif "llama" in model and "uncensored" not in model:
            model_data["Llama 2"] = model
        elif "mistral" in model:
            model_data["Mistral"] = model
    return model_data

def split_models_into_groups(model_data: dict[str, str]) -> tuple[dict[str, str], dict[str, str]]:
    all_keys = list(model_data.keys())
    random.shuffle(all_keys)
    midpoint = len(all_keys) // 2
    left_keys = all_keys[:midpoint]
    right_keys = all_keys[midpoint:]
    left_group = {key: model_data[key] for key in left_keys}
    right_group = {key: model_data[key] for key in right_keys}
    return left_group, right_group

def get_llm_response(model, system_prompt, prompt):
    raw_response = ollama.chat(model=model, messages=[{"role": "system", "content": SYSTEM_CONCISE + system_prompt}, {"role": 'user', "content": prompt}])
    model_response = raw_response['message']['content']
    return model_response

def get_llm_response_streaming(model, system_prompt, prompt, chat_history):
    print(f"\nchat_history: {chat_history}\n")
    system_message = {"role": "system", "content": SYSTEM_CONCISE + " " + system_prompt} # goes 1st
    user_message = {"role": "user", "content": prompt} # goes 3rd after chat_history
    messages = [ system_message ]
    messages.extend(chat_history)
    messages.append(user_message)
    streamed_response = ollama.chat(model=model, messages=messages, stream=True)                          
    return streamed_response

def remove_reasoning(response):
    return re.sub(r'<think>.*?</think>', '', response, flags=re.DOTALL)