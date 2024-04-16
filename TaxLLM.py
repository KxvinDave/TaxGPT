import openai
from dotenv import load_dotenv
import os


load_dotenv()

OAAPI = os.getenv('OPENAI_API_KEY')
def loadInstructions(path):
    with open(path, "r") as file:
        return file.read().strip()

class LLM:
    def __init__(self, key):
        self.api_key = key
        openai.api_key = self.api_key
        self.instructions = loadInstructions(path="instructions.txt")
    def interpret(self, query: str):
        if not isinstance(query, str):
            raise ValueError('Query must be a string.')
        messages = [
            {"role": "system", "content": self.instructions},
            {"role": "user", "content": query}
        ]
        try:
            response = openai.chat.completions.create(
                model='gpt-4-turbo',
                messages=messages
            )
            return response.choices[0].message.content.strip()
        except Exception as E:
            print(f'Please sort this out: {E}')
            return None