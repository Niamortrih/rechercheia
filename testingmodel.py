import numpy as np
import joblib



# board_equities = [0.46, 0.84, 0.84, 0.86, 0.16, 0.58, 0.74, 0.77, 0.12, 0.25, 0.54, 0.7, 0.1, 0.23, 0.31, 0.48]
# equity_vs_range = [0, 1, 0.8, 0.43, 0.82, 0.05, 1.0, 0.0, 1.0, 0.1, 1.0, 0.0, 1.0, 0.0, 1.0, 0.0, 1.0, 0.0, 1.0, 0.0, 1.0, 0.0, 1.0, 0.0, 1.0, 0.0, 1.0, 0.0, 1.0, 0.0, 1.0, 0.0, 1.0, 0.0, 1.0, 0.0, 1.0, 0.0, 1.0, 0.0, 1.0, 0.0, 1.0, 0.0, 1.0, 0.0, 1.0, 0.0, 1.0, 0.0]
# river_stats = [0.99, 0.01, 0.98, 0.98, 0.98, 0.98, 0.99, 0.99, 0.99, 0.99, 0.99, 0.99, 0.99, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, -0.53, -0.71]

board_equities = [0.52, 0.83, 0.85, 0.86, 0.22, 0.66, 0.77, 0.78, 0.16, 0.31, 0.65, 0.77, 0.14, 0.23, 0.28, 0.52]
equity_vs_range = [0, 1, 0.8, 0.43, 0.82, 0.05, 1.0, 0.0, 1.0, 0.1, 1.0, 0.0, 1.0, 0.0, 1.0, 0.0, 1.0, 0.0, 1.0, 0.0, 1.0, 0.0, 1.0, 0.0, 1.0, 0.0, 1.0, 0.0, 1.0, 0.0, 1.0, 0.0, 1.0, 0.0, 1.0, 0.0, 1.0, 0.0, 1.0, 0.0, 1.0, 0.0, 1.0, 0.0, 1.0, 0.0, 1.0, 0.0, 1.0, 0.0]
river_stats = [0.99, 0.01, 0.98, 0.98, 0.98, 0.98, 0.99, 0.99, 0.99, 0.99, 0.99, 0.99, 0.99, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, -0.53, -0.71]


input = np.array(board_equities + equity_vs_range + river_stats)

# Chargement du modèle et du scaler
model = joblib.load("modele_cbet_HGB.pkl")
scaler = joblib.load("scaler.pkl")  # Tu dois avoir sauvegardé ton scaler aussi

# Transformation de l'input
input_scaled = scaler.transform([input])  # reshape to (1, n_features)

# Prédiction
prediction = model.predict(input_scaled)[0]

# Affichage
print(f"Prédiction IA : {prediction/20:.2f} BB")
