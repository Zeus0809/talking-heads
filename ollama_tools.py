import ollama
import requests
import subprocess
import time
import pprint
import re

ollama_process = None
SYSTEM_CONCISE = "Keep your responses no more than 50 words. "
DEFAULT_SYSTEM_PROMPT_LEFT = "You are an absolute coffee fanatic. You advocate for everyone to drink coffee."
DEFAULT_SYSTEM_PROMPT_RIGHT = "You are an absolute tea fanatic. You advocate for everyone to drink tea."

def start_ollama():
    global ollama_process
    if ollama_process is None:
        ollama_process = subprocess.Popen(["ollama", "serve"])

def stop_ollama():
    global ollama_process
    if ollama_process:
        ollama_process.terminate()
        ollama_process = None

def get_models():
    response = requests.get("http://localhost:11434/api/tags").json()
    models = [model["name"] for model in response["models"]]
    return models

def get_llm_response(model, system_prompt, message, chat_history=None):
    raw_response = ollama.chat(model=model, messages=[{"role": "system", "content": SYSTEM_CONCISE + system_prompt}, {"role": 'user', "content": message}])
    model_response = raw_response['message']['content']
    return model_response

def remove_reasoning(response):
    return re.sub(r'<think>.*?</think>', '', response, flags=re.DOTALL)