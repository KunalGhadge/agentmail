import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    # Try streamlit secrets
    import streamlit as st
    try:
        api_key = st.secrets["GOOGLE_API_KEY"]
    except:
        pass

if not api_key:
    print("ERROR: No API key found.")
    exit(1)

genai.configure(api_key=api_key)

print(f"[*] Checking models for key: {api_key[:5]}...{api_key[-5:]}")
try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"- {m.name}")
except Exception as e:
    print(f"[!] Error listing models: {e}")
