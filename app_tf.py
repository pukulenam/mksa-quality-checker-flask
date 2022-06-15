import pickle
import sqlite3
import datetime

import numpy as np
import tensorflow as tf

from flask import Flask, render_template, request
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/calculate', methods=["POST"])
def calculate():
    text = request.form['text']
    summary = request.form['summary']
    date = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    model = tf.keras.models.load_model('model.h5')
    with open('tokenizer.pkl', 'rb') as f:
        tokenizer = pickle.load(f)

    max_text = 600
    max_summary = 60
    
    text_seqs = tokenizer.texts_to_sequences([text])
    summary_seqs = tokenizer.texts_to_sequences([summary])

    text_pad = pad_sequences(text_seqs, maxlen=max_text)
    summary_pad = pad_sequences(summary_seqs, maxlen=max_summary)

    features = np.array([
        [len(set(x1)), len(set(x2)), len(set(x1).intersection(x2))] for x1, x2 in zip(text_pad, summary_pad)
    ])

    score = model.predict([text_pad, summary_pad, features])[0, 0]
    
    return render_template('index.html', score=score, text=text, summary=summary, date=date)

if __name__ == '__main__':
    app.run()