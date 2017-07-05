#!/usr/bin/env python

import csv
import webbrowser
import time
from datetime import datetime
import shutil
import subprocess
import ConfigParser


NON_PS_SUPPORT_REPS = (['Grey Elerson', 'Stefan Nychka', 'Eddie Hsu',
                        'Zach Cowart', 'Robert Babcock', 'Brittany Luttrell'])


def get_creds():
    config = ConfigParser.ConfigParser()
    config.read('/Users/kevinmouritsen/python-projects/hively/hively/config/hively.config')
    url = config.get('Hively', 'url')
    username = config.get('Hively', 'username')
    password = config.get('Hively', 'password')
    return url, username, password


def download_csv():
    subprocess.call('killall -15 firefox', shell=True)
    webbrowser.open_new_tab('https://secure.teamhively.com/ratings/download.csv')
    time.sleep(25)
    webbrowser.open_new_tab('https://secure.teamhively.com/ratings/download.csv')
    time.sleep(15)


def get_today_date():
    date_dict = {}
    today = datetime.now()
    date_dict['year'] = str(today.year)
    date_dict['month'] = str(today.month)
    date_dict['day'] = str(today.day)
    if len(date_dict['day']) == 1:
        date_dict['day'] = '0' + date_dict['day']
    if len(date_dict['month']) == 1:
        date_dict['month'] = '0' + date_dict['month']
    return date_dict


def move_and_rename_downloaded_csv(date_dict):
    try:
    	shutil.move('/Users/kevinmouritsen/Downloads/ratings-'+date_dict['year']+'-'+\
        date_dict['month']+'-'+date_dict['day']+'.csv', \
        '/Users/kevinmouritsen/python-projects/hively/hively/files/hively.csv')
    except:
    	date_dict['day'] = int(date_dict['day']) + 1
    	date_dict['day'] = str(date_dict['day'])
    	if len(date_dict['day']) == 1:
    		date_dict['day'] = '0' + date_dict['day']
    	shutil.move('/Users/kevinmouritsen/Downloads/ratings-'+date_dict['year']+'-'\
            +date_dict['month']+'-'+date_dict['day']+'.csv', \
            '/Users/kevinmouritsen/python-projects/hively/hively/files/hively.csv')


def read_csv_data():
    hively_list = []
    with open('/Users/kevinmouritsen/python-projects/hively/hively/files/hively.csv', 'rb') as f:
    	reader = csv.reader(f)
    	hively_list = list(reader)
        return hively_list


def create_list_of_lists(hively_list):
    hively_data = []
    for item in hively_list:
    	hively_row = []
    	if item[4] == 'Points' or item[0] in NON_PS_SUPPORT_REPS:
    		continue
    	else:
    		if int(item[4]) > 0:
    			hively_row.append(1)
    		else:
    			hively_row.append(0)
    		hively_row.append(item[9][:-4])
    		hively_row.append(item[13])
    		hively_data.append(hively_row)
    return hively_data


def create_new_file(hively_data):
    with open('/Users/kevinmouritsen/python-projects/hively/hively/files/hively_data.csv', 'wb') as f:
	writer = csv.writer(f, delimiter='	')
	writer.writerows(hively_data)


def push_to_datahub(username, password, url):
    time.sleep(2)
    subprocess.call('curl --user '+username+':'+password+' --data-binary "@/Users/kevinmouritsen/python-projects/hively/hively/files/hively_data.csv" -H "Content-Type: application/octet-stream" -X PUT '+url+'  --insecure', shell=True)
    subprocess.call('killall -15 firefox', shell=True)
    print '\nFinished'

if __name__ == '__main__':
    url, username, password = get_creds()
    download_csv()
    date_data = get_today_date()
    move_and_rename_downloaded_csv(date_data)
    new_list = read_csv_data()
    hively_data = create_list_of_lists(new_list)
    create_new_file(hively_data)
    try:
        push_to_datahub(url=url, password=password, username=username)
    except IOError as e:
        print e
        time.sleep(5)
        push_to_datahub(url=url, password=password, username=username)
        