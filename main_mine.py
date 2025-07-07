import streamlit as st
import plotly.express as px
import pandas as pd
from threading import Thread
import sqlite3 # built in library
import os
import time
from datetime import datetime
import requests
import smtplib
import ssl
import selectorlib


URL = "https://programmer100.pythonanywhere.com/tours/"

# adding a headers variable to put into the requests.get() as the argument for the "headers" parameter
# did that since I was getting a return of "Edge: Too Many Requests"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

class Event:
    def scrape(self, url=URL, headers=HEADERS):
        response = requests.get(url ,headers = headers)
        source_text =  response.text
        return source_text

    # print(scrape(URL))

    def extract(self, source):
        extractor = selectorlib.Extractor.from_yaml_file("extract.yaml")
        value = extractor.extract(source)["tours"]
        return value


class Email:
    def send(self, message, username= "automated.huzaifaar2003@gmail.com"):
        host = "smtp.gmail.com"  # NOT "smtp@gmail.com"
        port = 465
        #username = "automated.huzaifaar2003@gmail.com"
        password = os.getenv("PASSWORD")
        receiver = "automated.huzaifaar2003@gmail.com"
        context = ssl.create_default_context()
        #message = message
        with smtplib.SMTP_SSL(host=host, port=port, context=context) as server:
            # explicit declaration of "context" argument because argument order wasn't followed
            server.login(username, password)
            server.sendmail(username, receiver, message)
        print("Email alert sent!\n\n\n")


class DatabaseTemps:
    def __init__(self):
        if os.path.exists("temps.db"):
            self.connection = sqlite3.connect("temps.db")
            # "self." has to be added before "connection =sqlite3......."
            # so self.connection = sqlite3.connect("temps.db")
            cursor = self.connection.cursor()
            # same here:  cursor = self.connection.cursor()
        else:
            with open("temps.db", "w") as file:
                file.write("")
            self.connection = sqlite3.connect("temps.db", check_same_thread=False)
            cursor = self.connection.cursor()
            cursor.execute('CREATE TABLE "temperatures" ("temp" INTEGER, "date" TEXT);')
            self.connection.commit()


    def store_db(self, value):  # value arrives as an integer
        now = datetime.now()
        currently = now.strftime('%Y-%m-%d %H-%M-%S')
        temp = value
        tpl = (temp, currently)

        cursor = self.connection.cursor()  # establishes connection
        cursor.execute("INSERT INTO temperatures VALUES (?,?)", (currently, temp))
        self.connection.commit()
        return tpl

    def read_db(self):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM temperatures")
        results = cursor.fetchall()
        self.connection.close()
        return results

class DatabaseEvents:
    def __init__(self):
        if os.path.exists("data.db"):
            self.connection = sqlite3.connect("data.db")
            # "self." has to be added before "connection =sqlite3......."
            # so self.connection = sqlite3.connect("temps.db")
            cursor = self.connection.cursor()
            # same here:  cursor = self.connection.cursor()
        else:
            with open("data.db", "w") as file:
                file.write("")
            self.connection = sqlite3.connect("data.db", check_same_thread=False)
            cursor = self.connection.cursor()
            cursor.execute('CREATE TABLE "events" ("band" TEXT, "city" TEXT, "date" TEXT);')
            self.connection.commit()

    def store_db(self, extracted):
        row = extracted.split(",")
        row = [item.strip() for item in row]
        cursor = self.connection.cursor()
        cursor.execute("INSERT INTO events VALUES(?,?,?)", row)
        self.connection.commit()

    def read_db_conditional(self, extracted):
        row = extracted.split(",")
        row = [item.strip() for item in row]
        band, city, date = row
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM events WHERE band=? AND city=? AND date=?", (band, city, date))
        rows = cursor.fetchall()
        print(rows)
        return rows

    def read_db(self):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM events")
        results = cursor.fetchall()
        self.connection.close()
        return results

# event = Event() # instantiate an object of class Event()
# source_text = event.scrape() # using the .scrape() method of the Event class to extract source text (the HTML as text)
# value = event.extract(source_text) # extracting only the relevant value from the source text
#
# db = Database() # instantiating an object of class Database()
# db.store_db(value) # storing the value extracting from webpage into the database
# db_values = db.read_db() # reading the database and storing the returned value(s) (list of tuples)
# print(db_values) # printing the returned value(s)




if __name__ == "__main__":
    list_values = []
    while True:
        event = Event()
        scraped = event.scrape(URL)
        extracted_value = event.extract(scraped)
        print(extracted_value)

        if extracted_value != "No upcoming tours":
            db = DatabaseEvents()
            if extracted_value not in list_values:
                list_values.append(extracted_value)
                db.store_db(extracted_value)
                print(db.read_db_conditional(extracted_value))
                print(db.read_db())
                email = Email()
                email.send(message="Hey, new event was found!")
            time.sleep(2)
