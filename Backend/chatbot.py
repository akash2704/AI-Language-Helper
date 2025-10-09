from datetime import datetime
from langchain.prompts import PromptTemplate
import google.generativeai as genai
import os
from db_utils import get_mistakes_by_language

# --- Configure Gemini 1.5 Flash API ---
API_KEY = os.getenv('GEMINI_API_KEY')
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

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

def get_feedback(source_lang):
    mistakes = get_mistakes_by_language(source_lang, limit=20)
    
    if not mistakes:
        return "No mistakes recorded during this session. Great job!"
    
    mistake_list = "\n".join([
        f"Input: {m['user_input']}, Corrections: {m['corrections']}" 
        for m in mistakes
    ])
    
    feedback_output = model.generate_content(
        feedback_prompt.format(source_lang=source_lang, mistakes=mistake_list)
    ).text
    return feedback_output.strip()
