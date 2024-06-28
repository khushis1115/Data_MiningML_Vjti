import json
import openai

# Load your API key from an environment variable or secret management service
openai.api_key = 'sk-proj-GmaNxGucsDP8TokzZ7WPT3BlbkFJ2NfOjGPAtbE1qPhBz33H'

# Function to extract text from the JSON file
def extract_text_from_json(json_file_path):
    with open(json_file_path, 'r') as file:
        data = json.load(file)

    # Check if data is a list of tactics
    if isinstance(data, dict):
        data = [data]

    # Initialize a list to store extracted text
    extracted_text = []

    # Extract tactics, techniques, and procedures
    for tactic in data:
        tactic_id = tactic.get('id', '')
        tactic_name = tactic.get('name', '')
        tactic_description = tactic.get('description', '')
        extracted_text.append(f"Tactic ID: {tactic_id}")
        extracted_text.append(f"Tactic Name: {tactic_name}")
        extracted_text.append(f"Tactic Description: {tactic_description}")

        for technique in tactic.get('techniques', []):
            technique_id = technique.get('technique_id', '')
            technique_name = technique.get('technique_name', '')
            technique_description = technique.get('technique_description', '')
            extracted_text.append(f"  Technique ID: {technique_id}")
            extracted_text.append(f"  Technique Name: {technique_name}")
            extracted_text.append(f"  Technique Description: {technique_description}")

            for procedure in technique.get('procedure_examples', []):
                procedure_id = procedure.get('procedure_id', '')
                procedure_name = procedure.get('procedure_name', '')
                procedure_description = procedure.get('procedure_description', '')
                extracted_text.append(f"    Procedure ID: {procedure_id}")
                extracted_text.append(f"    Procedure Name: {procedure_name}")
                extracted_text.append(f"    Procedure Description: {procedure_description}")

    return extracted_text

# Path to your JSON file
json_file_path = 'output.json'  # Replace with the path to your JSON file

# Extract text from the JSON file
extracted_text = extract_text_from_json(json_file_path)

# Combine the extracted text into a single string
combined_text = "\n".join(extracted_text)

# Send a prompt to the GPT-4 model
response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": "summarise it"},
        {"role": "user", "content": combined_text}
    ],
    max_tokens=100,
    stop=None
)

# Extracting and printing the model response
model_response = response['choices'][0]['message']['content']
print("Model Response:")
print(model_response)
