import math

def _alpha(cutoff, dt):
    """Convert a cutoff frequency (Hz) into an EMA weight for a time step of dt seconds."""
    tau = 1.0 / (2 * math.pi * cutoff)
    return 1.0 / (1.0 + tau / dt)

class OneEuroFilter:
    """Speed-adaptive smoothing for one number (Casiez et al., 2012)."""

    def __init__(self, min_cutoff=1.0, beta=0.007, d_cutoff=1.0):
        self.min_cutoff = min_cutoff
        self.beta = beta
        self.d_cutoff = d_cutoff
        self.reset()

    def reset(self):
        self.x_prev = None
        self.dx_prev = 0.0
        self.t_prev = None

    def __call__(self, x, t):
        if self.t_prev is None:          # first sample: nothing to smooth against yet
            self.x_prev, self.t_prev = x, t
            return x

        dt = t - self.t_prev
        if dt <= 0:
            return self.x_prev

        # 1. smoothed speed
        dx = (x - self.x_prev) / dt
        a_d = _alpha(self.d_cutoff, dt)
        dx_hat = a_d * dx + (1 - a_d) * self.dx_prev

        # 2. speed-dependent cutoff, 3. EMA with that cutoff
        cutoff = self.min_cutoff + self.beta * abs(dx_hat)
        a = _alpha(cutoff, dt)
        x_hat = a * x + (1 - a) * self.x_prev

        self.x_prev, self.dx_prev, self.t_prev = x_hat, dx_hat, t
        return x_hat


class PointFilter:
    """Smooths an (x, y) point with one OneEuroFilter per axis."""

    def __init__(self, **kwargs):
        self.fx = OneEuroFilter(**kwargs)
        self.fy = OneEuroFilter(**kwargs)

    def __call__(self, point, t):
        x, y = point
        return int(round(self.fx(x, t))), int(round(self.fy(y, t)))

    def reset(self):
        self.fx.reset()
        self.fy.reset()