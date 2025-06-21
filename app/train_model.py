import numpy as np
import pickle
from sklearn.linear_model import LinearRegression

# Data: [size (sq ft)], [price ($)]
X = np.array([[500], [1000], [1500], [2000], [2500]])
y = np.array([100000, 150000, 200000, 250000, 300000])

model = LinearRegression()
model.fit(X, y)

with open("house_price_model.pkl", "wb") as f:
    pickle.dump(model, f)
