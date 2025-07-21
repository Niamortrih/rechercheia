import numpy as np
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import mean_squared_error
from sklearn.preprocessing import StandardScaler

# Chargement du dataset
data = np.load("dataset6.npz")
X = data["X"]
y = data["y"].astype(np.float32)
names = data["names"]

# Suppression des lignes contenant des NaN
nan_mask = ~np.isnan(X).any(axis=1)
X = X[nan_mask]
y = y[nan_mask]
names = names[nan_mask]

# Split
X_train, X_test, y_train, y_test, names_train, names_test = train_test_split(
    X, y, names, test_size=0.2, random_state=42
)

# Standardisation
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Paramètres à tester pour le GridSearch
param_grid = {
    'learning_rate': [0.01, 0.03, 0.1],
    'max_iter': [500, 1000, 2000],
    'max_leaf_nodes': [31, 63, 127],
    'min_samples_leaf': [20, 50, 100]
}

# Modèle de base
base_model = HistGradientBoostingRegressor(random_state=42)

# GridSearchCV
grid = GridSearchCV(
    estimator=base_model,
    param_grid=param_grid,
    scoring='neg_root_mean_squared_error',
    cv=3,
    verbose=1,
    n_jobs=-1
)

grid.fit(X_train_scaled, y_train)

# Meilleur modèle
model = grid.best_estimator_

# Prédictions
y_pred = model.predict(X_test_scaled)

# Évaluation
rmse = mean_squared_error(y_test, y_pred, squared=False)
mean_error = np.mean(np.abs(y_test - y_pred)) / 20
print("\nMeilleurs hyperparamètres :", grid.best_params_)
print("RMSE:", rmse)
print(f"Moyenne d’erreur absolue : {mean_error:.3f} BB")

# Tri des erreurs
results = []
for i in range(len(y_test)):
    yt = y_test[i]
    yp = y_pred[i]
    err = abs(yt - yp)
    name = names_test[i]
    results.append((err, i, name, yt, yp))

results.sort(reverse=True)

print("\n Prédictions triées par erreur décroissante :\n")
for rank, (err, i, name, yt, yp) in enumerate(results, 1):
    print(f"{rank:3} | Board : {name} | EV Réelle : {yt/20:.2f} BB | IA : {yp/20:.2f} BB | Erreur : {err/20:.2f} BB")
