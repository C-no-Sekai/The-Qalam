from bs4 import BeautifulSoup
import threading
import requests


def verify_credentials(username, password):
    url = "https://qalam.nust.edu.pk/web/login"
    session = requests.Session()
    r = session.get(url)
    soup = BeautifulSoup(r.text, "html.parser")
    csrf_token = soup.find("input", {"name": "csrf_token"})["value"]
    login_data = {"csrf_token": csrf_token, "login": username, "password": password}
    r = session.post(url, data=login_data)
    if r.status_code == 200:
        soup = BeautifulSoup(r.text, "html.parser")
        name = soup.find('span', {'class': 'uk-text-truncate'}).text.strip()
        return True, name
    return False, None
