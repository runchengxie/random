import requests
import json
import os

# Use os.environ.get to get the environment variable
OPENROUTER_API_KEY = os.environ.get('OPENROUTER_API_KEY')

# Load the knowledge file
home_dir = os.path.expanduser(~)
file_path = os.path.join(home_dir, Downloads, long_text.txt)

# Open the file and read its content into a variable
with open(file_path, 'r', encoding='utf-8') as file
    knowledge = file.read()

response = requests.post(
  url=httpsopenrouter.aiapiv1chatcompletions,
  headers={
    Authorization fBearer {OPENROUTER_API_KEY},
  },
  data=json.dumps({
    model anthropicclaude-3-sonnetbeta, # Optional
    messages [
      {role user, content f{knowledge}n 巴菲特对于通货膨胀是怎么评价的？}
    ]
  })
)

print(json.dumps(response.json(), indent=4))