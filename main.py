from process import Process
from dotenv import load_dotenv
import os
import json
from TaxLLM import LLM

def main():
    load_dotenv()
    key = os.getenv('OPENAI_API_KEY')
    parse = Process()
    llm = LLM(key=key)

    while True:
        inp = input('Please enter some query: ')
        if not inp:
            print("No input provided, exiting.")
            break

        print("Original Input:", inp)
        preprocess = parse.preprocess(inp)
        print("Preprocessed Output:", preprocess)

        try:
            final_query = parse.simplify(preprocess)
            print("Simplified Query:", final_query)
            output = llm.interpret(query=final_query)
            print("LLM Output:", output)
        except Exception as e:
            print(f"Error processing query: {e}")

if __name__ == "__main__":
    main()