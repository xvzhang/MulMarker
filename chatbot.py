import os
import json
import openai
import config

openai.api_key = config.chatbotParm['openai.api_key']

def chat(prompt, conversation_history):

    conversation_history.append({"role": "user", "content": prompt})

    # Use conversation history with OpenAI API
    response = openai.ChatCompletion.create(
        # model="gpt-3.5-turbo",
        model="gpt-3.5-turbo-16k",
        messages=conversation_history,
        temperature=0.2,
        # max_tokens=4096,
        max_tokens=500,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    ) 

    try:
        answer = response['choices'][0]['message']['content']
        # Add bot's current message to conversation history
        conversation_history.append({"role": "assistant", "content": answer})
    except:
        answer = 'Oops... Please refresh the page...'

    return answer

