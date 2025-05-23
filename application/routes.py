from flask import Blueprint, jsonify
from . import db
from .models import StudyAbroad
import pandas as pd
import os

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return "API running"

@main.route('/cargar_csv', methods=['POST'])
def cargar_csv():
    path_csv = os.path.join(os.path.dirname(__file__), '..', 'data', 'dataset.csv')
    df = pd.read_csv(path_csv)

    # Normaliza los nombres de las columnas a minúsculas
    df.columns = df.columns.str.strip().str.lower()

    # print(df.columns.tolist())  # Útil para debug

    for _, row in df.iterrows():
        record = StudyAbroad(
            country=row['country'],
            city=row['city'],
            tuition=row['tuition_usd'],
            living_cost=row['living_cost_index'],
            total=row['tuition_usd'] + row['living_cost_index']  # O ajusta según tu modelo
        )
        db.session.add(record)

    db.session.commit()
    return jsonify({'status': 'Data loaded successfully'}), 201

@main.route('/data', methods=['GET'])
def get_data():
    records = StudyAbroad.query.all()
    result = [
        {
            'country': r.country,
            'city': r.city,
            'tuition': r.tuition,
            'living_cost': r.living_cost,
            'total': r.total
        } for r in records
    ]
    return jsonify(result)