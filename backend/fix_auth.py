import os

file_path = "d:\\AF\\Projects\\google-deepmind-hackathon\\justitia-lens\\backend\\app\\services\\cloudqwen_service.py"

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Change back to Authorization Bearer
old_auth = '"X-DashScope-API-Key": self.api_key'
new_auth = '"Authorization": f"Bearer {self.api_key}"'

content = content.replace(old_auth, new_auth)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Reverted to Authorization: Bearer format")
