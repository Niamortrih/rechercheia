import numpy as np

# Chargement du dataset
data = np.load("dataset1.npz")
X = data["X"]
names = data["names"]
y = data["y"]

# Nombre de features
nb_features = X.shape[1]

# Affichage des 5 premières lignes
print("Affichage des 5 premiers inputs avec leurs features :\n")
for i in range(5):
    print(f"--- Ligne {i+1} : {names[i]} ---")
    for j in range(nb_features):
        print(f"Feature {j:2} : {X[i][j]:.6f}")
    print(f"→ EV : {y[i]/20:.3f} BB")
    print()
