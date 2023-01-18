import re
import requests
from bs4 import BeautifulSoup


class Scrape:
    def __init__(self, username, password):
        self.url_base, self.url_login, self.url_aggregate, self.url_result = (
            "https://qalam.nust.edu.pk/",
            "https://qalam.nust.edu.pk/web/login",
            "https://qalam.nust.edu.pk/student/dashboard",
            "https://qalam.nust.edu.pk/student/results/id/"
        )
        self.session = requests.Session()
        self.username, self.password = username, password
        self.csrf_token = lambda x: x.find("input", {"name": "csrf_token"})["value"]

    def auth(self):
        r = self.session.get(self.url_login)
        soup = BeautifulSoup(r.text, "html.parser")
        csrf_token = self.csrf_token(soup)
        login_data = {"csrf_token": csrf_token, "login": self.username, "password": self.password}
        r = self.session.post(self.url_login, data=login_data)
        return r.status_code == 200

    def dashboard(self):
        r = self.session.get(self.url_aggregate)
        soup = BeautifulSoup(r.content, "html.parser")
        data = soup.find_all("div", {
            "class": ["uk-grid", "uk-grid-width-small-1-12", "uk-grid-width-medium-1-12", "uk-grid-width-medium-1-12",
                      "uk-grid-width-large-1-4", "uk-margin-medium-bottom"], "data-uk-grid-margin": "",
            "id": "hierarchical-show", "data-show-delay": "100"})[1].find_all("a")

        datajson = {}
        for i in data:
            datajson[i.find("span", {"class": "md-list-heading md-color-grey-900"}).text] = [
                self.url_base +
                re.findall(r'''<a data-uk-tooltip="{pos:'top'}" href="(.*?)" title="Open class">''', i.prettify())[0],
                i.find("span", {"class": "md-list-heading md-color-blue-grey-600"}).text,
                i.find("span", {"class": "sub-heading md-color-blue-grey-600"}).text
            ]
        return datajson

    def result(self, url):
        r = self.session.get(url)
        soup = BeautifulSoup(r.content, "html.parser")
        table = soup.findAll("table", {"class": "uk-table uk-table-nowrap uk-table-align-vertical table_tree"})
        table = str(table[0]) + str(table[1])
        table = BeautifulSoup(table, "html.parser")
        data = {}
        temp = []
        tempVar = ""
        for i in table.findAll("tr"):
            if i.text not in ['\nAssessment Type\nObtained Percentage\n',
                              '\nAssessment\nMax Mark\nObtained Marks\nClass Average\nPercentage\n']:
                x = i.text
                temp.append(" ".join(x.split()))
        for j in temp:
            if not re.search(r'\d+(\.\d+)?\s+', j):
                tempVar = j
                data[tempVar] = []
            else:
                data[tempVar].append(j.split())

        for ke, val in data.items():
            temp_test = {}
            for kx in val:
                while len(kx) > 5:
                    kx[0] += kx[1]
                    kx.pop(1)
                temp_test[kx[0]] = {
                    "maxMark": kx[1],
                    "obtained": kx[2],
                    "classAvg": kx[3],
                    "percentage": kx[4]
                }
            data[ke] = temp_test
        return data


def data_function():
    scraper = Scrape("madeel.bscs21seecs", "Student.123")
    scraper.auth()
    print(scraper.dashboard())


if __name__ == "__main__":
    print(data_function())
