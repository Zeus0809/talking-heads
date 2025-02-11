import streamlit as st
import requests

API_URL_MODELS = "http://192.168.0.122:1234/v1/models"
API_URL_CHAT = "http://192.168.0.122:1234/v1/chat/completions"
model_name = ""
prompt = ""

# retrieve LLM response
def get_llm_response(response):
    json = response.json()
    return json["choices"][0]["message"]["content"]

# Get data from user
user_model = input("What model would you like to ask? ").lower()
if user_model == "deepseek" :
    model_name = "deepseek-r1-distill-qwen-7b"
else :
    model_name = "mistral-7b-instruct-v0.3"
prompt = input("Enter the initial prompt: ")

# Construct the message for LLM server
messages = [{"role" : "user", "content": prompt}]

# Construct the payload for LLM
payload = {
    "model" : model_name ,
    "messages" : messages ,
    "max_tokens" : 100
}

# API call to LLM
response = requests.post(API_URL_CHAT, json=payload)

if response.status_code == 200 :
    print("AI: ", get_llm_response(response))
else :
    print("Error: ", response.status_code, response.text)





