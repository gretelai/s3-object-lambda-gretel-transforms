import requests

OBJECT = "2021-03-22.csv"

url_data = requests.get(
    "https://yh3glj0b89.execute-api.us-east-2.amazonaws.com/dev/share",
    params={"key": OBJECT}
)

retrieval_url = url_data.json()["url"]
transformed_data = requests.get(retrieval_url)
print(transformed_data.text)
