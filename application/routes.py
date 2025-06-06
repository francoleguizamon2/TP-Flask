import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from flask import Blueprint, jsonify, render_template, request, redirect, url_for
from . import db
from .models import StudyAbroad
import pandas as pd
import os

main = Blueprint('main', __name__)


@main.route('/')
def index():
    return render_template('index.html')


@main.route('/upload_csv', methods=['POST'])
def upload_csv():
    file = request.files['csv_file']
    if not file:
        return "No file uploaded", 400

    df = pd.read_csv(file)
    df.columns = df.columns.str.strip()

    for _, row in df.iterrows():
        record = StudyAbroad(
            country=row['Country'],
            city=row['City'],
            university=row['University'],
            program=row['Program'],
            level=row['Level'],
            duration=row['Duration_Years'],
            tuition=row['Tuition_USD'],
            rent=row['Rent_USD'],
            living_cost=row['Living_Cost_Index'],
            visa_fee=row['Visa_Fee_USD'],
            insurance=row['Insurance_USD'],
            exchange_rate=row['Exchange_Rate']
        )
        db.session.add(record)

    db.session.commit()
    return redirect(url_for('main.dashboard'))


@main.route('/upload', methods=['GET'])
def upload_form():
    return render_template('upload.html')


@main.route('/dashboard')
def dashboard():
    records = StudyAbroad.query.all()
    if not records:
        return render_template('data_table.html', data=[])

    data = [{
        'Country': r.country,
        'City': r.city,
        'University': r.university,
        'Program': r.program,
        'Level': r.level,
        'Duration_Years': r.duration,
        'Tuition_USD': r.tuition,
        'Rent_USD': r.rent,
        'Living_Cost_Index': r.living_cost,
        'Visa_Fee_USD': r.visa_fee,
        'Insurance_USD': r.insurance,
        'Exchange_Rate': r.exchange_rate
    } for r in records]

    df = pd.DataFrame(data)
    df['Total_Cost'] = df[['Tuition_USD', 'Rent_USD', 'Visa_Fee_USD', 'Insurance_USD']].sum(axis=1)

    promedio_total = round(df['Total_Cost'].mean(), 2)
    universidad_max = df.loc[df['Total_Cost'].idxmax(), 'University']
    duracion_promedio = round(df['Duration_Years'].mean(), 1)

    static_dir = os.path.join(os.path.dirname(__file__), 'static')
    os.makedirs(static_dir, exist_ok=True)

    # Top 5 universidades más costosas
    top5_costosas = df.groupby('University')['Total_Cost'].mean().sort_values(ascending=False).head(5).reset_index()
    plt.figure(figsize=(10, 6))
    top5_costosas = top5_costosas.iloc[::-1]
    plt.bar(top5_costosas['University'], top5_costosas['Total_Cost'], color='tomato', width=1, edgecolor='black')

    # Set y-axis limits to zoom in on the range of your data
    min_cost = top5_costosas['Total_Cost'].min()
    max_cost = top5_costosas['Total_Cost'].max()
    plt.ylim(min_cost * 0.98, max_cost * 1.01)  # Adjust the factors as needed

    plt.ylabel('Costo Total Promedio (USD)')
    plt.xlabel('Universidad')
    plt.title('Top 5 Universidades Más Costosas')
    plt.tight_layout()
    plt.savefig(os.path.join(static_dir, 'top5_costosas.png'))
    plt.close()

    # Top 5 universidades más baratas
    top5_baratas = df.groupby('University')['Total_Cost'].mean().sort_values().head(5).reset_index()
    plt.figure(figsize=(10, 6))
    plt.barh(top5_baratas['University'], top5_baratas['Total_Cost'], color='seagreen')
    plt.xlabel('Costo Total Promedio (USD)')
    plt.title('Top 5 Universidades Más Baratas')
    plt.tight_layout()
    plt.savefig(os.path.join(static_dir, 'top5_baratas.png'))
    plt.close()

    # Top 10 países con mayor costo promedio
    pais_promedio = df.groupby('Country')['Total_Cost'].mean().sort_values(ascending=False).head(10)
    plt.figure(figsize=(10, 6))
    pais_promedio.plot(kind='bar', color='royalblue')
    plt.ylabel('Costo Promedio Total (USD)')
    plt.title('Top 10 Países con Mayor Costo Promedio')
    plt.tight_layout()
    plt.savefig(os.path.join(static_dir, 'paises_mas_caros.png'))
    plt.close()

    # Top 10 países con menor costo promedio
    pais_mas_baratos = df.groupby('Country')['Total_Cost'].mean().sort_values().head(10)
    plt.figure(figsize=(10, 6))
    pais_mas_baratos.plot(kind='bar', color='mediumseagreen')
    plt.ylabel('Costo Promedio Total (USD)')
    plt.title('Top 10 Países con Menor Costo Promedio')
    plt.tight_layout()
    plt.savefig(os.path.join(static_dir, 'paises_mas_baratos.png'))
    plt.close()

    # Universidades con mayor duración promedio
    duracion_mayor = df.groupby('University')['Duration_Years'].mean().sort_values(ascending=False).head(10)
    plt.figure(figsize=(10, 6))
    duracion_mayor.plot(kind='barh', color='slateblue')
    plt.xlabel('Duración Promedio (años)')
    plt.title('Top 10 Universidades con Mayor Duración')
    plt.tight_layout()
    plt.savefig(os.path.join(static_dir, 'duracion_mas_larga.png'))
    plt.close()

    # Universidades con menor duración promedio
    duracion_menor = df.groupby('University')['Duration_Years'].mean().sort_values().head(10)
    plt.figure(figsize=(10, 6))
    duracion_menor.plot(kind='barh', color='lightcoral')
    plt.xlabel('Duración Promedio (años)')
    plt.title('Top 10 Universidades con Menor Duración')
    plt.tight_layout()
    plt.savefig(os.path.join(static_dir, 'duracion_mas_corta.png'))
    plt.close()

    return render_template(
        'dashboard.html',
        data=data,
        promedio_total=promedio_total,
        universidad_max=universidad_max,
        duracion_promedio=duracion_promedio
    )

@main.route('/data_table')
def data_table():
    records = StudyAbroad.query.all()
    if not records:
        return render_template('data_table.html', data=[])

    data = [{
        'Country': r.country,
        'City': r.city,
        'University': r.university,
        'Program': r.program,
        'Level': r.level,
        'Duration_Years': r.duration,
        'Tuition_USD': r.tuition,
        'Rent_USD': r.rent,
        'Living_Cost_Index': r.living_cost,
        'Visa_Fee_USD': r.visa_fee,
        'Insurance_USD': r.insurance,
        'Exchange_Rate': r.exchange_rate
    } for r in records]

    return render_template('data_table.html', data=data)