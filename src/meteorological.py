import netCDF4 as nc
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib as mpl
from ambiance import Atmosphere
import numpy as np
from saturation_pressures import measured_relative_humidity_ice,saturation_vapour_pressure_water,saturation_vapour_pressure_ice,relative_humidity_ice,saturation_vapour_pressure_ice_old, pres2alt, relative_humidity_water
from issr import alt2fl, fl2alt
import cartopy.crs as ccrs
import csv
style_reference = ["-","--","-.",":"]
years = ["2017","2018","2016"]
months = ["Jan", "Feb", "March", "April", "May", "June", "July", "Aug", "Sept", "Oct", "Nov", "Dec"]
issr_limits = ["90"]#,"100"]#95

plt.rcParams.update({'font.size': 12})

# For creating default alt list (using year 2018)
year = 2018
default_alt_file = "data/meteorological/relative_humidity_and_temperature_monthly_mean_{}_full.nc".format(year)
default_alt_ds = nc.Dataset(default_alt_file)  # 12 [months], 14 [levels], 180 [latitude], 360 [longitude])

pressure_levels = default_alt_ds['level'][:]
relative_humidity = default_alt_ds['r'][:]
temperature = default_alt_ds['t'][:]

pressure_level_ids = range(len(pressure_levels))
alt = np.zeros(len(pressure_levels))
fl = np.zeros(len(pressure_levels))

for i, pressure_level in enumerate(pressure_levels):
    alt[i] = pres2alt(pressure_level * 100) / 1000  # Pressure level hPa -> Pa, then m -> km
    fl[i] = alt2fl(alt[i] * 1000)

def plt_meteorological_contours(input_variable,variable_name,month,pressure_level_id,title=None,unit="",cmap='viridis',levels=None,ylimit=None,longitude_averaging=False,alt_plotting=True):
    if title == None: title = variable_name
    mpl.rcParams['axes.prop_cycle'] = plt.cycler("color", plt.cm.coolwarm(np.linspace(0,1,5)))
    if (type(pressure_level_id)!=int):
        pressure_iterating = True
        month_iterating = False

        # List of Pressure Levels
        pressure_level = pressure_levels[pressure_level_id[0]]
        variable = np.array(input_variable)[months.index(month)]
        pressure_level_id_to_plot = pressure_level_id[0] # Initial
        month_id_to_plot = 0 # Initial (but always, as no month iterating if pressure iterating)
    elif (type(month)!=str):
        pressure_iterating = False
        month_iterating = True

        pressure_level = pressure_levels[pressure_level_id]
        variable = np.array(input_variable)[:,pressure_level_id]
        pressure_level_id_to_plot = pressure_level_id # Initial
        month_id_to_plot = 0 # Initial
    else:
        pressure_iterating = False
        month_iterating = False

        pressure_level = pressure_levels[pressure_level_id]
        pressure_level_id_to_plot = pressure_level_id
        variable = np.array(input_variable)[months.index(month),pressure_level_id]
    alt_current = alt[pressure_level_id_to_plot]
    fl_current = int(round(fl[pressure_level_id_to_plot], -1))

    crs = ccrs.PlateCarree()

    if (not pressure_iterating) and (not month_iterating):
        # A single plot
        fig = plt.figure(figsize=(7.5, 6))
        ax = plt.axes(projection = crs)
        ax.set_anchor('C')
        ax.coastlines(resolution='110m',color='k',linewidth=1)

        if not alt_plotting:
            plt.title("{}\n(Altitude {:.1f} km, FL{}) in {} {}".format(title, alt_current, fl_current, month, year))
        else:
            plt.title("{}\nAltitude {:.1f} km in {} {}".format(title, alt_current, month, year))

        variable_to_plot = variable

        xgrid, ygrid = np.meshgrid(np.arange(360), np.arange(181))
        ygrid -= 90
        xgrid-=180
        cont = plt.contourf(xgrid, ygrid, variable_to_plot,cmap=cmap,levels=levels)
        c_bar = plt.colorbar(cont,shrink=0.8)
        c_bar.set_label(unit)
        plt.xlim(-180, 180)
        plt.ylim(-90, 90)
        plt.yticks(np.arange(-90, 91, step=45))
        plt.xticks(np.arange(-180, 181, step=45))
        plt.xlabel("Longitude")
        plt.ylabel("Latitude [{}]".format(chr(176)))
        plt.show()

    else:
        # A GIF of plots
        fig = plt.figure(figsize=(7.5, 7.5))
        ax1 = plt.subplot(211,projection=crs)
        ax1.set_anchor('C')
        ax2 = plt.subplot(212)
        ax1.coastlines(resolution='110m', color='k', linewidth=0.5)

        if not alt_plotting:
            ax1.set_title("{}\n(Altitude {:.1f} km, FL{}) in {} {}".format(title, alt_current, fl_current, months[month_id_to_plot], year))
        else:
            ax1.set_title("{}\nAltitude {:.1f} km in {} {}".format(title, alt_current, months[month_id_to_plot], year))

        xgrid, ygrid = np.meshgrid(np.arange(360), np.arange(181))
        ygrid -= 90
        xgrid -= 180

        if pressure_iterating:
            variable_to_plot = variable[pressure_level_id_to_plot]
            framecount = len(pressure_level_id)

            # Plot Global Average Line
            average_for_each_level = np.zeros(len(pressure_level_id))  # One Average for Each Level
            for index, pressure_level_id_individual in enumerate(pressure_level_id):
                ave = np.average(variable[pressure_level_id_individual])  # Month doesn't need included here as 'variable' already factors that in
                average_for_each_level[index] = ave
            if not alt_plotting: ax2.plot(fl,average_for_each_level,'k-.',label="Global Average")
            else: ax2.plot(alt,average_for_each_level,'k-.',label="Global Average")
            if(variable_name=="Temperature"):
                # Compare with ISA
                atm = Atmosphere(alt * 1000) # km -> m
                ISA_temp_for_each_level = atm.temperature
                if not alt_plotting: ax2.plot(fl, ISA_temp_for_each_level, 'r-.', label="ISA Temperature")
                else:  ax2.plot(alt, ISA_temp_for_each_level, 'r-.', label="ISA Temperature")
                ax2.legend()

            if not alt_plotting: current_marker = ax2.plot(fl_current,average_for_each_level[pressure_level_id_to_plot],'bx',markersize=10)
            else: current_marker = ax2.plot(alt_current,average_for_each_level[pressure_level_id_to_plot],'bx',markersize=10)

            # Plot lines of fixed Latitude (averaged across all Longitudes)
            if longitude_averaging:
                latitudes = [-60,-30,0,30,60]
                for latitude in latitudes:
                    latitude_index = latitude + 90
                    average_for_each_level2 = np.zeros(len(pressure_level_id))  # One Average for Each Level, for Each Latitude
                    for index, pressure_level_id_individual in enumerate(pressure_level_id):
                        ave = np.average(variable[pressure_level_id_individual,latitude_index])  # average for a given latitude across all longitudes
                        average_for_each_level2[index] = ave
                    if not alt_plotting: ax2.plot(fl, average_for_each_level2, label="Latitude {}".format(latitude))
                    else:  ax2.plot(alt, average_for_each_level2, label="Latitude {}".format(latitude))
                ax2.legend()

            if not alt_plotting: ax2.set_xlabel("Flight Level")
            else: ax2.set_xlabel("Altitude [km]")
            ax2.set_ylabel("Global Average {} {}".format(variable_name,unit))
        elif month_iterating:
            variable_to_plot = variable[month_id_to_plot]
            framecount = len(month)

            # Plot Global Average line
            average_for_each_month = np.zeros(len(month))  # One Average for Each Month
            for index, month_individual in enumerate(month):
                ave = np.average(variable[index])  # Pressure level doesn't need included here as 'variable' already factors that in
                average_for_each_month[index] = ave
            ax2.plot(month, average_for_each_month,'k-.',label="Global Average")

            current_marker = ax2.plot(month[month_id_to_plot], average_for_each_month[month_id_to_plot], 'bx',markersize=10)

            # Plot lines of fixed Latitude (averaged across all Longitudes)
            if longitude_averaging:
                latitudes = [-60,-30,0,30,60]
                for latitude in latitudes:
                    latitude_index = latitude+90
                    average_for_each_month2 = np.zeros(len(month))  # One Average for Each Month, for Each Latitude
                    for index, month_individual in enumerate(month):
                        ave = np.average(variable[index,latitude_index]) #average for a given latitude across all longitudes
                        average_for_each_month2[index] = ave
                    ax2.plot(month, average_for_each_month2,label="Latitude {}".format(latitude))
                ax2.legend()

            ax2.set_xlabel("Month")
            ax2.set_ylabel("Global Average {} {}".format(variable_name,unit))
        if(ylimit!=None): ax2.set_ylim(ylimit)
        cont = ax1.contourf(xgrid, ygrid, variable_to_plot, cmap=cmap, levels=levels)
        c_bar = plt.colorbar(cont,shrink=0.8,ax=ax1)
        c_bar.set_label("ISSR Frequency " + unit)
        ax1.set_xlim(-180, 180)
        ax1.set_ylim(-90, 90)
        ax1.set_yticks(np.arange(-90, 91, step=45))
        ax1.set_xticks(np.arange(-180, 181, step=45))
        ax1.set_xlabel("Longitude")
        ax1.set_ylabel("Latitude [{}]".format(chr(176)))

        def animate(i):
            nonlocal cont, pressure_level_id_to_plot, month_id_to_plot, pressure_iterating, month_iterating, current_marker, average_for_each_level

            if pressure_iterating:
                pressure_level_id_to_plot = pressure_level_id[i]
                pressure_level = pressure_levels[pressure_level_id_to_plot]
                month_i = month
                variable_to_plot = variable[pressure_level_id_to_plot]
                (current_marker.pop()).remove()
                if not alt_plotting: current_marker = ax2.plot(fl[pressure_level_id_to_plot],average_for_each_level[pressure_level_id_to_plot],'bo',markersize=10)
                else: current_marker = ax2.plot(alt[pressure_level_id_to_plot],average_for_each_level[pressure_level_id_to_plot],'bo',markersize=10)
            elif month_iterating:
                pressure_level = pressure_levels[pressure_level_id_to_plot]
                month_id_to_plot = i
                month_i = month[month_id_to_plot]
                variable_to_plot = variable[month_id_to_plot]
                (current_marker.pop()).remove()
                current_marker = ax2.plot(month_i, average_for_each_month[month_id_to_plot], 'bo', markersize=10)

            alt_current = alt[pressure_level_id_to_plot]
            fl_current = int(round(fl[pressure_level_id_to_plot], -1))

            for c in cont.collections:
                c.remove()  # removes only the contours, leaves the rest intact
            cont = ax1.contourf(xgrid, ygrid, variable_to_plot, cmap=cmap, levels=levels)
            # Old Title with Pressure
            # ax1.set_title("{} {}{}, {}\n{} hPa ({:.1f} km, FL{})".format(year,variable_name,unit,month_i,pressure_level,alt_current,fl_current))
            if not alt_plotting: ax1.set_title("{}\n(Altitude {:.1f} km, FL{}) in {} {}".format(title,alt_current,fl_current,month_i,year))
            else: ax1.set_title("{}\nAltitude {:.1f} km in {} {}".format(title,alt_current,month_i,year))
            return cont

        ani = animation.FuncAnimation(fig, animate, frames=framecount, interval=800, repeat=False)

        if(longitude_averaging): extra_string = "_for_latitudes"
        else: extra_string = ""
        spaceless_variable_name = variable_name.replace(" ","_")
        if(month_iterating): filelocation = "figures/{}/{}/Fixed Altitude/{}_{}_hPa{}.gif".format(year,variable_name,spaceless_variable_name,pressure_level,extra_string)
        elif(pressure_iterating): filelocation = "figures/{}/{}/Fixed Month/{}_{}{}{}.gif".format(year,variable_name,spaceless_variable_name,months.index(month),month,extra_string)
        ani.save(filelocation)
        plt.show()

def plt_meteorological_against_altitude_for_varying_latitude(variable,variable_name,title,unit="",alt_plotting=False,latitudes_lists=None):
    spaceless_variable_name = variable_name.replace(" ", "_")
    if(latitudes_lists == None): latitudes_lists = [[-80,-60,-50,-40,-30,-20,-10,0],[80,60,50,40,30,20,10,0],["average"]]
    mpl.rcParams['axes.prop_cycle'] = plt.cycler("color",plt.cm.gist_gray(np.linspace(0, 1, 5)))

    plt.rcParams.update({'font.size': 15})
    for index, latitudes in enumerate(latitudes_lists): # i.e: Northern Hemisphere or Southern Hemisphere
        fig = plt.figure(figsize=(6.5, 6))
        if(index==0): hemisphere = "Southern Hemisphere, Averaged across all Months"
        elif(index==1): hemisphere = "Northern Hemisphere, Averaged across all Months"
        else: hemisphere = "Averaged across all Longitudes and Months"

        variable_longitude_averaged = np.zeros((12,14,181))
        for x in range(len(variable_longitude_averaged)):
            for y in range(len(variable_longitude_averaged[x])):
                for z in range(len(variable_longitude_averaged[x,y])):
                    variable_longitude_averaged[x,y,z] = np.mean(variable[x,y,z])

        variable_longitude_and_month_averaged = np.zeros((14,181))
        for x in range(len(variable_longitude_and_month_averaged)):
            for y in range(len(variable_longitude_and_month_averaged[x])):
                variable_longitude_and_month_averaged[x,y] = np.mean(variable_longitude_averaged[:,x,y])
        for latitude in latitudes:
            if(latitude!="average"):
                latitude_index = latitude + 90
                variable_to_plot = variable_longitude_and_month_averaged[:,latitude_index]
                plt.legend()
            else:
                # Average across all latitudes
                variable_to_plot = np.average(variable_longitude_and_month_averaged,axis=1)
            if not alt_plotting:
                if(latitude=="average"):
                    plt.xlim(290,410)

                    plt.plot(fl, variable_to_plot, label="Global Average".format(latitude), marker='x', color='k',markersize=12)

                    plt.plot(fl, variable_longitude_and_month_averaged[:,170], lc="tab:blue",label="Arctic (Lat 80{})".format(latitude,chr(176)),
                             marker='x',markersize=12)
                    plt.plot(fl, variable_longitude_and_month_averaged[:,90], lc="red",label="Equator (Lat 0)".format(latitude),
                             marker='x',markersize=12)
                    plt.plot(fl, variable_longitude_and_month_averaged[:,10], lc="blue",label="Antarctic (Lat -80)".format(latitude),
                             marker='x',markersize=12)
                else: plt.plot(fl, variable_to_plot, label="Latitude {}".format(latitude),marker='x')

            else:
                if(latitude=="average"):
                    plt.xlim(6,14.5)
                    plt.plot(alt, variable_to_plot, label="Global Average".format(latitude), marker='o',markersize=8)

                    plt.plot(alt, variable_longitude_and_month_averaged[:,170],color="tab:blue", label="Arctic (Lat 80)".format(latitude),
                             marker='^',markersize=8)
                    plt.plot(alt, variable_longitude_and_month_averaged[:,90],color="red", label="Equator (Lat 0)".format(latitude),
                             marker='s',markersize=8)
                    plt.plot(alt, variable_longitude_and_month_averaged[:,10],color="blue",
                             label="Antarctic (Lat -80)".format(latitude),
                             marker='v',markersize=8)
                else: plt.plot(alt,variable_to_plot,label="Latitude {}".format(latitude),marker='x')

        #plt.title(year)
        plt.title("{}\n{} in {}".format(title,hemisphere,year))
        plt.ylabel(variable_name+unit)
        if not alt_plotting: plt.xlabel("Flight Level")
        else: plt.xlabel("Altitude [km]")
        plt.ylim(0,50)
        plt.legend()
        plt.savefig("figures/{}/{}_averaged_plot_for_latitudes_{}.png".format(year,spaceless_variable_name,hemisphere))

        plt.show()

def return_meteorological_against_altitude_for_given_latitude(variable,variable_name,title,unit="",alt_plotting=False,latitude=0):

    variable_longitude_averaged = np.zeros((12,14,181))
    for x in range(len(variable_longitude_averaged)):
        for y in range(len(variable_longitude_averaged[x])):
            for z in range(len(variable_longitude_averaged[x,y])):
                variable_longitude_averaged[x,y,z] = np.mean(variable[x,y,z])

    variable_longitude_and_month_averaged = np.zeros((14,181))
    for x in range(len(variable_longitude_and_month_averaged)):
        for y in range(len(variable_longitude_and_month_averaged[x])):
            variable_longitude_and_month_averaged[x,y] = np.mean(variable_longitude_averaged[:,x,y])

    if(latitude!="average"):
        latitude_index = latitude + 90
        variable_to_plot = variable_longitude_and_month_averaged[:,latitude_index]
    else:
        # Average across all latitudes
        variable_to_plot = np.average(variable_longitude_and_month_averaged,axis=1)

    return variable_to_plot, alt



def plt_meteorological_against_altitude_for_varying_month(variable,variable_name,title,latitude,unit="",alt_plotting=False):
    mpl.rcParams['axes.prop_cycle'] = plt.cycler("color", plt.cm.gist_gray(np.linspace(0, 1, 5)))

    spaceless_variable_name = variable_name.replace(" ", "_")
    latitude_index = latitude+90
    fig = plt.figure(figsize=(6.5, 6))

    # Average Across Longitudes
    variable_longitude_averaged = np.zeros((12,14,181))
    for x in range(len(variable_longitude_averaged)):
        for y in range(len(variable_longitude_averaged[x])):
            for z in range(len(variable_longitude_averaged[x,y])):
                variable_longitude_averaged[x,y,z] = np.mean(variable[x,y,z])

    for month_index,month in enumerate(months):
        variable_to_plot = variable_longitude_averaged[month_index,:,latitude_index]
    if not alt_plotting:
        plt.plot(fl,variable_to_plot,label="{}".format(month))
        if (latitude == "Average"): plt.xlim(8.5, 12.5)
    else:
        plt.plot(alt,variable_to_plot,label="{}".format(month))
        if (latitude == "Average"): plt.xlim(290, 410)

    plt.title("{}\n{}: Latitude {}".format(title,year, latitude))
    plt.ylabel(variable_name+unit)
    if not alt_plotting: plt.xlabel("Flight Level")
    else: plt.xlabel("Altitude [km]")
    plt.ylim(0,50)
    plt.legend()
    plt.savefig("figures/{}/{}_averaged_plot_for_months_latitude_{}.png".format(year,spaceless_variable_name,latitude))

    plt.show()

def plt_meteorological_against_latitude_for_varying_altitude(variable,variable_name,title,unit="",alt_plotting = False,plot_only_operating_altitudes=False):
    spaceless_variable_name = variable_name.replace(" ", "_")
    fig = plt.figure(figsize=(9, 4))
    flight_levels = fl
    latitudes = np.arange(-90,91,1)
    mpl.rcParams['axes.prop_cycle'] = plt.cycler("color", plt.cm.gist_gray(np.linspace(0, 1, 2+len(flight_levels[::2]))))

    variable_longitude_averaged = np.zeros((12,14,181))
    for x in range(len(variable_longitude_averaged)):
        for y in range(len(variable_longitude_averaged[x])):
            for z in range(len(variable_longitude_averaged[x,y])):
                variable_longitude_averaged[x,y,z] = np.mean(variable[x,y,z])

    variable_longitude_and_month_averaged = np.zeros((14,181))
    for x in range(len(variable_longitude_and_month_averaged)):
        for y in range(len(variable_longitude_and_month_averaged[x])):
            variable_longitude_and_month_averaged[x,y] = np.mean(variable_longitude_averaged[:,x,y])

    for i, fl_it in enumerate(flight_levels[::2]):
        pressure_level_id_it = int(np.where(fl==fl_it)[0])
        print(pressure_level_id_it)
        variable_to_plot = variable_longitude_and_month_averaged[pressure_level_id_it]
        linestyle = style_reference[i % len(style_reference)]
        if(not plot_only_operating_altitudes):
            if not alt_plotting: plt.plot(latitudes,variable_to_plot,linestyle=linestyle,label="FL{}".format(int(round(fl_it,-1))))
            else: plt.plot(latitudes,variable_to_plot,linestyle=linestyle,label="{} km".format(round((fl2alt(fl_it)/1000),1)))
        else:
            if(i==1):
                variable_to_plot_dashed1 = np.ma.masked_where(latitudes > 35, variable_to_plot)
                latitudes_dashed1 = np.ma.masked_where(latitudes > 35, latitudes)
                variable_to_plot_dashed = np.ma.masked_where(latitudes_dashed1 < -35, variable_to_plot_dashed1)
                latitudes_dashed = np.ma.masked_where(latitudes_dashed1 < -35, latitudes_dashed1)

                latitudes_solid = np.ma.masked_where((35 > latitudes) & (-35 < latitudes), latitudes)
                variable_to_plot_solid = np.ma.masked_where((35 > latitudes) & (-35 < latitudes), variable_to_plot)
                plt.plot(latitudes_solid, variable_to_plot_solid, "b",
                         label="{} km [Non-Equatorial]".format(round((fl2alt(fl_it) / 1000), 1)))
                plt.plot(latitudes_dashed, variable_to_plot_dashed, "b--")

            elif(i==3): plt.plot(latitudes, variable_to_plot, "k",
                     label="{} km [Conventional]".format(round((fl2alt(fl_it) / 1000), 1)))
            elif(i==5):
                variable_to_plot_solid1 = np.ma.masked_where(latitudes>25,variable_to_plot)
                latitudes_solid1 = np.ma.masked_where(latitudes>25,latitudes)
                variable_to_plot_solid = np.ma.masked_where(latitudes_solid1<-25,variable_to_plot_solid1)
                latitudes_solid = np.ma.masked_where(latitudes_solid1<-25,latitudes_solid1)

                latitudes_dashed = np.ma.masked_where((25>latitudes) & (-25<latitudes), latitudes)
                variable_to_plot_dashed = np.ma.masked_where((25>latitudes) & (-25<latitudes), variable_to_plot)
                plt.plot(latitudes_solid, variable_to_plot_solid, "r",label="{} km [Equatorial]".format(round((fl2alt(fl_it) / 1000), 1)))
                plt.plot(latitudes_dashed, variable_to_plot_dashed, "r--")

    #plt.title("{}\nAveraged across all Longitudes and Months in {}".format(title,year))
    plt.ylabel(variable_name+unit)
    plt.xlabel("Latitude [{}]".format(chr(176)))
    plt.ylim(0,50)
    plt.xlim(-90,90)

    if (plot_only_operating_altitudes):
        plt.fill_between((-90,-35),100,0,alpha=0.3,color="tab:blue")
        plt.fill_between((90,35),100,0,alpha=0.3,color="tab:blue")
        plt.fill_between((-25,25),100,0,alpha=0.3,color="tab:red")
        plt.axvline(-25)
        plt.axvline(25)
        plt.axvline(-35)
        plt.axvline(35)
    plt.legend(loc="upper left",title="Altitude",framealpha=1)
    plt.subplots_adjust(bottom=.15)
    plt.savefig("figures/{}/{}_averaged_plot_for_altitudes.png".format(year, spaceless_variable_name))

    plt.show()


def plt_meteorological_contour_averaged_month_and_longitude(variable,variable_name,title,unit="",cmap='Blues',levels=None):
    spaceless_variable_name = variable_name.replace(" ", "_")
    fig = plt.figure(figsize=(8, 6))
    flight_levels = fl
    latitudes = np.arange(-90,91,1)

    plt.rcParams.update({'font.size': 17})
    variable_longitude_averaged = np.zeros((12,14,181))
    for x in range(len(variable_longitude_averaged)):
        for y in range(len(variable_longitude_averaged[x])):
            for z in range(len(variable_longitude_averaged[x,y])):
                variable_longitude_averaged[x,y,z] = np.mean(variable[x,y,z])

    variable_longitude_and_month_averaged = np.zeros((14,181))
    for x in range(len(variable_longitude_and_month_averaged)):
        for y in range(len(variable_longitude_and_month_averaged[x])):
            variable_longitude_and_month_averaged[x,y] = np.mean(variable_longitude_averaged[:,x,y])

    cont = plt.contourf(latitudes, alt, variable_longitude_and_month_averaged, cmap=cmap, levels=levels)

    file_name = "csv Mean ISSR Frequency against Lat-Alt in " + str(year) + " with threshold " + str(issr_limit)
    file_title = file_name + ".csv"
    np.savetxt(file_name,variable_longitude_and_month_averaged,delimiter=",")
    np.savetxt("csv Altitudes",alt,delimiter=",")
    np.savetxt("csv Latitudes",latitudes,delimiter=",")
    #with open(file_title,"w+") as my_csv:
        #csvWriter = csv.writer(my_csv,delimiter=',')
        #csvWriter.writerows(variable_longitude_and_month_averaged)

    c_bar = plt.colorbar(cont, shrink=0.8)
    c_bar.set_label(variable_name+unit)
    #plt.title("{}\nAveraged across all Longitudes and Months in {}".format(title, year))
    plt.title(year)
    plt.ylabel("Altitude [km]")
    plt.xlabel("Latitude [{}]".format(chr(176)))
    plt.savefig("figures/{}/{}_contour_plot_averaged_across_month_and_longitude.png".format(year, spaceless_variable_name))
    plt.xticks([-90,-60,-30,0,30,60,90])
    #plt.axhline(10.9,color="k",lw=3)
    #plt.hlines(14,-90,-35,color="b",lw=3)
    #plt.hlines(14,35,90,color="b",lw=3)
    #plt.hlines(14,-35,35,color="b",linestyle=":")
    #plt.hlines(6,-25,25,color="r",lw=3)
    #plt.hlines(6,-90,-25,color="r",linestyle=":")
    #plt.hlines(6,25,90,color="r",linestyle=":")
    #plt.text(-80,14.2,"Non-Equatorial Low-Contrails Altitude",color="b")
    #plt.text(-80,11.1,"Typical Conventional Cruise Altitude",color="k")
    #plt.text(-80,6.2,"Equatorial Low-Contrails Altitude",color="r")
    plt.show()

if __name__ == "__main__":
    for year in years:
        file = "data/meteorological/relative_humidity_and_temperature_monthly_mean_{}_full.nc".format(year)
        ds = nc.Dataset(file)  # 12 [months], 14 [levels], 180 [latitude], 360 [longitude])

        pressure_levels = ds['level'][:]
        relative_humidity = ds['r'][:]
        temperature = ds['t'][:]

        pressure_level_ids = range(len(pressure_levels))
        alt = np.zeros(len(pressure_levels))
        fl = np.zeros(len(pressure_levels))

        for i, pressure_level in enumerate(pressure_levels):
            alt[i] = pres2alt(pressure_level * 100) / 1000  # Pressure level hPa -> Pa, then m -> km
            fl[i] = alt2fl(alt[i] * 1000)
        print("ALT: {}".format(alt))
        relative_humidity_ice = np.load("data/meteorological/relative_humidity_ice_monthly_mean_{}_full.npy".format(year))
        relative_humidity_delta = abs(relative_humidity - relative_humidity_ice)

        for issr_limit in issr_limits:


            issr_freq_percentage = np.load("data/meteorological/issr_freq_{}%_monthly_total_{}_full.npy".format(issr_limit, year))


            ice_supersaturation = relative_humidity_ice/100
            ice_supersaturation = np.where(ice_supersaturation<=.8,0,ice_supersaturation)

            # Plot RH Ice averaged by Month and Longitude
            levels = range(0, 105, 5)
            #plt_meteorological_contour_averaged_month_and_longitude(relative_humidity_ice,"Relative Humidity",title="Relative Humidity with respect to Ice",unit="[%]", levels=levels,cmap="winter")
            # Plot ISSR Freq averaged by Month and Longitude
            levels = range(0,64,2)
            plt_meteorological_contour_averaged_month_and_longitude(issr_freq_percentage,"ISSR Frequency",title="Frequency of Contrail Persistence Regions (RH Ice > {}%)".format(issr_limit), unit =" [%]",levels=levels)

            levels = range(0,85,5)#plt_meteorological_against_latitude_for_varying_altitude(issr_freq_percentage,"ISSR Frequency",title="Frequency of Contrail Persistence Regions (RH Ice > {}%)".format(issr_limit), unit=" [%]",alt_plotting=True)
            #plt_meteorological_against_altitude_for_varying_latitude(issr_freq_percentage, "ISSR Frequency",title="Frequency of Contrail Persistence Regions (RH Ice > {}%)".format(issr_limit), unit=" [%]",alt_plotting=True)
            #plt_meteorological_against_latitude_for_varying_altitude(issr_freq_percentage, "ISSR Frequency",plot_only_operating_altitudes=False,title="Frequency of Contrail Persistence Regions (RH Ice > {}%)".format(issr_limit), unit=" [%]",alt_plotting=True)
            #plt_meteorological_against_latitude_for_varying_altitude(issr_freq_percentage, "ISSR Frequency",
            #                                                         plot_only_operating_altitudes=True,
            #                                                        title="Frequency of Contrail Persistence Regions (RH Ice > {}%)".format(
            #                                                            issr_limit), unit=" [%]", alt_plotting=True)

            for month in months:
                levels = range(0, 120, 5)
                if(issr_limit == "100"): ylimit = [0,30]
                else: ylimit = [0,50]
                #plt_meteorological_contours(issr_freq_percentage,"ISSR Frequency ({}%)".format(issr_limit),month,pressure_level_ids,title = "Frequency of Contrail Persistence Regions (RH Ice > {}%)".format(issr_limit),unit=" [%]",cmap = "Blues",levels=levels,ylimit=ylimit,longitude_averaging=False,alt_plotting=True)


                ylimit = [0,0.2]
                levels = [0,.8,.9,1,1.1,1.2,1.3]
                #plt_meteorological_contours(ice_supersaturation,"Ice-Supersaturation",month,pressure_level_ids,unit="",cmap="ocean",levels=levels,ylimit=ylimit)

                ylimit = [200,280]
                levels = [180, 185, 190, 195, 200, 205, 210, 215, 220, 225, 230, 235, 240, 245, 250, 255, 260, 265, 270, 275,
                          280, 285]
                #plt_meteorological_contours(temperature,"Temperature",month,pressure_level_ids,unit=" [K]",cmap="coolwarm",levels=levels,ylimit=ylimit,longitude_averaging=True)

                ylimit = [0,80]
                levels = np.arange(0,120,5)
                #plt_meteorological_contours(relative_humidity,'RH Measured',month,pressure_level_ids,unit=" [%]",cmap="winter",levels=levels,ylimit=ylimit)
                #plt_meteorological_contours(relative_humidity_ice,'RH Ice',month,pressure_level_ids,title = "Relative Humidity with respect to Ice",unit="[%]",cmap="Blues",levels=levels,ylimit=ylimit,alt_plotting=True)

                ylimit = [-10,10]
                levels = np.arange(0,6,0.2)
                #plt_meteorological_contours(relative_humidity_delta, 'RH Measured - RH Ice', month, pressure_level_ids, unit="[%]",cmap="Blues",levels=levels,ylimit=ylimit)


            for pressure_level_id in pressure_level_ids:
                levels = range(0, 105, 5)
                if(issr_limit == "100"): ylimit = [0,30]
                else: ylimit = [0,50]
                #plt_meteorological_contours(issr_freq_percentage, "ISSR Frequency ({}%)".format(issr_limit), months, pressure_level_id, unit=" [%]",cmap="cool", levels=levels,ylimit=ylimit,longitude_averaging=True)

                ylimit = [0,0.2]
                levels = [0, .8, .9, 1, 1.1, 1.2, 1.3]
                #plt_meteorological_contours(ice_supersaturation, "Ice-Supersaturation", months, pressure_level_id, unit="",cmap="ocean", levels=levels,ylimit=ylimit)

                ylimit = [200,280]
                levels = [180,185,190,195,200,205,210,215,220,225,230,235,240,245,250,255,260,265,270,275,280,285]
                #plt_meteorological_contours(temperature,"Temperature",months,pressure_level_id,unit=" [K]",cmap="coolwarm",levels=levels,ylimit=ylimit)

                ylimit = [0,80]
                levels = [0,10,20,30,40,50,60,70,80,90,100,110,120]
                #plt_meteorological_contours(relative_humidity,'RH Measured',months,pressure_level_id,unit=" [%]",cmap="winter",levels=levels,ylimit=ylimit)
                #plt_meteorological_contours(relative_humidity_ice,'RH Ice',months,pressure_level_id,unit=" [%]",cmap="winter",levels=levels,ylimit=ylimit)

                ylimit = [-10,10]
                levels = [-10,-8,-6,-4,-2,0,2,4,6,8,10]
                #plt_meteorological_contours(relative_humidity_delta, 'RH Measured - RH Ice', months, pressure_level_id, unit="[%]",cmap="winter",levels=levels,ylimit=ylimit)
