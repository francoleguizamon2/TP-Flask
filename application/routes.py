from flask import Blueprint, jsonify, render_template, request
from . import db
from .models import StudyAbroad
import pandas as pd
import os

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return "API running"

@main.route('/upload_csv', methods=['POST'])
def upload_csv():
    file = request.files['csv_file']
    if not file:
        return "No file uploaded", 400

    import pandas as pd
    from .models import StudyAbroad

    df = pd.read_csv(file)
    df.columns = df.columns.str.strip()

    # OPCIONAL: print(df.columns.tolist()) para ver las columnas reales

    for _, row in df.iterrows():
        record = StudyAbroad(
            country=row['Country'],
            city=row['City'],
            tuition=row['Tuition_USD'],
            living_cost=row['Living_Cost_Index'],
        )
        db.session.add(record)

    db.session.commit()
    return jsonify({'status': 'Upload and insertion successful'}), 201

@main.route('/upload', methods=['GET'])
def upload_form():
    return render_template('upload.html')