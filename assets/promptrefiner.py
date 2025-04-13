import sys
import os
import google.generativeai as genai
from dotenv import load_dotenv
import re # Kept import, though might not be strictly needed now

# --- Configuration Loading ---
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
DEFAULT_MODEL = "gemini-2.5-pro-exp-03-25" #"gemini-1.5-flash"
GEMINI_MODEL_NAME = os.getenv("GEMINI_MODEL_NAME", DEFAULT_MODEL)

# --- Static Configuration ---
# Still useful for number lookup and displaying options
AVAILABLE_CATEGORIES = [
    "History", "Geography", "Science & Nature", "Technology",
    "Movies", "Television", "Music", "Literature", "Art",
    "Sports", "Mythology", "Food & Drink", "General Knowledge",
    "Mathematics", "Politics & Current Events", "Animals", "Space",
    "Video Games", "Comics", "Business & Finance", "World Religions",
    "Famous People", "Architecture", "Language & Linguistics"
]

# No longer need a map for fuzzy text matching, but keep the list
# CATEGORY_MAP_LOWER = {cat.lower(): cat for cat in AVAILABLE_CATEGORIES} # Removed

AVAILABLE_DIFFICULTIES = [
    "Easy",
    "Medium",
    "Hard",
]
DIFFICULTY_MAP_LOWER = {diff.lower(): diff for diff in AVAILABLE_DIFFICULTIES}

NUM_QUESTIONS_TO_REQUEST = input(f"Enter # of ?'s")

# --- Helper Functions ---

def format_list_for_prompt(item_list):
    """Formats a list of strings nicely for inclusion in the prompt."""
    if not item_list:
        return "Any"
    if len(item_list) == 1:
        return item_list[0]
    elif len(item_list) == 2:
        return f"{item_list[0]} and {item_list[1]}"
    else:
        return ", ".join(item_list[:-1]) + f", and {item_list[-1]}"

# MODIFIED FUNCTION
def get_category_selection():
    """
    Gets category selections from the user.
    Accepts numbers (maps to predefined list) or literal text.
    """
    print("Available Predefined Categories (use numbers for these):")
    cols = 3
    col_width = max(len(cat) for cat in AVAILABLE_CATEGORIES) + 6
    num_rows = (len(AVAILABLE_CATEGORIES) + cols - 1) // cols
    for r in range(num_rows):
        line = ""
        for c in range(cols):
            idx = r + c * num_rows
            if idx < len(AVAILABLE_CATEGORIES):
                 line += f"{idx+1:>3}. {AVAILABLE_CATEGORIES[idx]:<{col_width-6}}"
        print(line)

    selected_categories = []
    while not selected_categories:
        try:
            choice_str = input(f"\nEnter category numbers (mapped) or specific text names (comma-separated, e.g., 1, Movies, Custom Topic): ")
            parts = [p.strip() for p in choice_str.split(',') if p.strip()]

            current_selection = []
            invalid_numeric_indices = [] # Track numbers that are out of range
            seen_categories = set() # Use set for efficient deduplication (case-sensitive based on final string)

            if not parts:
                print("Error: No categories entered. Please provide at least one.")
                continue

            for part in parts:
                category_to_add = None
                is_numeric_input = False

                # Attempt to process as a number FIRST
                try:
                    index = int(part) - 1
                    is_numeric_input = True # It's definitely a number format
                    if 0 <= index < len(AVAILABLE_CATEGORIES):
                        # Valid number, map to predefined category
                        category_to_add = AVAILABLE_CATEGORIES[index]
                    else:
                        # Valid number format, but out of range
                        invalid_numeric_indices.append(part)
                        # We treat out-of-range numbers as literal text in this revised logic:
                        category_to_add = part # Use the number string itself as category
                except ValueError:
                    # Not a number format, treat as literal text
                    category_to_add = part

                # Add the determined category if it's not already seen
                if category_to_add is not None: # Should always be true unless part was empty/whitespace only
                     # Check seen_categories using the FINAL determined string
                     # Use case-insensitive check for deduplication for added robustness?
                     # E.g. if user enters `1` and `history`. Let's do case-insensitive check for *seen*
                     if category_to_add.lower() not in {seen.lower() for seen in seen_categories}:
                           current_selection.append(category_to_add)
                           seen_categories.add(category_to_add) # Add the potentially cased version
                     # else: print(f"Debug: Skipped duplicate '{category_to_add}'") # Optional debug

            # --- Reporting ---
            if invalid_numeric_indices:
                print(f"Warning: The following numbers were entered but are outside the valid range [1-{len(AVAILABLE_CATEGORIES)}]: {', '.join(invalid_numeric_indices)}. They have been treated as literal text categories.")

            if not current_selection:
                # This could happen if input was only invalid numbers and we chose *not* to add them as text,
                # or if the input was just commas/whitespace.
                print("Error: No valid categories could be determined from your input.")
                continue # Ask again

            # If we got here, at least one category was selected/entered
            selected_categories = current_selection
            print(f"Selected Categories to use in prompt: {format_list_for_prompt(selected_categories)}")
            return selected_categories

        except Exception as e:
            print(f"An unexpected error occurred during category selection: {e}")
            # Potentially add more robust error handling or exit


# --- Difficulty Selection (Unchanged) ---
def get_difficulty_selection():
    """Gets difficulty selections from the user, accepting numbers or names."""
    print("\nAvailable Difficulties:")
    for i, difficulty in enumerate(AVAILABLE_DIFFICULTIES):
        print(f"  {i+1}. {difficulty}")
    selected_difficulties = []
    while not selected_difficulties:
        try:
            choice_str = input(f"Enter difficulty numbers or names (comma-separated, e.g., 1, Hard): ")
            parts = [p.strip() for p in choice_str.split(',') if p.strip()]
            current_selection = []
            invalid_entries = []
            seen_difficulties = set()
            if not parts:
                 print("Error: No difficulties entered. Please provide at least one.")
                 continue
            for part in parts:
                found = False
                part_lower = part.lower()
                if part_lower in DIFFICULTY_MAP_LOWER:
                    canonical_name = DIFFICULTY_MAP_LOWER[part_lower]
                    if canonical_name.lower() not in {seen.lower() for seen in seen_difficulties}:
                        current_selection.append(canonical_name)
                        seen_difficulties.add(canonical_name)
                    found = True
                if not found:
                    try:
                        index = int(part) - 1
                        if 0 <= index < len(AVAILABLE_DIFFICULTIES):
                            canonical_name = AVAILABLE_DIFFICULTIES[index]
                            if canonical_name.lower() not in {seen.lower() for seen in seen_difficulties}:
                                current_selection.append(canonical_name)
                                seen_difficulties.add(canonical_name)
                            found = True
                    except ValueError:
                        pass
                if not found:
                    invalid_entries.append(part)
            if invalid_entries:
                 print(f"Error: Invalid or unrecognized difficulty entries: {', '.join(invalid_entries)}")
            if not current_selection:
                 if not invalid_entries:
                      print("Error: No valid difficulties selected from your input.")
                 continue
            selected_difficulties = current_selection
            print(f"Selected Difficulties: {format_list_for_prompt(selected_difficulties)}")
            return selected_difficulties
        except Exception as e:
            print(f"An unexpected error occurred during difficulty selection: {e}")


# --- LLM Prompt Generation (Unchanged Structurally) ---
def generate_llm_prompt(categories, difficulties, num_questions):
    """Constructs the prompt string for the LLM based on final category/difficulty lists."""
    print("\nGenerating prompt...")
    category_string = format_list_for_prompt(categories) # Will now contain mix of predefined/literal text
    difficulty_string = format_list_for_prompt(difficulties)
    prompt = f"""Generate exactly {num_questions} trivia questions based on the following criteria:

Categories: {category_string}
Difficulties: {difficulty_string}

Your goal is to create engaging and accurate trivia questions matching the specified difficulty levels and topics. Interpret the provided category names as best as possible, even if they are custom or unusual. Aim for a mix if multiple difficulties are selected.

Please format the output *strictly* as follows, with exactly one question and its corresponding answer per Q/A block. Each Q: and A: must start on a new line:
Q: [Question text]?
A: [Answer text]

Example of STRICT format:
Q: What element has the chemical symbol 'O'?
A: Oxygen

Provide *only* the requested {num_questions} Q&A pairs. Do not include any introductory text, concluding remarks, numbering (like 1., 2.), apologies, explanations, bolding, italics, or any other text outside the exact Q:/A: format specified above.
"""
    print("Prompt generated successfully.")
    return prompt

# --- API Call (Unchanged) ---
def call_gemini_api(prompt_text, api_key, model_name):
    """Calls the Gemini API with the generated prompt and returns the text response."""
    print(f"\nAttempting to call Gemini API (model: {model_name})...")
    try:
        if not api_key:
            print("\n" + "="*50 + "\nERROR: GEMINI_API_KEY not found.\nPlease ensure it is set in your .env file or as a system environment variable.\n" + "="*50)
            return None
        genai.configure(api_key=api_key)
        print(f"Using model: {model_name}")
        # Consider adding generation_config for finer control if needed
        # config = genai.types.GenerationConfig(temperature=0.7)
        model = genai.GenerativeModel(model_name)#, generation_config=config)

        response = model.generate_content(prompt_text)
        try:
            # Adding a check for parts existing and having text
            if response.candidates and response.candidates[0].content.parts and response.candidates[0].content.parts[0].text:
                print("API call successful. Received response.")
                return response.text
            else:
                 # More detailed check for block reason or other finish reasons
                 feedback = getattr(response, 'prompt_feedback', None)
                 block_reason_name = None
                 if feedback and feedback.block_reason:
                     block_reason_name = feedback.block_reason.name
                     print(f"API call blocked by safety filters. Reason: {block_reason_name}")
                     return f"API Call Blocked: {block_reason_name}"

                 finish_reason = "Unknown"
                 if response.candidates and hasattr(response.candidates[0], 'finish_reason'):
                    finish_reason = response.candidates[0].finish_reason.name

                 # Specific check for finish reason being 'OTHER' which might indicate API issue/no output
                 if finish_reason == 'OTHER':
                      print(f"API call finished with reason 'OTHER'. This may indicate an issue.")
                 elif not (response.candidates and response.candidates[0].content.parts):
                      print(f"API call returned successfully but with no content.")

                 print(f"Finish Reason: {finish_reason}")
                 # print(f"Full Response Object (for debugging): {response}") # uncomment for deep debug
                 return f"API Call Failed: No content received or processing error (Finish Reason: {finish_reason})."

        except (StopIteration, ValueError, AttributeError, IndexError) as e_resp:
             # Catch more potential errors during response processing
             print(f"Error processing API response content: {e_resp}")
             # print(f"Full Response Object (for debugging): {response}") # uncomment for deep debug
             return f"API Call Failed: Error processing response. {e_resp}"
    except Exception as e_api:
        print(f"\nAn error occurred during the Gemini API call: {e_api}")
        return f"API Call Error: {e_api}"


# --- Main Program (Unchanged logic, uses modified get_category_selection) ---
if __name__ == "__main__":
    print("--- Trivia Question Generation Simulation (using .env) ---")
    print("Supports multiple difficulties. Category input: Numbers are mapped, text is used literally.")
    print(f"(Will use model '{GEMINI_MODEL_NAME}' specified in .env or default '{DEFAULT_MODEL}'.)\n")

    if not GEMINI_API_KEY:
        print("Error: GEMINI_API_KEY not loaded. Please check your .env file or environment variables.")
        sys.exit(1)

    # 1. Get User Selections
    user_categories = get_category_selection() # Uses the new logic
    if not user_categories:
        print("\nExiting due to error or no categories selected.")
        sys.exit(1)

    user_difficulties = get_difficulty_selection()
    if not user_difficulties:
        print("\nExiting due to error or no difficulties selected.")
        sys.exit(1)

    # 2. Generate the Prompt
    final_prompt = generate_llm_prompt(user_categories, user_difficulties, NUM_QUESTIONS_TO_REQUEST)
    print("\n" + "="*40)
    print("Generated LLM Prompt (for debugging):")
    print("="*40)
    print(final_prompt)
    print("="*40)

    # 3. Call the LLM API
    llm_response = call_gemini_api(final_prompt, GEMINI_API_KEY, GEMINI_MODEL_NAME)

    # 4. Output the Result
    print("\n" + "="*40)
    print("LLM API Response:")
    print("="*40)
    if llm_response:
         print(llm_response)
    else:
        print("Failed to get a response from the LLM API (returned None).")
    print("="*40)
    print("\n--- Simulation Complete ---")