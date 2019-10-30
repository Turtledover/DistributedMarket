import requests


if __name__ == '__main__':
    url = 'http://master:8000/services/machine/init_cluster/'
    client = requests.session()
    response = client.post(url)
    print(response.status_code)

