'''
 # @ Create Time: 2024-02-12 21:51:43.021711
'''

from student_loan_functions import calculate_paid_off_year_and_total_paid_array_across_initial_debt_and_salary, plot_interactive_line_graph_of_total_paid_array_against_overpayment_and_initial_debt

from dash import Dash, html, dcc, Input, Output
import dash_bootstrap_components as dbc
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import numpy as np
import base64
from io import BytesIO

overpayment_factor_array = np.arange(0, 10, 0.1)

app = Dash(__name__, title="MyDashApp")

# Declare server for Heroku deployment. Needed for Procfile.
server = app.server

# assume you have a "long-form" data frame
# see https://plotly.com/python/px-arguments/ for more options

app.layout = dbc.Container([
    html.H1("Student Loan Calculator", className='mb-2', style={'textAlign': 'center',"font-weight":"bold","font-family":"arial"}),
    html.H4("David Barton, 2024", className='mb-2', style={'textAlign': 'center',"font-family":"arial"}),
    html.H5("Use the sliders at the bottom to input your current student loan debt,\ncurrent salary, and estimates of the average annual interest on the loan and\nyour average annual salary increase.\n\n➤  The first plot shows the total amount you will pay towards your loan until it\nis written-off or fully paid-off. This depends on the amount you pay per month above\nthe minimum required payment.\n\n➤  The second plot shows the number of years until the loan is paid-off or\nwritten-off for the same scenario.", className='mb-2', style={'textAlign': 'center','white-space':'pre',"font-family":"arial"}),
    html.Br(),
    dbc.Row([
        dbc.Col([
            html.Img(id='bar-graph-matplotlib')
        ])
    ],justify="start"),
    html.Br(),
    html.Br(),
    dbc.Row([
        dbc.Col([
            dcc.Slider(0,100,1,
                        marks={
                        0: {'label':'£0', 'style': {'fontSize': '12px'}},
                        20: {'label':'£20,000', 'style': {'fontSize': '12px'}},
                        40: {'label':'£40,000', 'style': {'fontSize': '12px'}},
                        60: {'label':'£60,000', 'style': {'fontSize': '12px'}},
                        80: {'label':'£80,000', 'style': {'fontSize': '12px'}},
                        100: {'label':'£100,000', 'style': {'fontSize': '12px'}}
                        },
                        id='initial_debt',
                        value=50,
                       tooltip={"placement": "top", "always_visible": True,"template":" Initial Debt: \n£{value},000",
                                "style": {"white-space":'pre',"fontSize": "18px","font-family":"arial"},},
                       )
        ], width=2),
        dbc.Col([
        ], width=2),
    ]),
    html.Br(),
    html.Br(),
    dbc.Row([
        dbc.Col([
            dcc.Slider(0,10,0.1,
                        marks={
                        0: {'label':'0%', 'style': {'fontSize': '12px'}},
                        2: {'label':'2%', 'style': {'fontSize': '12px'}},
                        4: {'label':'4%', 'style': {'fontSize': '12px'}},
                        6: {'label':'6%', 'style': {'fontSize': '12px'}},
                        8: {'label':'8%', 'style': {'fontSize': '12px'}},
                        10: {'label':'10%', 'style': {'fontSize': '12px'}}
                        },
                        id = "annual_loan_interest",
                        value=6,
                        tooltip={"placement": "top", "always_visible": True,"template":"Average Annual\n Interest on Loan: {value}% ",
                                "style": {"white-space":'pre',"fontSize": "18px","font-family":"arial"},},
                       )
        ], width=2),
        dbc.Col([html.Div(
            "☚ Plan 1 and 4 Student Loans are charged interest at a rate equal to\nwhichever is lower of:\n               A) RPI      B) Bank of England Base Rate + 1%\n☚ Plan 2 Student Loans are charged interest at a rate equal to RPI + 3%.\n☚ Plan 5 Student Loans are charged interest at a rate equal to RPI.")],
                width=2,style={"white-space": 'pre', 'fontSize':14,"font-family":"arial"})
    ]),
    html.Br(),
    dbc.Row([
        dbc.Col([
            dcc.Slider(0, 50, 1,
                       marks={
                           0: {'label': '0', 'style': {'fontSize': '12px'}},
                           10: {'label': '10', 'style': {'fontSize': '12px'}},
                           20: {'label': '20', 'style': {'fontSize': '12px'}},
                           30: {'label': '30', 'style': {'fontSize': '12px'}},
                           40: {'label': '40', 'style': {'fontSize': '12px'}},
                           50: {'label': '50', 'style': {'fontSize': '12px'}}
                       },
                       id="years_until_loan_written_off",
                       value=30,
                       tooltip={"placement": "top", "always_visible": True,
                                "template": "{value} Years until\n Loan is Written-Off ",
                                "style": {"white-space": 'pre', "fontSize": "18px","font-family":"arial"}, },
                       )
        ], width=2),
        dbc.Col([html.Div(
            "\n ☚ Plan 1 Student Loans are written off after 25 years.\n☚ Plan 2 and 4 Student Loans are written off after 30 years.\n☚ Plan 5 Student Loans are written off after 40 years.\n\n")],
            width=2, style={"white-space": 'pre', 'fontSize': 14,"font-family":"arial"})
    ]),
    html.Br(),
    html.Br(),
    dbc.Row([
        dbc.Col([
            dbc.Row([
                dcc.Slider(0, 100, 1,
                           marks={
                               0: {'label': '£0', 'style': {'fontSize': '12px'}},
                               20: {'label': '£20,000', 'style': {'fontSize': '12px'}},
                               40: {'label': '£40,000', 'style': {'fontSize': '12px'}},
                               60: {'label': '£60,000', 'style': {'fontSize': '12px'}},
                               80: {'label': '£80,000', 'style': {'fontSize': '12px'}},
                               100: {'label': '£100,000', 'style': {'fontSize': '12px'}}
                           },
                           id='initial_salary',
                           value=30,
                           tooltip={"placement": "top", "always_visible": True,
                                    "template": " Initial Salary: \n£{value},000",
                                    "style": {"white-space": 'pre', "fontSize": "18px","font-family":"arial"}, },
                           )
            ]),
            html.Br(),
            html.Br(),
            dbc.Row([
                dcc.Slider(0,10,0.1,
                        marks={
                            0: {'label':'0%', 'style': {'fontSize': '12px'}},
                            2: {'label':'2%', 'style': {'fontSize': '12px'}},
                            4: {'label':'4%', 'style': {'fontSize': '12px'}},
                            6: {'label':'6%', 'style': {'fontSize': '12px'}},
                            8: {'label':'8%', 'style': {'fontSize': '12px'}},
                            10: {'label':'10%', 'style': {'fontSize': '12px'}}
                        },
                        id = "annual_salary_increase",
                        value=6,
                        tooltip={"placement": "top", "always_visible": True,"template":"Average Annual\n Salary Increase: {value}% ",
                                "style": {"white-space":'pre',"fontSize": "18px","font-family":"arial"},},
                       )
            ])
        ], width=2),
        dbc.Col([html.Div(
            "WHAT STUDENT LOAN PLAN AM I ON?\nStudent Finance England:\n➤ Plan 1 if you started your course before September 2012.\n➤ Plan 2 if you started your course between August 2012 and August 2023.\n➤ Plan 5 if you started after July 2023.\nStudent Finance Wales:\n➤ Plan 1 if you started your course before September 12012.\n➤ Plan 2 if you started your course after August 2012.\nStudent Finance Northern Ireland: ➤ Plan 1.\nStudent Awards Agency Scotland: ➤ Plan 4.")],
                width=2,style={"white-space": 'pre', 'fontSize':14,"font-family":"arial"}),
    ]),
    dbc.Row([dbc.Col([html.Div(
            "PLANNED FEATURES:\n➤ Option to apply discount rates to the future cash flows which are used to predict 'Total Paid Over Lifetime' in order to create a fairer picture\nconsidering the interest that could have been accrued on money invested rather than used to repay the loan.\n➤ Option to change the x-axis variable (i.e. plotting against salary, initial debt, or similar).\n\n")],
                width=2,style={"white-space": 'pre', 'fontSize':14,"font-family":"arial"}),
    ]),
])

# Create interactivity between dropdown component and graph
@app.callback(
    Output(component_id='bar-graph-matplotlib', component_property='src'),
    Input('initial_debt', 'value'),
    Input('initial_salary', 'value'),
    Input('annual_loan_interest', 'value'),
    Input('annual_salary_increase', 'value'),
    Input('years_until_loan_written_off', 'value')
)

def plot_data(input_initial_debt,input_initial_salary,annual_loan_interest,annual_salary_increase,years_until_loan_written_off):
    annual_loan_interest = annual_loan_interest/100
    annual_salary_increase = annual_salary_increase/100
    # Build the matplotlib figure
    fig, (ax_cost,ax_time) = plt.subplots(2,1,figsize=(8,10),dpi=83,constrained_layout=True)

    initial_debt_and_salary_plot_data = calculate_paid_off_year_and_total_paid_array_across_initial_debt_and_salary(
        [input_initial_debt], [annual_salary_increase], overpayment_factor_array, initial_salary=input_initial_salary,
        n=annual_loan_interest, years_until_loan_written_off=years_until_loan_written_off)

    plot_interactive_line_graph_of_total_paid_array_against_overpayment_and_initial_debt(
        initial_debt_and_salary_plot_data[0],
        initial_debt_and_salary_plot_data[1],
        initial_debt_and_salary_plot_data[2],
        initial_debt_and_salary_plot_data[3],
        initial_debt_and_salary_plot_data[4], axis1=ax_cost, axis2=ax_time,
        years_until_loan_written_off=years_until_loan_written_off)

    # Save it to a temporary buffer.
    buf = BytesIO()
    fig.savefig(buf, format="png")
    # Embed the result in the html output.
    fig_data = base64.b64encode(buf.getbuffer()).decode("ascii")
    fig_bar_matplotlib = f'data:image/png;base64,{fig_data}'

    return fig_bar_matplotlib

if __name__ == '__main__':
    app.run_server(debug=True)
