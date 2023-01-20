import re
import requests
import random
import bs4
import threading

target = "https://qalam.nust.edu.pk/web/login"


def check_login_credentials(username, password):
    s = requests.Session()
    page1 = s.get(target)
    token = re.search(r'(?:<input type="hidden" name="csrf_token" value=")(.*?)(?:")', str(page1.content))[1]
    soup = bs4.BeautifulSoup(page1.content.decode('utf-8'), 'html.parser')
    user_id, password = username, password
    payload = {
        "csrf_token": token,
        "login": user_id,
        "password": password,
        "redirect": "",
        "as_sfid": soup.find('input', {'name': 'as_sfid'}).get('value'),
        "as_fid": soup.find('input', {'name': 'as_fid'}).get('value')
    }
    response = s.post(target, data=payload)
    if response.status_code != 200:
        return False
    return s


def form_filler(username, password):
    def fill_form(session, url, csrf=None, token=None, as_sfid=None, as_fid=None, get_vals=False):
        res = session.get('https://qalam.nust.edu.pk' + url)
        soup = bs4.BeautifulSoup(res.content.decode('utf-8'), 'html.parser')
        if soup.find('h1', text='Thank you!'):
            return
        if get_vals:
            as_sfid = soup.find('input', {'name': 'as_sfid'}).get('value')
            as_fid = soup.find('input', {'name': 'as_fid'}).get('value')
            csrf, token = \
                re.findall(r'(?:<form.*\s.*?value=")(.*)(?:".*\s.*?value=")(.*)(?:")', res.content.decode('utf-8'))[0]
        submit_btn = soup.find('button', {'class': 'btn btn-primary', 'value': 'finish'})
        payload = {'csrf_token': csrf, 'token': token, 'as_sfid': as_sfid, 'as_fid': as_fid, 'button_submit': 'next'}
        payload['question_id'] = soup.find('input', {'name': 'question_id'}).get('value')
        if submit_btn:
            # Write code for comment submission
            payload['button_submit'] = 'finish'
            payload[soup.find('textarea').get('name')] = '.'
            session.post('https://qalam.nust.edu.pk' + url.replace('fill', 'submit'), data=payload)
            return
        answer = random.choice(soup.find_all('input', {'type': 'radio'}))
        payload[answer.get('name')] = answer.get('value')
        session.post('https://qalam.nust.edu.pk' + url.replace('fill', 'submit'), data=payload)
        fill_form(session, url, csrf, token, as_sfid, as_fid)
    s = check_login_credentials(username, password)
    if not s:
        return
    eval_page = s.get("https://qalam.nust.edu.pk/student/qa/feedback")

    soup = bs4.BeautifulSoup(eval_page.content.decode('utf-8'), 'html.parser')
    links = []
    for div in soup.find_all('div'):
        if div.ul and div.ul.li and div.ul.li.a:
            li_last = div.find_all('li')[-1]
            if li_last.div and li_last.div.span:
                if li_last.div.span.text.strip() == "Not Submitted":
                    link = div.ul.li.a.get('href')
                    if link[:7] == "/survey":
                        links.append(link)
    if len(links) == 0:
        return

    threads = [threading.Thread(target=fill_form, args=(s, link, None, None, None, None, True)) for link in links]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    s.close()
