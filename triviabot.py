import pickle

import pandas as pd
import socket
import json

import config
from idle import idle_scan, get_question
from active import active_scan, verify_answer

# process helpers

def connect_twitch(s):
    s.connect((config.HOST, config.PORT))
    s.send('PASS {}\r\n'.format(config.PASS).encode('utf-8'))
    s.send('NICK {}\r\n'.format(config.NICK).encode('utf-8'))
    s.send('JOIN {}\r\n'.format(config.CHAN).encode('utf-8'))

def parse_questions(questions_csv):
    max_answers = len(questions_csv.columns) - 2
    questions = {}
    for _, row in questions_csv.iterrows():
        questions[row[0]] = [row[1], [row[x] for x in range(2, 2+max_answers) if not pd.isnull(row[x])]]

    return questions

def parse_answers(answers_csv):
    max_answers = len(answers_csv.columns) - 1
    answers = {}
    for _, row in answers_csv.iterrows():
        answers[row[0]] = [row[x] for x in range(1, 1+max_answers) if not pd.isnull(row[x])]

    return answers

def parse_values(values_csv):
    values = {}
    for _, row in values_csv.iterrows():
        values[row[0]] = row[1]

    return values

def manage_scans(s, questions, answers, values, launched, user_log):
    terminate = False

    while not terminate:
        idle_complete, question_data = idle_scan(s, questions, answers, values, launched, user_log)

        if question_data == 'terminate':
            terminate = True

        else:
            with open('logs/question.pickle', 'wb') as handle1:
                pickle.dump(question_data[0], handle1, protocol=pickle.HIGHEST_PROTOCOL)

            with open('logs/value.pickle', 'wb') as handle2:
                pickle.dump(values[question_data[0]], handle2, protocol=pickle.HIGHEST_PROTOCOL)

            active_complete, launched, user_log = active_scan(s, questions, answers, values, question_data, launched, user_log)

        with open('logs/user_log.txt', 'w') as file:
            file.write(json.dumps(user_log))

        print('User Log:\n\t{0}\n\n--NOW IDLE--\n'.format(user_log))

#--

def main():
    questions_csv = pd.read_csv('questions/questions.csv', header=None)
    questions = parse_questions(questions_csv)
    answers_csv = pd.read_csv('questions/answers.csv', header=None)
    answers = parse_answers(answers_csv)
    values_csv = pd.read_csv('questions/values.csv', header=None)
    values = parse_values(values_csv)


    launched = []
    user_log = dict((id, {}) for id in questions)

    print(questions_csv)
    #print(questions)
    #print(answers_csv)
    #print(answers)
    print(values_csv)
    print(values)
    #print(user_log)

    s = socket.socket()
    connect_twitch(s)

    manage_scans(s, questions, answers, values, launched, user_log)



if __name__ == '__main__':
    main()
