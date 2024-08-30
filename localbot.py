# You can use this little file to see if you can talk to the local bot with python
# without all the rest of the D&D crap gettin in the way.
# This should output some rhyming nonesense in the python command line

import requests

url = "http://localhost:1234/v1/chat/completions"
headers = {"Content-Type": "application/json"}
data = {
    "model": "lmstudio-community/Meta-Llama-3.1-8B-Instruct-GGUF/Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf",
    "messages": [
      { "role": "system", "content": "Always answer in rhymes. Today is Thursday" },
      { "role": "user", "content": "What day is it today?" }
    ],
    "temperature": 0.7,
    "max_tokens": -1,
    "stream": False
}

def make_post_request(url, headers, data):
    try:
        response = requests.post(url, json=data, headers=headers)
        
        if response.status_code == 200:
            #print("Request successful. Response:", response.json())
            choices = response.json()["choices"]
            for choice in choices:
                message_content = choice["message"]["content"]
                print(f"Message Content: {message_content}")
    
    except requests.exceptions.RequestException as e:
        print(f"Error making request: {e}")

try:
    make_post_request(url, headers, data)

except Exception as e:
    print(f"An unexpected error occurred: {e}")