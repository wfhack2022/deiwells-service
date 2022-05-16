import json
import os
import time
from elastic_enterprise_search import AppSearch



def get_diversity_by_name(company_name):
    key = os.environ['SEARCH_API_KEY']
    ent_search = AppSearch(
        "https://my-deployment-24a00a.ent.us-central1.gcp.cloud.es.io:443",
        bearer_auth=key
    )
    res = ent_search.search(engine_name='deiwells', filters={"name": [company_name],}, query=company_name)
    if res['meta']['total_results'] == 1:
        diversity = res['results'][0]['diversity']['raw']
        return diversity
    return 'Other'


def update_diversity(domains, category, ent_search):
    for domain in domains:
        domain = domain[8:]
        print('checking for', domain)
        res = ent_search.search(engine_name='deiwells', filters={"companyurl": [domain],}, query=domain)
        print(json.dumps(res['meta'], indent=3))
        if res['meta']['page']['total_results'] == 1:
            doc_id = res['results'][0]['id']['raw']
            diversity_string = res['results'][0]['diversity']['raw']
            if diversity_string == "Unknown":
                ent_search.put_documents(engine_name='deiwells', documents=[{
                 'id': doc_id,
                 'diversity': category
                }])
        print('updated', domain, category)

def start_elastic_search(keyword, category, ent_search):
    domains = set()
    res = ent_search.search(
        engine_name='idiversify',
        query=keyword,
    )
    domains.add(res['results'][0]['domains']['raw'][0])
    remaining_pages = res['meta']['page']['total_pages'] - 1
    print(remaining_pages)
    for current_page in range(1, 99):
        res = ent_search.search(
            engine_name='idiversify',
            query=keyword,
            current_page = current_page+1
        )
        for result in res['results']:
            domains.add(result['domains']['raw'][0])
    print(category, domains)
    update_diversity(domains, category, ent_search)


def start_diversity_search():
    print('initialize elastic')
    key = os.environ['SEARCH_API_KEY']
    if not key:
        print('ERROR:No API KEY set....')
        exit
    ent_search = AppSearch(
        "https://my-deployment-24a00a.ent.us-central1.gcp.cloud.es.io:443",
        bearer_auth=key
    )
    diversity_categories_keywords = {
        'Women Owned': 'Women Owned',
        'Black Led': 'Black or African American Led', 
        'LGBTQIA+': 'LGBTQIA+',
        'Veterans': 'Veterans',
    }
    for keyword, category in diversity_categories_keywords.items():
        start_elastic_search(keyword, category, ent_search)

start_diversity_search()

