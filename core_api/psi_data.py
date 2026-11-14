import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JSON_FILE = os.path.join(BASE_DIR, 'data', 'psi_experiments.json')

PSI_INVESTIGATIONS = [
    {
        "id": "bass-series",
        "name": "BASS & BASS-II",
        "full_name": "Burning and Suppression of Solids (BASS / BASS-II)",
        "facility": "Microgravity Science Glovebox (MSG)",
        "lead_pi": "Dr. Paul V. Ferkul (NASA GRC / NCSER)",
        "target_habitats": ["Space Stations (ISS)", "Spacecraft/Crew Capsules"],
        "gravity_range": "0.0 G (Microgravity)",
        "objectives": "Examine the burning and extinction characteristics of solid materials in microgravity under small forced airflow velocities (1 to 14 cm/s). Determine whether materials burn easier or harder in microgravity compared to normal gravity.",
        "fuels": {
            "materials": ["Polymethyl methacrylate (PMMA)", "SIBAL (Cotton 75% / Fiberglass 25%) fabric", "Nomex flame-resistant fabric"],
            "shapes_and_sizes": "Cast PMMA rods (6.35 mm diameter, 100 mm length), flat sheets (20 mm x 100 mm, thickness 1.2–3.0 mm), thin fabric strips (0.3 mm thick)."
        },
        "test_conditions": {
            "oxygen_pct_range": "16.0% to 21.0%",
            "airflow_speed_range": "1.0 to 14.0 cm/s",
            "pressure": "101.3 kPa (Standard 1.0 atm cabin pressure)",
            "diluent": "Nitrogen (N2)"
        },
        "intra_investigation_variables": {
            "varied": "Airflow velocity swept across 1 to 14 cm/s; oxygen concentrations decremented in steps down to extinction; concurrent vs opposed flow directions.",
            "held_constant": "Sample shape and mounting geometry within each sub-test; chamber volume; glovebox ambient temperature (293–298 K)."
        },
        "sensors_and_measurements": [
            "Color video camera (30 fps) for flame front tracking and regression rate",
            "Infrared camera for surface temperature distribution",
            "Thermocouple rake measuring gas phase thermal boundary layer",
            "Laser pyrometry and radiometers for heat flux emission"
        ],
        "key_nasa_callouts": {
            "paradox_title": "The 0G Ventilation Paradox",
            "paradox_description": "On Earth (1G), buoyant convection constantly rushes fresh air past a flame at ~30-40 cm/s, which provides oxygen but also extracts heat. In microgravity (0G), without buoyancy, low HVAC cabin airflow (3–14 cm/s) feeds oxygen faster than radiative cooling can quench the flame. Consequently, materials can burn at LOWER oxygen percentages in 0G (as low as 16.5% O2) than on Earth! Stagnant 0G starves the flame, but gentle drafts make it thrive."
        },
        "risk_rating": "Moderate to High (Airflow Sensitive)"
    },
    {
        "id": "flex-series",
        "name": "FLEX, FLEX-2 & CFI",
        "full_name": "Flame Extinguishment Experiment (FLEX / FLEX-2) & Cool Flames Investigation (CFI)",
        "facility": "Combustion Integrated Rack (CIR)",
        "lead_pi": "Dr. Forman A. Williams (UC San Diego) & Dr. Vedat Nayagam",
        "target_habitats": ["Space Stations (ISS)", "Spacecraft/Crew Capsules", "Pressurized Rovers"],
        "gravity_range": "0.0 G (Quiescent Microgravity)",
        "objectives": "Study isolated liquid fuel droplet combustion in microgravity. Discover flame extinction limits, vaporization rates (d^2-law), radiative quenching, and low-temperature chemical regimes in the absence of buoyant convection.",
        "fuels": {
            "materials": ["n-Heptane", "n-Octane", "n-Decane", "Methanol", "Hexadecane", "Heptane/Iso-octane mixtures"],
            "shapes_and_sizes": "Spherical droplets suspended on 14–80 μm silicon carbide (SiC) fibers, initial droplet diameter d0 = 1.5 to 5.0 mm."
        },
        "test_conditions": {
            "oxygen_pct_range": "15.0% to 40.0%",
            "airflow_speed_range": "0.0 cm/s (Quiescent) or slow co-flow 0–5 cm/s",
            "pressure": "50.0 to 300.0 kPa",
            "diluent": "Nitrogen (N2), Carbon Dioxide (CO2), Helium (He)"
        },
        "intra_investigation_variables": {
            "varied": "Initial droplet diameter d0 (1.5 to 5.0 mm); chamber gas composition and diluent heat capacity (N2 vs CO2 vs He); ambient pressure.",
            "held_constant": "Chamber volume (110 L CIR combustion chamber); ignition spark energy; fiber mount orientation."
        },
        "sensors_and_measurements": [
            "High-speed 1000 fps color camera for droplet shrinkage rate",
            "Broadband and narrow-band radiometers (CH* and C2* chemiluminescence)",
            "UV-sensitive cameras capturing OH* radical emissions",
            "Gas Chromatography / Mass Spectrometry (GC/MS) for exhaust product analysis"
        ],
        "key_nasa_callouts": {
            "cool_flame_title": "Discovery of Microgravity 'Invisible Cool Flames'",
            "cool_flame_description": "During FLEX experiments on the ISS, scientists observed that after a hot, luminous flame (~1500–1800 K) extinguished due to radiative heat loss, the liquid droplet continued to evaporate at a steady rate without visible light! This proved the existence of quasi-steady microgravity 'Cool Flames' (500–800 K) driven by low-temperature peroxy radical chemistry. These invisible flames pose a serious silent fire threat because they can reignite into hot fires if airflow changes.",
            "suppression_title": "Fine-Water-Mist Extinguishment",
            "suppression_description": "FLEX and CFI demonstrated that micro-droplet water mist (10–30 μm) provides effective fire extinguishment via latent heat absorption without flooding avionics racks or producing toxic halon breakdown gases."
        },
        "risk_rating": "Critical (Stealth Low-Temperature Hazard)"
    },
    {
        "id": "acme-bre",
        "name": "ACME — Burning Rate Emulator (BRE)",
        "full_name": "Advanced Combustion via Microgravity Experiments (ACME) — Burning Rate Emulator",
        "facility": "Combustion Integrated Rack (CIR) — Modular ACME Insert",
        "lead_pi": "Dr. James S. T'ien (Case Western Reserve University)",
        "target_habitats": ["Space Stations (ISS)", "Spacecraft/Crew Capsules", "Lunar Surface Bases (0.16G)"],
        "gravity_range": "0.0 G",
        "objectives": "Determine the flammability boundaries, extinction limits, and burning rates of condensed-phase fuels by burning gaseous fuels through porous flat burners with heat sink control in microgravity.",
        "fuels": {
            "materials": ["Methane (CH4)", "Ethylene (C2H4)", "Methane/N2 mixtures", "Ethylene/CO2 mixtures"],
            "shapes_and_sizes": "Modular 25 mm and 50 mm diameter sintered porous bronze/brass flat burners flush-mounted in flow duct."
        },
        "test_conditions": {
            "oxygen_pct_range": "15.0% to 35.0%",
            "airflow_speed_range": "0.0 to 18.0 cm/s",
            "pressure": "70.0 to 101.3 kPa",
            "diluent": "Nitrogen (N2) and Carbon Dioxide (CO2)"
        },
        "intra_investigation_variables": {
            "varied": "Fuel gas injection flow rate (simulating solid pyrolysis regression rate); burner surface heat loss (simulating internal conductive heat transfer of solids); co-flow oxidizer velocity.",
            "held_constant": "Modular ACME chamber insert hardware; burner diameter during each test block; gas supply temperature."
        },
        "sensors_and_measurements": [
            "Calibrated heat flux gauges embedded in burner face",
            "Thin-Filament Pyrometry (TFP) for 2D temperature maps",
            "Multi-wavelength photodiode radiometers",
            "High-resolution monochrome and color digital cameras"
        ],
        "key_nasa_callouts": {
            "modular_acme_title": "ACME Modular Hardware Ecosystem in CIR",
            "modular_acme_description": "The ACME project comprised 6 distinct experiments (BRE, CFI-2, CLD Flame, E-FIELD, Flame Design, and PEAC) that ALL utilized the SAME modular set of ACME hardware inside the Combustion Integrated Rack (CIR). This modularity maximized NASA science return by allowing quick robotic and astronaut changeouts of burners without replacing the main chamber or gas manifolds.",
            "bre_emulator_title": "Emulating Solids and Liquids via Gaseous Control",
            "bre_emulator_description": "BRE burned gaseous fuels through porous burners while precisely extracting heat to match the solid-phase energy balance. This allowed scientists to isolate gas-phase flammability limits of solids (like PMMA and space fabrics) without the confounding complications of dripping, bubbling, or char cracking."
        },
        "risk_rating": "High (Benchmarking Condensed Fuel Flammability)"
    },
    {
        "id": "same-daft-crosslink",
        "name": "SAME / SAME-R & DAFT / DAFT-2",
        "full_name": "Smoke Aerosol Measurement Experiment (SAME/SAME-R) & Dust and Aerosol Measurement Feasibility Test (DAFT/DAFT-2)",
        "facility": "Microgravity Science Glovebox (MSG) & Express Racks",
        "lead_pi": "Dr. David L. Urban (NASA GRC) & Marit Meyer (NASA GRC)",
        "target_habitats": ["Space Stations (ISS)", "Lunar Surface Bases (0.16G)", "Martian Habitats (0.38G)", "Pressurized Rovers"],
        "gravity_range": "0.0 G (with applicability to 0.16G Moon & 0.38G Mars)",
        "objectives": "Characterize smoke particulate size distributions produced by overheated spacecraft materials in microgravity (SAME) and cross-validate flight instruments to distinguish fire smoke from toxic/abrasive lunar and Martian regolith dust (DAFT).",
        "fuels": {
            "materials": ["Pyrolyzed Kapton wire insulation", "Teflon (PTFE) overheated cable jackets", "Silicone rubber", "Cellulose", "Lunar Regolith Simulant (JSC-1A)", "Martian Regolith Simulant (MGS-1)"],
            "shapes_and_sizes": "Standardized wire segments (10 cm), resistive heating coils, aerosol particle generators (0.05 to 10 μm diameter)."
        },
        "test_conditions": {
            "oxygen_pct_range": "18.0% to 23.5%",
            "airflow_speed_range": "5.0 to 25.0 cm/s sample flow",
            "pressure": "95.0 to 101.3 kPa",
            "diluent": "Standard cabin air"
        },
        "intra_investigation_variables": {
            "varied": "Material pyrolyzate chemistry; heating ramp rate (slow smolder vs fast overheat); aerosol particle concentration and transit time.",
            "held_constant": "Optical detector laser diode wavelength; aerosol sampling line diameter; flow velocity through optical scattering cell."
        },
        "sensors_and_measurements": [
            "P-Trak ultrafine condensation particle counter (CPC)",
            "DustTrak 90-degree light scattering photometer (dual-wavelength)",
            "Scanning Mobility Particle Sizer (SMPS) for size distribution (10 nm to 1 μm)",
            "Transmission Electron Microscopy (TEM) sample collection grids for post-flight morphological analysis"
        ],
        "key_nasa_callouts": {
            "hardware_reuse_title": "Direct Flight Hardware Cross-Link: SAME to DAFT",
            "hardware_reuse_description": "In one of NASA's most successful instrument spin-ins, the specialized smoke detection optical sensor developed for SAME/SAME-R was repurposed and flight-tested in DAFT and DAFT-2 to measure abrasive airborne lunar and Martian regolith dust! On the Moon and Mars, airlocks will inevitably introduce fine regolith into crew habitats. Ordinary optical smoke detectors would trigger false fire alarms daily. The SAME/DAFT multi-angle dual-wavelength sensor reliably distinguishes jagged mineral dust from carbonaceous fire smoke particles."
        },
        "risk_rating": "Critical Infrastructure (Detection & False Alarm Elimination)"
    },
    {
        "id": "saffire-sofie",
        "name": "Saffire I–VI & SOFIE",
        "full_name": "Spacecraft Fire Safety Demonstration (Saffire I–VI) & Solid Fuel Ignition and Extinction (SOFIE)",
        "facility": "Cygnus Autonomous Cargo Vehicle (Saffire) & CIR (SOFIE)",
        "lead_pi": "Dr. David L. Urban (NASA GRC) & Dr. Paul V. Ferkul (NASA GRC)",
        "target_habitats": ["Spacecraft/Crew Capsules", "Lunar Surface Bases (0.16G)", "Martian Habitats (0.38G)"],
        "gravity_range": "0.0 G (Microgravity with Exploration Atmosphere Testing)",
        "objectives": "Assess realistic large-scale spacecraft fire growth in enclosed vehicle volumes post-departure from ISS (Saffire), and establish fundamental ignition/extinction limits of solid fuels in low-pressure, high-oxygen exploration atmospheres (SOFIE).",
        "fuels": {
            "materials": ["SIBAL cotton/fiberglass composite fabric (0.4 m wide x 1.0 m long)", "PMMA sheets and cylinders", "Nomex/Kevlar fabrics", "Spacecraft composite structures"],
            "shapes_and_sizes": "Full-scale 1-meter fabric panels; thick structural polymer slabs (up to 10 mm); curved geometry cable bundles."
        },
        "test_conditions": {
            "oxygen_pct_range": "21.0% to 34.0% (Exploration Atmosphere)",
            "airflow_speed_range": "10.0 to 30.0 cm/s",
            "pressure": "55.0 to 101.3 kPa (8.0 to 14.7 psia)",
            "diluent": "Nitrogen (N2)"
        },
        "intra_investigation_variables": {
            "varied": "Enclosure scale (small CIR chamber vs full 40 m3 Cygnus vehicle); exploration atmospheric pressure (55 kPa vs 101 kPa) and O2% (up to 34%); concurrent vs opposed airflow; sample thickness.",
            "held_constant": "Autonomous data collection architecture; ignition wire thermal impulse."
        },
        "sensors_and_measurements": [
            "Calibrated pressure transducers capturing rapid vehicle pressurization",
            "Multipoint thermocouple arrays across 1-meter sample lengths",
            "High-speed digital video cameras with LED illumination",
            "Oxygen, CO, and CO2 gas concentration sensors",
            "Smoke obscuration optical meters"
        ],
        "key_nasa_callouts": {
            "large_scale_title": "Cygnus Full-Enclosure Fire Dynamics (Saffire)",
            "large_scale_description": "Conducted inside uncrewed Northrop Grumman Cygnus cargo vehicles after departing the ISS, Saffire answered the critical question of how large fires spread in true spacecraft interiors. It proved that flames on large surfaces can spread vigorously even in low airflow, driving dangerous smoke obscuration and toxic gas accumulation in minutes.",
            "exploration_atm_title": "Exploration Atmospheres (SOFIE): 34% O2 at 8.2 psia",
            "exploration_atm_description": "Future Artemis lunar and Martian habitats will utilize lower cabin pressures (56 kPa / 8.2 psia) with elevated oxygen (34% O2) to enable rapid EVA spacewalks without pre-breathing bends risks. SOFIE proved that in this atmosphere, solid materials ignite faster and burn with higher flame spread rates, requiring recalibrated fire codes."
        },
        "risk_rating": "Extreme (Large Scale & Exploration Atmospheres)"
    }
]

HABITAT_PRESETS = [
    {
        "id": "iss-space-station",
        "name": "Space Stations (ISS / Gateway)",
        "gravity_g": 0.0,
        "oxygen_pct": 21.0,
        "pressure_kpa": 101.3,
        "ventilation_speed_cms": 8.0,
        "diluent": "N2",
        "description": "Standard Earth sea-level equivalent microgravity atmosphere. High risk of the 0G Ventilation Paradox due to continuous module HVAC airflow (5–12 cm/s).",
        "recommended_suppression": "Fine-Water-Mist & Ventilation Cutoff",
        "detection_focus": "Multi-angle optical smoke aerosol detection (SAME-R heritage)"
    },
    {
        "id": "crew-capsule",
        "name": "Spacecraft / Crew Capsules (Orion / Dragon)",
        "gravity_g": 0.0,
        "oxygen_pct": 21.5,
        "pressure_kpa": 101.3,
        "ventilation_speed_cms": 12.0,
        "diluent": "N2",
        "description": "Compact crew volume with dense avionics wire harnesses. High risk of rapid smoke buildup and pyrolyzate spread across narrow service ducts.",
        "recommended_suppression": "Immediate Cabin Depressurization / Purge & Fine-Water-Mist",
        "detection_focus": "Early wire-insulation pyrolyzate sniffing"
    },
    {
        "id": "lunar-base",
        "name": "Lunar Surface Bases (Artemis Base Camp)",
        "gravity_g": 0.16,
        "oxygen_pct": 34.0,
        "pressure_kpa": 56.5,
        "ventilation_speed_cms": 6.0,
        "diluent": "N2",
        "description": "0.16G partial gravity with Exploration Atmosphere (8.2 psia, 34% O2). Weak buoyancy creates elongated flames with low soot cooling; abrasive regolith dust enters through airlocks.",
        "recommended_suppression": "Fine-Water-Mist + Rapid Depressurization",
        "detection_focus": "SAME/DAFT dual-mode dust vs smoke discrimination to prevent false alarms"
    },
    {
        "id": "martian-hab",
        "name": "Martian Habitats (Mars Base 1)",
        "gravity_g": 0.38,
        "oxygen_pct": 30.0,
        "pressure_kpa": 65.0,
        "ventilation_speed_cms": 7.0,
        "diluent": "N2",
        "description": "0.38G partial gravity. Buoyancy is ~1/3 of Earth, causing slower buoyant convection that fails to quench flames while high exploration O2 increases heat release.",
        "recommended_suppression": "CO2 / Fine-Water-Mist Hybrid with Ventilation Cutoff",
        "detection_focus": "Regolith dust filtering + sub-micron carbon soot detection"
    },
    {
        "id": "pressurized-rover",
        "name": "Pressurized Rovers (Lunar / Mars Exploration)",
        "gravity_g": 0.16,
        "oxygen_pct": 32.0,
        "pressure_kpa": 58.0,
        "ventilation_speed_cms": 5.0,
        "diluent": "N2",
        "description": "Extreme confined space with direct spacesuit ingress. Rapid toxic gas saturation if a smolder begins; strict dust mitigation required.",
        "recommended_suppression": "Automated Fine-Water-Mist localized nozzle array",
        "detection_focus": "DAFT-2 integrated dust/smoke spectrometer"
    }
]

CIR_HARDWARE_SCHEMATIC = {
    "name": "Combustion Integrated Rack (CIR) — NASA ISS Destiny Laboratory",
    "mass_kg": 544,
    "chamber_volume_liters": 110,
    "operational_features": [
        {
            "component": "Combustion Chamber Assembly (CCA)",
            "role": "Hermetically sealed 110 L stainless steel pressure vessel rated up to 100 atmospheres; features 8 optical windows made of synthetic quartz and sapphire for laser and radiometer access."
        },
        {
            "component": "Chamber Insert Assembly (CIA) — Modular ACME / FLEX / SOFIE",
            "role": "Interchangeable core rack payload. Allows rapid swap between the ACME modular gaseous burner array, the FLEX droplet dispensing SiC fiber rig, and the SOFIE solid fuel wind tunnel without changing the main rack infrastructure."
        },
        {
            "component": "Fuel and Oxidizer Gas Delivery System (FOGS)",
            "role": "Precise mass-flow controller network delivering custom gas mixtures (O2, N2, CO2, He, CH4, C2H4) with millisecond-accuracy solenoid shutoff."
        },
        {
            "component": "Optics Bench & Multi-Wavelength Diagnostics",
            "role": "Equipped with high-speed color camera (1000 fps), intensified UV/OH* chemiluminescence imaging, dual broadband radiometers, and Thin-Filament Pyrometry (TFP)."
        },
        {
            "component": "Exhaust Gas Recirculation & Filter Package",
            "role": "Scans and cleans chamber gases through HEPA particulate scrubbers and catalytic converters before venting to space vacuum or cabin return."
        }
    ]
}

EARTH_SPINOFFS = [
    {
        "title": "Clean Fine-Water-Mist Fire Extinguishers",
        "space_origin": "Developed and perfected in FLEX and CFI on the ISS to safely quench microgravity liquid and solid fires without flooding electronics or releasing toxic halocarbon gases.",
        "terrestrial_impact": "Adopted by modern hyperscale data centers, submarine machinery spaces, surgical suites, and aviation engine compartments. Absorbs massive heat without conductive pooling or chemical toxicity.",
        "icon": "fa-droplet"
    },
    {
        "title": "SAME / DAFT Optical Smoke vs. Dust Discriminators",
        "space_origin": "Engineered for SAME to detect spacecraft wire smolder smoke, then flight-repurposed for DAFT/DAFT-2 to detect lunar and Martian abrasive dust aerosols.",
        "terrestrial_impact": "Revolutionized terrestrial smoke detection in harsh industrial environments (coal mines, wood processing plants, semiconductor cleanrooms, grain silos) where false alarms previously caused costly evacuations.",
        "icon": "fa-shield-halved"
    },
    {
        "title": "Advanced High-Temperature Thermal Barriers & Aerogels",
        "space_origin": "Engineered for CIR internal flame isolation barriers, Saffire vehicle heat shields, and BASS sample boundary containment.",
        "terrestrial_impact": "Now incorporated into ultra-lightweight structural firefighter turnout jackets, electric vehicle (EV) battery pack runaway containment shields, and cryogenic liquid hydrogen storage tanks.",
        "icon": "fa-fire-extinguisher"
    }
]

COPILOT_KNOWLEDGE_BASE = [
    {
        "keywords": ["ventilation paradox", "0g paradox", "airflow paradox", "bass", "low airflow"],
        "title": "The 0G Ventilation Paradox (BASS / BASS-II Findings)",
        "answer": "In microgravity (0G), natural buoyant convection is eliminated. In completely stagnant air (0 cm/s), a flame suffocates under its own combustion products (CO2, H2O). However, NASA's BASS experiments proved that when low ventilation airflow (3 to 14 cm/s)—such as normal ISS cabin HVAC or crew movement drafts—is introduced, it continuously replenishes oxygen to the flame without inducing convective heat loss. As a result, solid materials (like PMMA and space fabrics) burn at LOWER oxygen concentrations in 0G (down to ~16.5% O2) than on Earth in 1G (where buoyant convection cools the reaction zone)! Countermeasure: Immediately shut down local ventilation dampers upon smoke detection."
    },
    {
        "keywords": ["cool flame", "cool flames", "cfi", "flex", "invisible flame", "droplet"],
        "title": "Invisible Cool Flames & Reignition Threat (FLEX / CFI Findings)",
        "answer": "Discovered in the Combustion Integrated Rack (CIR) during FLEX and CFI droplet experiments, Cool Flames occur when a hot luminous flame (~1500–1800 K) undergoes radiative heat loss extinction, but fails to stop reacting. Instead, it transitions into an invisible, low-temperature reaction zone (500–800 K) supported by peroxy radical chain chemistry. To the naked eye and normal cameras, the fire appears completely extinguished, yet it silently consumes fuel and can re-ignite into a raging hot flame if ventilation drafts increase or oxygen rises. NASA flight rules mandate continuous radiometer and thermal monitoring even after visible flames vanish."
    },
    {
        "keywords": ["acme", "bre", "burning rate emulator", "modular", "cir modular"],
        "title": "ACME Modular Architecture & Burning Rate Emulator (BRE)",
        "answer": "ACME (Advanced Combustion via Microgravity Experiments) comprised 6 distinct experiments inside the ISS Combustion Integrated Rack (CIR): BRE, CFI-2, CLD Flame, E-FIELD, Flame Design, and PEAC. ALL 6 experiments shared the SAME modular set of ACME hardware, saving launch mass and crew installation time. The Burning Rate Emulator (BRE) burned gaseous fuels (CH4, C2H4) through a porous sintered burner with controlled surface heat extraction to emulate the flammability limits and burning rates of condensed solids/liquids in quiescent atmospheres without the chaotic regression or dripping of real solids."
    },
    {
        "keywords": ["same", "daft", "dust", "smoke detector", "false alarm", "repurpose"],
        "title": "SAME / DAFT Flight Instrument Cross-Link",
        "answer": "The optical smoke detection instrument flown in the Smoke Aerosol Measurement Experiment (SAME / SAME-R) on the ISS was directly repurposed and flight-tested in the Dust and Aerosol Measurement Feasibility Test (DAFT and DAFT-2). On lunar and Martian bases, sharp abrasive regolith dust introduced through airlocks would cause traditional optical smoke detectors to trigger constant false alarms. By analyzing dual-wavelength, multi-angle light scattering proven in SAME/DAFT, systems can distinguish irregular mineral dust from spherical carbonaceous smoke soot."
    },
    {
        "keywords": ["saffire", "sofie", "cygnus", "large scale", "exploration atmosphere"],
        "title": "Saffire Large-Scale Enclosure Fires & SOFIE Exploration Atmospheres",
        "answer": "Saffire I–VI conducted large-scale enclosure fire tests inside uncrewed Cygnus cargo spacecraft after departing the ISS. Burning meter-long fabric panels and thick polymers, Saffire proved that real spacecraft fire growth causes rapid vehicle pressurization, heavy smoke obscuration, and oxygen depletion within minutes. SOFIE tested exploration atmospheres planned for Artemis lunar bases (34% O2 at 8.2 psia / 56 kPa), finding that higher oxygen drastically accelerates flame spread velocity, making terrestrial fire-retardant ratings invalid in exploration habitats."
    },
    {
        "keywords": ["fine water mist", "mist", "extinguisher", "suppression", "halon"],
        "title": "Next-Gen Fine-Water-Mist Fire Suppression",
        "answer": "Traditional spacecraft used Halon 1301 or CO2 extinguishers. However, Halon leaves toxic pyrolysis byproducts and CO2 displaces breathing air in closed habitats. FLEX and CFI validated Fine-Water-Mist suppression: micro-droplets (10–30 μm) evaporate instantly upon reaching the flame front, expanding 1700x and absorbing massive latent heat of vaporization (2260 kJ/kg). It quenches both hot and cool flames without wetting electronics or suffocating the crew."
    }
]

ROCKET_PROPULSION_SCOPE_NOTE = {
    "title": "NASA Scope Advisory: Rocket Propulsion vs. Habitable Crew Fire Safety",
    "status": "EXCLUDED FROM PSI HABITABLE REPOSITORIES",
    "physics_explanation": (
        "Fire safety involving rockets and liquid/solid propellants is strictly beyond the scope of the "
        "NASA Physical Sciences Informatics (PSI) database. Within rocket combustion chambers and turbopumps, "
        "extremely high fluid shear velocities (u > 100 to 300 m/s) generate turbulent Reynolds numbers (Re > 10^6) "
        "and Richardson numbers (Ri = Gr/Re^2 << 10^-4), rendering combustion physics effectively independent of gravity. "
        "In contrast, fire safety inside habitable crew volumes (spacecraft, space stations, lunar/Martian habitats, and rovers) "
        "operates in low-velocity regimes (0 to 30 cm/s) where the absence or reduction of buoyant natural convection drastically "
        "alters flammability boundaries, smoldering transitions, smoke transport, and extinction limits."
    ),
    "focus_areas": [
        "Cabin Atmospheric Regimes (21% to 34% O2, 55 to 101 kPa)",
        "Low-Velocity HVAC Forced Convection (0 to 30 cm/s)",
        "Condensed Solid & Liquid Materials Flammability (PMMA, Nomex, Wire Insulation, Alkane Droplets)",
        "Crew Habitat Suppression (Fine-Water-Mist, Depressurization, SAME/DAFT Dust/Smoke Discrimination)"
    ]
}

def rank_investigations_for_habitat(habitat_id):
    """
    Scientific Intelligence (SI) Engine: Computes a quantitative relevance score (0-100%)
    and actionable flight engineering prescriptions for any chosen habitable crew environment.
    """
    hab = next((h for h in HABITAT_PRESETS if h['id'] == habitat_id), HABITAT_PRESETS[0])
    
    ranked = []
    for inv in PSI_INVESTIGATIONS:
        score = 50.0
        rationale = []
        
        # 1. Target habitat affinity
        if any(hab['name'].split()[0].lower() in t.lower() for t in inv['target_habitats']):
            score += 25.0
            rationale.append("Direct operational habitat alignment")
            
        # 2. Gravity regime compatibility
        if "0.0 G" in inv['gravity_range'] and hab['gravity_g'] == 0.0:
            score += 15.0
            rationale.append("Identical microgravity (0G) buoyancy-free physics")
        elif ("0.16G" in str(inv) or "partial" in str(inv).lower()) and hab['gravity_g'] in [0.16, 0.38]:
            score += 15.0
            rationale.append(f"Partial gravity ({hab['gravity_g']}G) transition applicability")
            
        # 3. Atmosphere & test conditions match
        if hab['oxygen_pct'] > 25.0 and ("Exploration" in str(inv) or "34%" in str(inv) or "SOFIE" in inv['name']):
            score += 10.0
            rationale.append("Exploration atmosphere (high-O2 / low-pressure) calibration")
            
        # 4. Critical equipment or cross-link match
        if "dust" in hab['detection_focus'].lower() and ("DAFT" in inv['name'] or "SAME" in inv['name']):
            score += 10.0
            rationale.append("SAME/DAFT regolith dust vs. smoke false-alarm rejection")
            
        if "mist" in hab['recommended_suppression'].lower() and ("FLEX" in inv['name'] or "CFI" in inv['name']):
            score += 10.0
            rationale.append("Fine-Water-Mist latent heat suppression guidelines")
            
        if hab['gravity_g'] == 0.0 and ("BASS" in inv['name'] or "ACME" in inv['name']):
            score += 10.0
            rationale.append("0G Ventilation Paradox & HVAC airflow isolation protocols")

        score = min(99.0, max(45.0, score))
        snippet = ""
        for k, v in inv.get('key_nasa_callouts', {}).items():
            if 'description' in k:
                snippet = v[:180] + "..."
                break
        if not snippet:
            snippet = inv['objectives'][:180] + "..."

        ranked.append({
            "investigation_id": inv['id'],
            "investigation_name": inv['name'],
            "full_name": inv['full_name'],
            "facility": inv['facility'],
            "relevance_score_pct": round(score, 1),
            "match_rationale": " | ".join(rationale),
            "risk_rating": inv['risk_rating'],
            "key_takeaway": snippet
        })
        
    ranked.sort(key=lambda x: x['relevance_score_pct'], reverse=True)
    return {
        "habitat": hab,
        "ranked_investigations": ranked,
        "scope_advisory": ROCKET_PROPULSION_SCOPE_NOTE
    }

