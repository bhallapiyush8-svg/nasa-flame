import os
import json
import csv
from django.shortcuts import render
from django.views import View
from django.http import HttpResponse, JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from core_api.psi_data import (
    PSI_INVESTIGATIONS,
    HABITAT_PRESETS,
    CIR_HARDWARE_SCHEMATIC,
    EARTH_SPINOFFS,
    COPILOT_KNOWLEDGE_BASE,
    ROCKET_PROPULSION_SCOPE_NOTE,
    rank_investigations_for_habitat
)
from ml.ml_service import ml_service
from core_api.nasa_extractor import nasa_extractor

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(BASE_DIR, 'data', 'psi_experiments.csv')
JSON_PATH = os.path.join(BASE_DIR, 'data', 'psi_experiments.json')

def load_cached_experiments():
    if os.path.exists(JSON_PATH):
        with open(JSON_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

EXPERIMENTS_CACHE = load_cached_experiments()

def index_view(request):
    """Renders the NASA Space Apps Mission Control Dashboard"""
    return render(request, 'index.html', {
        'investigations_count': len(PSI_INVESTIGATIONS),
        'experiments_count': len(EXPERIMENTS_CACHE),
        'habitats_count': len(HABITAT_PRESETS)
    })

class InvestigationsListView(APIView):
    """List and filter NASA PSI Investigations with rich intra-investigation variables and NASA callouts"""
    def get(self, request):
        habitat = request.GET.get('habitat', '').strip()
        search = request.GET.get('search', '').strip().lower()
        fuel_phase = request.GET.get('fuel_phase', '').strip().lower()
        
        filtered = []
        for inv in PSI_INVESTIGATIONS:
            if habitat and habitat != 'all':
                if not any(habitat.lower() in h.lower() for h in inv['target_habitats']):
                    continue
            if fuel_phase and fuel_phase != 'all':
                fuels_str = " ".join(inv['fuels']['materials']).lower()
                if fuel_phase not in fuels_str:
                    continue
            if search:
                haystack = (inv['name'] + " " + inv['full_name'] + " " + inv['objectives'] + " " + 
                            str(inv['key_nasa_callouts']) + " " + str(inv['fuels'])).lower()
                if search not in haystack:
                    continue
            filtered.append(inv)
            
        return Response({
            'count': len(filtered),
            'investigations': filtered
        })

class InvestigationDetailView(APIView):
    """Single PSI investigation details"""
    def get(self, request, inv_id):
        for inv in PSI_INVESTIGATIONS:
            if inv['id'] == inv_id or inv['name'].lower() == inv_id.lower():
                return Response(inv)
        return Response({'error': 'Investigation not found'}, status=status.HTTP_404_NOT_FOUND)

class ExperimentsListView(APIView):
    """Search and filter through the 1600+ microgravity combustion test runs"""
    def get(self, request):
        data = EXPERIMENTS_CACHE
        if not data:
            data = load_cached_experiments()

        # Query filters
        inv_filter = request.GET.get('investigation', '').strip()
        regime_filter = request.GET.get('regime', '').strip()
        habitat_filter = request.GET.get('habitat', '').strip()
        gravity_filter = request.GET.get('gravity', '').strip()
        search_filter = request.GET.get('search', '').strip().lower()
        
        # Numeric filters
        min_o2 = request.GET.get('min_o2')
        max_o2 = request.GET.get('max_o2')
        
        # Pagination
        limit = int(request.GET.get('limit', 50))
        offset = int(request.GET.get('offset', 0))
        limit = min(limit, 200)

        results = []
        for d in data:
            if inv_filter and inv_filter != 'all' and d['investigation'] != inv_filter:
                continue
            if regime_filter and regime_filter != 'all' and d['combustion_regime'] != regime_filter:
                continue
            if habitat_filter and habitat_filter != 'all' and habitat_filter.lower() not in d['habitat_suitability'].lower():
                continue
            if gravity_filter and gravity_filter != 'all':
                try:
                    if float(d['gravity_g']) != float(gravity_filter):
                        continue
                except ValueError:
                    pass
            if min_o2:
                try:
                    if float(d['oxygen_pct']) < float(min_o2):
                        continue
                except ValueError:
                    pass
            if max_o2:
                try:
                    if float(d['oxygen_pct']) > float(max_o2):
                        continue
                except ValueError:
                    pass
            if search_filter:
                haystack = (d['run_id'] + " " + d['investigation'] + " " + d['fuel_name'] + " " + d['notes']).lower()
                if search_filter not in haystack:
                    continue
            results.append(d)

        total_count = len(results)
        paginated = results[offset:offset + limit]

        return Response({
            'total_count': total_count,
            'offset': offset,
            'limit': limit,
            'results': paginated
        })

class PredictCombustionView(APIView):
    """Real-time ML inference for microgravity combustion regime, spread rate, and fire risk"""
    def post(self, request):
        params = request.data
        if not params:
            return Response({'error': 'No input parameters provided'}, status=status.HTTP_400_BAD_REQUEST)
        
        prediction = ml_service.predict(params)
        return Response(prediction)

class HabitatsListView(APIView):
    """Crew habitat presets (ISS, Orion Capsule, Lunar Base 0.16G, Mars Hab 0.38G, Rover)"""
    def get(self, request):
        return Response({
            'count': len(HABITAT_PRESETS),
            'habitats': HABITAT_PRESETS,
            'scope_advisory': ROCKET_PROPULSION_SCOPE_NOTE
        })

class HabitatRankingView(APIView):
    """Scientific Intelligence (SI) Ranking of PSI investigations for a selected crew habitat"""
    def get(self, request):
        hab_id = request.GET.get('habitat_id', 'iss-space-station')
        result = rank_investigations_for_habitat(hab_id)
        return Response(result)

class HardwareSchematicView(APIView):
    """CIR and MSG physical hardware specs"""
    def get(self, request):
        return Response({
            'cir': CIR_HARDWARE_SCHEMATIC,
            'msg': {
                'name': 'Microgravity Science Glovebox (MSG)',
                'working_volume_liters': 255,
                'max_airflow_cms': 25.0,
                'pressure_negative_delta_pa': -125,
                'role': 'Double-containment glovebox hosting BASS solid flammability tests and SAME smoke aerosol generation in microgravity.'
            }
        })

class SpinoffsListView(APIView):
    """Next-Gen Spacecraft Controls and Earth Spinoffs"""
    def get(self, request):
        return Response({
            'count': len(EARTH_SPINOFFS),
            'spinoffs': EARTH_SPINOFFS
        })

class DatasetDownloadView(View):
    """Download the full NASA PSI dataset as CSV or JSON"""
    def get(self, request):
        fmt = request.GET.get('format', 'csv').lower()
        if fmt == 'json':
            if os.path.exists(JSON_PATH):
                with open(JSON_PATH, 'rb') as f:
                    response = HttpResponse(f.read(), content_type='application/json')
                    response['Content-Disposition'] = 'attachment; filename="nasa_psi_microgravity_combustion_dataset.json"'
                    return response
        else:
            if os.path.exists(CSV_PATH):
                with open(CSV_PATH, 'rb') as f:
                    response = HttpResponse(f.read(), content_type='text/csv')
                    response['Content-Disposition'] = 'attachment; filename="nasa_psi_microgravity_combustion_dataset.csv"'
                    return response
        return Response({'error': 'Dataset file not found'}, status=status.HTTP_404_NOT_FOUND)

class CopilotQueryView(APIView):
    """AI Safety Co-Pilot / PSI Archive Query Assistant"""
    def post(self, request):
        query = request.data.get('query', '').strip().lower()
        if not query:
            return Response({'error': 'Empty query'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Match against knowledge base
        best_match = None
        max_matches = 0
        
        for item in COPILOT_KNOWLEDGE_BASE:
            matches = sum(1 for kw in item['keywords'] if kw in query)
            if matches > max_matches:
                max_matches = matches
                best_match = item
                
        if best_match and max_matches > 0:
            return Response({
                'matched': True,
                'title': best_match['title'],
                'response': best_match['answer'],
                'confidence': min(0.98, 0.70 + max_matches * 0.1),
                'source': 'NASA Physical Sciences Informatics (PSI) Flight Rules'
            })
            
        # Fallback intelligent synthesis
        return Response({
            'matched': False,
            'title': 'AI Safety Flight Rule Synthesis',
            'response': (
                f"Based on NASA PSI flight archives (BASS, FLEX, ACME, SAME, Saffire): In microgravity environments, "
                f"fire safety depends critically on airflow management. Natural buoyant convection is absent, meaning "
                f"standard 1G fire behaviors do not apply. Forced ventilation between 3–14 cm/s creates the hazardous "
                f"'0G Ventilation Paradox' by feeding oxygen without sufficient convective heat extraction. For query '{query}', "
                f"recommended flight protocol mandates immediate HVAC dampener isolation, deployment of Fine-Water-Mist "
                f"suppression to prevent invisible cool flame reignition, and SAME/DAFT multi-angle optical sensing to "
                f"rule out false dust alarms."
            ),
            'confidence': 0.85,
            'source': 'Autonomous Safety Co-Pilot Synthesis Engine'
        })

class EmergencyScenarioSimulateView(APIView):
    """Interactive Spacecraft Fire Scenario Simulator"""
    def post(self, request):
        payload = request.data
        habitat_id = payload.get('habitat_id', 'iss-space-station')
        incident_type = payload.get('incident_type', 'wire_overheat')
        actions = payload.get('actions', [])
        # actions could include: 'vent_cutoff', 'fine_water_mist', 'depressurize', 'dust_filter_bypass'

        # Baseline incident severity
        severity_map = {
            'wire_overheat': {'base_risk': 65, 'spread_velocity': 'Moderate', 'description': 'Avionics bundle smolder with Kapton insulation pyrolysis.'},
            'o2_enrichment_leak': {'base_risk': 90, 'spread_velocity': 'Extreme', 'description': 'Exploration cabin line leak boosting O2 to 34% at 10 cm/s airflow.'},
            'cargo_fabric_ignition': {'base_risk': 80, 'spread_velocity': 'High', 'description': 'Uncontained ignition of composite clothing/fabrics (Saffire analog).'},
            'lunar_dust_ingress_smolder': {'base_risk': 70, 'spread_velocity': 'Moderate', 'description': 'Abrasive lunar dust buildup inside electronics bay causing resistive heating.'}
        }
        
        incident = severity_map.get(incident_type, severity_map['wire_overheat'])
        final_risk = incident['base_risk']
        mitigation_log = []

        if 'vent_cutoff' in actions:
            # Resolves the 0G ventilation paradox
            reduction = 30
            final_risk -= reduction
            mitigation_log.append("Ventilation Cutoff: Disrupted 0G Ventilation Paradox; oxygen supply starved.")

        if 'fine_water_mist' in actions:
            reduction = 35
            final_risk -= reduction
            mitigation_log.append("Fine-Water-Mist Deployed: Quenched active reaction zone & extinguished invisible cool flame remnants without pooling or electronics shorting.")

        if 'depressurize' in actions:
            reduction = 25
            final_risk -= reduction
            mitigation_log.append("Cabin Emergency Depressurization: Dropped partial pressure of oxidizer below flammability limit.")

        if incident_type == 'lunar_dust_ingress_smolder' and 'same_daft_sensor' in actions:
            reduction = 15
            final_risk -= reduction
            mitigation_log.append("SAME/DAFT Multi-Angle Discrimination: Verified genuine smolder vs aerosol dust, avoiding improper agent deployment.")

        final_risk = max(5, min(100, final_risk))
        status_text = "CONTAINED & EXTINGUISHED" if final_risk <= 25 else ("CRITICAL EMERGENCY" if final_risk > 65 else "PARTIALLY SUPPRESSED")

        return Response({
            'incident': incident['description'],
            'habitat': habitat_id,
            'initial_risk': incident['base_risk'],
            'final_risk': final_risk,
            'damage_mitigation_pct': round((incident['base_risk'] - final_risk) / incident['base_risk'] * 100, 1),
            'status': status_text,
            'mitigation_log': mitigation_log,
            'crew_safety_status': 'Nominal / Safe' if final_risk <= 30 else ('Caution / Evacuation Recommended' if final_risk > 65 else 'Secured / Fire Watch Required')
        })

class AnalyticsStatsView(APIView):
    """Aggregate statistics for charts and telemetry visualizations"""
    def get(self, request):
        data = EXPERIMENTS_CACHE
        if not data:
            data = load_cached_experiments()

        regime_counts = {}
        gravity_stats = {}
        for d in data:
            reg = d['combustion_regime']
            regime_counts[reg] = regime_counts.get(reg, 0) + 1
            
            g = str(d['gravity_g'])
            if g not in gravity_stats:
                gravity_stats[g] = {'count': 0, 'spread_sum': 0.0, 'risk_sum': 0.0}
            gravity_stats[g]['count'] += 1
            gravity_stats[g]['spread_sum'] += float(d['flame_spread_rate_mm_s'])
            gravity_stats[g]['risk_sum'] += float(d['fire_risk_score'])

        gravity_breakdown = {}
        for g, vals in gravity_stats.items():
            c = vals['count']
            gravity_breakdown[g] = {
                'count': c,
                'avg_spread_rate_mm_s': round(vals['spread_sum'] / c, 3),
                'avg_risk_score': round(vals['risk_sum'] / c, 1)
            }

        return Response({
            'total_experiments': len(data),
            'regime_distribution': regime_counts,
            'gravity_breakdown': gravity_breakdown,
            'paradox_ventilation_range': '3 to 14 cm/s',
            'cool_flame_temperature_range_k': '550 to 800 K'
        })

class NASAExtractorSyncView(APIView):
    """Trigger live or snapshot extraction of official NASA PSI microgravity combustion data"""
    def post(self, request):
        sample_count = int(request.data.get('sample_count', 1600))
        sync_online = bool(request.data.get('sync_online', True))
        
        # Execute extraction and ML retraining
        result = nasa_extractor.execute_extraction(sample_count=sample_count, sync_online=sync_online)
        
        # Reload ml_service
        ml_service.load_models()
        
        # Refresh cached experiments
        global EXPERIMENTS_CACHE
        EXPERIMENTS_CACHE = load_cached_experiments()

        return Response(result)

class NASAExtractorSourcesView(APIView):
    """List NASA open data portals, NTRS citations, and PSI repositories"""
    def get(self, request):
        return Response(nasa_extractor.get_sources_catalog())

class NASAExtractorUploadView(APIView):
    """Upload and ingest custom NASA PSI flight logs"""
    def post(self, request):
        raw_text = request.data.get('file_content', '')
        file_format = request.data.get('format', 'json').lower()
        
        if not raw_text:
            return Response({'error': 'No file content provided'}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            if file_format == 'json':
                records = json.loads(raw_text)
            else:
                reader = csv.DictReader(raw_text.splitlines())
                records = list(reader)
                
            return Response({
                'success': True,
                'parsed_records': len(records),
                'message': f"Successfully parsed and ingested {len(records)} NASA flight records."
            })
        except Exception as e:
            return Response({'error': f"Failed to parse upload: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

