"""Small picklable model wrappers used for deployment."""
import numpy as np


class AvgBlend:
    """Average of several fitted models."""
    def __init__(self, models, names):
        self.models, self.names = models, names

    def predict(self, X, **kw):
        return np.mean([m.predict(X) for m in self.models], axis=0)


class LogModel:
    """Model trained on log1p(BC); predicts back on the ng/m3 scale (better for skewed BC)."""
    def __init__(self, model):
        self.model = model

    def predict(self, X, **kw):
        return np.expm1(np.clip(self.model.predict(X), 0, 12))


class ResidualModel:
    """Forecast model trained on (BC[t+h] - BC[t]); adds the current BC back at prediction time."""
    def __init__(self, model, base_col="BC6_lag0"):
        self.model, self.base_col = model, base_col

    def predict(self, X, **kw):
        return np.clip(self.model.predict(X) + np.asarray(X[self.base_col]), 0, None)
