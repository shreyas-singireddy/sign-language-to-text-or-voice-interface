import pandas as pd
import numpy as np
import os
import pickle
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
import json

DATASET_CSV = '../data/landmarks.csv'
MODEL_PATH = '../app/utils/model.pkl'
LABELS_PATH = '../app/utils/labels.json'

def train():
    if not os.path.exists(DATASET_CSV):
        print(f"Error: Dataset {DATASET_CSV} not found. Run collect_data.py first.")
        return

    print("Loading dataset...")
    df = pd.read_csv(DATASET_CSV)

    if len(df) == 0:
        print("Dataset is empty. Run collect_data.py to collect samples.")
        return

    # Check class distribution
    print("\nDataset Class Distribution:")
    print(df['label'].value_counts())

    # Features and labels
    X = df.drop('label', axis=1).values
    y = df['label'].values

    # Encode labels
    classes = sorted(list(set(y)))
    label_to_id = {label: i for i, label in enumerate(classes)}
    id_to_label = {i: label for i, label in enumerate(classes)}
    
    y_encoded = np.array([label_to_id[label] for label in y])

    # Save label mappings
    with open(LABELS_PATH, 'w') as f:
        json.dump(id_to_label, f)

    # Train/test split
    X_train, X_test, y_train, y_test = train_test_split(X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded)

    print(f"\nTraining on {len(X_train)} samples, testing on {len(X_test)} samples.")

    # Train Random Forest
    print("Training Random Forest Classifier...")
    clf = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
    clf.fit(X_train, y_train)

    # Evaluate
    y_pred = clf.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"\nModel Accuracy: {acc * 100:.2f}%")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=[id_to_label[i] for i in sorted(id_to_label.keys())]))

    # Save model
    with open(MODEL_PATH, 'wb') as f:
        pickle.dump(clf, f)
    
    print(f"Model saved to {MODEL_PATH}")
    print(f"Label map saved to {LABELS_PATH}")

if __name__ == '__main__':
    train()
