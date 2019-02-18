import pickle

import pandas as pd
import time
import re

import config

def idle_scan(s, questions, answers, values, launched, user_log):
    idle = True

    # prints summary of unlaunched questions
    print('--SUMMARY--\nThe following questions are available:')
    if len(launched) == 0:
        print('\tunlaunched:', list(questions.keys()))
    else:
        print('\tunlaunched:', [el for el in list(questions.keys()) if el not in launched])
    print('-----------\n')

    while idle:
        response = s.recv(1024).decode('utf-8')
        lines = response.split('/n')

        # handles the Twitch API's ping check
        if response == 'PING :tmi.twitch.tv\r\n':
            s.send("PONG :tmi.twitch.tv\r\n".encode("utf-8"))

        for line in lines:
            print(line)

            try:
                user, resp = read_line(line)

                if user == config.leader_name and '!launch ' in resp:
                    # necessitates that question ids (col A) are in the form q[digits]
                    # reads q_id within the response
                    q_id = re.findall("q[0-9]+", resp.split('!launch ')[1])[0]
                    # finds question content
                    q_content = get_question(re.findall("q[0-9]+", resp.split('!launch ')[1])[0], questions)

                    if q_content:
                        #restructures q_content into an array
                        question_data = [q_id, q_content, len(q_content[1])]

                        # communications launch confirmation
                        print('--LAUNCH CONFIRMATION--\nYou are about to launch [{0}]:\n\tQ: {1}\n\tA: {2}'.format(q_id, q_content[0], q_content[1]))
                        q_confirm = input('*Enter y to confirm: ')

                        if q_confirm.lower() == 'y':
                            idle = False
                        else:
                            print('-Confirmation Denied (remaining in idle state)')

                        print('-----------------------\n')

                elif user == config.leader_name and '!results ' in resp:
                    q_id = re.findall("q[0-9]+", resp.split('!results ')[1])[0]

                    if q_id in user_log and len(user_log[q_id]) > 0:
                        #update answers
                        answers = update_answers()

                        o_count = len(questions[q_id][1])
                        results = dict(zip(range(1, o_count+1),
                                           [sum(x == num for x in user_log[q_id].values()) for num in range(1, o_count+1)]))
                        total_responses = sum(results.values())

                        print('--RESULTS [{0}]--'.format(q_id))

                        q_answers = answers[q_id]
                        total_correct = 0
                        for option in results:
                            tick = '*' if option in q_answers else ''
                            if option in q_answers:
                                total_correct += results[option]
                            print('\t{0}: {1}\t({2}%) {3}'.format(option,
                                                                  results[option],
                                                                  100 * results[option]/total_responses,
                                                                  tick))
                        #then pickle to pass to flask
                        #pass q_id and results
                        with open('logs/results.pickle', 'wb') as handle:
                            pickle.dump([q_id, results, answers[q_id], values[q_id], total_correct], handle, protocol=pickle.HIGHEST_PROTOCOL)
                    else:
                        print('-Results not found for {0}'.format(q_id))

                    print('----------------\n')

                elif user == config.leader_name and '!leaders' in resp:
                    #update_answers
                    answers = update_answers()
                    print('--LEADERS RAW--')
                    print('Answers (Raw): {}'.format(answers))

                    #get list of users
                    user_list = []
                    for k, v in user_log.items():
                        for k1, v1 in v.items():
                            if k1 not in user_list:
                                user_list.append(k1)

                    print('User List (Raw): {}'.format(user_list))

                    #get dict of correct questions per user
                    user_corrects = dict((el,[]) for el in user_list)
                    print(user_corrects)
                    for u in user_list:
                        for a_q in user_log:
                            try:
                                if user_log[a_q][u] in answers[a_q]:
                                    print('yee')
                                    user_corrects[u].append(a_q)
                            except KeyError:
                                pass

                    print('User Corrects (Raw): {}'.format(user_corrects))

                    #get correct users per question
                    correct_totals = {}
                    for b_q in user_log:
                        total_corr = 0
                        for response in user_log[b_q].values():
                            if response in answers[b_q]:
                                total_corr += 1
                        correct_totals[b_q] = total_corr

                    print('Correct Totals (Raw): {}'.format(correct_totals))

                    #values is value per question

                    #get value/user per question
                    values_per_user = {}
                    for c_q in correct_totals:
                        if correct_totals[c_q] != 0:
                            values_per_user[c_q] = values[c_q] // correct_totals[c_q]
                        else:
                            values_per_user[c_q] = 0

                    print('Val/User (Raw): {}'.format(values_per_user))

                    leader_results = {}
                    for a_user in user_corrects:
                        leader_results[a_user] = sum(values_per_user[qu] for qu in user_corrects[a_user])

                    print('Leader Results (Raw): {}'.format(leader_results))
                    print('---------------')

                    print('--LEADERBOARD--')
                    for k, v in sorted(leader_results.items()):
                        print('\t{0}: {1}'.format(k, v))


                elif user == config.leader_name and '!terminate' in resp:
                    print('--TERMINATION CONFIRMATION--\nYou are about to terminate the session.')
                    terminate_confirm = input("*Enter 'end' to confirm: ")

                    if terminate_confirm.lower() == 'end':
                        question_data = 'terminate'
                        idle = False
                    else:
                        print('-Confirmation Denied (remaining in idle state)')

                    print('----------------------------\n')
            except IndexError:
                pass
        time.sleep(.1)

    return True, question_data

def get_question(question, questions):

    if question in questions:
        active_question = questions[question]
    else:
        return False

    return active_question

def parse_answers(answers_csv):
    max_answers = len(answers_csv.columns) - 1
    answers = {}
    for _, row in answers_csv.iterrows():
        answers[row[0]] = [row[x] for x in range(1, 1+max_answers) if not pd.isnull(row[x])]

    return answers

def update_answers():
    answers_csv = pd.read_csv('questions/answers.csv', header=None)
    answers = parse_answers(answers_csv)

    return answers

def read_line(line):
    user = line.split('!', 1)[0].split(':', 1)[1]
    resp = line.split('PRIVMSG {0} :'.format(config.leader))[1]

    return user, resp
