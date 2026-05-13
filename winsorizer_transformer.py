from sklearn.base import BaseEstimator, TransformerMixin
import pandas as pd
import numpy as np

class WinsorizerTransformer(BaseEstimator, TransformerMixin):
    """
    Winsorisasi kolom tertentu dengan batas quantile.
    fit()      : hitung lower/upper bound dari data yang masuk (fold-train)
    transform(): clip nilai di luar batas - diterapkan ke fold-valid / test
    """
    def __init__(self, cols, lower_q=0.01, upper_q=0.99):
        self.cols = cols
        self.lower_q = lower_q
        self.upper_q = upper_q
    def fit(self, X, y=None):
        X_df = pd.DataFrame(X) if not isinstance(X, pd.DataFrame) else X
        self.bounds_ = {}
        for col in self.cols:
            if col in X_df.columns:
                lo = X_df[col].quantile(self.lower_q)
                hi = X_df[col].quantile(self.upper_q)
                self.bounds_[col] = {"lower": lo, "upper": hi}
        self.feature_names_in_ = np.array(X_df.columns.tolist(), dtype=object)
        return self
    def transform(self, X, y=None):
        X_out = X.copy() if isinstance(X, pd.DataFrame) else pd.DataFrame(X, columns=self.feature_names_in_)
        for col, b in self.bounds_.items():
            if col in X_out.columns:
                X_out[col] = X_out[col].clip(lower=b["lower"], upper=b["upper"])
        return X_out
    def get_feature_names_out(self, input_features=None):
        if input_features is not None:
            return np.array(input_features, dtype=object)
        if hasattr(self, "feature_names_in_"):
            return self.feature_names_in_.copy()
        return np.array(self.cols, dtype=object)
