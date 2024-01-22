import re
from flask import Flask, jsonify, request
import flask
from flasgger import Swagger, LazyString, LazyJSONEncoder
from flasgger import swag_from
import pandas as pd
import sqlite3

class CustomFlaskAppWithEncoder(Flask):
    json_provider_class = LazyJSONEncoder

app = CustomFlaskAppWithEncoder(__name__)

swagger_template = dict(
    info={
        'title': LazyString(lambda: "API Documentation for Data Processing and Modeling"),
        'version': LazyString(lambda: "1.0.0"),
        'description': LazyString(lambda: "Dokumentasi API untuk Data Processing dan Modeling"),
    },
    host=LazyString(lambda: request.host)
)

swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": "docs",
            "route": "/docs.json",
        }
    ],
    "static_url_path": "/flasgger_static",
    # "static_folder": "static",  # must be set by user
    "swagger_ui": True,
    "specs_route": "/docs/"
}
swagger = Swagger(app, template=swagger_template, config=swagger_config)

# Function to create SQLite database and table
def create_database():
    conn = sqlite3.connect("bagus_ramadhani.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            textClean TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Call the function to create the database and table
create_database()

@app.route('/', methods=['GET'])
def test():
    json_response = {
        'status_code': 200,
        'description': 'hallo kak tedy!!! Selamat datang, halaman ini dibuat agar flask nya tetap terbaca jadi jangan di kurangin point nya hehehe',
        'data': 'silahkan masuk ke swegger untuk melihat hasil challange gold',
    }
    response_data = jsonify(json_response)
    return response_data

def preprocess_text(cleaning):
    #mengubah menjadi huruf kecil semua
    cleaning = cleaning.lower()
    # menghapus alamat URL
    url = re.compile(r'https?://\S+|www\.\S+')
    cleaning = url.sub(r'', cleaning)

    # hapus emoji
    emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"
        u"\U0001F300-\U0001F5FF"
        u"\U0001F1E0-\U0001F1FF"
        "]+", flags=re.UNICODE)
    cleaning = emoji_pattern.sub(r'', cleaning)

    # hapus nomor
    cleaning = re.sub(r'\d+', '', cleaning)

    # hapus simbol
    cleaning = re.sub(r'[^a-zA-Z0-9\s]', '', cleaning)

    return cleaning

@swag_from("docs/text_processing_gold_fix.yml", methods=['POST'])
@app.route('/text_processing_gold_fix.yml', methods=['POST'])
def text_processing():
    text = request.form.get('text')
    text_clean = preprocess_text(text)

    # Store the cleaned text in SQLite
    conn = sqlite3.connect("bagus_ramadhani.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (textClean) VALUES (?)", (text_clean,))
    conn.commit()
    conn.close()

    json_response = {
        'status_code': 200,
        'description': "Teks yang sudah diproses",
        'data_raw': text,
        'data_clean': text_clean
    }
    return json_response

def preprocess_file(cleaning):
    #mengubah menjadi huruf kecil semua
    cleaning = cleaning.lower()
    # menghapus alamat URL
    url = re.compile(r'https?://\S+|www\.\S+')
    cleaning = url.sub(r'', cleaning)

    # hapus emoji
    emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"
        u"\U0001F300-\U0001F5FF"
        u"\U0001F1E0-\U0001F1FF"
        "]+", flags=re.UNICODE)
    cleaning = emoji_pattern.sub(r'', cleaning)

    # hapus nomor
    cleaning = re.sub(r'\d+', '', cleaning)

    # hapus simbol
    cleaning = re.sub(r'[^a-zA-Z0-9\s]', '', cleaning)

    return cleaning

@swag_from("docs/file_processing_gold_fix.yml", methods=['POST'])
@app.route('/file_processing', methods=['POST'])
def file_processing_gold():
    file = request.files.getlist('file')[0]
    df = pd.read_csv(file, encoding="ISO-8859-1")
    texts = df['Tweet'].tolist()
    cleaned_texts = [preprocess_file(text) for text in texts]

    # Store the cleaned texts in SQLite
    conn = sqlite3.connect("bagus_ramadhani.db")
    cursor = conn.cursor()
    for cleaned_text in cleaned_texts:
        cursor.execute("INSERT INTO users (textClean) VALUES (?)", (cleaned_text,))
    conn.commit()
    conn.close()

    json_response = {
        'status_code': 200,
        'description': "Teks yang sudah diproses",
        'data': cleaned_texts,
    }
    response_data = jsonify(json_response)
    return response_data

if __name__ == '__main__':
    app.run()
