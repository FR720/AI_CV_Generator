import google.generativeai as genai

# Replace with your API key
API_KEY = 'AIzaSyBa0Cl6xs6PQua9MwAI2D9duVJElhvAzc8'

# Configure the library
genai.configure(api_key=API_KEY)

# List available models and their supported methods
print("Available Models:")
for m in genai.list_models():
    print(f"- Model: {m.name}")
    print(f"  Supported generation methods: {m.supported_generation_methods}")
    print()

# Try to generate content
try:
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content('Hello, world!')
    print("\nTest Response:", response.text)
except Exception as e:
    print("\nError:", str(e))