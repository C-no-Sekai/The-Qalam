from bs4 import BeautifulSoup
import requests
import re
from concurrent.futures import ThreadPoolExecutor
import threading


class SupportFunctions:
    def __init__(self):
        self.url_base, self.url_login, self.url_aggregate, self.url_result = (
            "https://qalam.nust.edu.pk",
            "https://qalam.nust.edu.pk/web/login",
            "https://qalam.nust.edu.pk/student/dashboard",
            "https://qalam.nust.edu.pk/student/results/"
        )
        self.csrf_token = lambda x: x.find("input", {"name": "csrf_token"})["value"]

    def auth(self, username, password):
        session = requests.Session()
        r = session.get(self.url_login)
        soup = BeautifulSoup(r.text, "html.parser")
        csrf_token = self.csrf_token(soup)
        login_data = {"csrf_token": csrf_token, "login": username, "password": password}
        r = session.post(self.url_login, data=login_data)
        session.close()

        if r.status_code == 200:
            soup = BeautifulSoup(r.text, "html.parser")
            name = soup.find('span', {'class': 'uk-text-truncate'}).text.strip()
            return True, name
        return False, None

    def fetch_previous_terms(self, soup):
        result = {}  # {term: [{course: [credits, aggregate, grade]}, ...], ...}

        temp = soup.find('ul', {'id': 'tabs_anim1'}).find_all('li')[-1]
        for term in temp.find_all('tr', {'class': 'table-parent-row show_child_row'}):
            term_name = term.find('a').text.strip()
            term_details = []

            temp = term.find_next_sibling('tr').find_next_sibling('tr')
            while temp and temp.get('class') == ['table-child-row']:
                counter = 0
                for record in temp.find_all('td'):
                    if counter == 0:
                        course_name = record.text.strip()
                    elif counter == 1:
                        course_credits = record.text.strip()
                    elif counter == 2:
                        course_aggregate = record.text.strip()
                    elif counter == 3 or counter == 4:
                        pass
                    elif counter == 5:
                        course_grade = record.text.strip()
                    counter += 1
                term_details.append({course_name: [course_credits, course_aggregate, course_grade]})
                temp = temp.find_next_sibling('tr')

            result[term_name] = term_details

        return result

    def fetch_all_details(self, username, password):
        session = requests.Session()

        # Log in to the system
        r = session.get(self.url_login)
        soup = BeautifulSoup(r.text, "html.parser")
        csrf_token = self.csrf_token(soup)
        login_data = {"csrf_token": csrf_token, "login": username, "password": password}
        session.post(self.url_login, data=login_data)

        r = session.get(self.url_result)
        soup = BeautifulSoup(r.content, "html.parser")

        # Get Previous Terms
        # previous_terms = self.fetch_previous_terms(soup)
        # print(previous_terms)

        # Get Current Term
        cur_subs = soup.find_all('a', {'data-uk-tooltip': '{pos:\'top\'}'})

        all_subs = list(map(lambda x: (self.url_base + x.get('href'), session,
                                  x.find('span', {'class': 'md-list-heading'}).text.strip(),
                                  x.find_next_sibling("div").find('span', {'class': 'md-list-heading'}).text.strip()
                                  ), cur_subs))

        print(all_subs)

        # Not working for whatever reason
        with ThreadPoolExecutor() as executor:
            results = executor.map(self.result, list(all_subs))

        for res in results:
            print(res)
        # for subject in all_subs:
        #     soup = BeautifulSoup(session.get(subject[0]).content.decode('utf-8'), features='html.parser')
        #     temp_score = {}
        #
        #     exam_list = soup.find_all('a', class_="js-toggle-children-row")
        #     for exam in exam_list:
        #         temp_score[exam.text.strip()] = []
        #         score_row = exam.find_next('tr')
        #
        #         while score_row:
        #             score_row = score_row.find_next('tr', class_='table-child-row')
        #             if not score_row or score_row.findChild('th'):
        #                 break
        #             temp_score[exam.text.strip()].append(
        #                 float(re.findall(r"(.*)(?:\s*</td>, '\\n'])", str(score_row.contents))[0].strip()))
        #
        #     print(subject[1], subject[2], temp_score)

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

    def result(self, inputs):
        url, session, name, course_credits = inputs

        for key, link in links.items():
            soup = BeautifulSoup(s.get(link).content.decode('utf-8'), features='html.parser')
            temp_score = {}

            exam_list = soup.find_all('a', class_="js-toggle-children-row")
            for exam in exam_list:
                temp_score[exam.text.strip()] = []
                score_row = exam.find_next('tr')

                while score_row:
                    score_row = score_row.find_next('tr', class_='table-child-row')
                    if not score_row or score_row.findChild('th'):
                        break
                    temp_score[exam.text.strip()].append(
                        float(re.findall(r"(.*)(?:\s*</td>, '\\n'])", str(score_row.contents))[0].strip()))
        r = session.get(url)
        soup = BeautifulSoup(r.content, "html.parser")
        table = soup.findAll("table", {"class": "uk-table uk-table-nowrap uk-table-align-vertical table_tree"})
        if len(table) == 1:
            table = str(table[0])
        if len(table) == 2:
            table = str(table[0]) + str(table[1])
        table = BeautifulSoup(table, "html.parser")
        data = {'name': name, 'credits': course_credits}
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


if __name__ == '__main__':
    # Create an instance of the class
    obj = SupportFunctions()

    # Fetch all details
    obj.fetch_all_details('aaleem.bscs21seecs', 'Student.123')
