import netCDF4 as nc
import matplotlib.pyplot as plt
import numpy as np
countif=0
countelse=0
plt.rcParams["font.family"] = "Times New Roman"
plt.rcParams["figure.dpi"] = 320
plt.rcParams["figure.figsize"] = (6,4)

from propulsion import CFM56_5B3, CFM56_5B4
def saturation_vapour_pressure_water(kelvin_temp):
    # Goff Gratch Equation for Water Equilibrium Vapour Pressure
    # Input airtemp in Kelvin
    # Returns es in Pa
    if isinstance(kelvin_temp, list):
        n = len(kelvin_temp)
        es = np.zeros(n)

        for i in range(n):
            es[i] = saturation_vapour_pressure_water(kelvin_temp[i])

    else:
        celsius_temp = kelvin_temp - 273.15
        # Calculate saturation vapour pressure for water
        log_pw = 10.79574 * (1.0 - 273.16 / (celsius_temp + 273.15)) \
                 - 5.02800 * np.log10((celsius_temp + 273.15) / 273.16) \
                 + 1.50475E-4 * (1 - np.power(10, (-8.2969 * ((celsius_temp + \
                                                               273.15) / 273.16 - 1.0)))) + 0.42873E-3 * \
                 (np.power(10, (+4.76955 * (1.0 - 273.16 \
                                            / (celsius_temp + 273.15)))) - 1) + 0.78614
        es = np.power(10, log_pw) * 100 # hPa -> Pa

    return es

def saturation_vapour_pressure_ice(kelvin_temp):
    # NOT the Goff Gratch Equation for Ice Equilibrium Vapour Pressure
    # Input in Kelvin
    # Returns es in Pa

    if isinstance(kelvin_temp,list):
        n = len(kelvin_temp)
        es = np.zeros(n)

        for i in range(n):
            es[i] = saturation_vapour_pressure_ice(kelvin_temp[i])

    else:
        # Calculate saturation vapour pressure for ice
        celsius_temp = kelvin_temp - 273.15
        es = np.exp(43.494 - 6545.8/(celsius_temp+278))/((celsius_temp+868)**2)

    return es # hPa -> Pa

def saturation_vapour_pressure_ice_old(kelvin_temp):
    # Goff Gratch Equation for Ice Equilibrium Vapour Pressure
    # T input in Kelvin
    # Returns es in Pa
    if isinstance(kelvin_temp,list):
        n = len(kelvin_temp)
        es = np.zeros(n)

        for i in range(n):
            es[i] = saturation_vapour_pressure_ice_old(kelvin_temp[i])
    else:
        # Calculate saturation vapour pressure for ice
        celsius_temp = kelvin_temp - 273.15
        log_pi = - 9.09718 * (273.16 / (celsius_temp + 273.15) - 1.0) \
                 - 3.56654 * np.log10(273.16 / (celsius_temp + 273.15)) \
                 + 0.876793 * (1.0 - (celsius_temp + 273.15) / 273.16) \
                 + np.log10(6.1071)
        es = 100 * np.power(10, log_pi) # hPa -> Pa

    return es

def relative_humidity_ice(rh_water,T):
    if isinstance(T,list):
        n = len(T)

        if not isinstance(rh_water,list):
            rh_water = [rh_water] * n

        rh_ice = np.zeros(n)
        for i in range(n):
            rh_ice[i] = relative_humidity_ice(rh_water[i],T[i])

    else:
        rh_ice = rh_water * (saturation_vapour_pressure_water(T) / saturation_vapour_pressure_ice(T))

    return rh_ice

def relative_humidity_water(rh_ice,T):
    if isinstance(T,list):
        n = len(T)

        if not isinstance(rh_ice,list):
            rh_water = [rh_ice] * n

        rh_water = np.zeros(n)
        for i in range(n):
            rh_water[i] = relative_humidity_water(rh_ice[i],T[i])

    else:
        rh_water = rh_ice * (saturation_vapour_pressure_ice(T) / saturation_vapour_pressure_water(T))

    return rh_water
def pres2alt(pressure):
    '''
    Determine altitude from site pressure.

    Parameters
    ----------
    pressure : scalar or Series
        Atmospheric pressure (Pascals)

    Returns
    -------
    altitude : scalar or Series
        Altitude in meters above sea level

    Notes
    ------
    The following assumptions are made

    ============================   ================
    Parameter                      Value
    ============================   ================
    Base pressure                  101325 Pa
    Temperature at zero altitude   288.15 K
    Gravitational acceleration     9.80665 m/s^2
    Lapse rate                     -6.5E-3 K/m
    Gas constant for air           287.053 J/(kgK)
    Relative Humidity              0%
    ============================   ================

    References
    -----------

    "A Quick Derivation relating altitude to air pressure" from Portland
    State Aerospace Society, Version 1.03, 12/22/2004.

    '''

    alt = 44331.5 - 4946.62 * pressure ** (0.190263)
    return alt

def measured_relative_humidity_ice(rh,T):
    T = np.array(T)
    rh = np.array(rh)
    if (T.size!=1):
        global countif
        countif+=1
        print("IF: {}".format(countif))
        n = len(rh)
        rh_ice = []


        for i in range(n):
            rh_ice.append(measured_relative_humidity_ice(rh[i],T[i]))
    else:
        global countelse
        countelse+=1
        # T input in Kelvin
        if T<=250.15:
            # rh input is rh ice
            rh_ice = rh

        elif T>=273.15:
            # rh input is rh water
            rh_ice = relative_humidity_ice(rh,T)

        else:
            # rh input is interpolated between rh water and rh ice
            saturation_pressure_ratio = (saturation_vapour_pressure_ice(T) / saturation_vapour_pressure_water(T))
            rh_ice = (rh*23)/(273.15-T + (T-250.15)*saturation_pressure_ratio)

    return rh_ice

def determine_contrail_formation(rh_ambient,T_ambient,T_exhaust,p_exhaust):
    its = 60
    temperature_array_precise_part = np.linspace(round(T_ambient), 260, round(its * 2 / 3))
    temperature_array_imprecise_part = np.linspace(260, round(T_exhaust), round(its / 3))
    temperature_array = np.concatenate((temperature_array_precise_part, temperature_array_imprecise_part))

    p_ambient = rh_ambient * saturation_vapour_pressure_water(T_ambient)

    for T in temperature_array:
        mixing_line_gradient = (p_exhaust - p_ambient) / (T_exhaust - T_ambient)
        mixing_line_p = p_ambient + (T-T_ambient) * mixing_line_gradient
        if(mixing_line_p >= saturation_vapour_pressure_water(T)):
            print("TRUE:")
            print(mixing_line_p)
            print(saturation_vapour_pressure_water(T))
            return True
            break;
    print("FALSE")
    return False

def plt_saturation_vapour_pressures(temperature_array,rh_ambient = 0.1,T_ambient = 225,T_exhaust=700, plot_mixing_line=True):
    p_ambient = rh_ambient * saturation_vapour_pressure_water(T_ambient)

    svp_water_array = saturation_vapour_pressure_water(temperature_array)
    svp_ice_array = saturation_vapour_pressure_ice(temperature_array)

    #rh_exhaust = 0.8
    #p_exhaust = rh_exhaust * saturation_vapour_pressure_water(T_exhaust)

    plt.rcParams.update({'font.size': 12})
    p_exhaust = 1000# 0.1 * w
    plt.plot(temperature_array, svp_water_array, "k",label="Saturation vapour pressure with respect to water")
    plt.plot(temperature_array, svp_ice_array, "k-.",label="Saturation vapour pressure with respect to ice")

    plt.fill_between(temperature_array, svp_ice_array, 10000, alpha=1, fc="lightgrey",
                     label="Contrails persist if the ambient\ncondition is in this region")
    plt.fill_between(temperature_array, svp_water_array, 10000, hatch="...", alpha=0,
                     label="Contrails form if the mixing line\ncrosses through this region")
    plt.plot(T_exhaust,p_exhaust,"x",markersize=12,markeredgewidth=3,color="red")
    plt.text(T_exhaust-180,p_exhaust-15,"Exhaust Condition",color="red",fontweight="bold")

    if(plot_mixing_line):
        plt.plot([T_ambient,T_exhaust],[p_ambient,p_exhaust],color='red',lw=2,label="Mixing line")
    #plt.plot(T_ambient,p_ambient,"X",markersize=6,color="red",label="Ambient Condition")
        #plt.annotate("", xy=(T_ambient, p_ambient), xytext=(T_exhaust, p_exhaust),
        #                arrowprops=dict(color="red",lw=2,arrowstyle="->"))
        #plt.title(
        #    "Contrail Formation\n[Ambient Temperature {} K, Ambient Relative Humidity {}%]".format(T_ambient, int(np.ceil(100*rh_ambient))))

        #plt.plot(T_exhaust,p_exhaust,'rX',label="Typical Exhaust Condition")
        #plt.plot(T_ambient,p_ambient,'rX',label="Typical Ambient Condition")
    #plt.plot(230, 13, 'cX')
    #plt.plot(240, 37, 'cX')
    #plt.plot(250, 95, 'cX')
    #plt.plot(253, 103.2, 'gX')  # https://www.lyotechnology.com/images/vapor-pressure-of-ice.gif
    #plt.plot(243, 38, 'gX')  # https://www.lyotechnology.com/images/vapor-pressure-of-ice.gif
    #plt.plot(215, 1.41, 'gX')  # https://www.lyotechnology.com/images/vapor-pressure-of-ice.gif

    plt.xlim(210)
    plt.ylim(0,p_exhaust*1.1)
    plt.xlabel("Temperature [K]")
    plt.ylabel("Vapour Pressure [Pa]")

    # Reorder labels to improve formatting for report
    # get handles and labels
    #handles, labels = plt.gca().get_legend_handles_labels()
    # specify order of items in legend
    #order = [2,3,0,1]
    # add legend to plot
    #plt.legend([handles[idx] for idx in order], [labels[idx] for idx in order])
    # ---------------------------
    #plt.legend()
    plt.subplots_adjust(bottom=0.15)
    plt.show()


    plt.plot(temperature_array, svp_water_array, "k",label="Saturation vapour pressure\nwith respect to water")
    plt.plot(temperature_array, svp_ice_array, "k-.",label="Saturation vapour pressure\nwith respect to ice")
    plt.fill_between(temperature_array, svp_ice_array, 100, alpha=1, fc="lightgrey",
                     label="Contrails persist if the ambient\ncondition is in this region")
    plt.fill_between(temperature_array, svp_water_array, 100, hatch="...", alpha=0,
                     label="Contrails form if the mixing line\ncrosses through this region")

    if(plot_mixing_line):
        plt.plot(temperature_array, svp_water_array, "k")
        plt.plot(temperature_array, svp_ice_array, "k-.")
        plt.plot(T_ambient, p_ambient, "x", markersize=10, color="red",markeredgewidth=3)
        plt.text(T_ambient+1,p_ambient-0.25,"Ambient Condition",color="red",fontweight="bold")
        #plt.annotate("Exhaust\nCondition",color="red", fontweight="bold",xy=(239.8, 29.5),xytext=(234, 10),
        #                arrowprops=dict(color="red",lw=2,arrowstyle="-|>"))
    # Data points for checking
    #plt.plot(230, 13, 'cX')
    #plt.plot(240, 37, 'cX')
    #plt.plot(250, 95, 'cX')
    #plt.plot(253, 103.2, 'gX')  # https://www.lyotechnology.com/images/vapor-pressure-of-ice.gif
    #plt.plot(243, 38, 'gX')  # https://www.lyotechnology.com/images/vapor-pressure-of-ice.gif
    #plt.plot(215, 1.41, 'gX')  # https://www.lyotechnology.com/images/vapor-pressure-of-ice.gif

    xlim = 240
    ylim=35
    mixing_line_xlim = np.interp(ylim,[p_ambient,p_exhaust],[T_ambient,T_exhaust])
    if(plot_mixing_line):
        plt.plot([T_ambient, T_exhaust], [p_ambient, p_exhaust], color='red',lw=2, label="Mixing line")

        #plt.annotate("", xy=(T_ambient, p_ambient), xytext=(mixing_line_xlim, ylim),
        #                arrowprops=dict(color="red",lw=2,arrowstyle="->"))

        #plt.title("Hydrogen Aircraft: Contrail Formation and Persistence\n[Ambient Temperature {} K, Ambient Relative Humidity {}%]".format(T_ambient, int(np.ceil(100*rh_ambient))))

    #plt.plot(T_ambient,p_ambient,"r+",label="Ambient Condition")
    #plt.text(223, 20, "Contrails Form if mixing\nline crosses into this region", color="b",horizontalalignment="center")
    #plt.text(233, 5, "Contrails Persist if ambient\ncondition is in this region", color="k",horizontalalignment="center")
    #mixing_line = plt.annotate("", xy=(239, 31.5), xytext=(248, 17),
    #                           arrowprops=dict(color="k",arrowstyle="->"))
    plt.xlim(210,xlim)
    plt.ylim(0,ylim)
    plt.xlabel("Temperature [K]")
    plt.ylabel("Vapour Pressure [Pa]")

    plt.legend(framealpha=1)
    plt.subplots_adjust(bottom=0.15)
    plt.show()


def plt_contrail_formation_vs_ambient_conditions(p_exhaust = 800,T_exhaust = 640):
    ambient_temperature_array = np.linspace(200,300,21)
    rh_ambient_array = np.linspace(0,1,5)

    for rh_ambient in rh_ambient_array:
        contrail_formation_array = np.zeros(len(ambient_temperature_array))
        for i, T_ambient in enumerate(ambient_temperature_array):
            p_ambient = rh_ambient * saturation_vapour_pressure_water(T_ambient)
            contrail_formation_array[i] = determine_contrail_formation(p_ambient,T_ambient,T_exhaust,p_exhaust)
        plt.plot(ambient_temperature_array, contrail_formation_array,"--",label="Ambient Relative Humidity = {}".format(rh_ambient))

    plt.xlabel("Ambient Temperature [K]")
    plt.ylabel("Contrail Formation Probability")
    plt.legend()
    plt.title(
        "Contrail Formation vs Ambient Conditions\n[Exhaust Temperature {}, Exhaust Vapour Pressure {}]".format(T_exhaust, p_exhaust))
    plt.show()

def plt_contrail_formation_vs_exhaust_conditions(rh_ambient = 0.8,T_ambient = 225):
    plt.rcParams.update({'font.size': 13})
    exhaust_temperature_array = np.linspace(500,800,60)
    p_ambient = rh_ambient * saturation_vapour_pressure_water(T_ambient)
    p_exhaust_array = np.linspace(600,1200,100)

    contrail_formation_grid = np.zeros((len(exhaust_temperature_array),len(p_exhaust_array)))

    for j, p_exhaust in enumerate(p_exhaust_array):
        for i, T_exhaust in enumerate(exhaust_temperature_array):
            contrail_formation_grid[i,j] = determine_contrail_formation(rh_ambient,T_ambient,T_exhaust,p_exhaust)
        plt.plot(exhaust_temperature_array, contrail_formation_grid[:,j],"--",label="Exhaust Vapour Pressure = {} Pa".format(p_exhaust))

    plt.xlabel("Engine Exhaust Temperature [K]")
    plt.ylabel("Contrail Formation Probability")
    plt.legend()
    plt.title(
        "Contrail Formation vs Exhaust Conditions\n[Ambient Temperature {}, Ambient Relative Humidity {}]".format(T_ambient, rh_ambient))
    plt.show()

    # Contour Plot!
    cont = plt.contourf(p_exhaust_array, exhaust_temperature_array, contrail_formation_grid, levels=[0,0.5,1], colors=["white","tab:blue"])
    #c_bar = plt.colorbar(cont, shrink=0.8)
    #c_bar.set_label("Predicted Contrail Formation")
    plt.plot([],color="tab:blue",label="Contrails Form in Blue Regions ")
    plt.plot([],color="white",label="Contrails do not Form in White Regions")
    plt.ylabel("Engine Exhaust Temperature [K]")
    plt.xlabel("Exhaust Vapour Pressure [Pa]")
    plt.plot(1000,700,"rx",markersize=16,markeredgewidth=3,label="Typical Aircraft Exhaust")
    #plt.text(890,660,"Typical Aircraft Exhaust",color="r",weight="bold")
    plt.subplots_adjust(bottom=.15)
    plt.legend(loc="lower right")
    plt.show()

def plt_contrail_formation_vs_Mach(rh_ambient = 0.8,T_ambient = 225):
    plt.rcParams.update({'font.size': 13})
    Mach_array = np.linspace(0,1,80)
    p_ambient = rh_ambient * saturation_vapour_pressure_water(T_ambient)
    p_exhaust_array = np.linspace(600,1200,100)

    contrail_formation_grid = np.zeros((len(Mach_array),len(p_exhaust_array)))

    for j, p_exhaust in enumerate(p_exhaust_array):
        for i, Mach in enumerate(Mach_array):
            T_exhaust = CFM56_5B3.T5(Mach)
            contrail_formation_grid[i,j] = determine_contrail_formation(rh_ambient,T_ambient,T_exhaust,p_exhaust)
        plt.plot(Mach_array, contrail_formation_grid[:,j],"--",label="Exhaust Vapour Pressure = {} Pa".format(p_exhaust))

    plt.xlabel("Mach Number")
    plt.ylabel("Contrail Formation Probability")
    plt.legend()
    plt.title(
        "Contrail Formation vs Exhaust Conditions\n[Ambient Temperature {}, Ambient Relative Humidity {}]".format(T_ambient, rh_ambient))

    plt.show()

    # Contour Plot!
    cont = plt.contourf(p_exhaust_array, Mach_array, contrail_formation_grid, levels=[0,0.5,1], colors=["white","tab:blue"])
    #c_bar = plt.colorbar(cont, shrink=0.8)
    #c_bar.set_label("Predicted Contrail Formation")
    plt.plot([],color="tab:blue",label="Contrails Form in Blue Regions ")
    plt.plot([],color="white",label="Contrails do not Form in White Regions")
    plt.ylim(.35,1)
    plt.ylabel("Mach Number")
    plt.xlabel("Exhaust Vapour Pressure [Pa]")
    plt.plot(1000, 0.75, "rx", markersize=16, markeredgewidth=3,label="Typical Aircraft Exhaust")
    #plt.text(860, 0.6, "Typical Aircraft Exhaust",color='r',weight="bold")
    plt.subplots_adjust(bottom=.15)
    plt.legend(loc="upper right")
    plt.show()

if __name__ == "__main__":
    #print(saturation_vapour_pressure(250)
    T = 215

    print("\nSaturation Vapour Pressure Water: {}".format(saturation_vapour_pressure_water(T))) # Uses air temp in Celsius not Kelvin


    print("\nSaturation Vapour Pressure Ice: {}".format(saturation_vapour_pressure_ice(T)))  # Uses air temp in Celsius not Kelvin

    its = 120
    temperature_array_precise_part = np.linspace(200,300,round(its*5/6))
    temperature_array_imprecise_part = np.linspace(300,700,round(its/6))
    temperature_array = np.concatenate((temperature_array_precise_part,temperature_array_imprecise_part))

    plt_saturation_vapour_pressures(temperature_array,plot_mixing_line=True)
    rh_array = np.linspace(0,1,3)
    for rh in rh_array:
        rh = round(rh,2)
        #plt_saturation_vapour_pressures(temperature_array,rh_ambient=rh)

    #plt_contrail_formation_vs_Mach(rh_ambient=0.5,T_ambient=225)
    #plt_contrail_formation_vs_exhaust_conditions(rh_ambient=0.5,T_ambient=225)
    #plt_contrail_formation_vs_ambient_conditions()

    '''
    plt.plot(temperature_array,relative_humidity_ice(.5,temperature_array),label="RH w.r.t Water = 50%")
    plt.plot(temperature_array,relative_humidity_ice(1.,temperature_array),label="RH w.r.t Water = 100%")
    plt.plot(temperature_array,relative_humidity_ice(1.5,temperature_array),label="RH w.r.t Water = 150%")
    plt.xlabel("Temperature [K]")
    plt.ylabel("Relative Humidity w.r.t Ice")
    plt.legend()
    plt.show()

    temperature_array = np.linspace(250,273,its)
    plt.plot(temperature_array,saturation_vapour_pressure_water(temperature_array)/saturation_vapour_pressure_ice(temperature_array))
    plt.xlabel("Temperature [K]")
    plt.title("Ratio of Relative Humidity w.r.t Ice and Relative Humidity w.r.t Water")
    plt.xlim(250,273)
    plt.ylim(1,1.25)
    plt.show()
    '''
