import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GOOGLE_API_KEY")
CX = "01f641f2525a04ea4"

def google_search(query):
    url = "https://www.googleapis.com/customsearch/v1"
    
    params = {
        "key": API_KEY,
        "cx": CX,
        "q": query,
        "num": 10
    }

    try:
        response = requests.get(url, params=params)
        print(f"Status: {response.status_code}")
        
        if response.status_code != 200:
            error = response.json().get("error", {})
            print(f"Error: {error.get('message', 'Unknown error')}")
            return []
        
        data = response.json()
        results = []

        for item in data.get("items", []):
            results.append({
                "title": item["title"],
                "link": item["link"]
            })

        print(f"Found {len(results)} results")
        return results
        
    except Exception as e:
        print(f"Exception: {e}")
        return []


if __name__ == "__main__":
    print("Searching'...")
    results = google_search("punto de vents")

    for r in results:
        print(r["title"])
        print(r["link"])
        print("-" * 50)