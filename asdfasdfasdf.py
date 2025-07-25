import os
import json
from groq import Groq

# --- 1. Functions to manage prompts and conversation logs ---

def load_json_file(file_path: str, default_type: str = 'dict'):
    """Loads data from a JSON file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {} if default_type == 'dict' else []

def save_json_file(file_path: str, data: list):
    """Saves data to a JSON file."""
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# --- 2. Main execution ---
if __name__ == "__main__":
    # --- Configuration ---
    # !!! SECURITY WARNING !!!
    # Hardcoding API keys is a major security risk.
    # Please use environment variables for production.
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY environment variable is not set.")
    client = Groq(api_key=api_key)
    
    prompt_template_file = "prompt_template.json"
    conversation_log_file = "conversation_log.json"

    # --- Load existing data ---
    prompt_templates = load_json_file(prompt_template_file, 'dict')
    system_prompt = prompt_templates.get("trpg_system_prompt")
    conversation_history = load_json_file(conversation_log_file, 'list')

    # --- Prepare messages for the API call ---
    messages_to_send = []
    if system_prompt:
        messages_to_send.append(system_prompt)
    
    messages_to_send.extend(conversation_history)
    
    # Get new user input (for this example, it's hardcoded)
    new_user_input = "내 이름은 김철수야. 기억해줘."
    print(f"\n[User Input]: {new_user_input}")

    user_message = {"role": "user", "content": new_user_input}
    messages_to_send.append(user_message)

    print(f"--- Sending {len(messages_to_send)} total messages to API ---")

    # --- Call API and get response ---
    completion = client.chat.completions.create(
        model="compound-beta",
        messages=messages_to_send,
        temperature=0.6,
        max_completion_tokens=1024,
        top_p=1,
        stream=True,
        stop=None,
    )

    print("\n--- AI Response ---")
    ai_response_content = ""
    for chunk in completion:
        content_part = chunk.choices[0].delta.content or ""
        ai_response_content += content_part
        print(content_part, end="")
    print("\n-------------------")

    # --- Save the updated conversation ---
    # Add the latest user message and AI response to the history
    conversation_history.append(user_message)
    conversation_history.append({"role": "assistant", "content": ai_response_content})
    
    save_json_file(conversation_log_file, conversation_history)
    print(f"Conversation history has been updated in {conversation_log_file}")

