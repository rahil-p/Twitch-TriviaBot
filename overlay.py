import pickle

from triviabot import parse_questions
import pandas as pd

from flask import Flask, render_template
app = Flask(__name__)



@app.route('/display')
def display():

    questions_csv = pd.read_csv('questions/questions.csv', header=None)
    questions = parse_questions(questions_csv)

    with open('logs/question.pickle', 'rb') as handle1:
        q_id = pickle.load(handle1)

    with open('logs/value.pickle', 'rb') as handle2:
        q_val = pickle.load(handle2)

    return render_template('display.html', posts=[q_id, questions[q_id], q_val])

@app.route('/results')
def results():

    questions_csv = pd.read_csv('questions/questions.csv', header=None)
    questions = parse_questions(questions_csv)

    with open('logs/results.pickle', 'rb') as handle:
        results = pickle.load(handle)

    q_id = results[0]

    total = sum(results[1].values())
    percentages = dict(zip(results[1].keys(), [100 * results[1][i] / total for i in results[1].keys()]))
    print(results)
    print(total)
    print(percentages)

    return render_template('results.html', posts=[q_id, questions[q_id], results, percentages])

if __name__ == '__main__':
    app.run(debug=True)
