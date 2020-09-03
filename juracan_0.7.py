#!/usr/bin/env python3
# JURACAN 0.7 by teehay

# A Python(3) script that uses Firefox and Selenium to search the Hurricane Electric Internet Services website for a keyword and output
# or store the results. Please do not abuse the service by spamming requests.

# Current feature priorities:
#     EXCEPTION HANDLING!!
#     Handle commas in csv data

from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as expected
from selenium.webdriver.support.wait import WebDriverWait
from bs4 import BeautifulSoup
import argparse
import sys
import mysql.connector
import sqlite3

if __name__ == "__main__":

    ## Handle args
    parser = argparse.ArgumentParser(description='Gets ASN and ISP addresses related to the target keyword from the Hurricane Electric Internet Services website. Please do not abuse this service!')
    parser.add_argument('keyword', metavar='keyword', type=str, nargs='?', help='target keyword')
    parser.add_argument('-s', '--sqlite',  metavar=('dbpath', 'tablename'), \
    nargs=2, help="store results in a SQLite database; creates a new database and table if they don't already exist")
    parser.add_argument('-m', '--mysql',  metavar=('host', 'dbname', 'tblname', 'user', 'password'),\
    nargs=5, help="store results in a MySQL database; creates a new database and table if they don't exist" )
    parser.add_argument('-c', '--csv', action='store_true', \
    help="output table data as a CSV list")
    parser.add_argument('-r', '--result', action='store_true', \
    help="output the result column data only; if --csv is on, result column data is output as a CSV list")


    if len(sys.argv) < 2:
        parser.print_usage()
        sys.exit(1)
    else:
        arg = parser.parse_args()

    ## Set up WebDriver
    options = Options()
    options.add_argument('-headless')

    driver = Firefox(executable_path='/usr/bin/geckodriver', options=options)
    wait = WebDriverWait(driver, timeout=10)
    driver.get('https://bgp.he.net')

    ## Perform search and wait for results to populate
    wait.until(expected.presence_of_element_located((By.NAME, 'search[search]'))).send_keys(arg.keyword + Keys.ENTER)
    wait.until(expected.element_to_be_clickable((By.NAME, 'commit'))).click()
    wait.until(expected.presence_of_element_located((By.TAG_NAME, 'table')))

    ## Set up BeautifulSoup and find individual results
    soup = BeautifulSoup(driver.page_source, 'lxml')
    results = soup.find_all('tr')

    ## Set up databases
    if arg.sqlite:
        sqliteconn = sqlite3.connect(arg.sqlite[0])
        c = sqliteconn.cursor()
        if arg.csv:
            c.execute("CREATE TABLE IF NOT EXISTS " + arg.sqlite[1] + " (csv TEXT PRIMARY KEY)")
        else:
            c.execute("CREATE TABLE IF NOT EXISTS " + arg.sqlite[1] + " (result TEXT PRIMARY KEY, description TEXT, country TEXT)")

    if arg.mysql:
        mysqlconn = mysql.connector.connect(host=arg.mysql[0], user=arg.mysql[3], password=arg.mysql[4])
        if mysqlconn.is_connected():
            cur = mysqlconn.cursor()
            cur.execute("CREATE DATABASE IF NOT EXISTS " + arg.mysql[1])
            cur.execute("USE " + arg.mysql[1])
            if arg.csv:
                cur.execute("CREATE TABLE IF NOT EXISTS " + arg.mysql[2] + " (csv LONGTEXT)")
            else:
                cur.execute("CREATE TABLE IF NOT EXISTS " + arg.mysql[2] + " (result VARCHAR(192) PRIMARY KEY, description VARCHAR(256), country VARCHAR(128))")

    csvlist = []

    ## Cycle through results and print header, then results in formatted form
    for i in range(1, len(results)):
        if i == 1 and not arg.csv and not arg.result:
            print("Keyword: " + results[i].a.string)
            print(f"{'Results:':<44}{'Description:':<48}{'Country:':<16}")
        elif i > 1:
            data = results[i].find_all('td')

            res = data[0].get_text()
            desc = data[1].get_text()
            country = data[1].div.img['title']

            if arg.csv and arg.result:
                csvlist.append(res)
            elif arg.csv and not arg.result:
                if ',' in desc:
                    desc = "\"" + desc + "\""
                csvlist.extend([res, desc, country])
            elif not arg.csv and arg.result:
                print(f"{res:<44}")
            else:
                print(f"{res:<44}{desc:<48}{country:<16}")

            ## Handle database insertion
            if arg.sqlite:
                if arg.result and not arg.csv:
                    c.execute("INSERT INTO " + arg.sqlite[1] + " (result) VALUES (?)", (res,))
                elif not arg.result and not arg.csv:
                    c.execute("INSERT INTO " + arg.sqlite[1] + " (result, description, country) VALUES (?, ?, ?)", (res, desc, country))
                elif arg.csv and i == len(results) - 1:
                    c.execute("INSERT INTO " + arg.sqlite[1] + " (csv) VALUES (?)", (','.join(csvlist),))
            if arg.mysql:
                if arg.result and not arg.csv:
                    cur.execute("INSERT INTO " + arg.mysql[2] + " (result) VALUES (%s)",(res,))
                elif not arg.result and not arg.csv:
                    cur.execute("INSERT INTO " + arg.mysql[2] + " (result, description, country) VALUES (%s, %s, %s)", (res, desc, country))
                elif arg.csv and i == len(results) - 1:
                    cur.execute("INSERT INTO " + arg.mysql[2] + " (csv) VALUES (%s)", (','.join(csvlist),))

    if arg.csv:
        print(','.join(csvlist))

    ## Close db connections
    if arg.sqlite:
        sqliteconn.commit()
        sqliteconn.close() 
    if arg.mysql:
        mysqlconn.commit()
        mysqlconn.close()

    ## Close WebDriver
    driver.quit()
