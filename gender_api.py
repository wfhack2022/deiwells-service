import os
import requests

def get_gender_by_name(name):
    token = os.environ['GENDER_API_TOKEN']
    url = f'https://gender-api.com/get?name={name}&key={token}'
    r = requests.get(url)
    data = r.json()
    return data['gender']
