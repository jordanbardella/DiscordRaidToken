import requests
import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

with open('config.json', 'r') as config_file:
    config = json.load(config_file)

text = config["text"]
tokens = config["tokens"]
cids = config["cids"]

payload = {
    "mobile_network_type": "unknown",
    "content": "",
    "nonce": "", 
    "tts": False,
    "flags": 0,
    "poll": {
        "question": {
            "text": f"{text}"
        },
        "answers": [
            {"poll_media": {"text": f"{text}"}},
            {"poll_media": {"text": f"{text}"}},
            {"poll_media": {"text": f"{text}"}},
            {"poll_media": {"text": f"{text}"}},
            {"poll_media": {"text": f"{text}"}},
            {"poll_media": {"text": f"{text}"}},
            {"poll_media": {"text": f"{text}"}},
            {"poll_media": {"text": f"{text}"}},
            {"poll_media": {"text": f"{text}"}},
            {"poll_media": {"text": f"{text}"}}
        ],
        "allow_multiselect": False,
        "duration": 336,
        "layout_type": 1
    }
}

headers = {
    "content-type": "application/json",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
}

rt = {token: 0 for token in tokens}
tl = {tokens[i]: f"{i+1}" for i in range(len(tokens))}
sc = 0

def sm(cid, token):
    global sc
    url = f"https://discord.com/api/v9/channels/{cid}/messages"
    headers["authorization"] = token
    
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    
    if response.status_code == 200:
        sc += 1
        print(f"[{sc}] Message sent: {cid} | Token: [{tl[token]}]")
    elif response.status_code == 429:
        ra = response.json().get("retry_after", 1)
        rt[token] = time.time() + ra
        print(f"Rate limit: {tl[token]} wait {ra} seconds")
    else:
        print(f"Error {response.status_code}: {response.text} for Token: [{tl[token]}]")

while True:
    current_time = time.time()
    with ThreadPoolExecutor() as executor:
        futures = []
        for cid in cids:
            for token in tokens:
                if current_time >= rt[token]:
                    futures.append(executor.submit(sm, cid, token))
        
        for future in as_completed(futures):
            future.result()
