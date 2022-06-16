import os
import pickle
import sqlite3
import datetime

import numpy as np
import tensorflow as tf

from flask import Flask, render_template, request, redirect
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/calculate', methods=["POST"])
def calculate():
    max_text = 600
    max_summary = 60
    text = request.form['text']
    summary = request.form['summary']
    date = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    with open('tokenizer.pkl', 'rb') as f:
        tokenizer = pickle.load(f)


    with sqlite3.connect('db.sqlite3') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM scores WHERE text=? AND summary=?", (text, summary))
        row = cursor.fetchone()
        if row is None:
            with tf.device('/cpu:0'):
                model = tf.keras.models.load_model('model.h5')
                text_seqs = tokenizer.texts_to_sequences([text])
                text_pad = pad_sequences(text_seqs, maxlen=max_text)

                summary_seqs = tokenizer.texts_to_sequences([summary])
                summary_pad = pad_sequences(summary_seqs, maxlen=max_summary)

                features = np.array([
                    [len(set(x1)), len(set(x2)), len(set(x1).intersection(x2))] for x1, x2 in zip(text_pad, summary_pad)
                ])

                score = float(model.predict([text_pad, summary_pad, features])[0, 0])

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
        
    app.run(host='127.0.0.1', port=8080, debug=True)