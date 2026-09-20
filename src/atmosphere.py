"""International Standard Atmosphere (troposphere) and flight altitude profile."""

# Mean sea level values
R_UNIVERSAL = 8.314  # J/(mol*K) universal gas constant
T0=288.15 # K,mean sea level temperature
P0=101325.0   # Pa, sea-level standard pressure
L = 0.0065 # K/m temperature lapse rate  "for every 1 m increase in altitude, the temperature decreases by 0.0065 K"
G0=9.80665 # m/s^2, standard gravity
M_AIR=0.0289644 # kg/mol, molar mass of Earth's air


def isa_temperature(h_m: float)->float:
    "ISA temperature equation describes how ambient temperature changes linearly with altitude within a specific layer of the atmosphere."
    "T = T0 - L * h"
    # Note this equation is valid only for the troposphere (up to 11 km altitude)
    h=min(h_m,11000)# limit to 11 km
    return T0 -(L*h)


def isa_pressure(h_m:float)->float:
    "ISA pressure equation describes how ambient pressure changes with altitude within a specific layer of the atmosphere."
    # altitude icrease pressure decrease and temperature decreases
    # this affects the gas density ,gas moles,ullage condition and inerting behavior of the tank
    T=isa_temperature(h_m)
    P=P0*(T/T0)**((G0*M_AIR)/(R_UNIVERSAL*L))
    return P

class FlightProfile:
     """Three-phase climb/cruise/descent altitude profile."""
     def __init__(self,cruise_alt_m=10688.0,t_climb_s=1200,t_cruise_s=8400.0,t_descent_s=1200.0):
         self.cruise_alt_m=cruise_alt_m
         self.t_climb=t_climb_s
         self.t_cruise_end=t_climb_s+t_cruise_s
         self.t_total=t_descent_s+t_cruise_s+t_climb_s# total flight time in seconds
         """
        Climb = 20 min
        Cruise = 140 min
        Descent = 20 min
        total=180 min
        """
     def altitude(self,t:float)->float:
        # Altitude becomes a function of time h=h(t) as altitude changes with time during climb,cruise and descent phases of the flight.
        """ Returns the altitude at time t(in seconds) based on the flight profile"""
        if t<=self.t_climb:
             return self.cruise_alt_m * (t / self.t_climb)# linear climb to cruise altitude at t=0 h=0
        elif t<=self.t_cruise_end:
             return self.cruise_alt_m # cruise altitude is constant
        elif t<self.t_total:
             frac=(self.t_total-t)/(self.t_total-self.t_cruise_end)
             return self.cruise_alt_m*frac # linear descent to ground level at t=t_total
        else:
             return 0.0 # after t_total, altitude is 0
     def phase(self,t:float)->str:
        """ Returns the flight phase at time t(in seconds) based on the flight profile"""
        if t<=self.t_climb:
             return "climb"
        elif t<=self.t_cruise_end:
             return "cruise"
        elif t<self.t_total:
             return "descent"
        else:
             return "ground"


    




