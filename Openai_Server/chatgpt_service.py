import openai
import sys
import json

# Replace 'your_openai_api_key' with your actual OpenAI API key
openai.api_key = 'OpenAI API key'
def ask_openai(question):
    try:
        # Use ChatCompletion endpoint to get a response from ChatGPT
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Use "gpt-4" if you have access
            messages=[{"role": "user", "content": question}],
            max_tokens=100,
            temperature=0.7
        )
        # Extract and return the response content
        return response.choices[0].message['content'].strip()
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == "__main__":
    # Check if the question is provided as a command-line argument
    if len(sys.argv) < 2:
        print("Error: No question provided.")
        sys.exit(1)

    # Get the question from the command-line argument
    question = sys.argv[1]

    # Get the response from OpenAI
    response_text = ask_openai(question)

    # Print the response to be captured by script.py
    print(response_text)