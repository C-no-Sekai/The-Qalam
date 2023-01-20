import sqlite3
import os


class DBSetup:
    @staticmethod
    def initialize_db(cur):
        cur.execute('''CREATE TABLE IF NOT EXISTS user_details
            (id TEXT PRIMARY KEY, 
            password TEXT NOT NULL,
            username TEXT NOT NULL,
            class TEXT NOT NULL);
        ''')

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
        subject_number INTEGER PRIMARY KEY AUTOINCREMENT,
        UNIQUE(subject, term, teacher),
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

        quiz FLOAT DEFAULT 0,
        assign FLOAT DEFAULT 0,
        midterm FLOAT DEFAULT 0,
        finals FLOAT DEFAULT 0,
        lab FLOAT DEFAULT 0,
        project FLOAT DEFAULT 0,

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

    def exists(self, login, password):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute(f'SELECT * FROM user_details WHERE id = "{login}" AND password = "{password}";')
        return c.fetchone() is not None

    def add_user(self, login, password, username, section):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        # Check if username already exists
        c.execute(f'SELECT * FROM user_details WHERE login = "{login}";')
        if c.fetchone() is not None:
            c.execute(
                f'UPDATE user_details SET password = "{password}", username = "{username}", class = "{section}" WHERE id = "{login}";')
        else:
            c.execute(f'INSERT INTO user_details VALUES ("{login}", "{password}", "{username}", "{section}");')
        conn.commit()

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

    def add_subject_term(self, *args):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        for kwargs in args:
            c.execute(
                f'SELECT subject_number FROM subject_term WHERE subject = "{kwargs["subject"]}" AND term = "{kwargs["term"]}" AND teacher = "{kwargs["teacher"]}";')
            if c.fetchone() is not None:
                c.execute(
                    f'UPDATE subject_term SET subject = "{kwargs["subject"]}", term = "{kwargs["term"]}", teacher = "{kwargs["teacher"]}" WHERE subject_number = {c.fetchone()[0]};')
            else:
                c.execute(
                    f'INSERT INTO subject_term VALUES (""{kwargs["subject"]}", "{kwargs["term"]}", "{kwargs["teacher"]}");')
        conn.commit()

    def add_weightage(self, *args):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        for kwargs in args:
            c.execute(
                f'SELECT subject_number FROM subject_term WHERE subject = "{kwargs["subject"]}" AND term = "{kwargs["term"]}" AND teacher = "{kwargs["teacher"]}";')
            sub_num = c.fetchone()[0]

            c.execute(
                f'SELECT * FROM weightage WHERE subject_id = "{sub_num}";')
            if c.fetchone() is not None:
                c.execute(
                    f'UPDATE weightage SET quiz_weight = "{kwargs["quiz_weight"]}", assign_weight = "{kwargs["assign_weight"]}", midterm_weight = "{kwargs["midterm_weight"]}", finals_weight = "{kwargs["finals_weight"]}", lab_weight = "{kwargs["lab_weight"]}", project_weight = "{kwargs["project_weight"]}" WHERE subject_id = "{sub_num}" AND id = "{kwargs["id"]}";')
            else:
                c.execute(
                    f'INSERT INTO weightage (id, subject_number, quiz_weight, assign_weight, midterm_weight, final_weight, lab_weight, project_weight) VALUES ("{kwargs["id"]}", "{sub_num}", "{kwargs["quiz_weight"]}", "{kwargs["assign_weight"]}", "{kwargs["midterm_weight"]}", "{kwargs["finals_weight"]}", "{kwargs["lab_weight"]}", "{kwargs["project_weight"]}");')
        conn.commit()

    def add_grade_details(self, *args):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        for kwargs in args:
            c.execute(
                f'SELECT subject_number FROM subject_term WHERE subject = "{kwargs["subject"]}" AND term = "{kwargs["term"]}" AND teacher = "{kwargs["teacher"]}";')
            sub_num = c.fetchone()[0]
            c.execute(
                f'SELECT subject_id FROM weightage WHERE id = "{kwargs["id"]}" AND subject_number = {sub_num};')
            sub_id = c.fetchone()[0]

            c.execute(
                f'SELECT * FROM grade_details WHERE subject_id = "{sub_id}";')
            if c.fetchone() is not None:
                c.execute(
                    f'UPDATE grade_details SET quiz = "{kwargs["quiz"]}", assign = "{kwargs["assign"]}", midterm = "{kwargs["midterm"]}", finals = "{kwargs["finals"]}", lab = "{kwargs["lab"]}", project = "{kwargs["project"]}", grade = "{kwargs["grade"]}" WHERE subject_id = "{sub_num}";')
            else:
                c.execute(
                    f'INSERT INTO grade_details (subject_id, quiz, assign, midterm, finals, lab, project, grade) VALUES ("{sub_num}", "{kwargs["quiz"]}", "{kwargs["assign"]}", "{kwargs["midterm"]}", "{kwargs["finals"]}", "{kwargs["lab"]}", "{kwargs["project"]}", "{kwargs["grade"]}");')
        conn.commit()

    def add_grade_avg(self, *args):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        for kwargs in args:
            c.execute(
                f'SELECT subject_number FROM subject_term WHERE subject = "{kwargs["subject"]}" AND term = "{kwargs["term"]}" AND teacher = "{kwargs["teacher"]}";')
            sub_num = c.fetchone()[0]
            c.execute(
                f'SELECT subject_id FROM weightage WHERE id = "{kwargs["id"]}" AND subject_number = {sub_num};')
            sub_id = c.fetchone()[0]

            c.execute(
                f'SELECT * FROM grade_avg WHERE subject_id = "{sub_id}";')
            if c.fetchone() is not None:
                c.execute(
                    f'UPDATE grade_avg SET quiz_avg = "{kwargs["quiz_avg"]}", assign_avg = "{kwargs["assign_avg"]}", midterm_avg = "{kwargs["midterm_avg"]}", finals_avg = "{kwargs["finals_avg"]}", lab_avg = "{kwargs["lab_avg"]}", project_avg = "{kwargs["project_avg"]}", grade_avg = "{kwargs["grade_avg"]}" WHERE subject_id = "{sub_num}";')
            else:
                c.execute(
                    f'INSERT INTO grade_avg (subject_id, quiz_avg, assign_avg, midterm_avg, finals_avg, lab_avg, project_avg, grade_avg) VALUES ("{sub_num}", "{kwargs["quiz_avg"]}", "{kwargs["assign_avg"]}", "{kwargs["midterm_avg"]}", "{kwargs["finals_avg"]}", "{kwargs["lab_avg"]}", "{kwargs["project_avg"]}", "{kwargs["grade_avg"]}");')

    def add_old_term_record(self, *args):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        for kwargs in args:
            c.execute(
                f'SELECT subject_number FROM subject_term WHERE subject = "{kwargs["subject"]}" AND term = "{kwargs["term"]}" AND teacher = "{kwargs["teacher"]}";')
            sub_num = c.fetchone()[0]
            c.execute(
                f'SELECT subject_id FROM weightage WHERE id = "{kwargs["id"]}" AND subject_number = {sub_num};')
            sub_id = c.fetchone()[0]

            c.execute(
                f'SELECT * FROM old_term_record WHERE subject_id = "{sub_id}";')
            if c.fetchone() is not None:
                c.execute(
                    f'UPDATE old_term_record SET aggregate = "{kwargs["aggregate"]}", grade = "{kwargs["grade"]}" WHERE subject_id = "{sub_id}";')
            else:
                c.execute(
                    f'INSERT INTO old_term_record (subject_id, aggregate, grade) VALUES ("{sub_id}", "{kwargs["aggregate"]}", "{kwargs["grade"]}");')

    def fetch_subject_codes(self, *args):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        query = 'SELECT code FROM subjects WHERE '
        for subject in args:
            query += f'(subject_name = "{subject[0]}" AND credits = {subject[1]}) OR '
        query = query[:-4] + ';'

        c.execute(query)
        response = [i[0] for i in c.fetchall()]

        conn.close()
        if len(response) != len(args):
            raise ValueError('Subject not found')
        return response


if __name__ == '__main__':
    db = DBSetup('my_db.db')
    print(db.fetch_subject_codes(('Organizational Behaviour', 3), ('Human Resource Management', 2)))
