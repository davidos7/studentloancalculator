import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button, CheckButtons
import matplotlib as mpl
from matplotlib.ticker import (MultipleLocator, FormatStrFormatter,
                               AutoMinorLocator)
from cycler import cycler


marker_array = ["x","o","v"]
plotted_functions = 0

k_global = 0.06 # annual salary fractional increase
n = 0.073
initial_debt_global = 63 #27.754

default_cycler = (cycler(color=['black','red','orange','dodgerblue','b']) +
                  cycler(linestyle=['-', '-.', ':', '-.','-']))
def generate_all_student_loan_data(number_of_years_to_plot,initial_debt,k=k_global,overpayment_factor=0,initial_salary=30,n=0.073,years_until_loan_written_off=29): # n = annual average loan increase rate
    salary_array = np.zeros(number_of_years_to_plot)
    annual_minimum_loan_repayment_array = np.zeros(number_of_years_to_plot)
    annual_interest_on_loan_array = np.zeros(number_of_years_to_plot)
    outstanding_loan_array = np.zeros(number_of_years_to_plot)
    total_repaid_array = np.zeros(number_of_years_to_plot)

    for i in range(number_of_years_to_plot):
        salary_array[i] = initial_salary * ((1 + k)**i)
        annual_minimum_loan_repayment_array[i] = (salary_array[i] - 27.295) * 0.09 + overpayment_factor
        if i==0:
            outstanding_loan_array[i] = initial_debt
            total_repaid_array[i] = 0
        else:
            if(outstanding_loan_array[i-1]<annual_minimum_loan_repayment_array[i]):
                annual_minimum_loan_repayment_array[i] = outstanding_loan_array[i]
                outstanding_loan_array[i] = 0
            elif(i>=years_until_loan_written_off):
                annual_minimum_loan_repayment_array[i] = 0
                outstanding_loan_array[i] = 0
            else:
                outstanding_loan_array[i] = outstanding_loan_array[i-1] + annual_interest_on_loan_array[i-1] - annual_minimum_loan_repayment_array[i-1]
            total_repaid_array[i] = total_repaid_array[i-1] + annual_minimum_loan_repayment_array[i]
        annual_interest_on_loan_array[i] = outstanding_loan_array[i] * n

    return([outstanding_loan_array,salary_array,total_repaid_array,annual_interest_on_loan_array,annual_minimum_loan_repayment_array])

def calculate_paid_off_year_and_total_paid_array_across_initial_debt_and_salary(initial_debt_array,k_array,overpayment_factor_array,years_until_loan_written_off,initial_salary=30,n=0.073):
    paid_off_year_array = np.zeros([len(initial_debt_array),len(k_array),len(overpayment_factor_array)])
    total_paid_off_array = np.zeros([len(initial_debt_array),len(k_array),len(overpayment_factor_array)])
    for l, overpayment_factor in enumerate(overpayment_factor_array):
        for j, k in enumerate(k_array):
            for i, initial_debt in enumerate(initial_debt_array):
                student_loan_data = generate_all_student_loan_data(years_until_loan_written_off+2,initial_debt,k=k,overpayment_factor=overpayment_factor,initial_salary=initial_salary,n=n,years_until_loan_written_off=years_until_loan_written_off)
                outstanding_loan_array = student_loan_data[0]
                total_repaid_array = student_loan_data[2]

                #print("before outstanding index")
                #print(np.where(outstanding_loan_array<0.1)[0][0])
                #print("after outstanding index")
                paid_off_year_array[i,j,l] = np.where(outstanding_loan_array == 0)[0][0]
                #print("paid off year array")
                #print(paid_off_year_array[i])
                total_paid_off_array[i,j,l] = total_repaid_array[int(paid_off_year_array[i,j,l])]

    return initial_debt_array, k_array, overpayment_factor_array, paid_off_year_array, total_paid_off_array

def plot_interactive_line_graph_of_total_paid_array_against_overpayment_and_initial_debt(initial_debt_array, k_array,
                                                                                     overpayment_factor_array,
                                                                                     paid_off_year_array,
                                                                                     total_paid_off_array,axis1,axis2,years_until_loan_written_off):
    initial_debt_count = len(initial_debt_array)
    overpayment_factor_count = len(overpayment_factor_array)
    k_array = np.array(k_array) * 100
    overpayment_factor_array = np.array(overpayment_factor_array)
    plt.rcParams["axes.prop_cycle"] = plt.cycler(default_cycler)

    for k_index, k in enumerate(k_array):
        for i, initial_debt in enumerate(initial_debt_array):
            line_name = "Initial Debt: £" +str(initial_debt)+"k"
            #if(initial_debt == 80):
            #    line_colour =  'red'
            #    line_style ='-'
            #elif(initial_debt == 60):
            #    line_colour = 'orange'
            #    line_style ='-.'
            #elif(initial_debt == 40):
            #    line_colour = 'dodgerblue'
            #    line_style = ':'
            #elif(initial_debt == 20):
            #    line_colour = 'blue'
            #    line_style = '-.'
            #else:
            #    line_colour = 'black'
            #    line_style = '-'
            line_colour = 'red'
            line_style = '-'
            axis1.plot(overpayment_factor_array,total_paid_off_array[i,k_index, :],label=line_name,color=line_colour,ls=line_style)

            line_colour = 'blue'
            line_style = '-.'
            axis2.plot(overpayment_factor_array,paid_off_year_array[i,k_index, :],label=line_name,color=line_colour,ls=line_style)

        #axis1.legend()
        axis1.set_xlim(0,max(overpayment_factor_array))
        axis1.set_ylim(0,300)
        axis1.set_yticks([0,50,100,150,200,250,300])
        axis1.set_xticks([0,2,4,6,8,10])
        axis1.yaxis.set_major_formatter(FormatStrFormatter('£%d,000'))
        axis1.xaxis.set_major_formatter(FormatStrFormatter('£%s,000'))
        axis1.set_xlabel("Amount Paid Annually beyond\nMinimum Loan Repayment\n",fontsize="12",fontweight="bold")
        axis1.set_ylabel("    Total Paid over Lifetime",fontsize="12",fontweight="bold")

        #axis2.legend()
        axis2.set_xlim(0,max(overpayment_factor_array))
        axis2.set_ylim(0,45)
        axis2.set_yticks([0,5,10,15,20,25,30,35,40,45])
        axis2.set_xticks([0,2,4,6,8,10])
        axis2.yaxis.set_major_formatter(FormatStrFormatter('%d Years'))
        axis2.xaxis.set_major_formatter(FormatStrFormatter('£%s,000'))
        axis2.set_xlabel("Amount Paid Annually beyond\nMinimum Loan Repayment",fontsize="12",fontweight="bold")
        axis2.set_ylabel("    Years until Loan Repaid",fontsize="12",fontweight="bold")

        axis2.add_patch(
            mpl.patches.Rectangle((0, years_until_loan_written_off), 60, 4, facecolor='silver', edgecolor="k",
                                  linewidth=3, linestyle=":"))
        axis2.annotate("Loan Written-Off After " + str(years_until_loan_written_off) + " Years",
                         (0.25, years_until_loan_written_off + 1),fontsize="12",fontweight="bold")
        plt.setp(axis1.get_yticklabels()[0], visible=False)
        plt.setp(axis2.get_yticklabels()[0], visible=False)
        plt.setp(axis1.get_xticklabels()[0], visible=False)
        plt.setp(axis2.get_xticklabels()[0], visible=False)
        #plt.show()
        print(k)

# END OF STUDENT_LOAN_TURBOCHARGED

default_cycler = (cycler(color=['black','red','orange','dodgerblue','b']) +
                  cycler(linestyle=['-', '-.', ':', '-.','-']))
plt.rcParams["axes.prop_cycle"] = plt.cycler(default_cycler)

fig, (ax_cost,ax_time) = plt.subplots(1,2,figsize=(19,11))
plt.subplots_adjust(left=0.32, bottom=0.15)

initial_debt_array = [45]
overpayment_factor_array = np.arange(0, 10, 0.1)
initial_years_until_loan_written_off = 30

# Initial Plot
initial_debt_and_salary_plot_data = calculate_paid_off_year_and_total_paid_array_across_initial_debt_and_salary(initial_debt_array, [0.06], overpayment_factor_array,initial_salary=30,n=0.073,years_until_loan_written_off=initial_years_until_loan_written_off)

plot_interactive_line_graph_of_total_paid_array_against_overpayment_and_initial_debt(initial_debt_and_salary_plot_data[0],
                                                                             initial_debt_and_salary_plot_data[1],
                                                                             initial_debt_and_salary_plot_data[2],
                                                                             initial_debt_and_salary_plot_data[3],
                                                                             initial_debt_and_salary_plot_data[4],axis1=ax_cost,axis2=ax_time,years_until_loan_written_off=initial_years_until_loan_written_off)

axcolor = 'lightgoldenrodyellow'
ax_check_buttons = plt.axes([0.0675,0.35,0.2,0.28])

ax_salary_initial = plt.axes([0.13, 0.65, 0.1,0.02], facecolor=axcolor)
ax_loan_initial = plt.axes([0.13, 0.6, 0.1,0.02], facecolor=axcolor)
ax_salary_inc = plt.axes([0.13, 0.31, 0.1,0.02], facecolor=axcolor)
ax_loan_interest = plt.axes([0.13, 0.27, 0.1,0.02], facecolor=axcolor)
ax_write_off_years = plt.axes([0.13, 0.17, 0.1,0.02], facecolor=axcolor)
ax_reset = plt.axes([0.13, 0.065, 0.1, 0.04])
button_values_list = ["£80,000","£60,000","£40,000","£20,000"]
check = CheckButtons(ax=ax_check_buttons,labels=button_values_list,actives=[False]*len(button_values_list))
ax_check_buttons.annotate("Use the slider above to vary\nthe initial amount of debt, or\nuse the buttons on the left to\nsee the results for several\nstandard initial debts.", xy=(0.5, 0.5), xycoords='axes fraction', xytext=(0.43, 0.37))

[ll.set_linewidth(3) for l in check.lines for ll in l]

initial_salary_slider = Slider(ax_salary_initial, 'Initial Salary:',0,150,valinit=30,valfmt="£%d,000",orientation="horizontal",valstep=1)
initial_loan_slider = Slider(ax_loan_initial, 'Initial Debt:',0,120,valinit=45,valfmt="£%d,000",orientation="horizontal",valstep=1)
salary_increase_slider = Slider(ax_salary_inc, 'Average Annual Salary Increase:',0,10,valinit=6,valfmt="%.1f%%",orientation="horizontal",valstep=0.1)
annual_loan_interest_slider = Slider(ax_loan_interest, 'Average Annual Interest on Loan:',0,7.6,valinit=7.3,valfmt="%.1f%%",orientation="horizontal",valstep=0.1)
ax_loan_interest.annotate("(For Plan 1 and 4 Student Loans, this equals either\n BoE Base Rate + 1% or RPI, whichever is lower)\n(For Plan 2 Student Loans, this equals RPI + 3%)\n(For Plan 5 Student Loans, this equals RPI)",xy=(0.5, 0.5), xycoords='axes fraction', xytext=(-0.85, -3.5))
years_until_loan_written_off_slider = Slider(ax_write_off_years, 'Years until Loan Written-Off:',1,40,valinit=30,valfmt="%d Years",orientation="horizontal",valstep=1)
ax_write_off_years.annotate("(Plan 1 Student Loans are written off after 25 years)\n(Plan 2 and 4 Student Loans are written off after 30 years)\n(Plan 5 Student Loans are written off after 40 years)",xy=(0.5, 0.5), xycoords='axes fraction', xytext=(-0.85, -2.5))
def update(val):
    ax_cost.cla()
    ax_time.cla()
    annual_salary_increase = [0.01*salary_increase_slider.val]
    annual_loan_interest = 0.01* annual_loan_interest_slider.val
    initial_salary = initial_salary_slider.val
    initial_loan_array = [(initial_loan_slider.val)]
    years_until_loan_written_off = years_until_loan_written_off_slider.val
    if(check.lines[0][0].get_visible()): initial_loan_array += [80]
    if(check.lines[1][0].get_visible()): initial_loan_array += [60]
    if(check.lines[2][0].get_visible()): initial_loan_array += [40]
    if(check.lines[3][0].get_visible()): initial_loan_array += [20]

    initial_debt_and_salary_plot_data = calculate_paid_off_year_and_total_paid_array_across_initial_debt_and_salary(initial_loan_array, annual_salary_increase, overpayment_factor_array,initial_salary=initial_salary,n=annual_loan_interest,years_until_loan_written_off=years_until_loan_written_off)
    plot_interactive_line_graph_of_total_paid_array_against_overpayment_and_initial_debt(initial_debt_and_salary_plot_data[0],
                                                                             initial_debt_and_salary_plot_data[1],
                                                                             initial_debt_and_salary_plot_data[2],
                                                                             initial_debt_and_salary_plot_data[3],
                                                                             initial_debt_and_salary_plot_data[4],axis1=ax_cost,axis2=ax_time,years_until_loan_written_off=years_until_loan_written_off)

    fig.canvas.draw_idle()

salary_increase_slider.on_changed(update)
annual_loan_interest_slider.on_changed(update)
initial_salary_slider.on_changed(update)
initial_loan_slider.on_changed(update)
years_until_loan_written_off_slider.on_changed(update)
check.on_clicked(update)

reset_button = Button(ax_reset, 'Reset', color=axcolor, hovercolor='0.975')


def reset(event):
    salary_increase_slider.reset()
    annual_loan_interest_slider.reset()
    initial_salary_slider.reset()
    initial_loan_slider.reset()
    years_until_loan_written_off_slider.reset()

reset_button.on_clicked(reset)


fig.suptitle("Student Loan Calculator",fontsize=18,fontweight="bold",x=0.1)
fig.text(0.0105, .93, 'David Barton, 2024',fontsize=16, transform=fig.transFigure)
fig.text(0.0105, .91, 'Use the sliders below to input your student loan information.\n\nThe left plot shows the total amount you will pay until your\nstudent loan is fully repaid or written-off for different scenarios.\n\nThe right plot shows the number of years until your student\nloan is repaid or written-off for the same scenarios.',fontsize=11.5, transform=fig.transFigure,va="top")
fig.text(0.0105, 0.651, "Inputs",fontsize=18,fontweight="bold")
fig.text(0.32,0.001, "WHAT STUDENT LOAN PLAN AM I ON?\nStudent Finance England: Plan 1 if you started your course before Sept 2012.\n                                          Plan 2 if you started between Aug 2012 and Aug 2023.\n                                          Plan 5 if you started after July 2023.\nStudent Finance Wales:     Plan 1 if you started your course before Sept 2012.\n                                          Plan 2 if you started your course after Aug 2012.\nStudent Finance Northern Ireland: Plan 1.\nStudent Awards Agency Scotland: Plan 4.",fontsize=8)

fig.text(0.65,0.02, "PLANNED FEATURES\n\n1) Option to apply discount rates to future cash flows used to predict 'Total Paid over\n    Lifetime' in order to create a fairer picture considering the interest that could have\n    been accured on money invested rather than used to repay the loan.\n\n2) Option to change the x-axis variable (i.e. plotting against salary, initial debt, or similar).",fontsize=8)
#plt.show()