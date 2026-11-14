/**
 * NASA Space Apps 2026 — Flame in Freefall
 * Mission Control Main Application Controller
 */

document.addEventListener('DOMContentLoaded', () => {
  // Initialize Flame Simulator
  const flameSim = new window.MicrogravityFlameSimulator('flameCanvas');

  // State
  let allInvestigations = [];
  let comparisonQueue = [];
  let currentHabitat = 'iss-space-station';
  let habitatRankingMap = {};

  // ==========================================
  // NAVIGATION & TAB SWITCHING
  // ==========================================
  const tabBtns = document.querySelectorAll('.nav-tab-btn');
  const tabPanels = document.querySelectorAll('.tab-panel');

  tabBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      const target = btn.dataset.tab;
      tabBtns.forEach(b => b.classList.remove('active'));
      tabPanels.forEach(p => p.classList.remove('active'));

      btn.classList.add('active');
      const targetPanel = document.getElementById(target);
      if (targetPanel) {
        targetPanel.classList.add('active');
        if (target === 'tab-simulator' && flameSim) {
          flameSim.resizeCanvas();
        }
        if (target === 'tab-analytics') {
          loadAnalyticsCharts();
        }
      }
    });
  });

  // ==========================================
  // SIMULATOR CONTROLS & BINDINGS
  // ==========================================
  const gravBtns = document.querySelectorAll('.grav-btn');
  gravBtns.forEach(b => {
    b.addEventListener('click', () => {
      gravBtns.forEach(x => x.classList.remove('active'));
      b.classList.add('active');
      const g = parseFloat(b.dataset.g);
      flameSim.setGravity(g);
      // Sync ML form if user switches
      const mlGrav = document.getElementById('ml_gravity');
      if (mlGrav) mlGrav.value = g;
    });
  });

  const ventSlider = document.getElementById('simVentSlider');
  const ventValText = document.getElementById('simVentVal');
  if (ventSlider) {
    ventSlider.addEventListener('input', (e) => {
      const v = parseFloat(e.target.value);
      if (ventValText) ventValText.textContent = `${v.toFixed(1)} cm/s`;
      flameSim.setVentilation(v);
    });
  }

  const o2Slider = document.getElementById('simO2Slider');
  const o2ValText = document.getElementById('simO2Val');
  if (o2Slider) {
    o2Slider.addEventListener('input', (e) => {
      const o2 = parseFloat(e.target.value);
      if (o2ValText) o2ValText.textContent = `${o2.toFixed(1)}%`;
      flameSim.setOxygen(o2);
    });
  }

  const fuelSelect = document.getElementById('simFuelSelect');
  if (fuelSelect) {
    fuelSelect.addEventListener('change', (e) => {
      flameSim.setFuelType(e.target.value);
    });
  }

  const coolFlameToggle = document.getElementById('simCoolFlameToggle');
  if (coolFlameToggle) {
    coolFlameToggle.addEventListener('change', (e) => {
      flameSim.toggleCoolFlame(e.target.checked);
    });
  }

  const mistBtn = document.getElementById('simMistBtn');
  if (mistBtn) {
    mistBtn.addEventListener('click', () => {
      flameSim.triggerMistSuppression();
    });
  }

  // ==========================================
  // HABITAT PRESETS SELECTOR
  // ==========================================
  const habitatSelect = document.getElementById('globalHabitatPreset');
  if (habitatSelect) {
    habitatSelect.addEventListener('change', (e) => {
      applyHabitatPreset(e.target.value);
    });
  }

  async function applyHabitatPreset(habitatId) {
    currentHabitat = habitatId;
    try {
      const res = await fetch('/api/habitats/');
      const data = await res.json();
      const hab = data.habitats.find(h => h.id === habitatId);
      if (!hab) return;

      // Update simulator
      flameSim.setGravity(hab.gravity_g);
      flameSim.setVentilation(hab.ventilation_speed_cms);
      flameSim.setOxygen(hab.oxygen_pct);

      // Update UI controls
      if (ventSlider) {
        ventSlider.value = hab.ventilation_speed_cms;
        if (ventValText) ventValText.textContent = `${hab.ventilation_speed_cms} cm/s`;
      }
      if (o2Slider) {
        o2Slider.value = hab.oxygen_pct;
        if (o2ValText) o2ValText.textContent = `${hab.oxygen_pct}%`;
      }

      // Update gravity buttons
      gravBtns.forEach(b => {
        b.classList.toggle('active', parseFloat(b.dataset.g) === hab.gravity_g);
      });

      // Update ML input form
      const mlGrav = document.getElementById('ml_gravity');
      const mlO2 = document.getElementById('ml_oxygen');
      const mlPress = document.getElementById('ml_pressure');
      const mlVent = document.getElementById('ml_ventilation');
      const mlDiluent = document.getElementById('ml_diluent');

      if (mlGrav) mlGrav.value = hab.gravity_g;
      if (mlO2) mlO2.value = hab.oxygen_pct;
      if (mlPress) mlPress.value = hab.pressure_kpa;
      if (mlVent) mlVent.value = hab.ventilation_speed_cms;
      if (mlDiluent) mlDiluent.value = hab.diluent;

      // Update Habitat banner description
      const habBanner = document.getElementById('habitatDescriptionBanner');
      if (habBanner) {
        habBanner.innerHTML = `
          <strong>${hab.name} Profile Loaded:</strong> ${hab.description} 
          <span style="color:var(--accent-green); margin-left:8px;">Suppression: ${hab.recommended_suppression}</span>
        `;
      }

      // Automatically trigger ML prediction with new preset
      runMLPrediction();
    } catch (err) {
      console.error("Failed to load habitat preset:", err);
    }
  }

  // ==========================================
  // PSI INVESTIGATIONS EXPLORER & COMPARISON
  // ==========================================
  const invGrid = document.getElementById('investigationsGrid');
  const invHabitatFilter = document.getElementById('invHabitatFilter');
  const invSearchInput = document.getElementById('invSearchInput');

  async function loadInvestigations() {
    try {
      const [resInv, resRank] = await Promise.all([
        fetch('/api/investigations/'),
        fetch(`/api/habitats/ranking/?habitat_id=${currentHabitat}`)
      ]);
      const dataInv = await resInv.json();
      const dataRank = await resRank.json();

      allInvestigations = dataInv.investigations;
      habitatRankingMap = {};
      if (dataRank && dataRank.ranked_investigations) {
        dataRank.ranked_investigations.forEach(r => {
          habitatRankingMap[r.investigation_id] = r;
        });
      }
      renderInvestigations(allInvestigations);
    } catch (err) {
      console.error("Failed to load investigations:", err);
    }
  }

  function renderInvestigations(list) {
    if (!invGrid) return;
    if (list.length === 0) {
      invGrid.innerHTML = `<div style="grid-column: 1/-1; text-align:center; padding:3rem; color:var(--text-muted);">No investigations matching your criteria.</div>`;
      return;
    }

    invGrid.innerHTML = list.map(inv => {
      // Determine badge class
      let badgeClass = 'cir';
      if (inv.facility.includes('Glovebox') || inv.facility.includes('MSG')) badgeClass = 'msg';
      else if (inv.facility.includes('Cygnus')) badgeClass = 'cygnus';

      // Callout highlight
      let calloutBadge = '';
      if (inv.key_nasa_callouts.paradox_title) {
        calloutBadge = `<div class="inv-highlight-tag"><i class="fa-solid fa-triangle-exclamation"></i> <strong>${inv.key_nasa_callouts.paradox_title}</strong></div>`;
      } else if (inv.key_nasa_callouts.cool_flame_title) {
        calloutBadge = `<div class="inv-highlight-tag" style="border-color:var(--accent-purple); color:#c77dff;"><i class="fa-solid fa-ghost"></i> <strong>${inv.key_nasa_callouts.cool_flame_title}</strong></div>`;
      } else if (inv.key_nasa_callouts.modular_acme_title) {
        calloutBadge = `<div class="inv-highlight-tag" style="border-color:var(--accent-cyan); color:var(--accent-cyan);"><i class="fa-solid fa-cubes"></i> <strong>${inv.key_nasa_callouts.modular_acme_title}</strong></div>`;
      } else if (inv.key_nasa_callouts.hardware_reuse_title) {
        calloutBadge = `<div class="inv-highlight-tag" style="border-color:var(--accent-green); color:var(--accent-green);"><i class="fa-solid fa-arrows-split-up-and-left"></i> <strong>${inv.key_nasa_callouts.hardware_reuse_title}</strong></div>`;
      } else if (inv.key_nasa_callouts.large_scale_title) {
        calloutBadge = `<div class="inv-highlight-tag" style="border-color:var(--accent-amber); color:var(--accent-amber);"><i class="fa-solid fa-fire"></i> <strong>${inv.key_nasa_callouts.large_scale_title}</strong></div>`;
      }

      // SI Relevance Match Score for active crew habitat
      const ranking = habitatRankingMap[inv.id];
      let siMatchPill = '';
      if (ranking) {
        siMatchPill = `
          <div style="display:flex; align-items:center; justify-content:space-between; margin-top:0.3rem; background:rgba(0,210,255,0.08); border:1px solid rgba(0,210,255,0.25); border-radius:4px; padding:0.3rem 0.6rem; font-size:0.7rem;">
            <span style="color:var(--text-muted);"><i class="fa-solid fa-brain"></i> SI Habitat Match:</span>
            <span style="font-family:var(--font-mono); color:var(--accent-cyan); font-weight:700;">${ranking.relevance_score_pct}%</span>
          </div>
        `;
      }

      return `
        <div class="inv-card">
          <div class="inv-header">
            <div>
              <span class="inv-badge ${badgeClass}">${inv.facility}</span>
              <h3 class="inv-title" style="margin-top:4px;">${inv.name}</h3>
              <p style="font-size:0.75rem; color:var(--text-muted);">${inv.full_name}</p>
            </div>
            <button class="action-btn" style="padding:0.35rem 0.65rem; font-size:0.75rem;" onclick="openInvestigationModal('${inv.id}')">
              <i class="fa-solid fa-circle-info"></i> Full Dossier
            </button>
          </div>

          ${siMatchPill}

          <p style="font-size:0.8rem; color:#cbd5e1; line-height:1.4;">${inv.objectives}</p>

          ${calloutBadge}

          <div class="inv-meta-grid">
            <div class="inv-meta-item">
              <strong>Tested Fuels</strong>
              <span>${inv.fuels.materials.slice(0, 2).join(', ')}</span>
            </div>
            <div class="inv-meta-item">
              <strong>Oxygen Limits</strong>
              <span>${inv.test_conditions.oxygen_pct_range}</span>
            </div>
            <div class="inv-meta-item">
              <strong>Airflow Velocity</strong>
              <span>${inv.test_conditions.airflow_speed_range}</span>
            </div>
            <div class="inv-meta-item">
              <strong>Habitat Target</strong>
              <span>${inv.target_habitats[0]}</span>
            </div>
          </div>

          <div style="display:flex; justify-content:space-between; align-items:center; margin-top:auto; padding-top:0.5rem; border-top:1px solid rgba(255,255,255,0.06);">
            <span style="font-size:0.7rem; font-family:var(--font-mono); color:var(--text-muted);">PI: ${inv.lead_pi}</span>
            <label style="font-size:0.75rem; display:flex; align-items:center; gap:0.4rem; cursor:pointer;">
              <input type="checkbox" onchange="toggleCompareInv('${inv.id}', this.checked)"> Compare
            </label>
          </div>
        </div>
      `;
    }).join('');
  }

  // Filter investigations
  if (invHabitatFilter) {
    invHabitatFilter.addEventListener('change', () => filterInvestigations());
  }
  if (invSearchInput) {
    invSearchInput.addEventListener('input', () => filterInvestigations());
  }

  function filterInvestigations() {
    const hab = invHabitatFilter ? invHabitatFilter.value : 'all';
    const q = invSearchInput ? invSearchInput.value.toLowerCase().trim() : '';

    const filtered = allInvestigations.filter(inv => {
      const matchHab = hab === 'all' || inv.target_habitats.some(h => h.toLowerCase().includes(hab.toLowerCase()));
      const matchQ = !q || (inv.name + " " + inv.full_name + " " + inv.objectives + " " + JSON.stringify(inv.fuels)).toLowerCase().includes(q);
      return matchHab && matchQ;
    });
    renderInvestigations(filtered);
  }

  // Modal display for single investigation
  window.openInvestigationModal = (invId) => {
    const inv = allInvestigations.find(i => i.id === invId);
    if (!inv) return;

    const modal = document.getElementById('investigationModal');
    const content = document.getElementById('investigationModalContent');
    if (!modal || !content) return;

    let calloutSection = '';
    for (const [key, val] of Object.entries(inv.key_nasa_callouts)) {
      if (key.includes('title')) {
        const descKey = key.replace('title', 'description');
        const desc = inv.key_nasa_callouts[descKey] || '';
        calloutSection += `
          <div class="callout-box amber" style="margin:1rem 0;">
            <div class="callout-title"><i class="fa-solid fa-award"></i> ${val}</div>
            <p>${desc}</p>
          </div>
        `;
      }
    }

    content.innerHTML = `
      <div style="border-bottom:1px solid rgba(0,210,255,0.2); padding-bottom:1rem; margin-bottom:1rem;">
        <span class="inv-badge cir">${inv.facility}</span>
        <h2 style="color:#fff; font-size:1.6rem; margin-top:0.4rem;">${inv.full_name}</h2>
        <p style="color:var(--text-muted); font-size:0.85rem;">Principal Investigator: ${inv.lead_pi} | Target: ${inv.target_habitats.join(', ')}</p>
      </div>

      <div style="margin-bottom:1.25rem;">
        <h4 style="color:var(--accent-cyan); font-size:0.95rem; margin-bottom:0.4rem;">1. Experimental Objectives</h4>
        <p style="font-size:0.85rem; color:#cbd5e1;">${inv.objectives}</p>
      </div>

      ${calloutSection}

      <div style="display:grid; grid-template-columns:1fr 1fr; gap:1.25rem; margin-bottom:1.25rem;">
        <div style="background:rgba(5,10,18,0.7); padding:1rem; border-radius:var(--radius-sm); border:1px solid rgba(255,255,255,0.08);">
          <h4 style="color:var(--accent-cyan); font-size:0.9rem; margin-bottom:0.5rem;"><i class="fa-solid fa-flask"></i> Fuels & Sample Geometry</h4>
          <p style="font-size:0.8rem; margin-bottom:0.4rem;"><strong>Materials:</strong> ${inv.fuels.materials.join(', ')}</p>
          <p style="font-size:0.8rem;"><strong>Exact Shapes & Dimensions:</strong> ${inv.fuels.shapes_and_sizes}</p>
        </div>

        <div style="background:rgba(5,10,18,0.7); padding:1rem; border-radius:var(--radius-sm); border:1px solid rgba(255,255,255,0.08);">
          <h4 style="color:var(--accent-cyan); font-size:0.9rem; margin-bottom:0.5rem;"><i class="fa-solid fa-gauge-high"></i> Test Environmental Matrix</h4>
          <p style="font-size:0.8rem; margin-bottom:0.3rem;"><strong>Oxygen Conc:</strong> ${inv.test_conditions.oxygen_pct_range}</p>
          <p style="font-size:0.8rem; margin-bottom:0.3rem;"><strong>Airflow Velocity:</strong> ${inv.test_conditions.airflow_speed_range}</p>
          <p style="font-size:0.8rem; margin-bottom:0.3rem;"><strong>Chamber Pressure:</strong> ${inv.test_conditions.pressure}</p>
          <p style="font-size:0.8rem;"><strong>Diluent:</strong> ${inv.test_conditions.diluent}</p>
        </div>
      </div>

      <div style="background:rgba(0,210,255,0.05); border:1px solid rgba(0,210,255,0.25); border-radius:var(--radius-sm); padding:1rem; margin-bottom:1.25rem;">
        <h4 style="color:var(--accent-cyan); font-size:0.9rem; margin-bottom:0.5rem;"><i class="fa-solid fa-sliders"></i> Intra-Investigation Variables (Same vs Differed)</h4>
        <p style="font-size:0.8rem; margin-bottom:0.4rem;"><strong>Varied across tests:</strong> ${inv.intra_investigation_variables.varied}</p>
        <p style="font-size:0.8rem;"><strong>Held strictly constant:</strong> ${inv.intra_investigation_variables.held_constant}</p>
      </div>

      <div>
        <h4 style="color:var(--accent-cyan); font-size:0.9rem; margin-bottom:0.5rem;"><i class="fa-solid fa-satellite-dish"></i> Sensors & Flight Diagnostics</h4>
        <ul style="font-size:0.8rem; padding-left:1.2rem; color:#cbd5e1;">
          ${inv.sensors_and_measurements.map(s => `<li style="margin-bottom:0.25rem;">${s}</li>`).join('')}
        </ul>
      </div>
    `;

    modal.classList.add('active');
  };

  window.closeInvestigationModal = () => {
    const modal = document.getElementById('investigationModal');
    if (modal) modal.classList.remove('active');
  };

  // Compare investigations
  window.toggleCompareInv = (invId, isChecked) => {
    if (isChecked) {
      if (!comparisonQueue.includes(invId)) comparisonQueue.push(invId);
    } else {
      comparisonQueue = comparisonQueue.filter(id => id !== invId);
    }
    const compareBar = document.getElementById('compareActionBar');
    if (compareBar) {
      compareBar.style.display = comparisonQueue.length >= 2 ? 'flex' : 'none';
      const countEl = document.getElementById('compareCount');
      if (countEl) countEl.textContent = comparisonQueue.length;
    }
  };

  const launchCompareBtn = document.getElementById('launchCompareBtn');
  if (launchCompareBtn) {
    launchCompareBtn.addEventListener('click', () => {
      openComparisonMatrixModal();
    });
  }

  function openComparisonMatrixModal() {
    const modal = document.getElementById('comparisonModal');
    const matrix = document.getElementById('comparisonMatrixBody');
    if (!modal || !matrix) return;

    const selectedInvs = allInvestigations.filter(i => comparisonQueue.includes(i.id));

    matrix.innerHTML = `
      <div style="overflow-x:auto;">
        <table class="data-table" style="min-width:700px;">
          <thead>
            <tr>
              <th>Investigation Attribute</th>
              ${selectedInvs.map(i => `<th>${i.name}</th>`).join('')}
            </tr>
          </thead>
          <tbody>
            <tr>
              <td><strong>Flight Facility</strong></td>
              ${selectedInvs.map(i => `<td>${i.facility}</td>`).join('')}
            </tr>
            <tr>
              <td><strong>Target Habitat</strong></td>
              ${selectedInvs.map(i => `<td>${i.target_habitats.join(', ')}</td>`).join('')}
            </tr>
            <tr>
              <td><strong>Fuels & Dimensions</strong></td>
              ${selectedInvs.map(i => `<td>${i.fuels.materials.join(', ')}<br><small style="color:var(--text-muted);">${i.fuels.shapes_and_sizes}</small></td>`).join('')}
            </tr>
            <tr>
              <td><strong>Test Conditions (O2 / Airflow)</strong></td>
              ${selectedInvs.map(i => `<td>${i.test_conditions.oxygen_pct_range} O2<br>${i.test_conditions.airflow_speed_range}</td>`).join('')}
            </tr>
            <tr>
              <td><strong>Intra-Test Variables (Varied)</strong></td>
              ${selectedInvs.map(i => `<td>${i.intra_investigation_variables.varied}</td>`).join('')}
            </tr>
            <tr>
              <td><strong>Held Constant</strong></td>
              ${selectedInvs.map(i => `<td>${i.intra_investigation_variables.held_constant}</td>`).join('')}
            </tr>
            <tr>
              <td><strong>Sensors & Diagnostics</strong></td>
              ${selectedInvs.map(i => `<td>${i.sensors_and_measurements.slice(0, 2).join('; ')}</td>`).join('')}
            </tr>
            <tr>
              <td><strong>Key NASA Callout</strong></td>
              ${selectedInvs.map(i => {
                const calloutText = Object.values(i.key_nasa_callouts)[0] || 'Standard PSI matrix';
                return `<td style="color:#ffcc66; font-size:0.75rem;">${calloutText}</td>`;
              }).join('')}
            </tr>
          </tbody>
        </table>
      </div>
    `;

    modal.classList.add('active');
  }

  window.closeComparisonModal = () => {
    const modal = document.getElementById('comparisonModal');
    if (modal) modal.classList.remove('active');
  };

  // ==========================================
  // ML PREDICTION ENGINE (SCIKIT-LEARN)
  // ==========================================
  const mlForm = document.getElementById('mlPredictForm');
  if (mlForm) {
    mlForm.addEventListener('submit', (e) => {
      e.preventDefault();
      runMLPrediction();
    });
  }

  // Connect ML sliders to text
  ['ml_oxygen', 'ml_pressure', 'ml_ventilation', 'ml_thickness'].forEach(id => {
    const input = document.getElementById(id);
    const valDisplay = document.getElementById(`${id}_val`);
    if (input && valDisplay) {
      input.addEventListener('input', () => {
        valDisplay.textContent = input.value;
      });
    }
  });

  async function runMLPrediction() {
    const payload = {
      gravity_g: parseFloat(document.getElementById('ml_gravity')?.value || 0.0),
      oxygen_pct: parseFloat(document.getElementById('ml_oxygen')?.value || 21.0),
      pressure_kpa: parseFloat(document.getElementById('ml_pressure')?.value || 101.3),
      ventilation_speed_cms: parseFloat(document.getElementById('ml_ventilation')?.value || 6.0),
      sample_thickness_mm: parseFloat(document.getElementById('ml_thickness')?.value || 1.5),
      fuel_phase: document.getElementById('ml_phase')?.value || 'Solid',
      diluent_gas: document.getElementById('ml_diluent')?.value || 'N2',
      suppression_method: document.getElementById('ml_suppression')?.value || 'None'
    };

    try {
      const res = await fetch('/api/predict/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      const data = await res.json();
      displayPredictionResults(data);
    } catch (err) {
      console.error("ML prediction failed:", err);
    }
  }

  function displayPredictionResults(data) {
    const regimeEl = document.getElementById('mlResultRegime');
    const confEl = document.getElementById('mlResultConfidence');
    const spreadEl = document.getElementById('mlResultSpread');
    const riskEl = document.getElementById('mlResultRisk');
    const riskBar = document.getElementById('mlResultRiskBar');
    const insightsContainer = document.getElementById('mlResultInsights');

    if (regimeEl) {
      regimeEl.textContent = data.combustion_regime;
      regimeEl.className = `regime-title-badge regime-${data.combustion_regime.replace(/\s+/g, '')}`;
    }
    if (confEl) confEl.textContent = `${data.regime_confidence}% ML Confidence`;
    if (spreadEl) spreadEl.textContent = `${data.flame_spread_rate_mm_s} mm/s`;
    if (riskEl) riskEl.textContent = `${data.fire_risk_score} / 100`;

    if (riskBar) {
      riskBar.style.width = `${data.fire_risk_score}%`;
      if (data.fire_risk_score > 70) riskBar.style.backgroundColor = 'var(--accent-red)';
      else if (data.fire_risk_score > 35) riskBar.style.backgroundColor = 'var(--accent-amber)';
      else riskBar.style.backgroundColor = 'var(--accent-green)';
    }

    if (insightsContainer) {
      if (!data.physics_insights || data.physics_insights.length === 0) {
        insightsContainer.innerHTML = `<div style="color:var(--text-muted); font-size:0.8rem;">Standard microgravity conditions within expected operating envelope.</div>`;
      } else {
        insightsContainer.innerHTML = data.physics_insights.map(item => `
          <div class="callout-box ${item.level === 'CRITICAL' ? 'amber' : (item.level === 'WARNING' ? 'amber' : '')}">
            <div class="callout-title" style="color:${item.level === 'CRITICAL' ? 'var(--accent-purple)' : (item.level === 'WARNING' ? 'var(--accent-amber)' : 'var(--accent-green)')}">
              <i class="fa-solid fa-atom"></i> ${item.title}
            </div>
            <p style="font-size:0.8rem; line-height:1.4;">${item.text}</p>
          </div>
        `).join('');
      }
    }
  }

  // ==========================================
  // EMERGENCY SCENARIO SIMULATOR
  // ==========================================
  const simScenarioBtn = document.getElementById('runScenarioBtn');
  if (simScenarioBtn) {
    simScenarioBtn.addEventListener('click', async () => {
      const habitatId = document.getElementById('scenarioHabitatSelect')?.value || 'iss-space-station';
      const incidentType = document.getElementById('scenarioIncidentSelect')?.value || 'wire_overheat';
      
      const actions = [];
      if (document.getElementById('action_vent_cutoff')?.checked) actions.push('vent_cutoff');
      if (document.getElementById('action_fine_water_mist')?.checked) actions.push('fine_water_mist');
      if (document.getElementById('action_depressurize')?.checked) actions.push('depressurize');
      if (document.getElementById('action_same_daft')?.checked) actions.push('same_daft_sensor');

      try {
        const res = await fetch('/api/scenario/simulate/', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            habitat_id: habitatId,
            incident_type: incidentType,
            actions: actions
          })
        });
        const out = await res.json();
        renderScenarioResults(out);
      } catch (err) {
        console.error("Scenario simulation error:", err);
      }
    });
  }

  function renderScenarioResults(out) {
    const resBox = document.getElementById('scenarioResultBox');
    if (!resBox) return;

    let statusColor = 'var(--accent-green)';
    if (out.status.includes('CRITICAL')) statusColor = 'var(--accent-red)';
    else if (out.status.includes('PARTIAL')) statusColor = 'var(--accent-amber)';

    resBox.innerHTML = `
      <div style="border-bottom:1px solid rgba(255,255,255,0.08); padding-bottom:0.75rem; margin-bottom:0.75rem;">
        <span style="font-size:0.75rem; color:var(--text-muted); text-transform:uppercase; font-family:var(--font-mono);">Simulation Result</span>
        <h3 style="color:${statusColor}; font-size:1.3rem; font-family:var(--font-mono); margin-top:2px;">${out.status}</h3>
      </div>

      <div style="display:grid; grid-template-columns:1fr 1fr; gap:0.75rem; margin-bottom:1rem;">
        <div style="background:rgba(5,10,18,0.7); padding:0.6rem; border-radius:4px; text-align:center;">
          <div style="font-size:0.7rem; color:var(--text-muted);">INITIAL RISK</div>
          <div style="font-size:1.2rem; font-weight:700; color:var(--accent-red);">${out.initial_risk}</div>
        </div>
        <div style="background:rgba(5,10,18,0.7); padding:0.6rem; border-radius:4px; text-align:center;">
          <div style="font-size:0.7rem; color:var(--text-muted);">FINAL CONTAINED RISK</div>
          <div style="font-size:1.2rem; font-weight:700; color:${statusColor};">${out.final_risk}</div>
        </div>
      </div>

      <div style="margin-bottom:0.75rem;">
        <div style="font-size:0.75rem; color:var(--text-muted); margin-bottom:4px;">DAMAGE MITIGATION EFFICIENCY: <strong>${out.damage_mitigation_pct}%</strong></div>
        <div style="height:8px; background:#142236; border-radius:4px; overflow:hidden;">
          <div style="height:100%; width:${out.damage_mitigation_pct}%; background:${statusColor}; transition:width 0.4s ease;"></div>
        </div>
      </div>

      <div style="font-size:0.8rem; margin-bottom:0.75rem;">
        <strong>Crew Survival Assessment:</strong> <span style="color:${statusColor};">${out.crew_safety_status}</span>
      </div>

      <div style="font-size:0.75rem;">
        <strong>Intervention Event Sequence:</strong>
        <ul style="padding-left:1.2rem; margin-top:0.3rem; color:#cbd5e1;">
          ${out.mitigation_log.map(log => `<li>${log}</li>`).join('')}
        </ul>
      </div>
    `;
  }

  // ==========================================
  // AI SAFETY CO-PILOT
  // ==========================================
  const copilotInput = document.getElementById('copilotInput');
  const copilotSendBtn = document.getElementById('copilotSendBtn');
  const copilotMsgContainer = document.getElementById('copilotMessages');

  if (copilotSendBtn && copilotInput) {
    copilotSendBtn.addEventListener('click', () => sendCopilotQuery());
    copilotInput.addEventListener('keypress', (e) => {
      if (e.key === 'Enter') sendCopilotQuery();
    });
  }

  window.askCopilotPreset = (query) => {
    if (copilotInput) {
      copilotInput.value = query;
      sendCopilotQuery();
    }
  };

  async function sendCopilotQuery() {
    const q = copilotInput.value.trim();
    if (!q) return;

    // Add user message
    appendChatMessage('user', q);
    copilotInput.value = '';

    // Typing indicator
    const typingId = appendChatMessage('bot', '<i class="fa-solid fa-spinner fa-spin"></i> Querying NASA PSI flight archives...');

    try {
      const res = await fetch('/api/copilot/query/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: q })
      });
      const data = await res.json();

      // Replace typing with response
      const typingEl = document.getElementById(typingId);
      if (typingEl) {
        typingEl.innerHTML = `
          <div style="font-weight:700; color:var(--accent-cyan); margin-bottom:4px;">
            <i class="fa-solid fa-satellite"></i> ${data.title}
          </div>
          <div>${data.response}</div>
          <div style="margin-top:6px; font-size:0.7rem; color:var(--text-muted); font-family:var(--font-mono);">
            Source: ${data.source} | Confidence: ${Math.round(data.confidence * 100)}%
          </div>
        `;
      }
    } catch (err) {
      const typingEl = document.getElementById(typingId);
      if (typingEl) typingEl.textContent = "Error querying safety archive.";
    }
  }

  function appendChatMessage(sender, html) {
    const id = `msg-${Date.now()}-${Math.random().toString(36).substr(2, 5)}`;
    const bubble = document.createElement('div');
    bubble.className = `chat-bubble ${sender}`;
    bubble.id = id;
    bubble.innerHTML = html;
    copilotMsgContainer.appendChild(bubble);
    copilotMsgContainer.scrollTop = copilotMsgContainer.scrollHeight;
    return id;
  }

  // ==========================================
  // TERRESTRIAL SPINOFF IMPACT CALCULATOR
  // ==========================================
  const spinoffSectorSelect = document.getElementById('spinoffSectorSelect');
  const spinoffScaleSlider = document.getElementById('spinoffScaleSlider');
  const spinoffInputLabel = document.getElementById('spinoffInputLabel');
  const spinoffInputVal = document.getElementById('spinoffInputVal');
  const calculateSpinoffBtn = document.getElementById('calculateSpinoffBtn');

  if (spinoffSectorSelect && spinoffScaleSlider) {
    spinoffSectorSelect.addEventListener('change', () => {
      const sector = spinoffSectorSelect.value;
      if (sector === 'data_center') {
        if (spinoffInputLabel) spinoffInputLabel.textContent = 'Data Center Area (Square Meters)';
        spinoffScaleSlider.min = '500';
        spinoffScaleSlider.max = '10000';
        spinoffScaleSlider.step = '500';
        spinoffScaleSlider.value = '2500';
      } else if (sector === 'cleanroom_mine') {
        if (spinoffInputLabel) spinoffInputLabel.textContent = 'Deployed Detector Units';
        spinoffScaleSlider.min = '20';
        spinoffScaleSlider.max = '500';
        spinoffScaleSlider.step = '10';
        spinoffScaleSlider.value = '120';
      } else {
        if (spinoffInputLabel) spinoffInputLabel.textContent = 'Active Firefighter Personnel';
        spinoffScaleSlider.min = '20';
        spinoffScaleSlider.max = '400';
        spinoffScaleSlider.step = '10';
        spinoffScaleSlider.value = '80';
      }
      if (spinoffInputVal) spinoffInputVal.textContent = spinoffScaleSlider.value;
      updateSpinoffMetrics();
    });

    spinoffScaleSlider.addEventListener('input', () => {
      if (spinoffInputVal) spinoffInputVal.textContent = spinoffScaleSlider.value;
      updateSpinoffMetrics();
    });

    if (calculateSpinoffBtn) {
      calculateSpinoffBtn.addEventListener('click', () => updateSpinoffMetrics());
    }
  }

  function updateSpinoffMetrics() {
    const sector = spinoffSectorSelect ? spinoffSectorSelect.value : 'data_center';
    const scale = parseFloat(spinoffScaleSlider ? spinoffScaleSlider.value : 2500);

    const m1Val = document.getElementById('spinoffMetric1Val');
    const m1Lbl = document.getElementById('spinoffMetric1Label');
    const m2Val = document.getElementById('spinoffMetric2Val');
    const m2Lbl = document.getElementById('spinoffMetric2Label');
    const m3Val = document.getElementById('spinoffMetric3Val');
    const m3Lbl = document.getElementById('spinoffMetric3Label');
    const note = document.getElementById('spinoffSummaryNote');

    if (sector === 'data_center') {
      const waterSaved = Math.round(scale * 9.2);
      const damageAvoided = (scale * 0.0016).toFixed(1);
      if (m1Val) m1Val.textContent = `${waterSaved.toLocaleString()} L`;
      if (m1Lbl) m1Lbl.textContent = 'Water Conserved (vs. Deluge)';
      if (m2Val) m2Val.textContent = `$${damageAvoided}M`;
      if (m2Lbl) m2Lbl.textContent = 'Server Equipment Protected';
      if (m3Val) m3Val.textContent = '0 hrs';
      if (m3Lbl) m3Lbl.textContent = 'Corrosion Downtime';
      if (note) note.innerHTML = '<strong>FLEX/CFI Space Transfer:</strong> Micro-droplet Fine-Water-Mist quenches high-density server rack fires via latent heat absorption without puddle conductivity, avoiding catastrophic water damage associated with traditional 1G deluge sprinklers.';
    } else if (sector === 'cleanroom_mine') {
      const alarmsPrevented = Math.round(scale * 0.45);
      const dollarsSaved = Math.round(scale * 3200);
      if (m1Val) m1Val.textContent = `${alarmsPrevented} / yr`;
      if (m1Lbl) m1Lbl.textContent = 'False Alarms Eliminated';
      if (m2Val) m2Val.textContent = `$${(dollarsSaved / 1000).toFixed(0)}k`;
      if (m2Lbl) m2Lbl.textContent = 'Shutdown Losses Averted';
      if (m3Val) m3Val.textContent = '99.4%';
      if (m3Lbl) m3Lbl.textContent = 'Aerosol Classification Accuracy';
      if (note) note.innerHTML = '<strong>SAME/DAFT Space Transfer:</strong> Dual-wavelength multi-angle light scattering discriminates sharp mineral regolith/dust from carbonaceous fire soot particles, ending costly false industrial plant evacuations.';
    } else {
      const weightSaved = (scale * 4.2).toFixed(0);
      if (m1Val) m1Val.textContent = `${weightSaved} kg`;
      if (m1Lbl) m1Lbl.textContent = 'Cumulative SCBA Gear Weight Saved';
      if (m2Val) m2Val.textContent = '45 s';
      if (m2Lbl) m2Lbl.textContent = 'Flashover Escape Window (vs. 17s)';
      if (m3Val) m3Val.textContent = '-35%';
      if (m3Lbl) m3Lbl.textContent = 'Crew Heat Stress Fatigue';
      if (note) note.innerHTML = '<strong>BASS/Saffire Space Transfer:</strong> Spacecraft-certified silica aerogel thermal baffles and carbon-overwrapped composite pressure vessels insulate first responders while cutting breathing apparatus weight in half.';
    }
  }

  // ==========================================
  // DATASET EXPLORER & DOWNLOADS
  // ==========================================
  const dataTableBody = document.getElementById('datasetTableBody');
  const dataTablePagination = document.getElementById('datasetTablePagination');
  let currentOffset = 0;
  const pageLimit = 25;

  window.loadDatasetPage = async (offset = 0) => {
    currentOffset = offset;
    try {
      const res = await fetch(`/api/experiments/?offset=${offset}&limit=${pageLimit}`);
      const data = await res.json();
      renderDatasetRows(data.results);
      renderDatasetPagination(data.total_count, offset);
    } catch (err) {
      console.error("Dataset fetch failed:", err);
    }
  };

  function renderDatasetRows(rows) {
    if (!dataTableBody) return;
    dataTableBody.innerHTML = rows.map(r => `
      <tr>
        <td style="font-family:var(--font-mono); color:var(--accent-cyan); font-weight:600;">${r.run_id}</td>
        <td><strong>${r.investigation}</strong></td>
        <td>${r.fuel_name}</td>
        <td style="font-family:var(--font-mono);">${r.gravity_g} G</td>
        <td style="font-family:var(--font-mono);">${r.oxygen_pct}%</td>
        <td style="font-family:var(--font-mono);">${r.ventilation_speed_cms} cm/s</td>
        <td><span class="inv-badge ${r.combustion_regime === 'Quenched' ? 'msg' : (r.combustion_regime === 'Invisible Cool Flame' ? 'cir' : 'cygnus')}">${r.combustion_regime}</span></td>
        <td style="font-family:var(--font-mono);">${r.flame_spread_rate_mm_s}</td>
        <td style="font-family:var(--font-mono); font-weight:700; color:${r.fire_risk_score > 70 ? 'var(--accent-red)' : 'var(--accent-green)'};">${r.fire_risk_score}</td>
      </tr>
    `).join('');
  }

  function renderDatasetPagination(total, offset) {
    if (!dataTablePagination) return;
    const totalPages = Math.ceil(total / pageLimit);
    const currentPage = Math.floor(offset / pageLimit) + 1;

    dataTablePagination.innerHTML = `
      <div style="display:flex; justify-content:space-between; align-items:center; width:100%; font-size:0.8rem; color:var(--text-muted);">
        <span>Showing ${offset + 1}–${Math.min(offset + pageLimit, total)} of <strong>${total}</strong> NASA test runs</span>
        <div style="display:flex; gap:0.5rem;">
          <button class="action-btn" style="padding:0.3rem 0.6rem; font-size:0.75rem;" ${offset === 0 ? 'disabled' : ''} onclick="loadDatasetPage(${Math.max(0, offset - pageLimit)})">Previous</button>
          <span style="font-family:var(--font-mono); padding:0.3rem 0.5rem;">Page ${currentPage} of ${totalPages}</span>
          <button class="action-btn" style="padding:0.3rem 0.6rem; font-size:0.75rem;" ${offset + pageLimit >= total ? 'disabled' : ''} onclick="loadDatasetPage(${offset + pageLimit})">Next</button>
        </div>
      </div>
    `;
  }

  // ==========================================
  // ANALYTICS & CHART.JS INTEGRATION
  // ==========================================
  let regimeChart = null;
  let gravityChart = null;
  let paradoxChart = null;

  async function loadAnalyticsCharts() {
    if (!window.Chart) return;
    try {
      const res = await fetch('/api/stats/');
      const stats = await res.json();

      // 1. Regime distribution chart
      const regimeCtx = document.getElementById('regimeDistributionChart');
      if (regimeCtx && !regimeChart) {
        regimeChart = new Chart(regimeCtx, {
          type: 'doughnut',
          data: {
            labels: Object.keys(stats.regime_distribution),
            datasets: [{
              data: Object.values(stats.regime_distribution),
              backgroundColor: ['#8b9bb4', '#9d4edd', '#00d2ff', '#ff3366'],
              borderColor: '#050a12',
              borderWidth: 2
            }]
          },
          options: {
            responsive: true,
            plugins: {
              legend: { position: 'bottom', labels: { color: '#e6f1ff', font: { family: 'Inter' } } }
            }
          }
        });
      }

      // 2. Average spread rate vs gravity
      const gravCtx = document.getElementById('gravitySpreadChart');
      if (gravCtx && !gravityChart) {
        const gLabels = Object.keys(stats.gravity_breakdown).map(g => `${g} G`);
        const spreadVals = Object.values(stats.gravity_breakdown).map(v => v.avg_spread_rate_mm_s);
        const riskVals = Object.values(stats.gravity_breakdown).map(v => v.avg_risk_score);

        gravityChart = new Chart(gravCtx, {
          type: 'bar',
          data: {
            labels: gLabels,
            datasets: [
              {
                label: 'Avg Flame Spread (mm/s)',
                data: spreadVals,
                backgroundColor: 'rgba(0, 210, 255, 0.7)',
                borderColor: '#00d2ff',
                borderWidth: 1,
                yAxisID: 'y'
              },
              {
                label: 'Avg Fire Risk (0-100)',
                data: riskVals,
                backgroundColor: 'rgba(255, 153, 0, 0.7)',
                borderColor: '#ff9900',
                borderWidth: 1,
                yAxisID: 'y1'
              }
            ]
          },
          options: {
            responsive: true,
            scales: {
              x: { ticks: { color: '#8b9bb4' }, grid: { color: 'rgba(255,255,255,0.05)' } },
              y: { type: 'linear', position: 'left', ticks: { color: '#00d2ff' }, grid: { color: 'rgba(255,255,255,0.05)' } },
              y1: { type: 'linear', position: 'right', ticks: { color: '#ff9900' }, grid: { drawOnChartArea: false } }
            },
            plugins: {
              legend: { labels: { color: '#e6f1ff' } }
            }
          }
        });
      }

      // 3. 0G Ventilation Paradox Flammability Envelope
      const paradoxCtx = document.getElementById('paradoxCurveChart');
      if (paradoxCtx && !paradoxChart) {
        // Curve showing O2 minimum required for steady burn in 0G vs airflow speed
        const airflows = [0, 2, 4, 6, 8, 10, 12, 14, 18, 22, 26, 30];
        // 0G Paradox curve: dips down to ~16.5% between 4-12 cm/s
        const zeroGLOI = [24.0, 19.5, 16.8, 16.2, 16.5, 16.9, 17.5, 18.5, 20.8, 23.5, 27.0, 31.0];
        // 1G Earth control: roughly flat ~20.5% LOI
        const earthLOI = [20.5, 20.5, 20.6, 20.7, 20.8, 20.9, 21.0, 21.2, 21.8, 22.5, 23.5, 25.0];

        paradoxChart = new Chart(paradoxCtx, {
          type: 'line',
          data: {
            labels: airflows.map(a => `${a} cm/s`),
            datasets: [
              {
                label: '0G Limiting Oxygen Index (LOI %)',
                data: zeroGLOI,
                borderColor: '#00d2ff',
                backgroundColor: 'rgba(0, 210, 255, 0.15)',
                fill: true,
                tension: 0.35,
                borderWidth: 2
              },
              {
                label: '1G Earth Baseline LOI (%)',
                data: earthLOI,
                borderColor: '#ff9900',
                borderDash: [5, 5],
                tension: 0.2,
                borderWidth: 2
              }
            ]
          },
          options: {
            responsive: true,
            scales: {
              x: { title: { display: true, text: 'Cabin Ventilation Speed (cm/s)', color: '#8b9bb4' }, ticks: { color: '#8b9bb4' }, grid: { color: 'rgba(255,255,255,0.05)' } },
              y: { title: { display: true, text: 'Limiting Oxygen Index (O2 %)', color: '#8b9bb4' }, min: 14, max: 34, ticks: { color: '#8b9bb4' }, grid: { color: 'rgba(255,255,255,0.05)' } }
            },
            plugins: {
              legend: { labels: { color: '#e6f1ff' } }
            }
          }
        });
      }
    } catch (err) {
      console.error("Failed to load analytics charts:", err);
    }
  }

  // ==========================================
  // NASA DATA EXTRACTOR & INGESTION ENGINE
  // ==========================================
  const runExtractorBtn = document.getElementById('runExtractorBtn');
  const extractorTerminal = document.getElementById('extractorTerminalLogs');
  const extractorStatusBadge = document.getElementById('extractorStatusBadge');

  if (runExtractorBtn) {
    runExtractorBtn.addEventListener('click', async () => {
      const batchSize = parseInt(document.getElementById('extractorBatchSize')?.value || '1600');
      const liveSync = !!document.getElementById('extractorLiveSync')?.checked;

      // Update UI state
      runExtractorBtn.disabled = true;
      runExtractorBtn.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> Ingesting NASA Flight Data...`;
      if (extractorStatusBadge) {
        extractorStatusBadge.innerHTML = `<span style="color:var(--accent-amber);"><i class="fa-solid fa-satellite fa-spin"></i> EXTRACTING...</span>`;
      }

      if (extractorTerminal) {
        extractorTerminal.innerHTML = `
          <div>> Connecting to NASA Physical Sciences Informatics Gateway...</div>
          <div>> Contacting NASA NTRS Open Data APIs...</div>
          <div>> Batch Size Request: ${batchSize} flight test runs</div>
        `;
      }

      try {
        const res = await fetch('/api/extractor/sync/', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            sample_count: batchSize,
            sync_online: liveSync
          })
        });

        const out = await res.json();

        if (extractorTerminal && out.logs) {
          extractorTerminal.innerHTML = out.logs.map(log => {
            let color = '#00ff88';
            if (log.includes('Retraining') || log.includes('ML')) color = 'var(--accent-cyan)';
            if (log.includes('Offline') || log.includes('unreachable')) color = '#ffcc00';
            return `<div style="color:${color};">> ${log}</div>`;
          }).join('');
          extractorTerminal.scrollTop = extractorTerminal.scrollHeight;
        }

        if (extractorStatusBadge) {
          extractorStatusBadge.innerHTML = `<span style="color:var(--accent-green);"><i class="fa-solid fa-circle-check"></i> SYNC COMPLETE (${out.records_extracted} RUNS)</span>`;
        }

        // Refresh dataset and ML prediction
        loadDatasetPage(0);
        runMLPrediction();

      } catch (err) {
        console.error("NASA extraction error:", err);
        if (extractorTerminal) {
          extractorTerminal.innerHTML += `<div style="color:var(--accent-red);">> Error contacting NASA ingestion pipeline: ${err}</div>`;
        }
        if (extractorStatusBadge) {
          extractorStatusBadge.innerHTML = `<span style="color:var(--accent-red);"><i class="fa-solid fa-triangle-exclamation"></i> ERROR</span>`;
        }
      } finally {
        runExtractorBtn.disabled = false;
        runExtractorBtn.innerHTML = `<i class="fa-solid fa-satellite-dish"></i> Execute NASA PSI Ingestion Pipeline`;
      }
    });
  }

  // Initial runs
  loadInvestigations();
  loadDatasetPage(0);
  runMLPrediction();
});
