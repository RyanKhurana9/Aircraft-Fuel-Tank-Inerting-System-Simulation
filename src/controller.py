# PI controller job is to Look at the current O₂ level, compare it with the target O₂ level, and decide how much NEA flow to request.
class PIcontroller:
    def __init__(self,target_o2=0.12,kp=2.0,ki=0.0008,u_min=0.0, u_max=None):
        """
        target_o2: The desired oxygen concentration in the ullage (e.g., 0.12 for 12% O₂).
        kp: Proportional gain for the PI controller.
        ki: Integral gain for the PI controller.
        u_min: Minimum flow rate command (e.g., 0.0 for no flow).
        u_max: Maximum flow rate command (e.g., 0.15 for 15% of maximum flow). If None, no upper limit is applied.
        """
        self.target = target_o2
        self.kp = kp
        self.ki = ki
        self.u_min = u_min
        self.u_max = u_max
        self.integral = 0.0

    def compute_flow(self,current_o2,dt,u_max_now=None):
        """
        current_o2: The current oxygen concentration in the ullage.
        dt: Time step in seconds.
        u_max_now: Optional maximum flow rate command for this specific call. If None, uses the controller's u_max.
        """
        u_max=u_max_now if u_max_now is not None else self.u_max
      #  error target-current
        error=self.target - current_o2 # positive: O2 too high
        u_unsat=self.kp*error+self.ki*self.integral
        u = u_unsat
        if u_max is not None:
            u = min(u, u_max)
        u = max(u, self.u_min)
        if u == u_unsat:          # anti-windup: freeze integral while saturated
            self.integral += error * dt
            # Inew=Iold+error*dt

        return u
    """
    If O₂ is too high → error positive → increase NEA.
If O₂ is too low → error negative → decrease NEA.
"""
        

