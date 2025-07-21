import numpy as np
import joblib

# Chargement du dataset
data = np.load("dataset7.npz")
X = data["X"]
y = data["y"].astype(np.float32)
names = data["names"]

# Chargement du modèle et du scaler
model = joblib.load("modele_cbet_HGB.pkl")
scaler = joblib.load("scaler.pkl")

# Paramètre : la target recherchée (en BB)
target_recherche_bb = 5
target_recherche = target_recherche_bb * 20  # Convertie en unité du modèle

# Calcul des distances
distances = []
for i in range(len(y)):
    distance = abs(y[i] - target_recherche)
    distances.append((distance, i))

# Tri par distance croissante
distances.sort()

# Affichage des 5 plus proches
print(f"\nLes 5 inputs avec une target proche de {target_recherche_bb:.2f} BB :\n")
for rank, (dist, i) in enumerate(distances[:20], 1):
    x_raw = X[i]
    x_scaled = scaler.transform([x_raw])
    prediction = model.predict(x_scaled)[0]

    print(f"{rank}. Board : {names[i]}")
    print(f"   Target réelle   : {y[i]/20:.2f} BB")
    print(f"   Prédiction IA   : {prediction/20:.2f} BB")
    print(f"   Écart absolu    : {dist/20:.2f} BB")
    print(f"   Inputs          : {[round(v, 2) for v in x_raw]}\n")
