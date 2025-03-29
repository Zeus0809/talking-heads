system = {
    'role': 'system',
    'content': 'You are a helpful assistant that can answer questions and help with tasks.',
}

chat_history = [
  {
    'role': 'user',
    'content': 'Why is the sky blue?',
  },
  {
    'role': 'assistant',
    'content': "The sky is blue because of the way the Earth's atmosphere scatters sunlight.",
  },
  {
    'role': 'user',
    'content': 'What is atmosphere?',
  },
  {
    'role': 'assistant',
    'content': "It's a giant layer of gases that surrounds the Earth. It's made up of nitrogen, oxygen, and other gases.",
  },
]

user_message = {
    'role': 'user',
    'content': 'Tell me more about those gases.',
}

messages = [system]
messages.extend(chat_history)
messages.append(user_message)

print(messages)