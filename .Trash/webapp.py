from flask import Flask, render_template, request, session
import os
import json
import openai
import config

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Generate a random session key

openai.api_key = config.chatbotParm['openai.api_key']
system_prompt = config.Qprompt

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        user_message = request.form.get('message')
        
        # Ensure we're working with a list
        conversation_history = json.loads(session.get('conversation_history', json.dumps([{"role": "system", "content": system_prompt}])))
        
        bot_response = chat(user_message, conversation_history)
        
        # Convert back to string before storing to session
        session['conversation_history'] = json.dumps(conversation_history)
        
        return render_template('index.html', bot_response=bot_response)

    # This initializes the session with a default list containing the system prompt
    session['conversation_history'] = json.dumps([{"role": "system", "content": system_prompt}])
    return render_template('index.html', bot_response=None)

def chat(prompt, conversation_history):
    conversation_history.append({"role": "user", "content": prompt})

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-16k",
        messages=conversation_history,
        temperature=0.2,
        max_tokens=500,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )

    try:
        answer = response['choices'][0]['message']['content']
        conversation_history.append({"role": "assistant", "content": answer})
    except:
        answer = 'Oops... Please refresh the page...'

    return answer

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
