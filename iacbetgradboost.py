import numpy as np
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import euclidean_distances
import joblib
from sklearn.inspection import permutation_importance

# Chargement du dataset
data = np.load("dataset6.npz")
X = data["X"]
y = data["y"].astype(np.float32)
names = data["names"]

# Split train/test (on split aussi les noms)
X_train, X_test, y_train, y_test, names_train, names_test = train_test_split(
    X, y, names, test_size=0.2, random_state=42
)

# Standardisation
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Entraînement du modèle
model = HistGradientBoostingRegressor(
    max_iter=45000,
    random_state=42,
    verbose=1,
    max_leaf_nodes=31,
    min_samples_leaf=400,
    learning_rate=0.04
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

# Affichage trié
print("\n Prédictions triées par erreur décroissante :\n")
for rank, (err, i, name, yt, yp) in enumerate(results, 1):
    print(f"{rank:3} | Board : {name} | EV Réelle : {yt/20:.2f} BB | Prédiction IA : {yp/20:.2f} BB | Erreur : {err/20:.2f} BB")

# Moyenne d'erreur absolue
mean_error = np.mean(np.abs(y_test - y_pred)) / 20
print(f"\nMoyenne d’erreur absolue : {mean_error:.3f} BB")

# Sauvegarde du modèle
joblib.dump(model, "modele_cbet_HGB.pkl")

# Importance des features
print("\nCalcul de l’importance des features (permutation)...")
result = permutation_importance(model, X_test_scaled, y_test, n_repeats=10, random_state=42)
importances = result.importances_mean

indices = np.argsort(importances)[::-1]
top_n = 10

print("\nTop 10 features les plus importantes :")
for i in range(top_n):
    print(f"{i+1}. Feature {indices[i]} - Importance : {importances[indices[i]]:.4f}")

def analyse_voisins_pondérés(X_test_scaled, X_test_raw, y_test, y_pred, names_test, top_erreurs, importances, top_k=5, k_voisins=5):
    print("\n--- Analyse des plus proches voisins pondérés pour les pires erreurs ---\n")
    for rank, (err, i, name, yt, yp) in enumerate(top_erreurs[:top_k], 1):
        x_target_scaled = X_test_scaled[i]
        x_target_raw = X_test_raw[i]
        print(f"\n#{rank} - Main cible : {name} | EV Réelle : {yt/20:.2f} BB | IA : {yp/20:.2f} BB | Erreur : {err/20:.2f} BB")
        print(f"   Inputs   : {[round(v, 2) for v in x_target_raw]}")

        distances = []
        for j, x in enumerate(X_test_scaled):
            if j == i:
                continue
            dist = np.sqrt(np.sum(importances * (x - x_target_scaled) ** 2))
            distances.append((dist, j))

        distances.sort()
        for v_rank, (dist, j) in enumerate(distances[:k_voisins], 1):
            name_v = names_test[j]
            yt_v = y_test[j]
            yp_v = y_pred[j]
            x_voisin_raw = X_test_raw[j]
            print(f"   → Voisin {v_rank} : {name_v} | EV : {yt_v/20:.2f} BB | IA : {yp_v/20:.2f} BB | ΔEV : {abs(yt - yt_v)/20:.2f} BB | Distance : {dist:.4f}")
            print(f"     Inputs : {[round(v, 2) for v in x_voisin_raw]}")

analyse_voisins_pondérés(X_test_scaled, X_test, y_test, y_pred, names_test, results, importances, top_k=5, k_voisins=5)
