import json
from openai import OpenAI
api_key = "sk-f2hYHFd6I7b5f1hVWEHJhGtCrjWqT8Kds3sP03WAnW5M6amN"
base_url = "https://api.f2gpt.com"
with open("D:\CAE\\reference_extract_code.json", "r", encoding="utf-8") as file:
    Reference_extract_code = json.load(file)

extracted_code = Reference_extract_code["extracted_reference_code"]

client = OpenAI(api_key=api_key, base_url=base_url)
response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {"role": "system", "content": "You are an senior programmer who focuses on multi-language interaction and inter-process communication technology"},
        {"role": "user", "content": f"{extracted_code}\n Please understand this code and generate the corresponding prompt for this code for LLM to generate this code.No additional examples are required in the prompt content.The prompt data format is saved in a json file"},
    ],
    temperature=0.1,
    top_p=0.9,
    stream=False
)

print(response.choices[0].message.content)