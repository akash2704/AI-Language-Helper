import sqlite3
from datetime import datetime
from langchain.prompts import PromptTemplate
import google.generativeai as genai
import os
import dotenv
dotenv.load_dotenv()


# --- Configure Gemini 1.5 Flash API ---
API_KEY = os.getenv('GEMINI_API_KEY')  # Replace with your actual API key
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

# --- Database Setup ---
def init_db():
    conn = sqlite3.connect("language_mistakes.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS mistakes 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  user_input TEXT, 
                  mistake_type TEXT, 
                  incorrect TEXT, 
                  correct TEXT, 
                  explanation TEXT, 
                  timestamp TEXT)''')
    conn.commit()
    conn.close()

# --- Prompt Templates ---
scene_prompt = PromptTemplate(
    input_variables=["target_lang", "source_lang", "level"],
    template="You are a language teacher helping a student learn {target_lang}. Their native language is {source_lang}, and their level is {level}. Set an appropriate scene and start a conversation in {target_lang}. Output in two parts: 'Response: [conversation start]' and 'Corrections: No corrections needed for first turn'."
)

chat_prompt = PromptTemplate(
    input_variables=["target_lang", "source_lang", "user_input"],
    template="Continue the conversation in {target_lang} based on the student's response: '{user_input}'. Output in two parts: 'Response: [reply in {target_lang}]' and 'Corrections: [list mistakes with type, incorrect, correct, explanation in {source_lang}, or 'No corrections needed']'."
)

feedback_prompt = PromptTemplate(
    input_variables=["source_lang", "mistakes"],
    template="Review the student's mistakes: {mistakes}. Provide a summary in {source_lang}, highlighting strengths, common mistake types, and improvement suggestions."
)

# --- Functions ---
def parse_output(output):
    response = output.split("Corrections:")[0].replace("Response:", "").strip()
    corrections = output.split("Corrections:")[1].strip() if "Corrections:" in output else "No corrections needed"
    return response, corrections

def record_mistake(user_input, corrections, source_lang):
    if "No corrections needed" not in corrections:
        conn = sqlite3.connect("language_mistakes.db")
        c = conn.cursor()
        for correction in corrections.split("\n"):
            if correction.strip():
                parts = correction.split(", ")
                mistake_type = parts[0].replace("Type: ", "").strip()
                incorrect = parts[1].replace("Incorrect: ", "").strip()
                correct = parts[2].replace("Correct: ", "").strip()
                explanation = parts[3].replace("Explanation: ", "").strip()
                c.execute("INSERT INTO mistakes (user_input, mistake_type, incorrect, correct, explanation, timestamp) VALUES (?, ?, ?, ?, ?, ?)",
                          (user_input, mistake_type, incorrect, correct, explanation, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
        conn.close()

def get_feedback(source_lang):
    conn = sqlite3.connect("language_mistakes.db")
    c = conn.cursor()
    c.execute("SELECT mistake_type, incorrect, correct, explanation FROM mistakes")
    mistakes = c.fetchall()
    conn.close()
    
    if not mistakes:
        return "No mistakes recorded during this session. Great job!"
    
    mistake_list = "\n".join([f"Type: {m[0]}, Incorrect: {m[1]}, Correct: {m[2]}, Explanation: {m[3]}" for m in mistakes])
    feedback_output = model.generate_content(feedback_prompt.format(source_lang=source_lang, mistakes=mistake_list)).text
    return feedback_output.strip()

# --- Main Chatbot Logic (Not Used in API, Kept for Reference) ---
def run_chatbot():
    init_db()
    
    target_lang = input("What language do you want to learn? ")
    source_lang = input("What language do you know? ")
    level = input("What is your current level in the learning language (beginner/intermediate/advanced)? ")
    
    scene_output = model.generate_content(scene_prompt.format(target_lang=target_lang, source_lang=source_lang, level=level)).text
    response, corrections = parse_output(scene_output)
    print(f"\nBot: {response}")
    print(f"Corrections: {corrections}\n")
    
    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit":
            break
        
        chat_output = model.generate_content(chat_prompt.format(target_lang=target_lang, source_lang=source_lang, user_input=user_input)).text
        response, corrections = parse_output(chat_output)
        print(f"\nBot: {response}")
        print(f"Corrections: {corrections}\n")
        record_mistake(user_input, corrections, source_lang)
    
    feedback = get_feedback(source_lang)
    print("\n--- Session Feedback ---")
    print(feedback)

if __name__ == "__main__":
    run_chatbot()