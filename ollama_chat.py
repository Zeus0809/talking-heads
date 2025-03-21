import ollama
import requests
import subprocess

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


