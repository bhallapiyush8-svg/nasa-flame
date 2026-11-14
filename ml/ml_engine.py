import os
import csv
import json
import math
import random
import numpy as np
import joblib
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score, mean_squared_error, r2_score

# Base directories
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
ML_DIR = os.path.join(BASE_DIR, 'ml')
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(ML_DIR, exist_ok=True)

CSV_FILE = os.path.join(DATA_DIR, 'psi_experiments.csv')
JSON_FILE = os.path.join(DATA_DIR, 'psi_experiments.json')
CLASSIFIER_FILE = os.path.join(ML_DIR, 'regime_classifier.joblib')
SPREAD_REGRESSOR_FILE = os.path.join(ML_DIR, 'spread_regressor.joblib')
RISK_REGRESSOR_FILE = os.path.join(ML_DIR, 'risk_regressor.joblib')
ENCODER_FILE = os.path.join(ML_DIR, 'feature_metadata.json')

def generate_psi_dataset(n_samples=1500, seed=42):
    random.seed(seed)
    np.random.seed(seed)
    
    investigations = [
        {"name": "BASS", "full_name": "Burning and Suppression of Solids - I", "phase": "Solid", "rack": "MSG", "default_fuels": ["PMMA Cast Sheet (20x100mm)", "SIBAL Cotton/Fiberglass (0.3mm)", "Nomex Fabric"]},
        {"name": "BASS-II", "full_name": "Burning and Suppression of Solids - II", "phase": "Solid", "rack": "MSG", "default_fuels": ["PMMA Cast Cylinder (6.35mm)", "Black PMMA Flat (10x100mm)", "SIBAL Cotton/Fiberglass (0.3mm)"]},
        {"name": "FLEX", "full_name": "Flame Extinguishment Experiment", "phase": "Liquid", "rack": "CIR", "default_fuels": ["n-Heptane Droplet (d0=2.5mm)", "Methanol Droplet (d0=3.0mm)", "n-Octane Droplet (d0=2.0mm)"]},
        {"name": "FLEX-2", "full_name": "Flame Extinguishment Experiment - 2", "phase": "Liquid", "rack": "CIR", "default_fuels": ["n-Decane Droplet (d0=3.5mm)", "Hexadecane Droplet (d0=4.0mm)", "n-Heptane/Iso-octane Blend"]},
        {"name": "CFI", "full_name": "Cool Flames Investigation", "phase": "Liquid", "rack": "CIR", "default_fuels": ["n-Heptane Droplet (d0=3.0mm)", "n-Octane Droplet (d0=3.0mm)", "n-Decane Droplet (d0=3.2mm)"]},
        {"name": "ACME-BRE", "full_name": "ACME - Burning Rate Emulator", "phase": "Gas", "rack": "CIR (ACME Insert)", "default_fuels": ["Methane Gas (25mm Porous Burner)", "Ethylene Gas (50mm Porous Burner)", "Methane/N2 Mix (25mm Burner)"]},
        {"name": "SAME-R", "full_name": "Smoke Aerosol Measurement Experiment - Reflight", "phase": "Smoke/Aerosol", "rack": "MSG", "default_fuels": ["Pyrolyzed Kapton Wire Insulation", "Overheated Teflon Wire (PTFE)", "Silicone Rubber Smolder"]},
        {"name": "DAFT-2", "full_name": "Dust and Aerosol Measurement Feasibility Test - 2", "phase": "Dust/Aerosol", "rack": "Express Rack / MSG", "default_fuels": ["Lunar Regolith Simulant (JSC-1A)", "Martian Dust Simulant (MGS-1)", "Cellulose Smoke Particles"]},
        {"name": "Saffire-IV", "full_name": "Spacecraft Fire Safety Demonstration - IV", "phase": "Solid", "rack": "Cygnus Enclosure", "default_fuels": ["SIBAL Cotton/Fiberglass (0.4x1.0m)", "Nomex/Kevlar Space Suit Fabric", "Plexiglas Panel (10mm)"]},
        {"name": "SOFIE-GEL", "full_name": "Solid Fuel Ignition and Extinction - Growth & Extinction Limits", "phase": "Solid", "rack": "CIR", "default_fuels": ["PMMA Flat Sheet (30x100mm)", "Polyester/Cotton Blend", "High-Performance Wire Insulation"]}
    ]
    
    habitats = [
        "Space Stations (ISS)",
        "Spacecraft/Crew Capsules",
        "Lunar Surface Bases (0.16G)",
        "Martian Habitats (0.38G)",
        "Pressurized Rovers"
    ]
    
    diluent_options = ["N2", "CO2", "He", "Ar"]
    suppression_options = ["None", "Fine-Water-Mist", "N2 Flooding", "CO2 Discharge", "Cabin Depressurization", "Ventilation Cutoff"]
    
    dataset = []
    
    for i in range(1, n_samples + 1):
        inv = random.choice(investigations)
        inv_name = inv["name"]
        fuel_phase = inv["phase"]
        fuel_name = random.choice(inv["default_fuels"])
        
        # Habitat assignment tailored to science relevance
        if "Saffire" in inv_name or "Capsule" in fuel_name:
            habitat = "Spacecraft/Crew Capsules"
        elif "SOFIE" in inv_name or "DAFT" in inv_name:
            habitat = random.choice(["Lunar Surface Bases (0.16G)", "Martian Habitats (0.38G)", "Pressurized Rovers"])
        else:
            habitat = random.choice(habitats)
            
        # Gravity levels matching exploration targets
        if "Lunar" in habitat:
            gravity_g = 0.16
        elif "Martian" in habitat:
            gravity_g = 0.38
        elif habitat == "Pressurized Rovers":
            gravity_g = random.choice([0.16, 0.38])
        else:
            # ISS or Crew Capsules
            gravity_g = 0.0 if random.random() < 0.9 else 1.0  # Some 1G ground control comparative runs
            
        # Exploration atmospheres vs Standard
        # Standard: 21% O2, 101.3 kPa
        # Exploration (Moon/Mars): 28-34% O2, 55-70 kPa (8.2 psia)
        is_exploration_atm = (gravity_g in [0.16, 0.38]) or (random.random() < 0.35)
        if is_exploration_atm:
            oxygen_pct = round(random.uniform(24.0, 36.0), 1)
            pressure_kpa = round(random.uniform(52.0, 75.0), 1)
        else:
            oxygen_pct = round(random.uniform(15.0, 23.5), 1)
            pressure_kpa = round(random.uniform(95.0, 102.5), 1)
            
        # Ventilation speed (cm/s)
        # Critical for the 0G Ventilation Paradox
        ventilation_speed_cms = round(random.uniform(0.0, 32.0), 1)
        
        # Sample thickness or droplet diameter (mm)
        if fuel_phase == "Solid":
            sample_thickness_mm = round(random.uniform(0.3, 10.0), 2)
        elif fuel_phase == "Liquid":
            sample_thickness_mm = round(random.uniform(1.2, 5.0), 2)
        elif fuel_phase == "Gas":
            sample_thickness_mm = round(random.uniform(25.0, 50.0), 1)  # Burner diameter
        else:
            sample_thickness_mm = round(random.uniform(0.1, 2.0), 2)
            
        diluent = random.choices(diluent_options, weights=[0.70, 0.18, 0.08, 0.04])[0]
        suppression = random.choices(suppression_options, weights=[0.60, 0.15, 0.10, 0.05, 0.05, 0.05])[0]
        
        # ==========================================
        # REALISTIC MICROGRAVITY PHYSICS LOGIC
        # ==========================================
        # 1. 0G Ventilation Paradox:
        # In 0G, at v = 0, soot and CO2 build up; heat loss by radiation quenches the flame unless O2 is high.
        # But at gentle airflow (3 to 14 cm/s), O2 is continuously replenished while convection is too weak to cool flame.
        # Thus, solid burns more readily at lower O2 in 0G (3-14 cm/s) than 1G!
        
        # Calculate effective oxidizer flux factor
        effective_o2_transport = 1.0
        if gravity_g == 0.0:
            if ventilation_speed_cms < 2.0:
                effective_o2_transport = 0.40  # Stagnant starvation
            elif 2.0 <= ventilation_speed_cms <= 14.0:
                effective_o2_transport = 1.35  # The 0G Ventilation Paradox sweet spot
            else:
                effective_o2_transport = max(0.3, 1.35 - (ventilation_speed_cms - 14.0) * 0.05)
        else:
            # In gravity, buoyant convection u_buoyant ~ sqrt(g * L * deltaT / T_inf)
            u_buoy = math.sqrt(gravity_g * 9.81 * 0.05 * 1200 / 300) * 100.0  # cm/s approx 30-40 cm/s
            total_effective_u = math.sqrt(u_buoy**2 + ventilation_speed_cms**2)
            effective_o2_transport = 0.85 + (total_effective_u / 50.0) * 0.25
            
        # Diluent cooling factor (CO2 has higher molar heat capacity than N2, He conducts heat rapidly)
        diluent_retardation = 1.0
        if diluent == "CO2":
            diluent_retardation = 0.65
        elif diluent == "He":
            diluent_retardation = 0.55
            
        # Suppression reduction
        suppression_factor = 1.0
        if suppression == "Fine-Water-Mist":
            suppression_factor = 0.25
        elif suppression == "N2 Flooding":
            suppression_factor = 0.40
        elif suppression == "CO2 Discharge":
            suppression_factor = 0.35
        elif suppression == "Cabin Depressurization":
            suppression_factor = 0.15
        elif suppression == "Ventilation Cutoff":
            suppression_factor = 0.50 if gravity_g == 0.0 else 0.80
            
        # Flammability score metric (base chemical driving potential)
        chem_potential = (oxygen_pct / 21.0) * (pressure_kpa / 101.3) * effective_o2_transport * diluent_retardation * suppression_factor
        
        # Check Cool Flame conditions (prominent in FLEX, CFI for liquid alkanes in 0G with low-to-moderate O2)
        is_cool_flame_candidate = (
            fuel_phase == "Liquid" and
            gravity_g == 0.0 and
            16.0 <= oxygen_pct <= 32.0 and
            ventilation_speed_cms <= 8.0 and
            suppression in ["None", "Ventilation Cutoff"]
        )
        
        # Determine Regime
        if chem_potential < 0.55:
            regime = "Quenched"
            flame_spread_rate_mm_s = 0.0
            peak_temp_k = round(random.uniform(320.0, 480.0), 1)
            soot_fraction_ppm = 0.0
            flame_color = "Extinguished"
            risk_score = round(max(2.0, chem_potential * 20.0), 1)
        elif is_cool_flame_candidate and (random.random() < 0.60 or chem_potential < 0.85):
            regime = "Invisible Cool Flame"
            flame_spread_rate_mm_s = round(random.uniform(0.15, 0.65), 3)
            peak_temp_k = round(random.uniform(550.0, 780.0), 1)
            soot_fraction_ppm = round(random.uniform(0.001, 0.04), 4)  # Negligible soot!
            flame_color = "Invisible / Weak Violet IR"
            risk_score = round(random.uniform(42.0, 68.0), 1)  # High stealth danger (can re-ignite!)
        elif chem_potential >= 1.35 or (oxygen_pct > 30.0 and ventilation_speed_cms > 5.0 and suppression == "None"):
            regime = "Vigorous Spread"
            base_spread = 1.8 + (chem_potential - 1.35) * 1.5 + (ventilation_speed_cms / 30.0) * 1.2
            flame_spread_rate_mm_s = round(base_spread, 2)
            peak_temp_k = round(random.uniform(1550.0, 2100.0), 1)
            soot_fraction_ppm = round(random.uniform(0.3, 2.5) * (1.0 if gravity_g > 0 else 0.35), 3)
            flame_color = "Yellow / Bright Orange" if gravity_g > 0 else "Brilliant Blue with White Core"
            risk_score = round(min(99.0, 75.0 + chem_potential * 15.0), 1)
        else:
            regime = "Steady Hot Burn"
            base_spread = 0.45 + (chem_potential - 0.55) * 0.95 + (ventilation_speed_cms / 30.0) * 0.4
            flame_spread_rate_mm_s = round(base_spread, 2)
            peak_temp_k = round(random.uniform(1150.0, 1600.0), 1)
            soot_fraction_ppm = round(random.uniform(0.05, 0.8) * (1.0 if gravity_g > 0 else 0.25), 3)
            flame_color = "Spherical Blue" if gravity_g == 0.0 else "Teardrop Yellow/Blue"
            risk_score = round(min(74.0, 35.0 + chem_potential * 32.0), 1)
            
        # Specific NASA physics notes
        notes = []
        if inv_name in ["BASS", "BASS-II"]:
            if 3.0 <= ventilation_speed_cms <= 14.0 and gravity_g == 0.0:
                notes.append("0G Ventilation Paradox confirmed: Airflow (3-14 cm/s) supplied O2 faster than convective cooling, sustaining burn below terrestrial LOI.")
            elif ventilation_speed_cms < 2.0 and gravity_g == 0.0:
                notes.append("Stagnant 0G accumulation of combustion products; diffusion starvation observed.")
        elif inv_name in ["FLEX", "FLEX-2", "CFI"]:
            if regime == "Invisible Cool Flame":
                notes.append("Visible hot flame quenched via radiative heat loss, transitioning into quasi-steady second-stage Cool Flame (550-750 K).")
            if suppression == "Fine-Water-Mist":
                notes.append("Fine-Water-Mist droplets absorbed latent vaporization heat without damaging CIR electronics.")
        elif "ACME" in inv_name:
            notes.append("Conducted with modular ACME insert inside CIR; gaseous fuel emulated condensed-phase burning rate physics.")
        elif "SAME" in inv_name:
            notes.append("Particle measurement calibrated for smoke aerosol detection; optical sensor later flight-adapted for DAFT regolith dust.")
        elif "DAFT" in inv_name:
            notes.append("SAME flight hardware repurposed to measure lunar/Martian dust aerosol dynamics and false-alarm rejection.")
        elif "Saffire" in inv_name:
            notes.append("Large-scale enclosure burn in Cygnus cargo craft; high flame spread rate across meter-scale fabric.")
        elif "SOFIE" in inv_name:
            notes.append("Exploration atmosphere evaluation: low-pressure / elevated-O2 flammability boundaries.")
            
        record = {
            "run_id": f"PSI-{inv_name}-{1000 + i}",
            "investigation": inv_name,
            "investigation_full": inv["full_name"],
            "rack_hardware": inv["rack"],
            "habitat_suitability": habitat,
            "fuel_phase": fuel_phase,
            "fuel_name": fuel_name,
            "sample_thickness_mm": sample_thickness_mm,
            "gravity_g": gravity_g,
            "oxygen_pct": oxygen_pct,
            "pressure_kpa": pressure_kpa,
            "ventilation_speed_cms": ventilation_speed_cms,
            "diluent_gas": diluent,
            "suppression_method": suppression,
            "combustion_regime": regime,
            "flame_spread_rate_mm_s": flame_spread_rate_mm_s,
            "peak_temperature_k": peak_temp_k,
            "soot_volume_fraction_ppm": soot_fraction_ppm,
            "flame_color": flame_color,
            "fire_risk_score": risk_score,
            "notes": " | ".join(notes) if notes else "Standard parameter characterization in microgravity test matrix."
        }
        dataset.append(record)
        
    return dataset

def save_dataset(dataset):
    # Save CSV
    keys = list(dataset[0].keys())
    with open(CSV_FILE, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(dataset)
    print(f"Dataset successfully saved to CSV: {CSV_FILE} ({len(dataset)} records)")
    
    # Save JSON
    with open(JSON_FILE, mode='w', encoding='utf-8') as f:
        json.dump(dataset, f, indent=2)
    print(f"Dataset successfully saved to JSON: {JSON_FILE}")

def train_and_export_models(dataset):
    print("\n--- Training NASA Space Apps Microgravity ML Models ---")
    
    # Feature engineering
    fuel_phases = sorted(list(set(d["fuel_phase"] for d in dataset)))
    diluents = sorted(list(set(d["diluent_gas"] for d in dataset)))
    suppressions = sorted(list(set(d["suppression_method"] for d in dataset)))
    regimes = ["Quenched", "Invisible Cool Flame", "Steady Hot Burn", "Vigorous Spread"]
    
    # Save categorical metadata for frontend and API inference
    meta = {
        "fuel_phases": fuel_phases,
        "diluents": diluents,
        "suppression_methods": suppressions,
        "regimes": regimes,
        "features": [
            "gravity_g",
            "oxygen_pct",
            "pressure_kpa",
            "ventilation_speed_cms",
            "sample_thickness_mm"
        ] + [f"phase_{p}" for p in fuel_phases] + [f"diluent_{d}" for d in diluents] + [f"supp_{s}" for s in suppressions]
    }
    
    with open(ENCODER_FILE, 'w', encoding='utf-8') as f:
        json.dump(meta, f, indent=2)
    print(f"Feature metadata saved to {ENCODER_FILE}")
    
    X = []
    y_regime = []
    y_spread = []
    y_risk = []
    
    for d in dataset:
        vec = [
            float(d["gravity_g"]),
            float(d["oxygen_pct"]),
            float(d["pressure_kpa"]),
            float(d["ventilation_speed_cms"]),
            float(d["sample_thickness_mm"])
        ]
        # One-hot encode fuel_phase
        for p in fuel_phases:
            vec.append(1.0 if d["fuel_phase"] == p else 0.0)
        # One-hot encode diluent
        for dil in diluents:
            vec.append(1.0 if d["diluent_gas"] == dil else 0.0)
        # One-hot encode suppression
        for sup in suppressions:
            vec.append(1.0 if d["suppression_method"] == sup else 0.0)
            
        X.append(vec)
        y_regime.append(d["combustion_regime"])
        y_spread.append(float(d["flame_spread_rate_mm_s"]))
        y_risk.append(float(d["fire_risk_score"]))
        
    X = np.array(X)
    y_regime = np.array(y_regime)
    y_spread = np.array(y_spread)
    y_risk = np.array(y_risk)
    
    # Split using same indices
    indices = np.arange(len(X))
    train_idx, test_idx = train_test_split(indices, test_size=0.2, random_state=42, stratify=y_regime)
    
    X_train, X_test = X[train_idx], X[test_idx]
    y_reg_train, y_reg_test = y_regime[train_idx], y_regime[test_idx]
    y_spr_train, y_spr_test = y_spread[train_idx], y_spread[test_idx]
    y_rsk_train, y_rsk_test = y_risk[train_idx], y_risk[test_idx]
    
    # 1. Classifier: Combustion Regime
    clf = RandomForestClassifier(n_estimators=120, max_depth=14, random_state=42)
    clf.fit(X_train, y_reg_train)
    reg_preds = clf.predict(X_test)
    acc = accuracy_score(y_reg_test, reg_preds)
    print(f"Combustion Regime Classifier Accuracy: {acc * 100:.2f}%")
    joblib.dump(clf, CLASSIFIER_FILE)
    print(f"Saved classifier model -> {CLASSIFIER_FILE}")
    
    # 2. Regressor: Flame Spread Rate (mm/s)
    spr_reg = RandomForestRegressor(n_estimators=100, max_depth=12, random_state=42)
    spr_reg.fit(X_train, y_spr_train)
    spr_preds = spr_reg.predict(X_test)
    spr_r2 = r2_score(y_spr_test, spr_preds)
    spr_mae = np.mean(np.abs(y_spr_test - spr_preds))
    print(f"Flame Spread Regressor: R2={spr_r2:.4f}, MAE={spr_mae:.4f} mm/s")
    joblib.dump(spr_reg, SPREAD_REGRESSOR_FILE)
    print(f"Saved flame spread regressor -> {SPREAD_REGRESSOR_FILE}")
    
    # 3. Regressor: Habitat Fire Risk Score (0-100)
    risk_reg = RandomForestRegressor(n_estimators=100, max_depth=12, random_state=42)
    risk_reg.fit(X_train, y_rsk_train)
    risk_preds = risk_reg.predict(X_test)
    risk_r2 = r2_score(y_rsk_test, risk_preds)
    risk_mae = np.mean(np.abs(y_rsk_test - risk_preds))
    print(f"Habitat Fire Risk Regressor: R2={risk_r2:.4f}, MAE={risk_mae:.4f}")
    joblib.dump(risk_reg, RISK_REGRESSOR_FILE)
    print(f"Saved risk score regressor -> {RISK_REGRESSOR_FILE}")
    
    print("\n--- ML Training Complete! All artifacts generated ---")

if __name__ == "__main__":
    dataset = generate_psi_dataset(n_samples=1600, seed=42)
    save_dataset(dataset)
    train_and_export_models(dataset)
