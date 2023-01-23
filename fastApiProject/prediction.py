import numpy as np
import scipy.stats as stats
from math import sqrt
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import io
import base64

weights = np.load('model_weights.npy', allow_pickle=True).tolist()
scores = list(x / 1000 for x in range(1000))
all_grades = {'A', 'B+', 'B', 'C+', 'C', 'D+', 'D', 'F'}
grade_pos = {'A': 0, 'B+': 1, 'B': 2, 'C+': 3, 'C': 4, 'D+': 5, 'D': 6, 'F': 7}

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
        while tries < 2 and entities != 8:
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


def generate_image(boundaries, label, data):
    boundaries = boundaries[::-1]
    plt.clf()
    plt.cla()
    if not data.size:
        return
    mean = data.mean()
    std_deviation = sqrt(data.var())

    # Plot the new curve and save it
    x = np.linspace(mean - 3 * std_deviation, mean + 3 * std_deviation, 100)
    # if std_deviation:
    y = stats.norm.pdf(x, mean, std_deviation)

    x = [y for y in x]
    y = [x for x in y]
    for i in range(int(x[0]) + 1):
        x.insert(0, i)
        y.insert(0, 0)
    for i in range(int(x[-1]) + 1, 101):
        x.insert(-1, i)
        y.insert(-1, 0)
    x = np.array(x)
    y = np.array(y)

    plt.plot(x, y, label=label, color="black")
    plt.rcParams["figure.figsize"] = (10, 1)
    # filling colors Start from
    try:
        start = np.where(x > boundaries[-1])[0][0]
    except IndexError:
        print("Actual Was:", np.where(x > boundaries[-1]))
        print(np.where(x > boundaries[-1])[0])
        print("[-] ERROR boundaries were: ", boundaries)
        return
    plt.fill_between(x[start:], 0, y[start:], color='green', alpha=0.7)

    end = start + 3
    start = np.where(x > boundaries[-2])[0][0]
    plt.fill_between(x[start:end], 0, y[start:end], color='blue', alpha=0.3)

    end = start + 3
    start = np.where(x > boundaries[-3])[0][0]
    plt.fill_between(x[start:end], 0, y[start:end], color='red', alpha=0.3)

    end = start + 3
    start = np.where(x > boundaries[-4])[0][0]
    plt.fill_between(x[start:end], 0, y[start:end], color='pink', alpha=0.3)

    end = start + 3
    start = np.where(x > boundaries[-5])[0][0]
    plt.fill_between(x[start:end], 0, y[start:end], color='purple', alpha=0.3)

    end = start + 3
    start = np.where(x > boundaries[-6])[0][0]
    plt.fill_between(x[start:end], 0, y[start:end], color='brown', alpha=0.3)

    end = start + 3
    start = np.where(x > boundaries[-7])[0][0]
    plt.fill_between(x[start:end], 0, y[start:end], color='red', alpha=0.3)

    end = start + 3
    start = np.where(x > boundaries[-8])[0][0]
    plt.fill_between(x[start:end], 0, y[start:end], color='black', alpha=0.3)

    patch1 = mpatches.Patch(color='green', label='A')
    patch2 = mpatches.Patch(color='blue', label='B+')
    patch3 = mpatches.Patch(color='red', label='B')
    patch4 = mpatches.Patch(color='pink', label='C+')
    patch5 = mpatches.Patch(color='purple', label='C')
    patch6 = mpatches.Patch(color='brown', label='D+')
    patch7 = mpatches.Patch(color='red', label='D')
    patch8 = mpatches.Patch(color='black', label='F')

    plt.legend(handles=[patch1, patch2, patch3, patch4, patch5, patch6, patch7, patch8])
    plt.title(label)

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)

    # Encode the image to base64
    image = base64.b64encode(buf.read())
    return image


def get_img(ch, subject, data):
    if subject.split('-')[0] not in subject_map:
        return None
    temp = sorted(predict_boundary(ch, subject.split('-')[0], data).items(), key=lambda x: x[1], reverse=True)
    # If boundary for some grade is empty
    boundary = [float(x[1]) for x in temp]
    left_over = all_grades - set(x[0] for x in temp)
    for grade in left_over:
        try:
            boundary.insert(grade_pos[grade], boundary[grade_pos[grade] + 1] + 0.5)
        except IndexError:
            boundary.append(boundary[-1] - 0.5)

    img = generate_image(boundary, subject, data)

    return img


def grade_detail(ch, subject, score, data):
    if subject not in subject_map:
        return '-', '-', '-', '-'
    temp = sorted(predict_boundary(ch, subject, data).items(), key=lambda x: x[1], reverse=True)
    index = 0
    for k, v in temp:
        if score >= int(v):
            grade = k
            break
        index += 1

    up = round(100 - (stats.norm.cdf((temp[index - 1][1] - score) / sqrt(data.var())) * 100), 2) if grade != 'A' else 0
    down = round((stats.norm.cdf((temp[index + 1][1] - score) / sqrt(data.var())) * 100), 2) if grade != 'F' else 0

    return grade, down, up
