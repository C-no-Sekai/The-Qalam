from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from db_setup import DBSetup
from support_functions import SupportFunctions
import threading
from form_filler import form_filler


class Validation(BaseModel):
    login: str = None
    password: str = None
    section: str = None

    class Config:
        orm_mode = True


class SubjectRequest(BaseModel):
    login: str = None
    term: str = None

    class Config:
        orm_mode = True


class ImageRequest(BaseModel):
    login: str = None
    term: str = None
    subject: str

    class Config:
        orm_mode = True


class Cred(BaseModel):
    password: str = None

    class Config:
        orm_mode = True


class NewWeights(BaseModel):
    login: str = None
    term: str = None
    subject: str = None
    quiz_weight: int = None
    assign_weight: int = None
    lab_weight: int = None
    project_weight: int = None
    midterm_weight: int = None
    finals_weight: int = None

    class Config:
        orm_mode = True


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_methods=['*'],
)

dbHandler = DBSetup('my_db.db')
support_func = SupportFunctions()


# This is the function that will be called when the user clicks on the "Register" button
def add_user(input_data: Validation):
    if not all(input_data.dict().values()):
        return
    # Verify credentials from Qalam
    valid, name = support_func.auth(input_data.login, input_data.password)
    if not valid:
        return
    # Add user to database
    dbHandler.add_user(input_data.login, input_data.password, name, input_data.section)
    print('[+] User Added')

    # fetch all details from qalam to fill grades table
    previous_terms, cur_sub_details, teachers = support_func.fetch_all_details(input_data.login, input_data.password)
    print('[+] Fetched all details from Qalam')

    # add all details to relevant db tables
    # add to db tables all fields

    # find current term

    temp = list(previous_terms.keys())[-1]
    year = int(temp[-4:])
    term = temp[0:-5]

    term = term == 'spring' and 'fall' or 'spring'
    year = term == 'spring' and year + 1 or year

    cur_term = term + ' ' + str(year)

    # Find subject codes and teacher name for cur_term
    temp = [(sub['name'].replace('&', 'and'), sub['credits']) for sub in cur_sub_details]
    sub_codes = dbHandler.fetch_subject_codes(*temp)
    teacher_names = [teachers[subject['name']] for subject in cur_sub_details]

    # add to subject_term table
    records = []
    for sub, teach in zip(sub_codes, teacher_names):
        records.append({'subject': sub, 'term': cur_term, 'teacher': teach if teach else 'visiting'})
    dbHandler.add_subject_term(*records)
    print('[+] Added to subject_term table')

    # {term: [{course: [credits, aggregate, grade]}, ...], ...}
    old_sub = []
    old_sub_details = []

    for key, val in previous_terms.items():
        for rec in val:
            for course_name, detail in rec.items():
                old_sub.append((course_name.lower().replace('&', 'and'), detail[0]))
                old_sub_details.append({'term': key, 'aggregate': detail[1], 'grade': detail[2], 'teacher': 'visiting',
                                        'id': input_data.login})

    old_sub_codes = dbHandler.fetch_subject_codes(*old_sub)
    old_sub_details = [{**details, 'subject': code} for details, code in zip(old_sub_details, old_sub_codes)]

    dbHandler.add_subject_term(*old_sub_details)
    print('[+] Added to subject_term table')

    # add to weightage table
    records = [{**record, 'id': input_data.login} for record in records]
    dbHandler.add_weightage(*records)
    print('[+] Added to weightage table')

    dbHandler.add_weightage(*old_sub_details)
    print('[+] Added to weightage table')

    # add to grades and grade_avg table
    records = [{**record, **grade, 'grade': 'P'} for record, grade in zip(records, cur_sub_details)]
    dbHandler.add_grade_details(*records)
    dbHandler.add_grade_avg(*records)
    print('[+] Added to grades and grade_avg table')

    # add to old_term_record table
    dbHandler.add_old_term_record(*old_sub_details)
    print('[+] Added to old_term_record table')


@app.post("/validate")
async def starter(input_data: Validation):
    result = dbHandler.exists(input_data.login, input_data.password)
    if result:
        return {'result': "success", 'name': result[0]}
    return {'result': False}


@app.post("/addUser")
async def starter(input_data: Validation):
    threading.Thread(target=lambda: add_user(input_data)).start()
    return {'result': 'pending'}


@app.post("/fillForms")
async def starter(input_data: Validation):
    threading.Thread(target=lambda: form_filler(input_data.login, input_data.password)).start()
    return {'result': 'pending'}


@app.post("/getGrades")
async def starter(input_data: SubjectRequest):
    return {'grades': dbHandler.fetch_term_result(input_data.login, input_data.term)}


@app.post("/getImage")
async def starter(input_data: ImageRequest):
    return {'image': dbHandler.fetch_image(input_data.login, input_data.term, input_data.subject)}


@app.post("/getTerms")
async def starter(input_data: Validation):
    return {'terms': dbHandler.fetch_terms(input_data.login)}


@app.post("/editWeightage")
async def starter(input_data: NewWeights):
    return {'result': dbHandler.update_and_fetch_new_record(**input_data.dict())}


@app.post("/prepareNextTerm")
async def starter(input_data: Cred):
    # Match with a very strong password
    threading.Thread(target=dbHandler.send_features, args=([input_data.password])).start()
    return {'result': 'pending'}
