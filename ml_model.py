from sklearn.ensemble import RandomForestClassifier
import joblib
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "model", "attack_model.pkl")


def train():
    X = [[5, 10, 1], [2, 0, 1], [10, 5, 2]]
    y = ["Brute Force", "Normal", "Scanning"]

    model = RandomForestClassifier()
    model.fit(X, y)

    os.makedirs(os.path.join(BASE_DIR, "model"), exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    return model


def load():
    if not os.path.exists(MODEL_PATH):
        return train()
    return joblib.load(MODEL_PATH)


model = load()


def predict(features):
    return model.predict([features])[0]
