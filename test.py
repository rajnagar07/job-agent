from ai.chatmodel import chat_model

response = chat_model.invoke("Say Hello")

print(type(response))
print(response)