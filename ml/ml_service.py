import os
import json
import joblib
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ML_DIR = os.path.join(BASE_DIR, 'ml')
CLASSIFIER_FILE = os.path.join(ML_DIR, 'regime_classifier.joblib')
SPREAD_REGRESSOR_FILE = os.path.join(ML_DIR, 'spread_regressor.joblib')
RISK_REGRESSOR_FILE = os.path.join(ML_DIR, 'risk_regressor.joblib')
ENCODER_FILE = os.path.join(ML_DIR, 'feature_metadata.json')

class MicrogravityMLEngine:
    def __init__(self):
        self.meta = None
        self.classifier = None
        self.spread_regressor = None
        self.risk_regressor = None
        self.load_models()

    def load_models(self):
        try:
            with open(ENCODER_FILE, 'r', encoding='utf-8') as f:
                self.meta = json.load(f)
            self.classifier = joblib.load(CLASSIFIER_FILE)
            self.spread_regressor = joblib.load(SPREAD_REGRESSOR_FILE)
            self.risk_regressor = joblib.load(RISK_REGRESSOR_FILE)
            print("[MLEngine] Loaded Scikit-Learn models successfully.")
        except Exception as e:
            print(f"[MLEngine] Warning: Failed to load models: {e}")

    def prepare_vector(self, data):
        gravity_g = float(data.get('gravity_g', 0.0))
        oxygen_pct = float(data.get('oxygen_pct', 21.0))
        pressure_kpa = float(data.get('pressure_kpa', 101.3))
        ventilation_speed_cms = float(data.get('ventilation_speed_cms', 5.0))
        sample_thickness_mm = float(data.get('sample_thickness_mm', 1.5))
        fuel_phase = str(data.get('fuel_phase', 'Solid'))
        diluent_gas = str(data.get('diluent_gas', 'N2'))
        suppression_method = str(data.get('suppression_method', 'None'))

        vec = [
            gravity_g,
            oxygen_pct,
            pressure_kpa,
            ventilation_speed_cms,
            sample_thickness_mm
        ]

        for p in self.meta["fuel_phases"]:
            vec.append(1.0 if fuel_phase.lower() == p.lower() else 0.0)
        for d in self.meta["diluents"]:
            vec.append(1.0 if diluent_gas.upper() == d.upper() else 0.0)
        for s in self.meta["suppression_methods"]:
            vec.append(1.0 if suppression_method.lower() == s.lower() else 0.0)

        return np.array([vec]), {
            "gravity_g": gravity_g,
            "oxygen_pct": oxygen_pct,
            "pressure_kpa": pressure_kpa,
            "ventilation_speed_cms": ventilation_speed_cms,
            "sample_thickness_mm": sample_thickness_mm,
            "fuel_phase": fuel_phase,
            "diluent_gas": diluent_gas,
            "suppression_method": suppression_method
        }

    def predict(self, params):
        if not self.classifier or not self.meta:
            self.load_models()

        X_vec, clean_params = self.prepare_vector(params)

        # Predictions
        regime = self.classifier.predict(X_vec)[0]
        regime_probs = self.classifier.predict_proba(X_vec)[0]
        classes = self.classifier.classes_
        confidence = float(np.max(regime_probs))
        class_prob_map = {classes[i]: round(float(regime_probs[i]), 3) for i in range(len(classes))}

        spread_rate = float(self.spread_regressor.predict(X_vec)[0])
        spread_rate = max(0.0, round(spread_rate, 3))
        if regime == "Quenched":
            spread_rate = 0.0

        risk_score = float(self.risk_regressor.predict(X_vec)[0])
        risk_score = max(0.0, min(100.0, round(risk_score, 1)))
        if regime == "Quenched" and clean_params["suppression_method"] != "None":
            risk_score = min(risk_score, 15.0)

        # Physics Diagnostic & NASA Callouts
        physics_insights = []
        g = clean_params["gravity_g"]
        v = clean_params["ventilation_speed_cms"]
        o2 = clean_params["oxygen_pct"]
        phase = clean_params["fuel_phase"]
        supp = clean_params["suppression_method"]

        # 0G Ventilation Paradox Callout
        if g == 0.0:
            if 3.0 <= v <= 14.0:
                physics_insights.append({
                    "title": "0G Ventilation Paradox Active",
                    "level": "WARNING",
                    "text": f"At {v} cm/s cabin ventilation, airflow sweeps fresh O2 ({o2}%) across the fuel surface faster than radiative heat loss can quench it. Materials burn at lower O2 thresholds in microgravity than in terrestrial 1G environments!"
                })
            elif v < 2.0:
                physics_insights.append({
                    "title": "Diffusion-Limited Stagnant 0G",
                    "level": "INFO",
                    "text": "In near-zero airflow, combustion products (CO2, H2O) envelope the flame. The reaction zone is purely diffusion-controlled and tends toward self-extinction."
                })
            elif v > 20.0:
                physics_insights.append({
                    "title": "Convective Blow-Off Regime",
                    "level": "INFO",
                    "text": f"Airflow velocity of {v} cm/s induces severe convective heat removal, pushing the flame toward edge blowout."
                })

        # Cool Flame Callout
        if regime == "Invisible Cool Flame" or (phase == "Liquid" and g == 0.0):
            physics_insights.append({
                "title": "Invisible Cool Flame Hazard (FLEX / CFI Dynamics)",
                "level": "CRITICAL" if regime == "Invisible Cool Flame" else "INFO",
                "text": "Liquid alkane droplets in 0G can undergo radiative hot-flame extinction and transition into quasi-steady invisible cool flames (500–800 K). Senses no visible soot or bright emission, but fuel continues to vaporize and can abruptly re-ignite if cabin ventilation surges."
            })

        # Suppression notes
        if supp == "Fine-Water-Mist":
            physics_insights.append({
                "title": "Fine-Water-Mist Suppression Active",
                "level": "SUCCESS",
                "text": "Micro-droplets (10–30 μm) extract latent vaporization enthalpy directly from the flame reaction zone without flooding avionics racks or creating toxic decomposition byproducts."
            })

        return {
            "combustion_regime": regime,
            "regime_confidence": round(confidence * 100, 1),
            "regime_probabilities": class_prob_map,
            "flame_spread_rate_mm_s": spread_rate,
            "fire_risk_score": risk_score,
            "input_parameters": clean_params,
            "physics_insights": physics_insights
        }

# Global singleton
ml_service = MicrogravityMLEngine()
