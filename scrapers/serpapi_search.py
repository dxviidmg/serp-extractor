import os
from dotenv import load_dotenv

load_dotenv()

client = serpapi.Client(api_key=os.getenv("SERPAPI_API_KEY"))
results = client.search({
  "engine": "google",
  "location": "Mexico",
  "hl": "es",
  "gl": "mx",
  "q": "punto de venta"
})

results_dict = dict(results)

print(results_dict.keys())
input()

for r in results:
    print('*****', r)
    print(results[r])
    input()