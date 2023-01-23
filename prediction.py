import numpy as np
import scipy.stats as stats
from math import sqrt
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import io
import base64

all_grades = {'A', 'B+', 'B', 'C+', 'C', 'D+', 'D', 'F'}
grade_pos = {'A': 0, 'B+': 1, 'B': 2, 'C+': 3, 'C': 4, 'D+': 5, 'D': 6, 'F': 7}
grade_map = {'0': "A", '1': "B+", '2': "B", '3': "C+", '4': "C", '5': "D+", '6': "D", '7': "F"}

# Use our model for prediction of boundary
subject_map = {'PHY': [1, 0, 0, 0, 0, 0],
               'HU': [0, 1, 0, 0, 0, 0],
               'MATH': [0, 0, 1, 0, 0, 0],
               'EE': [0, 0, 0, 1, 0, 0],
               'MGT': [0, 0, 0, 0, 1, 0],
               'CS': [0, 0, 0, 0, 0, 1]}

l1_weights = np.loadtxt("params/w1.txt")
l1_bias = np.loadtxt("params/b1.txt")

l2_weights = np.loadtxt("params/w2.txt")
l2_bias = np.loadtxt("params/b2.txt")

l3_weights = np.loadtxt("params/w3.txt")
l3_bias = np.loadtxt("params/b3.txt")


def make_prediction(input_data):
    return np.matmul(
        np.maximum(0, np.matmul(np.maximum(0, np.matmul(input_data, l1_weights) + l1_bias), l2_weights) + l2_bias),
        l3_weights) + l3_bias


def get_boundary(score, ch, mean, data):
    prev_grade = 0
    cur_grade = 0
    boundaries = []

    while len(boundaries) != 8 and score > 0:
        while not prev_grade < cur_grade:
            SB = list(1 if score > x > mean else 0 for x in data).count(1) if score > mean else -list(
                1 if score < x < mean else 0 for x in data).count(1)
            SB /= len(data)
            res = make_prediction(np.array([[score, ch, mean, SB, score ** 2, score * ch, score * mean, score * SB,
                                             ch ** 2, ch * mean, ch * SB, mean ** 2, mean * SB, SB ** 2]]))[0]
            cur_grade = np.where(res == np.max(res))[0][0]  # gives index for grade
            score -= 1
        score += 0.9
        cur_grade = prev_grade

        while not prev_grade < cur_grade:
            SB = list(1 if score > x > mean else 0 for x in data).count(1) if score > mean else -list(
                1 if score < x < mean else 0 for x in data).count(1)
            SB /= len(data)
            res = make_prediction(np.array([[score, ch, mean, SB, score ** 2, score * ch, score * mean, score * SB,
                                             ch ** 2, ch * mean, ch * SB, mean ** 2, mean * SB, SB ** 2]]))[0]
            cur_grade = np.where(res == np.max(res))[0][0]  # gives index for grade
            score -= 0.1
        boundaries.insert(0, score + 0.1)

        prev_grade = cur_grade
        if cur_grade == 7:
            boundaries.insert(0, score)
            break

    for i in range(8 - len(boundaries)):
        boundaries.insert(0, 0)

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
    code = subject.split('-')[0]
    if code not in subject_map:
        code = 'CS'
    boundary = get_boundary(min(data.mean() + 3 * sqrt(data.var()), 89), ch, data.mean(), data)[::-1]
    img = generate_image(boundary, subject, data)

    return img


def grade_detail(ch, subject, score, data):
    if subject not in subject_map:
        subject = 'CS'
        # return '-', '-', '-', '-'
    boundaries = get_boundary(min(data.mean() + 3 * sqrt(data.var()), 89), ch, data.mean(), data)

    mean = data.mean()
    SB = list(1 if score > x > mean else 0 for x in data).count(1) if score > mean else -list(
        1 if score < x < mean else 0 for x in data).count(1)
    SB /= len(data)
    res = make_prediction(np.array([[score, ch, mean, SB,
                                     score ** 2, score * ch, score * mean, score * SB,
                                     ch ** 2, ch * mean, ch * SB,
                                     mean ** 2, mean * SB,
                                     SB ** 2]]))[0]
    grade = np.where(res == np.max(res))[0][0]

    try:
        up = round(100 - (stats.norm.cdf((boundaries[8 - grade] - score) / sqrt(data.var())) * 100),
                   2) if grade else "0"
    except ZeroDivisionError:
        up = 0
    try:
        down = round((stats.norm.cdf((boundaries[7 - grade] - score) / sqrt(data.var())) * 100),
                     2) if grade != 7 else "0"
    except ZeroDivisionError:
        down = 0

    return grade_map[str(grade)], down, up
