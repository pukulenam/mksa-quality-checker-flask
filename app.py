import os
import sqlite3
import datetime

from flask import Flask, render_template, request, redirect

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/calculate', methods=["POST"])
def calculate():
    text = request.form['text']
    summary = request.form['summary']
    date = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")

    with sqlite3.connect('db.sqlite3') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM scores WHERE text=? AND summary=?", (text, summary))
        row = cursor.fetchone()
        if row is None:
            score = 50
            cursor.execute("INSERT INTO scores (text, summary, date, score) VALUES (?, ?, ?, ?)", (text, summary, date, score))
            conn.commit()
        else:
            score = row[3]

    return render_template('index.html', score=score, text=text, summary=summary, date=date)

@app.route('/scores')
def scores():
    with sqlite3.connect('db.sqlite3') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM scores")
        rows = cursor.fetchall()

    return render_template('scores.html', rows=rows)

@app.route('/delete', methods=["POST"])
def delete():
    date = list(request.form.keys())[0]
    with sqlite3.connect('db.sqlite3') as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM scores WHERE date=?", (date,))
        conn.commit()

    return redirect('/scores')

if __name__ == '__main__':
    if not os.path.exists('db.sqlite3'):
        with open('db.sqlite3', 'w') as f:
            pass

    with sqlite3.connect('db.sqlite3') as conn:
        cursor = conn.cursor()    
        cursor.execute("CREATE TABLE IF NOT EXISTS scores (text TEXT, summary TEXT, date TEXT, score REAL)")
        conn.commit()

    app.run(debug=True)