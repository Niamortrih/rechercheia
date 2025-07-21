import numpy as np
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from sklearn.preprocessing import StandardScaler
import joblib
from sklearn.inspection import permutation_importance

# Chargement du dataset
data = np.load("dataset_300_All.npz")
X = data["X"]
y = data["y"].astype(np.float32)
names = data["names"]


print(f"X shape: {X.shape}, y shape: {y.shape}, names shape: {names.shape}")

# # Split train/test (on split aussi les noms)
# X_train, X_test, y_train, y_test, names_train, names_test = train_test_split(
#     X, y, names, test_size=0.2, random_state=42
# )
# Déterminer la taille du test set (20 %)
n_total = len(X)
n_test = int(n_total * 0.2)
n_train = n_total - n_test

# Split manuel : 80 % pour l'entraînement, 20 % pour le test (à la fin)
X_train, X_test = X[:n_train], X[n_train:]
y_train, y_test = y[:n_train], y[n_train:]
names_train, names_test = names[:n_train], names[n_train:]


# Standardisation
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Entraînement du modèle
model = HistGradientBoostingRegressor(
    max_iter=4000,
    random_state=42,
    verbose=1
)
model.fit(X_train_scaled, y_train)

# Prédiction
y_pred = model.predict(X_test_scaled)

# Évaluation
rmse = mean_squared_error(y_test, y_pred, squared=False)
print("RMSE:", rmse)

# Calcul des erreurs et tri par erreur décroissante
results = []
for i in range(len(y_test)):
    yt = y_test[i]
    yp = y_pred[i]
    err = abs(yt - yp)
    name = names_test[i]
    results.append((err, i, name, yt, yp))

results.sort(reverse=True)

# Affichage trié (Top 50 avec inputs)
print("\n Prédictions triées par erreur décroissante (top 50) :\n")
for rank, (err, i, name, yt, yp) in enumerate(results[:50], 1):
    inputs = X_test[i]
    print(f"{rank:3} | Board : {name} | EV Réelle : {yt/20:.2f} BB | Prédiction IA : {yp/20:.2f} BB | Erreur : {err/20:.2f} BB")
    print(f"      Inputs : {[round(v, 2) for v in inputs]}")

# Moyenne d'erreur absolue
mean_error = np.mean(np.abs(y_test - y_pred)) / 20
print(f"\nMoyenne d’erreur absolue : {mean_error:.3f} BB")

# # Sauvegarde du modèle
# joblib.dump(model, "modele_cbet_HGB.pkl")
# joblib.dump(scaler, "scaler.pkl")
