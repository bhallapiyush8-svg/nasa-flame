import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'flame_project.settings')
django.setup()

from django.test import Client
import json

def run_tests():
    c = Client()
    print("=== Testing Django Backend Endpoints ===")

    # 1. Test Home page
    res = c.get('/')
    assert res.status_code == 200, f"Home page returned {res.status_code}"
    assert b"FLAME IN" in res.content, "Home page missing title"
    print(" [PASS] GET / -> 200 OK")

    # 2. Test Investigations API
    res = c.get('/api/investigations/')
    assert res.status_code == 200, f"Investigations API returned {res.status_code}"
    data = res.json()
    assert data['count'] >= 5, f"Expected at least 5 investigations, got {data['count']}"
    
    # Check NASA callouts in investigations
    inv_names = [i['name'] for i in data['investigations']]
    print(f" [PASS] GET /api/investigations/ -> Found: {inv_names}")
    
    # Verify specific NASA callouts
    bass = next(i for i in data['investigations'] if 'BASS' in i['name'])
    assert '0G Ventilation Paradox' in bass['key_nasa_callouts']['paradox_title']
    print(" [PASS] BASS 0G Ventilation Paradox Verified")

    flex = next(i for i in data['investigations'] if 'FLEX' in i['name'])
    assert 'Cool Flames' in flex['key_nasa_callouts']['cool_flame_title']
    print(" [PASS] FLEX / CFI Cool Flames & Fine-Water-Mist Verified")

    acme = next(i for i in data['investigations'] if 'ACME' in i['name'])
    assert 'Modular Hardware' in acme['key_nasa_callouts']['modular_acme_title']
    assert 'Emulating Solids' in acme['key_nasa_callouts']['bre_emulator_title']
    print(" [PASS] ACME 6-in-1 Modular CIR Hardware & BRE Emulator Verified")

    same = next(i for i in data['investigations'] if 'SAME' in i['name'])
    assert 'SAME to DAFT' in same['key_nasa_callouts']['hardware_reuse_title']
    print(" [PASS] SAME / DAFT Flight Instrument Cross-Link Verified")

    # 3. Test ML Predict API
    payload = {
        "gravity_g": 0.0,
        "oxygen_pct": 21.0,
        "pressure_kpa": 101.3,
        "ventilation_speed_cms": 6.0,
        "sample_thickness_mm": 1.5,
        "fuel_phase": "Solid",
        "diluent_gas": "N2",
        "suppression_method": "None"
    }
    res = c.post('/api/predict/', data=json.dumps(payload), content_type='application/json')
    assert res.status_code == 200, f"Predict API returned {res.status_code}"
    pred = res.json()
    print(f" [PASS] POST /api/predict/ -> Regime: {pred['combustion_regime']} ({pred['regime_confidence']}%), Spread: {pred['flame_spread_rate_mm_s']} mm/s, Risk: {pred['fire_risk_score']}")
    assert len(pred['physics_insights']) > 0, "Expected physics insights"
    assert any('0G Ventilation Paradox' in ins['title'] for ins in pred['physics_insights'])
    print(" [PASS] Automated 0G Ventilation Paradox Physics Diagnostic Verified")

    # 4. Test Scenario Simulator
    scenario_payload = {
        "habitat_id": "iss-space-station",
        "incident_type": "wire_overheat",
        "actions": ["vent_cutoff", "fine_water_mist"]
    }
    res = c.post('/api/scenario/simulate/', data=json.dumps(scenario_payload), content_type='application/json')
    assert res.status_code == 200
    sc_data = res.json()
    assert sc_data['damage_mitigation_pct'] > 50
    print(f" [PASS] POST /api/scenario/simulate/ -> Status: {sc_data['status']}, Mitigation: {sc_data['damage_mitigation_pct']}%")

    # 5. Test AI Co-Pilot Query
    q_payload = {"query": "Tell me about the 0G ventilation paradox in BASS"}
    res = c.post('/api/copilot/query/', data=json.dumps(q_payload), content_type='application/json')
    assert res.status_code == 200
    co_data = res.json()
    assert "Ventilation Paradox" in co_data['title']
    print(f" [PASS] POST /api/copilot/query/ -> Answered: '{co_data['title']}' (Confidence: {co_data['confidence']})")

    # 6. Test Experiments List API
    res = c.get('/api/experiments/?limit=10')
    assert res.status_code == 200
    exp_data = res.json()
    assert exp_data['total_count'] >= 1000
    assert len(exp_data['results']) == 10
    print(f" [PASS] GET /api/experiments/ -> Total Runs: {exp_data['total_count']}")

    # 7. Test Stats API
    res = c.get('/api/stats/')
    assert res.status_code == 200
    st_data = res.json()
    assert 'regime_distribution' in st_data
    print(f" [PASS] GET /api/stats/ -> Regimes: {list(st_data['regime_distribution'].keys())}")

    # 8. Test Dataset Download
    res_csv = c.get('/api/dataset/download/?format=csv')
    assert res_csv.status_code == 200
    assert res_csv['Content-Type'] == 'text/csv'
    print(" [PASS] GET /api/dataset/download/?format=csv -> Valid CSV stream")

    res_json = c.get('/api/dataset/download/?format=json')
    assert res_json.status_code == 200
    assert res_json['Content-Type'] == 'application/json'
    print(" [PASS] GET /api/dataset/download/?format=json -> Valid JSON stream")

    # 9. Test NASA Extractor Sources API
    res_sources = c.get('/api/extractor/sources/')
    assert res_sources.status_code == 200
    sources_data = res_sources.json()
    assert len(sources_data['sources']) >= 3
    assert len(sources_data['citations']) >= 5
    print(f" [PASS] GET /api/extractor/sources/ -> Found {len(sources_data['sources'])} NASA Sources & {len(sources_data['citations'])} Primary Flight Citations")

    # 10. Test NASA Extractor Ingestion Sync API
    sync_payload = {"sample_count": 1600, "sync_online": False}
    res_sync = c.post('/api/extractor/sync/', data=json.dumps(sync_payload), content_type='application/json')
    assert res_sync.status_code == 200
    sync_data = res_sync.json()
    assert sync_data['success'] is True
    assert sync_data['records_extracted'] == 1600
    print(f" [PASS] POST /api/extractor/sync/ -> Extracted {sync_data['records_extracted']} records, ML re-trained in {sync_data['execution_time_seconds']}s")

    print("\n ALL SYSTEM TESTS PASSED CLEANLY (10/10)! READY FOR MISSION!")

if __name__ == '__main__':
    run_tests()
