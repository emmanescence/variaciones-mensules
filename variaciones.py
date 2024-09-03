import streamlit as st
import pandas as pd
import yfinance as yf

def get_monthly_returns(ticker):
    data = yf.download(ticker, start='2004-01-01', end='2024-8-25', progress=False)
    monthly_data = data['Adj Close'].resample('M').last()
    monthly_returns = monthly_data.pct_change() * 100
    matrix = monthly_returns.to_frame().reset_index()
    matrix['Year'] = matrix['Date'].dt.year
    matrix['Month'] = matrix['Date'].dt.month
    pivot_matrix = matrix.pivot(index='Year', columns='Month', values='Adj Close')
    return pivot_matrix

def create_combined_matrix(tickers, selected_months=None):
    # Obtener las matrices de variaciones mensuales para todos los tickers
    matrices = [get_monthly_returns(ticker) for ticker in tickers]

    # Filtrar para los últimos 20 años
    matrices = [matrix[-30:] for matrix in matrices]

    # Combinar las matrices en una sola
    combined_matrix = pd.concat(matrices, axis=1, keys=tickers)

    # Renombrar columnas para que tengan nombres de mes
    combined_matrix.columns = [f'{month}_{ticker}' for ticker in tickers for month in combined_matrix.columns.levels[1]]

    # Filtrar para los meses seleccionados si se especifican
    if selected_months is not None:
        selected_columns = [col for col in combined_matrix.columns if int(col.split('_')[0]) in selected_months]
        combined_matrix_filtered = combined_matrix[selected_columns]
    else:
        combined_matrix_filtered = combined_matrix

    # Convertir los valores a cadena con formato de coma decimal
    combined_matrix_formatted = combined_matrix_filtered.applymap(lambda x: f"{x:,.2f}".replace('.', ','))

    return combined_matrix_formatted

# Función para asignar colores en una escala de rojo a verde y ajustar el color del texto
def color_map(val):
    if isinstance(val, str):  # Solo aplicar el estilo si el valor es una cadena (formateado)
        val = float(val.replace(',', '.'))  # Convertir de nuevo a float para aplicar colores
    if val < 0:
        bg_color = f'rgba(255, {int(255 * (1 + val / 100))}, {int(255 * (1 + val / 100))}, 1)'
    elif val > 0:
        bg_color = f'rgba({int(255 * (1 - val / 100))}, 255, {int(255 * (1 - val / 100))}, 1)'
    else:
        bg_color = 'white'

    # Decidir el color del texto
    text_color = 'black' if val < 100.5 else 'white'
    return f'background-color: {bg_color}; color: {text_color}'

# Iniciar la aplicación de Streamlit
st.title("Matriz de Variaciones Mensuales")

# Entrada de los tickers
tickers_input = st.text_input("Ingrese los tickers separados por comas", "GGAL.BA, YPFD.BA, PAMP.BA, BMA.BA, METR.BA")
tickers = [ticker.strip() for ticker in tickers_input.split(',')]

# Selección de meses
selected_months = st.multiselect("Seleccione los meses que desea observar", list(range(1, 13)), [9])

# Botón para generar la matriz
if st.button("Generar Matriz"):
    # Crear la matriz combinada filtrada por meses
    combined_matrix_formatted = create_combined_matrix(tickers, selected_months)

    # Aplicar el estilo a la matriz combinada
    styled_matrix_combined = combined_matrix_formatted.style.applymap(color_map)

    # Mostrar la matriz con estilo en Streamlit
