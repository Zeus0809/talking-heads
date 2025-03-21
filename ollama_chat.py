import ollama
import requests
import subprocess
import time
import pprint

ollama_process = None

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


