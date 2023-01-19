import re
import json
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor


class Scrape:
    def __init__(self, username, password):
        self.url_base, self.url_login, self.url_aggregate, self.url_result = (
            "https://qalam.nust.edu.pk",
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
        if len(table) == 1:
            table = str(table[0])
        if len(table) == 2:
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

    def result_all(self):
        data = self.dashboard()
        list_of_urls = []
        for ke, val in data.items():
            list_of_urls.append(val[0])
        with ThreadPoolExecutor() as executor:
            results = executor.map(self.result, list_of_urls)
        for i, j in zip(data.values(), results):
            i.append(j)
            i.pop(0)
        return data


def data_function():
    scraper = Scrape("aaleem.bscs21seecs", "Student.123")
    scraper.auth()
    data = scraper.result_all()
    for course in data:
        obtained_marks_total = 0
        class_avg_total = 0
        marks_total = 0
        tests_count = 0
        for category, values in data[course][2].items():
            for subcategory, subvalues in values.items():
                marks_total += float(subvalues["maxMark"])
                obtained_marks_total += float(subvalues["obtained"])
                class_avg_total += float(subvalues["classAvg"])
                tests_count += 1
                data[course][2][category][subcategory] = [
                    (float(subvalues["obtained"]) / float(subvalues["maxMark"])) * 100,
                    (float(subvalues["classAvg"]) / float(subvalues["maxMark"])) * 100
                ]
        for category, values in data[course][2].items():
            temp = [0, 0]
            templen = len(values)
            for subvalues in values.values():
                temp[0] += subvalues[0]
                temp[1] += subvalues[1]
            data[course][2][category] = [temp[0] / templen, temp[1] / templen]
    return {"data": data}


if __name__ == "__main__":
    with open("output.json", "w") as f:
        json.dump(data_function(), f, indent=4)
