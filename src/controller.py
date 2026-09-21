class PIController:
    def __init__(self, target_o2=0.12, kp=2.0, ki=0.0008, u_min=0.0, u_max=None):
        self.target = target_o2
        self.kp = kp
        self.ki = ki
        self.u_min = u_min
        self.u_max = u_max
        self.integral = 0.0

    def compute_flow(self, current_o2, dt, u_max_now=None):
        u_max = u_max_now if u_max_now is not None else self.u_max

        error = current_o2 - self.target          # >0 when O2 too high -> more NEA
        u_unsat = self.kp * error + self.ki * (self.integral + error * dt)

        u = max(u_unsat, self.u_min)
        if u_max is not None:
            u = min(u, u_max)

        # conditional integration: only block the integral if it would push
        # further into saturation; allow it to unwind otherwise
        sat_high = u_max is not None and u_unsat > u_max
        sat_low = u_unsat < self.u_min
        if not ((sat_high and error > 0) or (sat_low and error < 0)):
            self.integral += error * dt

        return u