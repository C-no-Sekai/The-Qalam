from bs4 import BeautifulSoup
import requests
import re
from concurrent.futures import ThreadPoolExecutor
from collections import defaultdict


class SupportFunctions:
    def __init__(self):
        self.url_base, self.url_login, self.url_teachers, self.url_result = (
            "https://qalam.nust.edu.pk",
            "https://qalam.nust.edu.pk/web/login",
            "https://qalam.nust.edu.pk/student/enrolled/courses",
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

    @staticmethod
    def fetch_previous_terms(soup):
        result = {}  # {term: [{course: [credits, aggregate, grade]}, ...], ...}

        temp = soup.find('ul', {'id': 'tabs_anim1'}).find_all('li')[-1]
        for term in temp.find_all('tr', {'class': 'table-parent-row show_child_row'}):
            term_name = term.find('a').text.strip().lower()
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
        previous_terms = self.fetch_previous_terms(soup)

        # Get Current Term
        cur_subs = soup.find_all('a', {'data-uk-tooltip': '{pos:\'top\'}'})

        all_subs = list(map(lambda x: (self.url_base + x.get('href'), session,
                                       x.find('span', {'class': 'md-list-heading'}).text.strip(),
                                       x.find_next_sibling("div").find('span',
                                                                       {'class': 'md-list-heading'}).text.strip()
                                       ), cur_subs))

        with ThreadPoolExecutor() as executor:
            results = executor.map(self.result, list(all_subs))
        cur_sub_details = list(results)

        # Get Teacher Names
        teachers = self.get_teacher_names(session)

        session.close()

        return previous_terms, cur_sub_details, teachers

    def get_teacher_names(self, session):
        r = session.get(self.url_teachers)
        soup = BeautifulSoup(r.text, "html.parser")

        result = {}
        for img in soup.find_all('img', {'data-uk-tooltip': "{pos:'top'}"}):
            sub = img.find_parent('div').find_parent('div').find_next_sibling('div').find('span', {
                'class': 'md-list-heading'}).text.strip()
            result[sub.lower()] = img['title'].lower()

        return result

    @staticmethod
    def result(inputs):
        url, session, name, course_credits = inputs

        results = {'name': name.lower(),
                   'credits': course_credits}  # {name, credits, quiz, quiz_avg, assign, assign_avg, mid_avg, final, final_avg, lab, lab_avg, project, project_avg}
        soup = BeautifulSoup(session.get(url).text, features='html.parser')
        temp_score = defaultdict(list)
        class_avg = defaultdict(list)

        exam_list = soup.find_all('a', class_="js-toggle-children-row")
        for exam in exam_list:
            score_row = exam.find_next('tr')

            while score_row:
                score_row = score_row.find_next('tr', class_='table-child-row')
                if not score_row or score_row.findChild('th'):
                    break

                counter = 0
                for td in score_row.find_all('td'):
                    if counter == 0 or counter == 2:
                        pass
                    elif counter == 1:  # Max Mark
                        max_marks = float(td.text.strip())
                    elif counter == 3:  # Class Avg
                        avg = float(td.text.strip())
                    elif counter == 4:
                        score = float(td.text.strip())
                    counter += 1

                temp_score[exam.text.strip()].append(score)
                class_avg[exam.text.strip()].append(round(avg * 100 / max_marks, 2))

                temp_score[exam.text.strip()].append(
                    float(re.findall(r"(.*)(?:\s*</td>, '\\n'])", str(score_row.contents))[0].strip()))

        for key in temp_score.keys():
            if 'quiz' in key.lower():
                results['quiz'] = sum(temp_score[key]) / len(temp_score[key])
                results['quiz_avg'] = sum(class_avg[key]) / len(class_avg[key])
            elif 'assignment' in key.lower():
                results['assign'] = sum(temp_score[key]) / len(temp_score[key])
                results['assign_avg'] = sum(class_avg[key]) / len(class_avg[key])
            elif 'mid term' in key.lower() or 'one hour' in key.lower():
                results['midterm'] = sum(temp_score[key]) / len(temp_score[key])
                results['midterm_avg'] = sum(class_avg[key]) / len(class_avg[key])
            elif 'lab work' in key.lower():
                results['lab'] = sum(temp_score[key]) / len(temp_score[key])
                results['lab_avg'] = sum(class_avg[key]) / len(class_avg[key])
            elif 'lab' in key.lower() or 'project' in key.lower():
                results['project'] = sum(temp_score[key]) / len(temp_score[key])
                results['project_avg'] = sum(class_avg[key]) / len(class_avg[key])
            elif 'final' in key.lower():
                results['finals'] = sum(temp_score[key]) / len(temp_score[key])
                results['finals_avg'] = sum(class_avg[key]) / len(class_avg[key])

        if 'lab' not in results:
            results['lab'] = 0
            results['lab_avg'] = 0
        if 'project' not in results:
            results['project'] = 0
            results['project_avg'] = 0
        return results


if __name__ == '__main__':
    # Create an instance of the class
    obj = SupportFunctions()

    # Fetch all details
    obj.fetch_all_details('aaleem.bscs21seecs', 'Student.123')
