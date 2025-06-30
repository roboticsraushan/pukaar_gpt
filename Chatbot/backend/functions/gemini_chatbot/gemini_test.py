from vertexai.generative_models import GenerativeModel
import vertexai

vertexai.init(project="pkr-prod-in-core", location="asia-south2-b")

model = GenerativeModel("gemini-2.0-flash-001")  # Or another name you found

response = model.generate_content("Explain the concept of gravity.")
print(response.text)

