import numpy as np
import matplotlib.pyplot as plt
from ambiance import Atmosphere
from scipy import optimize
from units import ft

dir_issr = "data/issr/"
seasons = ("mam", "jja", "son", "djf")
issr_lat_data = {}

for season in seasons:
    issr_lat_data[season] = np.genfromtxt(dir_issr + season + ".csv",
                                      delimiter=',', names=True)

issr_p_lvl_data = np.genfromtxt(dir_issr + "p_level_var.csv",
                                delimiter=",", names=True)


def alt2fl(height):
    """
    Returns a flight level corresponding to a certain ISA altitude in m

    """

    return (height / ft) / 100


def fl2alt(fl):
    """
    Returns an ISA altitude in m corresponding to the input flight level

    """

    return fl * 100 * ft


def issr_freq_215(latitude, season="avg"):
    """


    Parameters
    ----------
    latitude : float
        Latitude in degrees.
    season : str, optional
        One of "MAM", "JJA", "SON", "DJF" (case insensitive). Pass "avg" for
        the seasonal average. The default is "avg".

    Returns
    -------
    float
        Frequency of occurrence of ice-supersaturated regions at a pressureS
        level of 215 hPa.

    """

    if season.lower() in seasons:
        season = season.lower()
        lat = issr_lat_data[season]["latitude"]
        freq = issr_lat_data[season]["frequency"]
        return np.interp(latitude, lat, freq, left=np.nan, right=np.nan)
    elif season.lower() == "avg":
        return np.mean([issr_freq_215(latitude, s) for s in seasons], axis=0)
    else:
        raise ValueError(("Unrecognised season '{}'. Options are {}"
                          ).format(season, [*seasons, "avg"]))


def find_alt(p_level, FL=False):
    """
    Returns the ISA altitude (m) at which we will encounter a given
    pressure level (Pa).

    If the FL argument is set to True, it instead returns the flight level
    corresponding to that height.

    """

    p_actual = (lambda h: Atmosphere(h).pressure)
    h = optimize.root_scalar(lambda h: p_actual(h) - p_level,
                             bracket=(-5000, 80000))
    if FL:
        return alt2fl(h.root)
    else:
        return h.root


def alt_variation(delta_p, season):
    """


    Parameters
    ----------
    delta_p : float
        p_layer - p_therm_TPH. A positive value indicates a pressure level
        below that of the tropopause.
    season : str, optional
        One of "MAM", "JJA", "SON", "DJF" (case insensitive). Pass "avg" for
        the seasonal average.

    Returns
    -------
    float
        Expected frequency of occurence of ISSR.

    """

    if season.lower() in seasons:
        # convert from % to fraction
        freq = issr_p_lvl_data[season.lower()] / 100
        return np.interp(delta_p, issr_p_lvl_data["delta_p"], freq,
                         left=np.nan, right=np.nan)

    elif season.lower() == "avg":
        return np.mean([alt_variation(delta_p, s) for s in seasons], axis=0)
    else:
        raise ValueError(("Unrecognised season '{}'. Options are {}"
                          ).format(season, [*seasons, "avg"]))


def issr_freq(latitude, fl, season="avg"):

    # Tropopause altitude
    trop_alt = 11000
    # ISA altitude
    altitude = fl2alt(fl)
    # Find pressure difference between altitude and tropopause
    # Note: a negative value indicates we are HIGHER THAN the tropopause
    [p_delta] = Atmosphere(altitude).pressure - Atmosphere(trop_alt).pressure
    # Find pressure difference between 215 hPa level and tropopause
    [p_to_215] = 215 * 100 - Atmosphere(trop_alt).pressure # in Pa
    # Find frequency of occurrence at 215 hPa
    freq_215 = issr_freq_215(latitude, season)
    # Find new frequency of occurrence at desired altitude
    freq_alt = freq_215 * (alt_variation(p_delta, season)
                           / alt_variation(p_to_215, season))
    return freq_alt


if __name__ == "__main__":
    plt.style.use("seaborn")
    lat_array = np.linspace(-80, 80, 801)
    plt.figure(dpi=150)
    for season in seasons:
        lat = issr_lat_data[season]["latitude"]
        freq = issr_lat_data[season]["frequency"]
        plt.plot(lat, freq*100, label=season.upper())
    plt.plot(lat_array, issr_freq_215(lat_array, "avg")*100, '--k',
             label="avg")
    plt.xlim(-90, 90)
    plt.xlabel("latitude [°]")
    plt.ylabel("ISSR frequency of occurrence [%]")
    plt.legend()
    plt.show()

    plt.figure(dpi=150)
    for season in seasons:
        p_lvl = issr_p_lvl_data["delta_p"]
        freq = alt_variation(p_lvl, season)
        plt.plot(freq*100, p_lvl, label=season.upper())
    plt.plot(alt_variation(p_lvl, "avg")*100, p_lvl, '--k', label="avg")
    plt.yticks(p_lvl)
    plt.gca().invert_yaxis()
    plt.xlabel("ISSR frequency of occurrence [%]")
    plt.ylabel(r"$\Delta p = p_{\mathrm{layer}} - p_{\mathrm{therm. TPH.}}$ [Pa]")
    plt.legend()
    plt.show()


    plt.figure(dpi=150)
    plt.plot(lat_array,issr_freq(lat_array,350, "avg")*100, '--', label="avg 350")
    plt.plot(lat_array,issr_freq(lat_array,360, "avg")*100, '--', label="avg 360")
    plt.plot(lat_array,issr_freq(lat_array,370, "avg")*100, '--', label="avg 370")
    plt.plot(lat_array,issr_freq(lat_array,380, "avg")*100, '--', label="avg 380")
    plt.plot(lat_array,issr_freq(lat_array,390, "avg")*100, '--', label="avg 390")
    plt.ylabel("ISSR frequency of occurrence [%]")
    plt.xlabel("latitude [°]")
    plt.legend()
    plt.show()
