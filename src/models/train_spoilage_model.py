"""
AgroShield AI — Grain Spoilage & Silo Condensation Predictive Model
Author: Enzo Oliveira dos Santos
Field: Agribusiness AI & Post-Harvest Risk Mitigation

Trains a high-precision Scikit-Learn ensemble model on Iowa climate and silo sensor telemetry.
"""

import os
import json
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, f1_score
import joblib

# Import local EMC engine
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from src.models.emc import calculate_emc, evaluate_condensation_risk


def generate_iowa_telemetry_dataset(n_samples: int = 3000, random_state: int = 42) -> pd.DataFrame:
    """
    Synthesizes calibrated post-harvest silo sensor records representing
    Iowa conditions (Des Moines / Ames, Oct-Feb season).
    Combines ambient weather with grain bin physical telemetry.
    """
    np.random.seed(random_state)
    
    # 0 = Corn (60%), 1 = Soybeans (40%)
    crop_type = np.random.choice(["corn", "soybeans"], size=n_samples, p=[0.6, 0.4])
    crop_code = np.where(crop_type == "corn", 0, 1)
    
    # Ambient Temperature: Iowa autumn/winter (-15°C to 25°C)
    ambient_temp = np.random.normal(loc=4.0, scale=8.0, size=n_samples)
    ambient_temp = np.clip(ambient_temp, -18.0, 30.0)
    
    # Ambient Relative Humidity (30% to 98%)
    ambient_rh = np.random.normal(loc=72.0, scale=14.0, size=n_samples)
    ambient_rh = np.clip(ambient_rh, 25.0, 99.0)
    
    # Days in Storage (1 to 180 days)
    days_in_storage = np.random.randint(1, 180, size=n_samples)
    
    # Grain Temperature (starts warm after harvest, cools with management: 0°C to 35°C)
    grain_temp = np.random.normal(loc=16.0, scale=6.5, size=n_samples)
    grain_temp = np.clip(grain_temp, 0.0, 38.0)
    
    # Grain Moisture % (target is 13-14%, but wet harvest can reach 18%+)
    grain_moisture = np.random.normal(loc=14.2, scale=1.8, size=n_samples)
    grain_moisture = np.clip(grain_moisture, 10.5, 22.0)
    
    # Calculate physical features
    emc_values = [
        calculate_emc(rh, t, c) 
        for rh, t, c in zip(ambient_rh, ambient_temp, crop_type)
    ]
    
    temp_gradient = grain_temp - ambient_temp
    
    # Target definition according to agrophysical risk thresholds
    # 0 = SAFE, 1 = WARNING_AERATE, 2 = CRITICAL_SPOILAGE_MOLD
    targets = []
    for g_temp, g_moist, t_grad, emc, crop in zip(grain_temp, grain_moisture, temp_gradient, emc_values, crop_type):
        safe_max_m = 14.0 if crop == "corn" else 13.0
        
        # Critical criteria: excessive moisture + thermal shock or high heat respiration
        if (g_moist >= safe_max_m + 2.5 and g_temp >= 20.0) or (t_grad >= 14.0 and g_moist >= safe_max_m + 1.0):
            targets.append(2)  # CRITICAL
        elif (g_moist > safe_max_m) or (t_grad >= 9.0) or (g_temp >= 22.0):
            targets.append(1)  # WARNING_AERATE
        else:
            targets.append(0)  # SAFE
            
    df = pd.DataFrame({
        "crop_type": crop_type,
        "crop_code": crop_code,
        "grain_temp_c": np.round(grain_temp, 1),
        "grain_moisture_pct": np.round(grain_moisture, 2),
        "ambient_temp_c": np.round(ambient_temp, 1),
        "ambient_rh_pct": np.round(ambient_rh, 1),
        "days_in_storage": days_in_storage,
        "emc_pct": np.round(emc_values, 2),
        "temp_gradient_c": np.round(temp_gradient, 1),
        "risk_level": targets
    })
    
    return df


def train_and_export_model():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
        
    print("[AgroShield AI] Generating calibrated Iowa silo telemetry dataset...")
    df = generate_iowa_telemetry_dataset(n_samples=3200)
    
    features = [
        "crop_code",
        "grain_temp_c",
        "grain_moisture_pct",
        "ambient_temp_c",
        "ambient_rh_pct",
        "days_in_storage",
        "emc_pct",
        "temp_gradient_c",
    ]
    X = df[features]
    y = df["risk_level"]
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )
    
    print("[AgroShield AI] Training RandomForest Classifier (Ensemble Architecture)...")
    clf = RandomForestClassifier(
        n_estimators=150,
        max_depth=12,
        min_samples_split=4,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1
    )
    
    clf.fit(X_train, y_train)
    y_pred = clf.predict(X_test)
    
    acc = accuracy_score(y_test, y_pred)
    f1_macro = f1_score(y_test, y_pred, average="macro")
    cv_scores = cross_val_score(clf, X, y, cv=5, scoring="f1_macro")
    
    print(f"[OK] Accuracy on Test Set: {acc * 100:.2f}%")
    print(f"[OK] F1-Score (Macro): {f1_macro:.4f}")
    print(f"[OK] 5-Fold Cross Validation Mean F1: {cv_scores.mean():.4f} (+/- {cv_scores.std() * 2:.4f})")
    
    report = classification_report(y_test, y_pred, target_names=["SAFE", "WARNING_AERATE", "CRITICAL_MOLD"], output_dict=True)
    conf_matrix = confusion_matrix(y_test, y_pred).tolist()
    
    # Feature Importances
    feat_importances = dict(zip(features, [round(float(v), 4) for v in clf.feature_importances_]))
    sorted_importances = dict(sorted(feat_importances.items(), key=lambda item: item[1], reverse=True))
    
    # Save artifacts
    artifacts_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "artifacts"))
    os.makedirs(artifacts_dir, exist_ok=True)
    
    samples_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data/samples"))
    os.makedirs(samples_dir, exist_ok=True)
    
    model_path = os.path.join(artifacts_dir, "spoilage_model.joblib")
    metrics_path = os.path.join(artifacts_dir, "model_metrics.json")
    dataset_path = os.path.join(samples_dir, "iowa_silo_telemetry_sample.csv")
    
    joblib.dump(clf, model_path)
    
    metrics_payload = {
        "model_type": "RandomForestClassifier",
        "n_estimators": 150,
        "n_samples": len(df),
        "accuracy_pct": round(acc * 100, 2),
        "f1_macro": round(f1_macro, 4),
        "cv_f1_mean": round(float(cv_scores.mean()), 4),
        "feature_importances": sorted_importances,
        "confusion_matrix": conf_matrix,
        "classification_report": report,
        "training_metadata": {
            "author": "Enzo Oliveira dos Santos",
            "jurisdiction": "Iowa (Midwest US Grain Corridor)",
            "standards": ["ASAE D245.5", "NOAA GHCN"]
        }
    }
    
    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump(metrics_payload, f, indent=2)
        
    df.to_csv(dataset_path, index=False)
    
    print(f"[SAVED] Model saved to: {model_path}")
    print(f"[SAVED] Metrics saved to: {metrics_path}")
    print(f"[SAVED] Dataset sample saved to: {dataset_path}")
    
    return metrics_payload


if __name__ == "__main__":
    train_and_export_model()
