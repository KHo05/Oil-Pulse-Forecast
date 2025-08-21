import requests

# Replace the "demo" apikey below with your own key from https://www.alphavantage.co/support/#api-key
# Below is a free but limited API key for demo purposes
url = 'https://www.alphavantage.co/query?function=SYMBOL_SEARCH&keywords=oil&apikey=S8T54DZ7NA1DLK7I'
r = requests.get(url)
data = r.json()

print(data)
