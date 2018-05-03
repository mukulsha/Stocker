import csv
import dash
import dash_html_components as html
import dash_core_components as dcc

from stocker import stocker_v4

# GLOBAL VARIABLES

ticker_name = None
ticker_company = None
decision = None
lastPrice = 0
lastPriceDate = None
flastPrice = 0
flastPriceDate = None
maxStockPrice = 0
maxStockPriceDate = None
lastTradeQuantity = None
ticker = None
sliderValue = 0
predictionTime = 30

stock_plot_date = None
stock_plot_stat = None

stock_history_ds = None
stock_history_y = None
future_ds1 = None
future_yhat1 = None
future_ds_pydatetime = None
future_yhat_upper = None
future_yhat_lower = None

train_ds = None
train_y = None
test_ds = None
test_y = None
future_ds = None
future_yhat = None

historyButton = 0
futureButton = 0
predictButton = 0
goButton = 0
processing = False


# GLOBAL GRAPHS
history = []
future = []
predict = []
maindiv = []

# PREDEFINDE COMPONENTS

# DISCLAIMER
disclaimer = [
    html.Div(
        className='card-panel teal lighten-2 flow-text',
        style={'color': 'white', 'margin': '100px', 'margin-bottom': '20px' },
        children="The information provided by the StockMarker is for information purposes only and is not intended for trading purposes or advice. StockMarker do not hold themselves out as providing any legal, financial or other advice. They also do not make any recommendation or endorsement as to any investment or advisor. In addition, StockMarker do not offer any advice regarding the nature, potential value or suitability of any particular investment, security or investment strategy. The information provided by the StockMarker does not constitute advice and you should not rely on any information provided by them to make (or refrain from making) any decision or take (or refrain from taking) any action. StockMarker does not make recommendations for buying or selling any securities or options."
    )
]
# STATDATA
statdata = [
    html.Div(
        className='lighten-2 flow-text',
        style={'color': 'white', 'margin': '100px', 'margin-top': '20px'},
        children=[
            # COMPANY NAME
            html.Div(
                className='card-panel teal lighten-2 flow-text',
                style={'color': 'white', 'width':'48%', 'float':'left', 'margin-right':'40px'},
                children=[
                    html.Div(children='business', id='logo', className='material-icons brand-logo left', style={'font-size': '35px', 'color': 'white'}),
                    html.Div(children='Company: '+str(ticker_company), id='logo', className='left', style={'font-size': '25px', 'color': 'white'}),
                ]
            ),
            # COMPANY TICKER
            html.Div(
                className='card-panel teal lighten-2 flow-text',
                style={'color': 'white', 'width':'48%', 'float':'left'},
                children=[
                    html.Div(children='insert_chart', id='logo', className='material-icons brand-logo left', style={'font-size': '35px', 'color': 'white'}),
                    html.Div(children='Ticker: '+str(ticker_name), id='logo', className='left', style={'font-size': '25px', 'color': 'white'}),
                ]
            ),
            # LAST STOCK PRICE
            html.Div(
                className='card-panel teal lighten-2 flow-text',
                style={'color': 'white', 'width':'48%', 'float':'left', 'margin-right':'40px'},
                children=[
                    html.Div(children='business_center', id='logo', className='material-icons brand-logo left', style={'font-size': '35px', 'color': 'white'}),
                    html.Div(children='Last Price: '+str(lastPrice), id='logo', className='left', style={'font-size': '25px', 'color': 'white'}),
                ]
            ),
            # LAST STOCK PRICE DATE
            html.Div(
                className='card-panel teal lighten-2 flow-text',
                style={'color': 'white', 'width':'48%', 'float':'left'},
                children=[
                    html.Div(children='monetization_on', id='logo', className='material-icons brand-logo left', style={'font-size': '35px', 'color': 'white'}),
                    html.Div(children=ticker_name, id='logo', className='left', style={'font-size': '25px', 'color': 'white'}),
                ]
            ),
            # MAX STOCK PRICE
            html.Div(
                className='card-panel teal lighten-2 flow-text',
                style={'color': 'white', 'width':'48%', 'float':'left', 'margin-right':'40px'},
                children=[
                    html.Div(children='business_center', id='logo', className='material-icons brand-logo left', style={'font-size': '35px', 'color': 'white'}),
                    html.Div(children='ticker_name', id='logo', className='left', style={'font-size': '25px', 'color': 'white'}),
                ]
            ),
            # MAX STOCK PRICE DATE
            html.Div(
                className='card-panel teal lighten-2 flow-text',
                style={'color': 'white', 'width':'48%', 'float':'left'},
                children=[
                    html.Div(children='monetization_on', id='logo', className='material-icons brand-logo left', style={'font-size': '35px', 'color': 'white'}),
                    html.Div(children=ticker_name, id='logo', className='left', style={'font-size': '25px', 'color': 'white'}),
                ]
            ),
        ]
    )
]

# POPULATE DROPDOWN LIST
dropdown_list = []
with open('good_company.csv', 'r') as company_list:
    for company in csv.reader(company_list):
        dropdown_list.append({'label': company[1], 'value': company[0]})

def     getStats():
    global ticker_company, lastPrice, lastPriceDate, flastPrice, flastPriceDate, maxStockPrice, maxStockPriceDate
    with open('good_company.csv', 'r') as company_list:
        for company in csv.reader(company_list):
            if company[0].split('/')[1] == ticker_name:

                ticker_company = company[1]
    lastPrice = stock_plot_stat.iloc[-1]
    lastPriceDate = (stock_plot_date.iloc[-1]).date()
    maxStockPrice = max(future_yhat1[-predictionTime:])
    print(lastPrice)
    print(lastPriceDate)
    print(maxStockPrice)
    for i in range(future_yhat1.count() - predictionTime, future_yhat1.count()):
        if future_yhat1.iloc[i] == maxStockPrice:
            maxStockPriceDate = (future_ds1.iloc[i]).date()
    print(maxStockPriceDate)
    flastPrice = future_yhat1.iloc[-1]
    flastPriceDate = (future_ds1.iloc[-1]).date()
    print(flastPrice)
    print(flastPriceDate)

app = dash.Dash()
app.config['suppress_callback_exceptions']=True
# Append an externally hosted CSS stylesheet
my_css_url = "https://cdnjs.cloudflare.com/ajax/libs/materialize/1.0.0-beta/css/materialize.min.css"
app.css.append_css({
    "external_url": [my_css_url, 'https://fonts.googleapis.com/icon?family=Material+Icons']
})

# Append an externally hosted JS bundle
my_js_url = 'https://cdnjs.cloudflare.com/ajax/libs/materialize/1.0.0-beta/js/materialize.min.js'
app.scripts.append_script({
    "external_url": my_js_url
})

# MAIN DIVISION
app.layout = html.Div(style={'padding': '10px'}, children=[

    # NAVIGATION BAR
    html.Div(id='top-navigation-bar',
             children=[
                 html.Div(children='bubble_chart', id='logo', className='material-icons brand-logo left',
                          style={'font-size': '55px', 'color': 'teal'}),
                 html.Div(children='Stock Data Prediction', id='log', className='brand-logo left',
                          style={'font-size': '50px', 'color': 'teal'}),

                 html.Button('Future', id='future-button', className='waves-effect waves-light btn-large right'),
                 html.Button('Prediction', id='predict-button', className='waves-effect waves-light btn-large  right'),
                 html.Button('History', id='history-button', className='waves-effect waves-light btn-large  right'),
             ]),

    # PROGRESS BAR
    html.Div(className='progress', id='progress-bar',
             style={'font-size': '55px', 'bgcolor': 'red', 'margin-top': '3px'},
             children=[
                 html.Div(className='indeterminate', id='progress-bar-animation')
             ],
             ),

    # DROPDOWN
    html.Div(
        dcc.Dropdown(
            id='company-dropdown',
            options=dropdown_list,
        ),
        className='dropdown-trigger',

        style={'width': '95%', 'float': 'left'},

    ),
    # GO BUTTON
    html.Div(children=[
        html.Button('arrow_forward', id='go-button',
                    className='btn-floating btn waves-effect waves-light material-icons right', ),
    ],
        style={'float': 'left'},

    ),

    # SLIDER
    html.Div(dcc.Slider(
        id='slider',
        min=0,
        max=7,
        marks={0: 'Day',
               1: 'Week',
               2: 'Fortnight',
               3: 'Month',
               4: '2 Months',
               5: 'Quarter',
               6: 'Half-Year',
               7: 'Annual',
               },
        value=3,
    ), style={'padding': '20px', 'margin-top': '40px'}),

    # GRAPH DIVISION
    html.Div(id='main-div',
             children=disclaimer,
             ),

    # DROPDOWN BUTTON
    html.Div(children=[
        html.Button('arrow_downward', id='dropdown-button',
                    className='btn-floating btn waves-effect waves-light material-icons', ),
    ],
    style = {'margin-left':'100px'}
    ),
    html.Div(id='statistics',
             children=statdata,
             ),

])


# BUILDERS
def makeHistory():
    global history, stock_plot_date, stock_plot_stat
    stock_plot_date, stock_plot_stat = ticker.plot_stock(start_date='01/01/2017')

    history = [
        dcc.Graph(
            id='plot-stock-graph',
            figure={
                'data': [

                    {'x': stock_plot_date, 'y': stock_plot_stat, 'type': 'line', 'name': ticker_name+'History'},
                ],
                'layout': {
                    'title': ticker_name
                }
            }
        ),
    ]

def makeFuture():
    global future, stock_history_ds, stock_history_y, future_ds1, future_yhat1, future_ds_pydatetime, future_yhat_upper, future_yhat_lower
    if predictionTime == 0:
        print(predictionTime)
        future = ['Hello']
        return
    stock_history_ds, stock_history_y, future_ds1, future_yhat1, future_ds_pydatetime, future_yhat_upper, future_yhat_lower = ticker.create_prophet_model(days=predictionTime)
    future = [
        dcc.Graph(
            id='create-prophet-model-graph',
            figure={
                'data': [
                    {'x': stock_history_ds, 'y': stock_history_y, 'type': 'line', 'name': 'History'},
                    {'x': future_ds1, 'y': future_yhat1, 'type': 'line', 'name': 'Future'},
                    # {'x': future_ds_pydatetime, 'y': future_yhat_lower, 'type': 'line', 'name': 'Future'},
                    # {'x': future_ds_pydatetime, 'y': future_yhat_upper, 'type': 'line', 'name': 'Future'},
                ],
                'layout': {
                    'title': ticker_name+' Prophet Model'
                }
            }
        ),
    ]

def makePredict():
    global predict, train_ds, train_y, test_ds, test_y, future_ds, future_yhat
    train_ds, train_y, test_ds, test_y, future_ds, future_yhat = ticker.evaluate_prediction()
    predict=[
        dcc.Graph(
            id='evaluate-prediction-graph',
            figure={
                'data': [
                    {'x': train_ds, 'y': train_y, 'type': 'line', 'name': 'History'},
                    {'x': test_ds, 'y': test_y, 'type': 'line', 'name': 'Test'},
                    {'x': future_ds, 'y': future_yhat, 'type': 'line', 'name': 'Future'},
                    # {'x': future_ds_pydatetime, 'y': future_yhat_upper, 'type': 'line', 'name': 'FutureUpper'},
                ],
                'layout': {
                    'title': ticker_name+' Prediction'
                }
            }
        ),
    ]
    return
@app.callback(
    dash.dependencies.Output('statistics','children'),
    [dash.dependencies.Input('dropdown-button', 'n_clicks'),],
)
def showhidestats(dropdown):
    if dropdown is not None:
        if dropdown % 2 == 0:
            return []
        else:
            return [
    html.Div(
        className='lighten-2 flow-text',
        style={'color': 'white', 'margin': '100px', 'margin-top ': '20px'},
        children=[
            # COMPANY NAME
            html.Div(
                className='card-panel teal lighten-2 flow-text',
                style={'color': 'white', 'width':'48%', 'float':'left', 'margin-right':'40px'},
                children=[
                    html.Div(children='business', id='logo', className='material-icons brand-logo left', style={'font-size': '35px', 'color': 'white'}),
                    html.Div(children='Company: '+str(ticker_company), id='logo', className='left', style={'font-size': '25px', 'color': 'white'}),
                ]
            ),
            # COMPANY TICKER
            html.Div(
                className='card-panel teal lighten-2 flow-text',
                style={'color': 'white', 'width':'48%', 'float':'left'},
                children=[
                    html.Div(children='insert_chart', id='logo', className='material-icons brand-logo left', style={'font-size': '35px', 'color': 'white'}),
                    html.Div(children='Stock Name: '+str(ticker_name), id='logo', className='left', style={'font-size': '25px', 'color': 'white'}),
                ]
            ),
            # LAST STOCK PRICE
            html.Div(
                className='card-panel teal lighten-2 flow-text',
                style={'color': 'white', 'width':'48%', 'float':'left', 'margin-right':'40px'},
                children=[
                    html.Div(children='attach_money', id='logo', className='material-icons brand-logo left', style={'font-size': '35px', 'color': 'white'}),
                    html.Div(children='Last Price: '+str(lastPrice), id='logo', className='left', style={'font-size': '25px', 'color': 'white'}),
                ]
            ),
            # LAST STOCK PRICE DATE
            html.Div(
                className='card-panel teal lighten-2 flow-text',
                style={'color': 'white', 'width':'48%', 'float':'left'},
                children=[
                    html.Div(children='date_range', id='logo', className='material-icons brand-logo left', style={'font-size': '35px', 'color': 'white'}),
                    html.Div(children='Date: '+str(lastPriceDate), id='logo', className='left', style={'font-size': '25px', 'color': 'white'}),
                ]
            ),
            # MAX STOCK PRICE
            html.Div(
                className='card-panel teal lighten-2 flow-text',
                style={'color': 'white', 'width': '48%', 'float': 'left', 'margin-right': '40px'},
                children=[
                    html.Div(children='attach_money', id='logo', className='material-icons brand-logo left',
                             style={'font-size': '35px', 'color': 'white'}),
                    html.Div(children='Max Price: ' + str(maxStockPrice), id='logo', className='left',
                             style={'font-size': '25px', 'color': 'white'}),
                ]
            ),
            # MAX STOCK PRICE DATE
            html.Div(
                className='card-panel teal lighten-2 flow-text',
                style={'color': 'white', 'width': '48%', 'float': 'left'},
                children=[
                    html.Div(children='date_range', id='logo', className='material-icons brand-logo left',
                             style={'font-size': '35px', 'color': 'white'}),
                    html.Div(children='Date: ' + str(maxStockPriceDate), id='logo', className='left',
                             style={'font-size': '25px', 'color': 'white'}),
                ]
            ),
            # FINAL STOCK PRICE
            html.Div(
                className='card-panel teal lighten-2 flow-text',
                style={'color': 'white', 'width': '48%', 'float': 'left', 'margin-right': '40px'},
                children=[
                    html.Div(children='attach_money', id='logo', className='material-icons brand-logo left',
                             style={'font-size': '35px', 'color': 'white'}),
                    html.Div(children='Final Price: ' + str(flastPrice), id='logo', className='left',
                             style={'font-size': '25px', 'color': 'white'}),
                ]
            ),
            # FINAL STOCK PRICE DATE
            html.Div(
                className='card-panel teal lighten-2 flow-text',
                style={'color': 'white', 'width': '48%', 'float': 'left'},
                children=[
                    html.Div(children='date_range', id='logo', className='material-icons brand-logo left',
                             style={'font-size': '35px', 'color': 'white'}),
                    html.Div(children='Date: ' + str(flastPriceDate), id='logo', className='left',
                             style={'font-size': '25px', 'color': 'white'}),
                ]
            ),
            # MAX PROFIT
            html.Div(
                className='card-panel teal lighten-2 flow-text',
                style={'color': 'white', 'width': '48%', 'float': 'left', 'margin-right': '40px'},
                children=[
                    html.Div(children='attach_money', id='logo', className='material-icons brand-logo left',
                             style={'font-size': '35px', 'color': 'white'}),
                    html.Div(children='Max P|L: '+ str(maxStockPrice-lastPrice), id='logo', className='left',
                             style={'font-size': '25px', 'color': 'white'}),
                ]
            ),
            # BUY HOLD PROFIT
            html.Div(
                className='card-panel teal lighten-2 flow-text',
                style={'color': 'white', 'width': '48%', 'float': 'left'},
                children=[
                    html.Div(children='attach_money', id='logo', className='material-icons brand-logo left',
                             style={'font-size': '35px', 'color': 'white'}),
                    html.Div(children='Buy&Hold P|L : '+ str(float(flastPrice)-float(lastPrice)), id='output', className='left',
                             style={'font-size': '25px', 'color': 'white'}),
                ]
            ),
        ]
    )
]

# @app.callback(
#     dash.dependencies.Output(component_id='output', component_property='children'),
#     [dash.dependencies.Input(component_id='input', component_property='value')]
# )
# def update_value(input_data):
#     return 'Return: ' + str(maxStockPrice*int(input_data))



@app.callback(
    dash.dependencies.Output('main-div', 'children'),
    [dash.dependencies.Input('go-button', 'n_clicks'),
     dash.dependencies.Input('history-button', 'n_clicks'),
     dash.dependencies.Input('future-button', 'n_clicks'),
     dash.dependencies.Input('predict-button', 'n_clicks')],
    [dash.dependencies.State('company-dropdown', 'value'),
     dash.dependencies.State('slider', 'value')]
)
def show_loading_bar(go_button, history_button, future_button, predict_button, company, slider_value):
    global historyButton, futureButton, predictButton, goButton, ticker_name, ticker, processing, predictionTime, history, future, predict, maindiv, disclaimer, sliderValue

    if go_button is not None and go_button > goButton:
        goButton = go_button
        print(go_button)
        if company is not None:
            if ticker_name != company.split('/')[1]:
                history = []
                future = []
                predict = []
                ticker_name = company.split('/')[1]
                sliderValue = slider_value
                # doing this here for time being
                if slider_value == 1:
                    predictionTime = 7
                elif slider_value == 2:
                    predictionTime = 15
                elif slider_value == 3:
                    predictionTime = 30
                elif slider_value == 4:
                    predictionTime = 60
                elif slider_value == 5:
                    predictionTime = 90
                elif slider_value == 6:
                    predictionTime = 182
                elif slider_value == 7:
                    predictionTime = 365
                else:
                    predictionTime = 1
                ticker = stocker_v4.Stocker_v4(ticker_name, predictionTime)
                print("predTime")
                print(predictionTime)
                makeHistory()
                makeFuture()
                makePredict()
                getStats()
                processing = True
                maindiv = history
            if slider_value != sliderValue:
                future = []
                predict = []
                return history
    elif history_button is not None and history_button > historyButton:
        print(history_button)
        historyButton = history_button
        if history == []:
            makeHistory()
        maindiv = history
    elif future_button is not None and future_button > futureButton:
        print(future_button)
        futureButton = future_button
        if future == []:
            makeFuture()
        maindiv = future
    elif predict_button is not None and predict_button > predictButton:
        print(predict_button)
        predictButton = predict_button
        if predict == []:
            makePredict()
        maindiv = predict
    else:
        maindiv = disclaimer
    return maindiv
#
# @app.callback(
#     dash.dependencies.Output('processor','children'),
#     [dash.dependencies.Input('interval-component', 'n_intervals')]
# )
# def updater():
#     print('update')
#     if history is not []:
#         if future == []:
#             makeFuture()
#         if predict == []:
#             makePredict()
#         getStats()
#     return []

if __name__ == '__main__':
    app.run_server(debug=True)

# html.Div(
#
# ),
