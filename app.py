import sqlite3
import datetime

from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/calculate', methods=["POST"])
def calculate():
    text = request.form['text']
    summary = request.form['summary']
    date = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")

    sql = sqlite3.connect('db.sqlite3')
    cursor = sql.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS scores (text TEXT, summary TEXT, date TEXT, score REAL)")
    cursor.execute("INSERT INTO scores (text, summary, date, score) VALUES (?, ?, ?, ?)", (text, summary, date, 100))
    sql.commit()
    sql.close()

    return render_template('index.html', score=100, text=text, summary=summary, date=date)

@app.route('/scores')
def scores():
    sql = sqlite3.connect('db.sqlite3')
    cursor = sql.cursor()
    cursor.execute("SELECT * FROM scores")
    rows = cursor.fetchall()
    sql.close()

    return render_template('scores.html', rows=rows)

if __name__ == '__main__':
    app.run(debug=True)