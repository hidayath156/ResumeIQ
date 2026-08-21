"""Train, evaluate and export the KNN resume-quality classifier.

Run:
    python ML/generate_dataset.py
    python ML/train_knn.py

Outputs:
    ML/resume_knn_model.pkl   - pickled {scaler, knn} pipeline (scikit-learn)
    ML/knn_model.json         - scaler stats + training points, consumed by the
                                app backend so the same trained model runs
                                inside the deployed server runtime.
"""

import json
import os
import pickle

import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler

HERE = os.path.dirname(__file__)
FEATURES = [
    "skills_count",
    "years_experience",
    "education_level",
    "certifications_count",
    "project_relevance",
    "resume_completeness",
]
LABELS = ["Needs Improvement", "Moderate Resume", "Strong Resume"]
K = 7


def main():
    df = pd.read_csv(os.path.join(HERE, "resume_dataset.csv"))
    X = df[FEATURES].values.astype(float)
    y = df["label"].values.astype(int)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    scaler = StandardScaler().fit(X_train)
    knn = KNeighborsClassifier(n_neighbors=K, weights="distance")
    knn.fit(scaler.transform(X_train), y_train)

    pred = knn.predict(scaler.transform(X_test))
    print(f"K = {K}")
    print("Accuracy:", round(accuracy_score(y_test, pred), 4))
    print("\nClassification report:\n", classification_report(y_test, pred, target_names=LABELS))
    print("Confusion matrix:\n", confusion_matrix(y_test, pred))

    with open(os.path.join(HERE, "resume_knn_model.pkl"), "wb") as f:
        pickle.dump({"scaler": scaler, "knn": knn, "features": FEATURES, "labels": LABELS}, f)

    export = {
        "k": K,
        "features": FEATURES,
        "labels": LABELS,
        "mean": scaler.mean_.tolist(),
        "scale": scaler.scale_.tolist(),
        "accuracy": round(float(accuracy_score(y_test, pred)), 4),
        "points": [
            {"x": [round(v, 4) for v in row], "y": int(label)}
            for row, label in zip(scaler.transform(X_train).tolist(), y_train.tolist())
        ],
    }
    with open(os.path.join(HERE, "knn_model.json"), "w") as f:
        json.dump(export, f)
    print("\nSaved resume_knn_model.pkl and knn_model.json")


if __name__ == "__main__":
    main()
