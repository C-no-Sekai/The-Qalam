from bs4 import BeautifulSoup
import requests


class Scrape:

    def __init__(self, username, password):
        self.url_login = "https://qalam.nust.edu.pk/web/login"
        self.url_form = "https://qalam.nust.edu.pk/student/dashboard"
        # self.url_predictor = ""
        self.session = requests.Session()
        self.username = username
        self.password = password
        self.csrf_token = lambda x: x.find("input", {"name": "csrf_token"})["value"]

    def auth(self):
        r = self.session.get(self.url_login)
        soup = BeautifulSoup(r.text, "html.parser")
        csrf_token = self.csrf_token(soup)
        login_data = {"csrf_token": csrf_token, "login": self.username, "password": self.password}
        r = self.session.post(self.url_login, data=login_data)
        if r.status_code != 200:
            print("Login Failed")
            return False
        return True

    def 
if __name__ == "__main__":
    scraper = Scrape("madeel.bscs21seecs", "Student.123")
    scraper.auth()
