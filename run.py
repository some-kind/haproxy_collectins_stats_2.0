# TODO сделать тестовую приложуху, которая будет имитировать стату HAProxy по GET запросу
# TODO пофиксить запись в файл JSON

import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go

from config import URL, TIME, ARGS  # подтягиваем переменные из конфига
from data_definition import get_haproxy_stats  # подтягиваем функцию

# Ваши данные
statistic_data = {}

# Создаем Dash приложение
app = dash.Dash(__name__)


# TODO НЕСРОЧНОЕ - исправить отображение, чтобы было несколько графиков на одной строке
# Определяем функцию для отрисовки графика для каждого сервера
def draw_graphs():
    graphs = []

    # Итерируемся по каждому серверу и создаем графики для каждого параметра
    for server, params in statistic_data.items():
        if server == "time":  # пропускаем время в нашем словаре
            continue

        # Создаем список словарей для хранения данных о каждом графике
        traces = []

        # Итерируемся по каждому параметру сервера
        for param, values in params.items():
            # Создаем график для текущего параметра
            trace = go.Scatter(x=statistic_data["time"]["time"], y=values, mode='lines', name=f'{ARGS[param]}')
            traces.append(trace)

        # Создаем словарь данных и графической компоновки для текущего сервера
        layout = go.Layout(title=f'HAProxy статистика - {server}', xaxis=dict(title='Время'), yaxis=dict(title='Показания'))
        fig = go.Figure(data=traces, layout=layout)

        # Создаем элемент dcc.Graph для текущего сервера и добавляем его в список графиков
        graph_element = dcc.Graph(id=f'graph-{server}', figure=fig)
        graphs.append(graph_element)

    return graphs


# Определяем layout для Dash приложения
app.layout = html.Div([
    html.Div(id='graphs-container'),  # Контейнер для графиков
    dcc.Interval(
        id='interval-component',
        interval=TIME * 1000,  # в миллисекундах
        n_intervals=0
    )
])


# Определяем callback функцию для обновления графика
@app.callback(Output('graphs-container', 'children'),
              Input('interval-component', 'n_intervals'))
def update_graphs(n):
    global statistic_data
    # Получаем новые данные
    statistic_data = get_haproxy_stats(URL, statistic_data)

    # Создаем новые графики с обновленными данными
    graph_elements = draw_graphs()

    # Возвращаем новые графики для отображения
    return graph_elements


# Запускаем Dash приложение
if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0')
