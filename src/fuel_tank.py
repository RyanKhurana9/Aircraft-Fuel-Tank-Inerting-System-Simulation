"""Fuel tank state: fuel mass, ullage volume, ullage temperature.""" 
class FuelTank:
    def __init__(self,volume_m3=18.0,initial_fuel_kg=12000.0,fuel_density_kg_m3=800.0,thermal_tau_s=900.0, initial_temp_K=288.15, burn_rate_climb=1.1, burn_rate_cruise=0.6, burn_rate_descent=0.3):

        # thermal_tau_s dictates how quickly or slowly the tank's internal temperature reacts to the freezing outside air at high altitudes.
        self.V_tank=volume_m3
        self.rho_fuel=fuel_density_kg_m3
        self.fuel_mass=initial_fuel_kg
        self.tau_thermal=thermal_tau_s
        self.T_ullage=initial_temp_K
        self.burn_rate_climb={
            "climb":burn_rate_climb,# kg/s
            "cruise":burn_rate_cruise,
            "descent":burn_rate_descent
    }
    def fuel_volume(self)->float:
        """ Returns the current fuel volume in cubic meters based on the current fuel mass and density."""
        return self.fuel_mass/self.rho_fuel
    def ullage_volume(self)->float:
        return max(self.V_tank-self.fuel_volume(),1e-3)# 1e-3 prevents for 0 value
    def step(self,dt:float,phase:str,T_ambient:float)->float:
        burn=self.burn_rate_climb.get(phase,0.0)
        self.fuel_mass=max(self.fuel_mass-burn*dt,0.0)
        #It means the ullage temperature doesn't instantly become the atmospheric temperature.
        self.T_ullage+=dt*(T_ambient-self.T_ullage)/self.tau_thermal
        return burn   