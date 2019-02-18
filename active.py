import pandas as pd
import time

import config

def active_scan(s, questions, answers, values, question_data, launched, user_log):
    active = True

    q_id = question_data[0]
    q = question_data[1][0]
    q_options = dict(zip(range(1, question_data[2]+1), question_data[1][1]))

    print('--QUESTION ACTIVE--\n[{0}] is now active:\n\tQ: {1}\n\tA: {2}\n-------------------\n'.format(q_id, q, q_options))

    while active:
        response = s.recv(1024).decode('utf-8')
        lines = response.split('/n')

        if response == 'PING :tmi.twitch.tv\r\n':
            s.send("PONG :tmi.twitch.tv\r\n".encode("utf-8"))

        for line in lines:
            print(line)

            try:
                user, resp = read_line(line)
                if user == config.leader_name and '!end' in resp:
                    print('--END CONFIRMATION--\nYou are about to end [{0}]'.format(q_id))
                    end_confirm = input('*Enter y to confirm: ')

                    if end_confirm.lower() == 'y':
                        active = False
                        launched.append(q_id)
                        print('[{0}] has ended'.format(q_id))

                    else:
                        print('-Confirmation Denied (remaining in active state)')

                    print('--------------------\n')

                elif user == config.leader_name and '!status' in resp:
                    print('--[{0}] STATUS--\n\tValid responses: {1}'.format(q_id, len(user_log[q_id])))

                    #update_answers
                    answers = update_answers()

                    q_answers = answers[q_id]
                    for i, o in enumerate(q_options):
                        tick = '*' if o in q_answers else ''
                        o_count = sum(x == i+1 for x in user_log[q_id].values())
                        print('\t\t{0}: {1} {2}'.format(i+1,
                                                        o_count,
                                                        tick))

                    print('---------------\n')

                elif '!answer' in resp:
                    #only allows for single character answer codes (first digit after alias)
                    answer = resp.split('!answer ')[1][0]
                    verified = verify_answer(answer, q_options)

                    if verified:
                        user_log[q_id][user] = int(answer)

            except IndexError:
                pass
        time.sleep(.1)

    return True, launched, user_log

def verify_answer(answer, q_options):
    try:
        if int(answer) in q_options:
            print('\tAnswer verified')
            return True
        else:
            print('\tAnswer is in incorrect format')
            return False
    except:
        print('\tAnswer is in incorrect format')
        return False

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
