import threading
import time
import os
import random
import requests
import string
import sys
import argparse

###GLOBAL VARIABLES
phone_and_country_code_dict = {}
proxies_list = []
THREAD_NUM = 1
RUNNER = True
TIMEOUT = 3
COUNT = 0
SAVE_LOGS = True
DONE_THREADS = 0
TOTAL_TO_BE_CHECKED = 0
START_TIME = time.time()

mutex = threading.Lock()

class Thread_Manager:
    def __init__(self, THREAD_NUM):
        self.amount_of_threads = THREAD_NUM
    
    def tread_runner(self):
        global TOTAL_TO_BE_CHECKED
        TOTAL_TO_BE_CHECKED = len(phone_and_country_code_dict)

        print(f"\nStarting {self.amount_of_threads} threads...\n")

        for i in range(self.amount_of_threads):
            new_thread = threading.Thread(target=checker, args=(i,))
            new_thread.start()

    
    def thread_closer(self):
        global RUNNER

        RUNNER = False
        print("Shutting down threads\nSome results will still be logged but not shown while all threads are closing\nThe elements that were not scanned will be added to a new file")
        sys.stdout = open(os.devnull, 'w')


        ###Adds the remaining combos to a new file
        mutex.acquire()
        with open('unscanned.txt', 'w') as file:
            for phone_number, country_code in phone_and_country_code_dict.items():
                file.write(f"{phone_number}:{country_code}\n")
        mutex.release()

def intro():
    intro_string = '''
 __                     ___ _                            ___ _               _    
/ _\\_ __   __ _ _ __   / _ \\ |__   ___  _ __   ___      / __\\ |__   ___  ___| | __
\\ \\| '_ \\ / _` | '_ \\ / /_)/ '_ \\ / _ \\| '_ \\ / _ \\    / /  | '_ \\ / _ \\/ __| |/ /
_\\ \\ | | | (_| | |_) / ___/| | | | (_) | | | |  __/   / /___| | | |  __/ (__|   < 
\\__/_| |_|\\__,_| .__/\\/    |_| |_|\\___/|_| |_|\\___|___\\____/|_| |_|\\___|\\___|_|\\_\\
               |_|                               |_____|                          

Author: 7Wardens
Github: https://github.com/7Wardens

'''
    os.system('cls||clear')
    print(intro_string)


def argument_parser():

    def positive_int(value):
        try:
            value = int(value)
            if value <= 0:
                raise argparse.ArgumentTypeError("Number of threads must be higher or equal to 1")
        except ValueError:
            raise argparse.ArgumentTypeError("Parameter is not an integer")

        return value

    global THREAD_NUM
    parser = argparse.ArgumentParser(description='Check if phone numbers are linked to a snapchat account')

    parser.add_argument('-l',nargs=1, metavar='filepath', help='Specify a list path for combolist with phone_number:country_Code format', required=True)
    parser.add_argument('-p',nargs=1, metavar='proxies_path', help='Enable use of proxies and specify path to list')
    parser.add_argument('-t',nargs=1, metavar='threads', help='Specify amount of threads (default 1)', type=positive_int)

    args = vars(parser.parse_args())

    load_combolist(args['l'][0])

    if (args['p']):
        load_proxies(args['p'][0])

    if (args['t']):
        THREAD_NUM = args['t'][0]


def load_combolist(combo_path):
    global phone_and_country_code_dict
    if os.path.exists(combo_path):
        with open(combo_path, 'r', encoding='utf-8') as combo_file:
            file_lines = combo_file.read().splitlines()
        
        for target in file_lines:
            phone_number, country_code = target.split(":", 1)
            phone_and_country_code_dict[phone_number]=country_code

    print(f"[*]Combolist path: {combo_path} - Amount: {len(phone_and_country_code_dict)}")

def load_proxies(proxies_path):
    global proxies_list
    if os.path.exists(proxies_path):
        with open(proxies_path, 'r', encoding='utf-8') as proxies_file:
            file_lines = proxies_file.read().splitlines()
        
        for proxy in file_lines:
            proxy_string = f"http://{proxy}"
            proxies_list.append(proxy_string)

    print(f"[*]Proxie-list path: {proxies_path} - Amount: {len(proxies_list)}")

def checker(thread_id):
    global  RUNNER, TIMEOUT, COUNT, TOTAL_TO_BE_CHECKED, START_TIME, DONE_THREADS
    global phone_and_country_code_dict, proxies_list
    current_proxy = ""

    while RUNNER:
        mutex.acquire()
        COUNT = COUNT +1

        if COUNT%150==0:
            checked_string = f"CURRENTLY CHECKED: {COUNT}/{TOTAL_TO_BE_CHECKED}"
            time_string = f"CURRENT TIME: {time.time() - START_TIME:.2f} s"
            print(f"*------------------------------------------------*\n|{checked_string:^48}|\n|{time_string:^48}|\n*------------------------------------------------*")

        if len(phone_and_country_code_dict)<=0:
            DONE_THREADS += 1
            mutex.release()
            return -1


        phone_number = random.choice(list(phone_and_country_code_dict.keys()))
        phone_country_code = phone_and_country_code_dict.pop(phone_number)

        '''
        BUG -> If a person wants to use proxies but all available proxies are in use
        then the script will continue to do the request without using any proxy

        FIX -> Implement a waiting method, and force the user to have as many proxies
        as threads

        PRE_FIX -> It is already recommended to use proxies, in order to hide identiy,
        to prevent the use of non-proxy request, make sure you have a big list of proxies
        or at least double(2 for each just in case) the amount of threads
        '''
        if current_proxy=="" and len(proxies_list)>0:
            current_proxy = proxies_list.pop(0)

        mutex.release()

        TOKEN = ''.join([random.choice(string.ascii_letters + string.digits) for _ in range(22)])

        headers = {
            'Cookie':f'xsrf_token={TOKEN}',
            "User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36"
        }

        data = {
            'phone_country_code':phone_country_code,
            'phone_number':phone_number,
            'xsrf_token':TOKEN
        }

        try:

            response = requests.post('https://accounts.snapchat.com/accounts/validate_phone_number', headers=headers, data=data, proxies={'https': current_proxy}, timeout=TIMEOUT)

            if response.status_code==429:
                raise requests.exceptions.ConnectionError
            
        except (requests.exceptions.ProxyError, requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout) as exception:
            print(f"thread:{thread_id}> Caught error: {exception}")
            if current_proxy!="": # <- possible error based on previous bug mentioned
                proxies_list.append(current_proxy)
                current_proxy=proxies_list.pop(0)

                phone_and_country_code_dict[phone_number] = phone_country_code

                empty_space = " " * len(f"thread:{thread_id}")
                print(f"{empty_space}> new proxy - {current_proxy}")

            continue
                
        except Exception as exception:
            print(f"thread:{thread_id}> Unexpected erorr: {exception}")
            if current_proxy!="":
                proxies_list.append(current_proxy)
                current_proxy=proxies_list.pop(0)

                phone_and_country_code_dict[phone_number] = phone_country_code

                empty_space = " " * len(f"thread:{thread_id}")
                print(f"{empty_space}> new proxy - {current_proxy}")

            continue


        if response.status_code==200:
            result_parser(phone_number, phone_country_code, response, thread_id)
            time.sleep(4)

def result_parser(phone_number, phone_country_code, response, thread_id):
    global SAVE_LOGS

    json_formatted = response.json()

    if 'status_code' in json_formatted:
        print(f"thread:{thread_id}> ", end="")


        if json_formatted['status_code']=='TAKEN_NUMBER':
            print(f"{phone_number} is taken")

            if SAVE_LOGS:
                mutex.acquire()
                with open('./logs/taken.log', 'a') as taken_log_file:
                    taken_log_file.write(f'{phone_number}:{phone_country_code}\n')
                mutex.release()

            
        elif json_formatted['status_code']=='OK':
            print(f"{phone_number} is available")

            if SAVE_LOGS:
                mutex.acquire()
                with open('./logs/available.log', 'a') as taken_log_file:
                    taken_log_file.write(f'{phone_number}:{phone_country_code}\n')
                mutex.release()


        elif json_formatted['status_code']=='INVALID_NUMBER':
            print(f"{phone_number} is invalid - Check the phone number and country code")

            if SAVE_LOGS:
                mutex.acquire()
                with open('./logs/invalid.log', 'a') as taken_log_file:
                    taken_log_file.write(f'{phone_number}:{phone_country_code}\n')
                mutex.release()

        else:
            print(f'Error fetching response of status')

    else:
        print(f"Error obtaining the phone data")


def main():
    intro()
    argument_parser()

    manager_t = Thread_Manager(THREAD_NUM)
    manager_t.tread_runner()

    try:
        while True:
            if DONE_THREADS == THREAD_NUM:
                print("Done checking all numbers")
                break
        
    except KeyboardInterrupt:
        manager_t.thread_closer()


    print(f'Total Execution Time: {time.time()-START_TIME:.2f} s')

if __name__=='__main__':
    main()