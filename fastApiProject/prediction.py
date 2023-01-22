import numpy as np
import scipy.stats as stats
from math import sqrt

weights = np.load('model_weights.npy', allow_pickle=True).tolist()
scores = list(x / 1000 for x in range(1000))
# Use our model for prediction of boundary
subject_map = {'PHY': [1, 0, 0, 0, 0, 0],
               'HU': [0, 1, 0, 0, 0, 0],
               'MATH': [0, 0, 1, 0, 0, 0],
               'EE': [0, 0, 0, 1, 0, 0],
               'MGT': [0, 0, 0, 0, 1, 0],
               'CS': [0, 0, 0, 0, 0, 1]}


def make_prediction(data: np.ndarray):
    l1 = np.matmul(data, weights[0]) + weights[1]
    act = np.where(l1 > 0, l1, l1 * 0.2)
    l2 = np.matmul(act, weights[2]) + weights[3]
    act = np.where(l2 > 0, l2, l2 * 0.2)
    l3 = np.matmul(act, weights[4]) + weights[5]
    act = np.where(l3 > 0, l3, l3 * 0.2)
    l4 = np.matmul(act, weights[6]) + weights[7]

    act = np.power(1 + np.exp(-l4), -1)
    return act


def predict_boundary(ch, sub, data):
    avg = data.mean()

    sbs = [list(1 if score >= x > avg else 0 for x in data).count(1) if score > avg else -list(
        1 if score <= x < avg else 0 for x in data).count(1) / len(data) for score in scores]

    avg /= 100

    test = np.array([np.array([ch, score, avg, sb, *subject_map[sub], score ** 2, score * ch, score * avg, score * sb,
                               ch ** 2, ch * avg, ch * sb, avg ** 2, avg * sb, sb ** 2]) for score, sb in
                     zip(scores, sbs)])
    results = make_prediction(test)

    def get_boundary(**kwargs):
        result = []
        for rec in kwargs['record']:
            if 0 <= rec < kwargs['A']:
                result.append('A')
            elif kwargs['A'] <= rec < kwargs['B+']:
                result.append('B+')
            elif kwargs['B+'] <= rec < kwargs['B']:
                result.append('B')
            elif kwargs['B'] <= rec < kwargs['C+']:
                result.append('C+')
            elif kwargs['C+'] <= rec < kwargs['C']:
                result.append('C')
            elif kwargs['C'] <= rec < kwargs['D+']:
                result.append('D+')
            elif kwargs['D+'] <= rec < kwargs['D']:
                result.append('D')
            elif kwargs['D'] <= rec < kwargs['F']:
                result.append('F')
        return result

    # Has the numbers as you wanted
    tries = 1
    entities = 0
    key_maps = {'B+': 'A', 'B': 'B+', 'C+': 'B', 'C': 'C+', 'D+': 'C', 'D': 'F'}
    keys = {'A': 1 / 8, 'B+': 2 / 8, 'B': 3 / 8, 'C+': 4 / 8, 'C': 5 / 8, 'D+': 6 / 8, 'D': 7 / 8, 'F': 8 / 8}
    try:
        while tries < 10 and entities != 8:
            temp = get_boundary(**keys, record=results)
            left_overs = set(keys.keys()) - set(temp)
            entities = 8 - len(left_overs)
            for key in left_overs:
                if key == 'A':
                    keys['A'] += 0.06 / tries
                    continue
                keys[key_maps[key]] -= 0.07 / tries
                keys[key] += 0.07 / tries
            tries += 1
    except KeyError:
        pass

    boundaries = {}
    for grade in keys.keys():
        if grade in temp:
            boundaries[grade] = temp.index(grade) / 10

    return boundaries


def grade_detail(ch, subject, score, data):
    if subject not in subject_map:
        return ['-', '-', '-']
    print(ch, subject, score, data.shape)
    temp = sorted(predict_boundary(ch, subject, data).items(), key=lambda x: x[1], reverse=True)
    index = 0
    print(temp)
    for k, v in temp:
        if score >= int(v):
            grade = k
            break
        index += 1

    up = round(100 - (stats.norm.cdf((temp[index - 1][1] - score) / sqrt(data.var())) * 100), 2) if index else 0
    down = round((stats.norm.cdf((temp[index + 1][1] - score) / sqrt(data.var())) * 100), 2) if index + 1 < len(
        temp) else 0

    return grade, up, down
