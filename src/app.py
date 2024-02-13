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
    html.H1("Student Loan Calculator", className='mb-2', style={'textAlign': 'left',"font-weight":"bold","font-family":"arial"}),
    html.H4("David Barton, 2024 - Optimised for Mobile Viewing", className='mb-2', style={'textAlign': 'left',"font-family":"arial"}),
    html.H5("The aim of this tool is to provide insight into whether there are\nany long-term saving benefits of paying more than the minimum\nannual student loan repayment. This depends heavily on how\nmuch you owe, how much you can pay, and how much you\nexpect to earn in the future.",
        className='mb-2', style={'textAlign': 'start', 'white-space': 'pre', "font-family": "arial"}),

    html.H5("Use the sliders at the bottom to input the relevant values,\nand the plots will then update to reflect your situation.\n\n➤  The first plot shows the total amount you will pay towards\nyour loan until it is written-off or fully paid-off (see the red line).\nThe x-axis shows the effect of increasing the amount you repay\nannually above the minimum required payment; if the red line\ndrops off immediately right of the y-axis, it may be worth\npaying extra if possible.\n\n➤  The second plot shows the number of years until the loan is\npaid-off or written-off (blue dashed line), against the same x-axis.", className='mb-2', style={'textAlign': 'start','white-space':'pre',"font-family":"arial"}),
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
                        20: {'label':'£20,000', 'style': {'fontSize': '12px',"font-family":"arial"}},
                        40: {'label':'£40,000', 'style': {'fontSize': '12px',"font-family":"arial"}},
                        60: {'label':'£60,000', 'style': {'fontSize': '12px',"font-family":"arial"}},
                        80: {'label':'£80,000', 'style': {'fontSize': '12px',"font-family":"arial"}},
                        100: {'label':'£100,000', 'style': {'fontSize': '12px',"font-family":"arial"}}
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
                        0: {'label':'0%', 'style': {'fontSize': '12px',"font-family":"arial"}},
                        2: {'label':'2%', 'style': {'fontSize': '12px',"font-family":"arial"}},
                        4: {'label':'4%', 'style': {'fontSize': '12px',"font-family":"arial"}},
                        6: {'label':'6%', 'style': {'fontSize': '12px',"font-family":"arial"}},
                        8: {'label':'8%', 'style': {'fontSize': '12px',"font-family":"arial"}},
                        10: {'label':'10%', 'style': {'fontSize': '12px',"font-family":"arial"}}
                        },
                        id = "annual_loan_interest",
                        value=6,
                        tooltip={"placement": "top", "always_visible": True,"template":" Estimated Average Annual \nInterest on Loan: {value}%",
                                "style": {"white-space":'pre',"fontSize": "18px","font-family":"arial"},},
                       )
        ], width=2),
        dbc.Col([html.Div(
            "➤ Plan 1 and 4 loans are charged interest at a rate equal\nto the lower of: Bank of England Base Rate + 1%, or RPI.\n➤ Plan 2 loans are charged interest at a rate equal to RPI + 3%.\n➤ Plan 5 loans are charged interest at a rate equal to RPI.\n\n")],
                width=2,style={"white-space": 'pre', 'fontSize':14,"font-family":"arial"})
    ]),
    html.Br(),
    html.Br(),
    html.Br(),
    dbc.Row([
        dbc.Col([
            dcc.Slider(0, 50, 1,
                       marks={
                           0: {'label': '0', 'style': {'fontSize': '12px',"font-family":"arial"}},
                           10: {'label': '10', 'style': {'fontSize': '12px',"font-family":"arial"}},
                           20: {'label': '20', 'style': {'fontSize': '12px',"font-family":"arial"}},
                           30: {'label': '30', 'style': {'fontSize': '12px',"font-family":"arial"}},
                           40: {'label': '40', 'style': {'fontSize': '12px',"font-family":"arial"}},
                           50: {'label': '50', 'style': {'fontSize': '12px',"font-family":"arial"}}
                       },
                       id="years_until_loan_written_off",
                       value=30,
                       tooltip={"placement": "top", "always_visible": True,
                                "template": "{value} Years until\n Loan is Written-Off ",
                                "style": {"white-space": 'pre', "fontSize": "18px","font-family":"arial"}, },
                       )
        ], width=2),
        dbc.Col([html.Div(
            "➤ Plan 1 loans are written off after 25 years.\n➤ Plan 2 and 4 loans are written off after 30 years.\n➤ Plan 5 loans are written off after 40 years.\n\n")],
            width=2, style={"white-space": 'pre', 'fontSize': 14,"font-family":"arial"})
    ]),
    html.Br(),
    html.Br(),
    html.Br(),
    dbc.Row([
        dbc.Col([
            dbc.Row([
                dcc.Slider(0, 100, 1,
                           marks={
                               0: {'label': '£0', 'style': {'fontSize': '12px'}},
                               20: {'label': '£20,000', 'style': {'fontSize': '12px',"font-family":"arial"}},
                               40: {'label': '£40,000', 'style': {'fontSize': '12px',"font-family":"arial"}},
                               60: {'label': '£60,000', 'style': {'fontSize': '12px',"font-family":"arial"}},
                               80: {'label': '£80,000', 'style': {'fontSize': '12px',"font-family":"arial"}},
                               100: {'label': '£100,000', 'style': {'fontSize': '12px',"font-family":"arial"}}
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
                            0: {'label':'0%', 'style': {'fontSize': '12px',"font-family":"arial"}},
                            2: {'label':'2%', 'style': {'fontSize': '12px',"font-family":"arial"}},
                            4: {'label':'4%', 'style': {'fontSize': '12px',"font-family":"arial"}},
                            6: {'label':'6%', 'style': {'fontSize': '12px',"font-family":"arial"}},
                            8: {'label':'8%', 'style': {'fontSize': '12px',"font-family":"arial"}},
                            10: {'label':'10%', 'style': {'fontSize': '12px',"font-family":"arial"}}
                        },
                        id = "annual_salary_increase",
                        value=6,
                        tooltip={"placement": "top", "always_visible": True,"template":" Estimated Average Annual \nSalary Increase: {value}%",
                                "style": {"white-space":'pre',"fontSize": "18px","font-family":"arial"},},
                       )
            ])
        ], width=2),
        dbc.Col([html.Div(
            "\n\nWHAT STUDENT LOAN PLAN AM I ON?\n\nStudent Finance England:\n➤ Plan 1 if you started your course before September 2012.\n➤ Plan 2 if you started your course between August 2012 and\nAugust 2023.\n➤ Plan 5 if you started your course after July 2023.\n\nStudent Finance Wales:\n➤ Plan 1 if you started your course before September 2012.\n➤ Plan 2 if you started your course after August 2012.\n\nStudent Finance Northern Ireland:\n➤ Plan 1.\n\nStudent Awards Agency Scotland:\n➤ Plan 4.")],
                width=2,style={"white-space": 'pre', 'fontSize':14,"font-family":"arial"}),
    ]),
    dbc.Row([dbc.Col([html.Div(
            "\n\n\nPLANNED FEATURES:\n\n➤ Option to apply discount rates to the future cash flows which\nare used to predict 'Total Paid Over Lifetime' in order to create\na fairer picture considering the interest that could have been\naccrued on money invested rather than used to repay the loan.\n\n➤ Option to change the x-axis variable (i.e. plotting against\nsalary, initial debt, or similar).\n\n")],
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
    fig, (ax_cost,ax_time) = plt.subplots(2,1,figsize=(4.8,8),dpi=85,constrained_layout=True)

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
