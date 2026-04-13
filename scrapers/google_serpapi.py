import os
from urllib.parse import urlparse
from dotenv import load_dotenv
from serpapi import Client
import tldextract

load_dotenv()

def clean_link(link):
    ext = tldextract.extract(link)
    base_domain = f"{ext.domain}.{ext.suffix}"
    return base_domain

def search_serpapi(query, get_related_searches=0):
    client = Client(api_key=os.getenv("SERPAPI_API_KEY"))
    
    results = client.search({
        "engine": "google",
        "location": "Mexico",
        "hl": "es",
        "gl": "mx",
        "q": query
    })
    
    results_dict = dict(results)

    x = []
    if get_related_searches == 0:
            
      for r in results['organic_results']:
          clean = clean_link(r['link'])
          data_to_insert = {'source': 'SERPAPI', 'query': query, 'title': r['title'], 'link_original': r['link'], 'link_clean': clean, 'type': 'organic_results'}
          x.append(data_to_insert)
          print(data_to_insert)
          input()
      
      
      for r in results['related_questions']:
          clean = clean_link(r['link'])
          print('*****', r['question'])
          print('*****', clean)
          data_to_insert = {'source': 'SERPAPI', 'query': query, 'title': r['question'], 'link': clean, 'type': 'related_questions', 'link_original': r['link'], 'link_clean': clean}
          x.append(data_to_insert)
          print(data_to_insert)

      return x
    

    else:
      for r in results['related_searches']:
        x.append(r['query'])
      return x


search_serpapi('punto de venta')
