import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from flask import Blueprint, jsonify, render_template, request, redirect, url_for
from . import db
from .models import StudyAbroad
import pandas as pd
import os
import numpy as np
import seaborn as sns
import json

main = Blueprint('main', __name__)


@main.route('/', methods=['GET', 'POST'])
def index():
    from flask import flash

    records = StudyAbroad.query.all()

    paises = sorted({r.country for r in records if r.country})
    programas = sorted({r.program for r in records if r.program})

    combinaciones = {}
    for r in records:
        pais = r.country
        prog = r.program
        dur = r.duration
        if pais not in combinaciones:
            combinaciones[pais] = {"programas": set(), "duraciones": set()}
        combinaciones[pais]["programas"].add(prog)
        combinaciones[pais]["duraciones"].add(float(dur))

    for pais in combinaciones:
        combinaciones[pais]["programas"] = list(combinaciones[pais]["programas"])
        combinaciones[pais]["duraciones"] = list(combinaciones[pais]["duraciones"])

    df_minimos = pd.DataFrame([{
        "Country": r.country,
        "Total_Cost": r.tuition + r.rent + r.visa_fee + r.insurance
    } for r in records if r.tuition and r.rent and r.visa_fee and r.insurance])
    minimos_por_pais = df_minimos.groupby("Country")["Total_Cost"].min().round(0).astype(int).to_dict()

    if request.method == 'POST':
        presupuesto = request.form.get('presupuesto', type=float)
        pais = request.form.get('pais')
        duracion = request.form.get('duracion', type=float)
        programa = request.form.get('programa')

        if pais:
            if presupuesto and presupuesto < minimos_por_pais.get(pais, 0):
                flash(f'El presupuesto mínimo para {pais} es USD {minimos_por_pais[pais]}.', 'danger')
                return render_template('index.html', paises=paises, programas=programas, minimos=minimos_por_pais, combinaciones=combinaciones)

            if programa and programa not in combinaciones.get(pais, {}).get('programas', []):
                flash(f'El programa "{programa}" no está disponible en {pais}.', 'danger')
                return render_template('index.html', paises=paises, programas=programas, minimos=minimos_por_pais, combinaciones=combinaciones)

            if duracion and duracion not in combinaciones.get(pais, {}).get('duraciones', []):
                flash(f'No se ofrecen programas con duración de {duracion} años en {pais}.', 'danger')
                return render_template('index.html', paises=paises, programas=programas, minimos=minimos_por_pais, combinaciones=combinaciones)

        return redirect(url_for('main.recomendaciones', presupuesto=presupuesto, pais=pais, duracion=duracion, programa=programa))

    return render_template('index.html',
                           paises=paises,
                           programas=programas,
                           minimos=json.dumps(minimos_por_pais),
                           combinaciones=json.dumps(combinaciones))


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
    
    pais_promedio = df.groupby('Country')['Total_Cost'].mean().sort_values(ascending=False).head(10)
    plt.figure(figsize=(10, 6))
    pais_promedio.plot(kind='bar', color='royalblue')
    plt.ylabel('Costo Promedio Total (USD)')
    plt.title('Top 10 Países con Mayor Costo Promedio')
    plt.tight_layout()
    plt.savefig(os.path.join(static_dir, 'paises_mas_caros.png'))
    plt.close()

    
    pais_mas_baratos = df.groupby('Country')['Total_Cost'].mean().sort_values().head(10)
    plt.figure(figsize=(10, 6))
    pais_mas_baratos.plot(kind='bar', color='mediumseagreen')
    plt.ylabel('Costo Promedio Total (USD)')
    plt.title('Top 10 Países con Menor Costo Promedio')
    plt.tight_layout()
    plt.savefig(os.path.join(static_dir, 'paises_mas_baratos.png'))
    plt.close()

    
    duracion_mayor_paises = df.groupby('Country')['Duration_Years'].mean().sort_values(ascending=False).head(10)
    plt.figure(figsize=(10, 6))
    duracion_mayor_paises.plot(kind='barh', color='slateblue')
    plt.xlabel('Duración Promedio (años)')
    plt.title('Top 10 Países con Mayor Duración Promedio')
    plt.tight_layout()
    plt.savefig(os.path.join(static_dir, 'duracion_mas_larga.png'))
    plt.close()

    
    duracion_menor_paises = df.groupby('Country')['Duration_Years'].mean().sort_values().head(10)
    plt.figure(figsize=(10, 6))
    duracion_menor_paises.plot(kind='barh', color='lightcoral')
    plt.xlabel('Duración Promedio (años)')
    plt.title('Top 10 Países con Menor Duración Promedio')
    plt.tight_layout()
    plt.savefig(os.path.join(static_dir, 'duracion_mas_corta.png'))
    plt.close()

    programas_unicos_por_pais = df.groupby('Country')['Program'].nunique().sort_values(ascending=False).head(10)
    plt.figure(figsize=(10, 6))
    programas_unicos_por_pais.plot(kind='bar', color='darkorange')
    plt.title('Top 10 Países con Mayor Variedad de Programas')
    plt.ylabel('Cantidad de Programas Únicos')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(os.path.join(static_dir, 'paises_mas_variedad_programas.png'))
    plt.close()

    costo_por_pais = df.groupby('Country')['Total_Cost'].mean()
    pais_mas_economico = costo_por_pais.idxmin()
    costo_min_promedio = round(costo_por_pais.min(), 2)


    programas_por_pais = df.groupby('Country')['Program'].nunique()
    pais_mayor_variedad = programas_por_pais.idxmax()
    cantidad_programas = programas_por_pais.max()

    return render_template(
        'dashboard.html',
        data=data,
        promedio_total=promedio_total,
        universidad_max=universidad_max,
        duracion_promedio=duracion_promedio,
        pais_mas_economico=pais_mas_economico,
        costo_min_promedio=costo_min_promedio,
        pais_mayor_variedad=pais_mayor_variedad,
        cantidad_programas=cantidad_programas
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

@main.route('/recomendaciones')
def recomendaciones():

    presupuesto = request.args.get('presupuesto', type=float)
    pais = request.args.get('pais', default=None)
    duracion = request.args.get('duracion', type=float)
    programa = request.args.get('programa', default=None)

    
    records = StudyAbroad.query.all()
    data = [{
        'University': r.university,
        'Country': r.country,
        'City': r.city,
        'Program': r.program,
        'Tuition_USD': r.tuition,
        'Rent_USD': r.rent,
        'Visa_Fee_USD': r.visa_fee,
        'Insurance_USD': r.insurance,
        'Duration_Years': r.duration,
        'Level': r.level
    } for r in records]

    df = pd.DataFrame(data)
    df['Total_Cost'] = df[['Tuition_USD', 'Rent_USD', 'Visa_Fee_USD', 'Insurance_USD']].sum(axis=1)

    df_pais = pd.DataFrame()
    if pais and presupuesto:
        df_pais = df[df['Country'].str.lower() == pais.lower()]
        if not df_pais.empty:
            costo_minimo = df_pais['Total_Cost'].min()
            if presupuesto < costo_minimo:
                return render_template(
                'recomendaciones.html',
                resultados=[],
                alerta=f'El presupuesto ingresado es demasiado bajo para {pais}. El mínimo registrado es USD {round(costo_minimo, 2)}.',
                presupuesto=presupuesto,
                pais=pais,
                duracion=duracion
            )


    if presupuesto:
        df = df[df['Total_Cost'] <= presupuesto]
    if duracion:
        df = df[df['Duration_Years'] <= duracion]
    if pais:
        df = df[df['Country'].str.lower() == pais.lower()]
    if programa:
        df = df[df['Program'].str.lower() == programa.lower()]

    df = df.drop_duplicates(subset=['University', 'Program', 'City', 'Country', 'Duration_Years', 'Total_Cost'])

    resultados = df.sort_values(by='Total_Cost').to_dict(orient='records')

    static_dir = os.path.join(os.path.dirname(__file__), 'static')
    os.makedirs(static_dir, exist_ok=True)

    if not df.empty:
        plt.figure(figsize=(10, 6))
        sns.barplot(data=df.sort_values('Total_Cost').head(10), x='Total_Cost', y='University', palette='viridis')
        plt.title('Universidades más accesibles según tus filtros')
        plt.xlabel('Costo Total (USD)')
        plt.tight_layout()
        plt.savefig(os.path.join(static_dir, 'reco_bar_universidades.png'))
        plt.close()

    if not df.empty and 'Duration_Years' in df.columns and 'Total_Cost' in df.columns:
        plt.figure(figsize=(8, 6))
        sns.scatterplot(data=df, x='Duration_Years', y='Total_Cost', hue='Country', palette='Set2', s=80)
        plt.title('Duración vs. Costo Total (Universidades filtradas)')
        plt.xlabel('Duración (años)')
        plt.ylabel('Costo Total (USD)')
        plt.tight_layout()
        plt.savefig(os.path.join(static_dir, 'reco_scatter_duracion_costo.png'))
        plt.close()

    componentes = ['Tuition_USD', 'Rent_USD', 'Visa_Fee_USD', 'Insurance_USD']
    if all(c in df.columns for c in componentes):
        costos = df[componentes].mean().tolist()
        costos += costos[:1]
        labels = componentes
        angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
        angles += angles[:1]

        fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
        ax.plot(angles, costos, color='teal')
        ax.fill(angles, costos, alpha=0.25)
        ax.set_thetagrids(np.degrees(angles[:-1]), labels)
        plt.title("Promedio de Componentes de Costo")
        plt.tight_layout()
        plt.savefig(os.path.join(static_dir, 'reco_radar_costos.png'))
        plt.close()

    if 'Duration_Years' in df.columns and (df['Duration_Years'] > 0).all():
        df['Monthly_Cost'] = df['Total_Cost'] / (df['Duration_Years'] * 12)
        plt.figure(figsize=(12, 8))
        sns.barplot(data=df.sort_values('Monthly_Cost').head(10), x='Monthly_Cost', y='University', palette='coolwarm')
        plt.title('Costo mensual estimado por universidad')
        plt.xlabel('Costo mensual (USD)')
        plt.tight_layout()
        plt.savefig(os.path.join(static_dir, 'reco_costo_mensual.png'))
        plt.close()

    if not df.empty:
        df_stacked = df.set_index('University')[['Tuition_USD', 'Rent_USD', 'Visa_Fee_USD', 'Insurance_USD']]
        if not df_stacked.empty:
            df_stacked.plot(kind='barh', stacked=True, figsize=(18, 10), colormap='tab20')
            plt.title('Composición del costo total por universidad')
            plt.xlabel('Costo Total (USD)')
            plt.tight_layout()
            plt.savefig(os.path.join(static_dir, 'reco_costos_stacked.png'))
            plt.close()

    if 'Total_Cost' in df.columns and not df['Total_Cost'].isnull().all():
        plt.figure(figsize=(8, 5))
        sns.histplot(df['Total_Cost'], bins=10, kde=True, color='slateblue')
        plt.title('Distribución del Costo Total')
        plt.xlabel('Costo Total (USD)')
        plt.ylabel('Cantidad de Universidades')
        plt.tight_layout()
        plt.savefig(os.path.join(static_dir, 'reco_histograma_costo.png'))
        plt.close()

    if 'Program' in df.columns and not df['Program'].isnull().all():
        program_counts = df['Program'].value_counts(normalize=True)
        main_programs = program_counts[program_counts >= 0.03]
        others_sum = program_counts[program_counts < 0.03].sum()
        new_programs = main_programs.copy()
        if others_sum > 0:
            new_programs['Otros'] = others_sum

        plt.figure(figsize=(7, 7))
        new_programs.plot.pie(autopct='%1.1f%%', startangle=140)
        plt.title('Distribución por Programa Académico')
        plt.ylabel('')
        plt.tight_layout()
        plt.savefig(os.path.join(static_dir, 'reco_torta_programas.png'))
        plt.close()

    if not df.empty:
        plt.figure(figsize=(10, 6))
        df.groupby('Program')['Total_Cost'].mean().sort_values().head(10).plot(kind='bar', color='darkcyan')
        plt.title('Top 10 Programas más Económicos')
        plt.ylabel('Costo Promedio (USD)')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.savefig(os.path.join(static_dir, 'reco_programas_mas_economicos.png'))
        plt.close()

    if not df.empty:
        plt.figure(figsize=(10, 6))
        df.groupby('Program')['Duration_Years'].mean().sort_values(ascending=False).head(10).plot(kind='bar', color='mediumpurple')
        plt.title('Top 10 Programas más Largos')
        plt.ylabel('Duración Promedio (años)')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.savefig(os.path.join(static_dir, 'reco_programas_mas_largos.png'))
        plt.close()

    return render_template('recomendaciones.html',
                           resultados=resultados,
                           presupuesto=presupuesto,
                           pais=pais,
                           duracion=duracion)