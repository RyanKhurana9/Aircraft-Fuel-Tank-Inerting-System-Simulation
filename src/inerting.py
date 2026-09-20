"""The inerting system controls the oxygen concentration in the fuel-tank ullage by injecting nitrogen-enriched air (NEA)."""

# Models the gas inside the tank as a mixture of ideal gases. The model is based on the ideal gas law and assumes that the gases do not interact with each other. The model also assumes that the temperature and pressure inside the tank are uniform.
from .atmosphere import R_UNIVERSAL
class InertingSystem:
    def __init__(self,x_o2_nea=0.05, max_flow_sea_level=0.15, min_flow_fraction=0.2):# NEA->Nitrogen Enriched Air
        self.x_o2_nea = x_o2_nea#The oxygen concentration of the incoming inert gas (NEA) pumped into the tank. The remaining 95% is nitrogen.
        self.max_flow_sl = max_flow_sea_level#maximum gas delivery capacity at sea level
        self.min_flow_fraction = min_flow_fraction#The minimum output floor (20% of maximum capacity) to simulate a system that never completely stops generating gas, even at very high, thin altitudes.(self.min_flow_fraction = 0.2 acts as a safety floor to prevent the system's gas output from dropping to zero at high cruise altitudes.)
        self.n_o2 = None# Oxygen molecules currently inside the tank, measured in moles.
        self.n_n2 = None# Nitrogen molecules currently inside the tank, measured in moles.
    def initialize(self, P_ullage, V_ullage, T_ullage, x_o2_initial=0.2095):
        # x_o2_initial is the initial oxygen concentration in the ullage, typically around 20.95% for air.
        # PV=nRT, where n is the number of moles of gas, R is the universal gas constant, and T is the temperature in Kelvin.
        n_total=(P_ullage*V_ullage)/(R_UNIVERSAL*T_ullage)
        self.n_o2=x_o2_initial*n_total
        self.n_n2=n_total*(1-x_o2_initial)
        return n_total
    def o2_fraction(self):
        #calculates the current oxygen concentration.
        n_total=self.n_o2+self.n_n2
        if(n_total>0):
            return self.n_o2 / n_total
        else:
            return 0.0
    def max_flow(self, P_ambient, P0=101325.0):
        # calculates the maximum flow rate of NEA based on the ambient pressure. The flow rate decreases with altitude (lower ambient pressure)
         ratio=P_ambient / P0
         return self.max_flow_sl*ratio
    def step(self, dt, inert_flow_cmd, P_ullage, V_ullage, T_ullage, P_ambient):
        # updates the gas state one timestep forward.
        # dt is the timestep in seconds.
        #MAXIMUM FLOW RATE
        max_flow_rate=self.max_flow(P_ambient)#How much NEA can the system physically supply at the current altitude?
        inert_flow=max(0.0,min(inert_flow_cmd,max_flow_rate))# inert_flow_cmd is the commanded flow rate of NEA, which is limited by the maximum flow rate WHICH CANNOT EXCEED THE MAXIMUM FLOW RATE. The flow rate is also limited to be non-negative.
        n_total_prev=self.n_o2+self.n_n2#Total number of moles of gas in the tank before the timestep.
        x_o2_prev=self.o2_fraction()#Current oxygen concentration before the timestep.
        n_total_target=P_ullage*V_ullage/(R_UNIVERSAL*T_ullage)#Target total number of moles of gas in the tank after the timestep, based on the ideal gas law.
        inert_moles=inert_flow*dt
       # f_ext = the extra gas needed from outside the NEA system.
        f_ext=n_total_target-n_total_prev-inert_moles# determines how much additional gas exchange is needed
        d_o2 = inert_moles * self.x_o2_nea
        d_n2 = inert_moles * (1.0 - self.x_o2_nea)

        if f_ext>0:# if the target is greater than the current amount of gas in the tank, we need to add more gas to the tank.
            d_o2 += f_ext * 0.2095
            d_n2 += f_ext * 0.7905
            """ if f_ext is positive  it means that the tank needs more gas than what NEA has supplied, so we need to add more gas from outside the NEA system. The additional gas is assumed to be air, which has an oxygen concentration of 20.95% and a nitrogen concentration of 79.05%. """

        else:# there is too much gas in the tank, so we need to vent some gas out of the tank.
            # for example if f_ext=-10 mole then oxygen that has to be vented out is -10*0.2095=-2.095 mole and nitrogen that has to be vented out is -10*0.7905=-7.905 mole
            d_o2 += f_ext * x_o2_prev#-2.095
            d_n2+=f_ext*(1-x_o2_prev)#-7.905

        n_o2_new=max(self.n_o2+d_o2,0.0)
        n_n2_new=max(self.n_n2+d_n2,0.0)# we take max in order to prevent negative moles of gas in the tank, which is physically impossible.
        n_total_new = n_o2_new + n_n2_new
        if n_total_new > 0 and n_total_target > 0:
            scale = n_total_target / n_total_new  # enforce gas-law constraint exactly
            n_o2_new *= scale
            n_n2_new *= scale
            # WE SCALE THE NEW MOLES BECAUSE IF THE NEW TOTAL MOLES IS NOT EQUAL TO THE TARGET TOTAL MOLES, THEN THE IDEAL GAS LAW WOULD BE VIOLATED. SCALING ENSURES THAT THE NEW TOTAL MOLES MATCHES THE TARGET TOTAL MOLES, MAINTAINING PHYSICAL CONSISTENCY.
            #ex-> total_target=100 and new=104 scale=100/104=0.9615, so new o2=10*0.9615=9.615 and new n2=94*0.9615=90.231, so total new=99.846 which is close to 100.

        self.n_o2,self.n_n2=n_o2_new,n_n2_new
        return inert_flow



""" calculte the new o2 and n2 moles in the tank after the timestep. The change in moles of oxygen and nitrogen is calculated based on the commanded flow rate of NEA and the additional gas exchange needed to reach the target total number of moles. The new moles of oxygen and nitrogen are then updated accordingly. 
            """            


            