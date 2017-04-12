import os
import json
import urllib
import urllib2

def read_webhose_key():
    webhose_api_key = None
    
    if os.path.isfile('search.key'):
        key_file_path = 'search.key'
    else:
        key_file_path = '../search.key'

    try:
        with open(key_file_path,'r') as f:
            webhose_api_key = f.readline().strip()
    except:
        raise IOError('search key file not found')

    return webhose_api_key

def run_query(search_terms,size=10):
    webhose_api_key = read_webhose_key()

    if not webhose_api_key:
        raise KeyError('webhose key not found')

    root_url = 'http://www.webhose.io/search'
 
    query_string = urllib.quote(search_terms)

    search_url = ("{root_url}?token={key}&format=json&q={query}&sort=relevancy&size={size}" \
                      .format(root_url=root_url,key=webhose_api_key,query=query_string,size=size))

    results = []

    try:
        response = urllib2.urlopen(search_url).read()
        json_response = json.loads(response)

        for post in json_response['posts']:
            results.append({'title':post['title'],'link':post['url'],'summary':post['text'][:200]})
    except Exception,e:
        print('Error when querying the webhose api,%s'%e)

    return results

if __name__ == '__main__':
    print read_webhose_key()
    print run_query('django')
