/**
 * NASA Space Apps 2026 — Flame in Freefall
 * Physics-Accurate Microgravity / Partial-G Flame Simulator (HTML5 Canvas 60 FPS)
 */

class MicrogravityFlameSimulator {
  constructor(canvasId) {
    this.canvas = document.getElementById(canvasId);
    if (!this.canvas) return;
    this.ctx = this.canvas.getContext('2d');
    
    // Physics parameters
    this.gravity_g = 0.0; // 0.0G (ISS), 0.16G (Moon), 0.38G (Mars), 1.0G (Earth)
    this.ventilation_speed_cms = 6.0; // cm/s
    this.oxygen_pct = 21.0;
    this.cool_flame_mode = false;
    this.suppression_active = false;
    this.fuel_type = 'solid'; // 'solid', 'droplet', 'burner'
    
    // Computed state
    this.flame_temp_k = 1450;
    this.flame_radius = 48;
    this.flame_status = 'STEADY 0G DIFFUSION FLAME';
    this.paradox_active = true;
    
    // Animation & particles
    this.particles = [];
    this.mist_particles = [];
    this.animTime = 0;
    this.isRunning = true;
    
    this.resizeCanvas();
    window.addEventListener('resize', () => this.resizeCanvas());
    
    this.loop = this.loop.bind(this);
    requestAnimationFrame(this.loop);
  }

  resizeCanvas() {
    const rect = this.canvas.parentElement.getBoundingClientRect();
    this.canvas.width = rect.width;
    this.canvas.height = rect.height || 520;
    this.cx = this.canvas.width / 2;
    this.cy = this.canvas.height / 2 + 40;
  }

  setGravity(g) {
    this.gravity_g = parseFloat(g);
    this.updatePhysics();
  }

  setVentilation(v) {
    this.ventilation_speed_cms = parseFloat(v);
    this.updatePhysics();
  }

  setOxygen(o2) {
    this.oxygen_pct = parseFloat(o2);
    this.updatePhysics();
  }

  setFuelType(fuel) {
    this.fuel_type = fuel;
  }

  toggleCoolFlame(enable) {
    this.cool_flame_mode = enable;
    this.updatePhysics();
  }

  triggerMistSuppression() {
    this.suppression_active = true;
    // Spawn micro-droplet mist
    for (let i = 0; i < 90; i++) {
      const angle = Math.random() * Math.PI * 2;
      const dist = 120 + Math.random() * 80;
      this.mist_particles.push({
        x: this.cx + Math.cos(angle) * dist,
        y: this.cy + Math.sin(angle) * dist,
        vx: -Math.cos(angle) * (2.5 + Math.random() * 2),
        vy: -Math.sin(angle) * (2.5 + Math.random() * 2),
        radius: 1.5 + Math.random() * 1.5,
        alpha: 0.9,
        life: 1.0
      });
    }
    setTimeout(() => {
      this.suppression_active = false;
    }, 3500);
  }

  updatePhysics() {
    const g = this.gravity_g;
    const v = this.ventilation_speed_cms;
    const o2 = this.oxygen_pct;

    // Check 0G Ventilation Paradox
    if (g === 0.0) {
      if (v >= 3.0 && v <= 14.0) {
        this.paradox_active = true;
        this.flame_temp_k = this.cool_flame_mode ? 680 : 1580;
        this.flame_radius = 52 + (o2 - 21) * 1.2;
        this.flame_status = '0G VENTILATION PARADOX (OPTIMAL COMBUSTION)';
      } else if (v < 2.0) {
        this.paradox_active = false;
        this.flame_temp_k = this.cool_flame_mode ? 520 : 1100;
        this.flame_radius = 34;
        this.flame_status = '0G STAGNANT STARVATION (DIFFUSION CHOKING)';
      } else {
        this.paradox_active = false;
        this.flame_temp_k = this.cool_flame_mode ? 600 : 1350;
        this.flame_radius = Math.max(20, 48 - (v - 14) * 1.5);
        this.flame_status = v > 24 ? 'BLOWOUT / HIGH CONVECTIVE QUENCH' : 'FORCED CONVECTION ELONGATION';
      }
    } else {
      this.paradox_active = false;
      // Buoyancy u_buoy ~ sqrt(g * L * deltaT / T_inf)
      const u_buoy = Math.sqrt(g * 9.81 * 0.05 * 1100 / 300) * 100;
      this.flame_temp_k = 1400 + g * 350 + (o2 - 21) * 20;
      this.flame_radius = 42 + g * 15;
      if (g === 0.16) this.flame_status = 'LUNAR PARTIAL GRAVITY (0.16G)';
      else if (g === 0.38) this.flame_status = 'MARTIAN PARTIAL GRAVITY (0.38G)';
      else this.flame_status = 'EARTH BUOYANT FLAME (1.0G)';
    }

    if (this.cool_flame_mode) {
      this.flame_status = 'INVISIBLE COOL FLAME (550-780 K)';
      this.flame_temp_k = 640;
    }

    if (this.suppression_active) {
      this.flame_status = 'FINE-WATER-MIST SUPPRESSION ACTIVE';
      this.flame_temp_k = Math.max(350, this.flame_temp_k - 600);
    }
  }

  spawnCombustionParticles() {
    const g = this.gravity_g;
    const v = this.ventilation_speed_cms;
    const count = this.cool_flame_mode ? 2 : (g > 0 ? 5 : 3);

    for (let i = 0; i < count; i++) {
      const angle = Math.random() * Math.PI * 2;
      const r = Math.random() * (this.flame_radius * 0.4);
      
      // Velocity components
      // Gravity creates upward buoyant force (-vy)
      const buoyantVy = -g * (1.8 + Math.random() * 2.2);
      // Ventilation creates horizontal draft (+vx)
      const ventVx = (v / 8.0) * (0.8 + Math.random() * 0.5);

      this.particles.push({
        x: this.cx + Math.cos(angle) * r,
        y: this.cy + Math.sin(angle) * r,
        vx: Math.cos(angle) * 0.4 + ventVx,
        vy: Math.sin(angle) * 0.4 + buoyantVy,
        life: 1.0,
        decay: 0.015 + Math.random() * 0.02,
        size: 3 + Math.random() * 5,
        colorType: g === 0 ? 'blue' : (g < 0.5 ? 'mild_yellow' : 'sooty_yellow')
      });
    }
  }

  updateAndDrawParticles() {
    const ctx = this.ctx;
    for (let i = this.particles.length - 1; i >= 0; i--) {
      const p = this.particles[i];
      p.x += p.vx;
      p.y += p.vy;
      p.life -= p.decay;

      if (p.life <= 0) {
        this.particles.splice(i, 1);
        continue;
      }

      ctx.save();
      ctx.globalAlpha = p.life * (this.cool_flame_mode ? 0.35 : 0.85);

      let grad = ctx.createRadialGradient(p.x, p.y, 0, p.x, p.y, p.size);
      if (this.cool_flame_mode) {
        grad.addColorStop(0, 'rgba(180, 100, 255, 0.5)');
        grad.addColorStop(1, 'rgba(100, 40, 200, 0)');
      } else if (p.colorType === 'blue') {
        grad.addColorStop(0, 'rgba(120, 230, 255, 0.9)');
        grad.addColorStop(0.5, 'rgba(0, 140, 255, 0.6)');
        grad.addColorStop(1, 'rgba(0, 50, 180, 0)');
      } else if (p.colorType === 'mild_yellow') {
        grad.addColorStop(0, 'rgba(255, 230, 150, 0.9)');
        grad.addColorStop(0.6, 'rgba(0, 180, 255, 0.5)');
        grad.addColorStop(1, 'rgba(255, 100, 0, 0)');
      } else {
        grad.addColorStop(0, 'rgba(255, 255, 200, 0.95)');
        grad.addColorStop(0.4, 'rgba(255, 180, 30, 0.8)');
        grad.addColorStop(1, 'rgba(255, 60, 0, 0)');
      }

      ctx.fillStyle = grad;
      ctx.beginPath();
      ctx.arc(p.x, p.y, p.size * (1 + (1 - p.life)), 0, Math.PI * 2);
      ctx.fill();
      ctx.restore();
    }

    // Update and draw mist particles
    for (let i = this.mist_particles.length - 1; i >= 0; i--) {
      const m = this.mist_particles[i];
      m.x += m.vx;
      m.y += m.vy;
      m.life -= 0.02;

      if (m.life <= 0) {
        this.mist_particles.splice(i, 1);
        continue;
      }

      ctx.save();
      ctx.globalAlpha = m.life * 0.9;
      ctx.fillStyle = '#00f0ff';
      ctx.beginPath();
      ctx.arc(m.x, m.y, m.radius, 0, Math.PI * 2);
      ctx.fill();

      // Evaporation steam vapor
      if (Math.hypot(m.x - this.cx, m.y - this.cy) < this.flame_radius) {
        ctx.fillStyle = 'rgba(200, 240, 255, 0.3)';
        ctx.beginPath();
        ctx.arc(m.x, m.y, m.radius * 3, 0, Math.PI * 2);
        ctx.fill();
      }
      ctx.restore();
    }
  }

  drawFuelSource() {
    const ctx = this.ctx;
    ctx.save();

    if (this.fuel_type === 'droplet') {
      // FLEX / CFI Droplet on SiC fiber
      // Fiber line
      ctx.strokeStyle = 'rgba(200, 220, 240, 0.4)';
      ctx.lineWidth = 1.5;
      ctx.beginPath();
      ctx.moveTo(this.cx - 100, this.cy);
      ctx.lineTo(this.cx + 100, this.cy);
      ctx.stroke();

      // Liquid droplet
      const dropGrad = ctx.createRadialGradient(this.cx - 3, this.cy - 3, 1, this.cx, this.cy, 12);
      dropGrad.addColorStop(0, '#ffffff');
      dropGrad.addColorStop(0.5, '#70d6ff');
      dropGrad.addColorStop(1, '#0077b6');
      ctx.fillStyle = dropGrad;
      ctx.beginPath();
      ctx.arc(this.cx, this.cy, 10, 0, Math.PI * 2);
      ctx.fill();
    } else if (this.fuel_type === 'burner') {
      // ACME Modular Porous Burner
      ctx.fillStyle = '#8a7d65';
      ctx.fillRect(this.cx - 35, this.cy + 10, 70, 25);
      // Porous holes
      ctx.fillStyle = '#3a3224';
      for (let x = -30; x <= 30; x += 10) {
        ctx.beginPath();
        ctx.arc(this.cx + x, this.cy + 15, 2, 0, Math.PI * 2);
        ctx.fill();
      }
      ctx.fillStyle = '#61543e';
      ctx.fillRect(this.cx - 15, this.cy + 35, 30, 40);
    } else {
      // BASS PMMA Solid rod / flat sample
      const rodGrad = ctx.createLinearGradient(this.cx - 12, this.cy, this.cx + 12, this.cy);
      rodGrad.addColorStop(0, '#3a4b60');
      rodGrad.addColorStop(0.5, '#7a92af');
      rodGrad.addColorStop(1, '#2c394a');
      ctx.fillStyle = rodGrad;
      ctx.fillRect(this.cx - 8, this.cy + 5, 16, 90);

      // Pyrolysis boundary
      ctx.fillStyle = 'rgba(255, 140, 0, 0.7)';
      ctx.fillRect(this.cx - 8, this.cy + 5, 16, 6);
    }

    ctx.restore();
  }

  drawFlameEnvelope() {
    const ctx = this.ctx;
    const g = this.gravity_g;
    const v = this.ventilation_speed_cms;
    const time = this.animTime;
    
    // Natural oscillation
    const pulse = Math.sin(time * 0.05) * 2;
    const r = Math.max(10, this.flame_radius + pulse);

    ctx.save();

    // Draft displacement
    const driftX = (v / 8.0) * 12;
    // Buoyant displacement upward
    const buoyantStretch = g * 45;
    const flameCenterY = this.cy - buoyantStretch * 0.5;
    const flameCenterX = this.cx + driftX;

    if (g === 0.0) {
      // ==========================================
      // TRUE 0G SPHERICAL DIFFUSION FLAME (BLUE / SOOT-FREE)
      // ==========================================
      const grad = ctx.createRadialGradient(
        flameCenterX, flameCenterY, 4,
        flameCenterX, flameCenterY, r * 1.3
      );

      if (this.cool_flame_mode) {
        // Invisible Cool Flame (Weak Violet / Near IR)
        grad.addColorStop(0, 'rgba(180, 100, 255, 0.4)');
        grad.addColorStop(0.4, 'rgba(140, 60, 220, 0.25)');
        grad.addColorStop(0.8, 'rgba(90, 20, 160, 0.1)');
        grad.addColorStop(1, 'rgba(50, 0, 100, 0)');
      } else {
        // Brilliant soot-free blue spherical shell
        grad.addColorStop(0, 'rgba(180, 240, 255, 0.85)');
        grad.addColorStop(0.3, 'rgba(0, 180, 255, 0.75)');
        grad.addColorStop(0.7, 'rgba(0, 80, 230, 0.45)');
        grad.addColorStop(0.95, 'rgba(0, 30, 160, 0.2)');
        grad.addColorStop(1, 'rgba(0, 10, 80, 0)');
      }

      ctx.fillStyle = grad;
      ctx.beginPath();
      // Spherical in 0G
      ctx.arc(flameCenterX, flameCenterY, r * 1.3, 0, Math.PI * 2);
      ctx.fill();

      // Outer faint chemiluminescence shell
      ctx.strokeStyle = this.cool_flame_mode ? 'rgba(170, 90, 255, 0.4)' : 'rgba(0, 210, 255, 0.6)';
      ctx.lineWidth = 2;
      ctx.stroke();

    } else {
      // ==========================================
      // BUOYANT TEARDROP FLAME (0.16G MOON, 0.38G MARS, 1.0G EARTH)
      // ==========================================
      const topY = flameCenterY - buoyantStretch * 1.6;
      const bottomY = this.cy + 10;
      const flicker = Math.sin(time * 0.12) * (g * 4);

      ctx.beginPath();
      ctx.moveTo(flameCenterX, bottomY);
      // Left bezier curve
      ctx.bezierCurveTo(
        flameCenterX - r, this.cy,
        flameCenterX - r * 0.7 + flicker, topY + buoyantStretch * 0.5,
        flameCenterX + flicker * 0.5, topY
      );
      // Right bezier curve
      ctx.bezierCurveTo(
        flameCenterX + r * 0.7 + flicker, topY + buoyantStretch * 0.5,
        flameCenterX + r, this.cy,
        flameCenterX, bottomY
      );
      ctx.closePath();

      const tearGrad = ctx.createLinearGradient(flameCenterX, bottomY, flameCenterX, topY);
      if (g < 0.25) {
        // Lunar: mostly blue base with mild yellow tip
        tearGrad.addColorStop(0, 'rgba(0, 180, 255, 0.85)');
        tearGrad.addColorStop(0.5, 'rgba(0, 120, 255, 0.65)');
        tearGrad.addColorStop(0.85, 'rgba(255, 200, 80, 0.7)');
        tearGrad.addColorStop(1, 'rgba(255, 120, 0, 0)');
      } else if (g < 0.5) {
        // Martian: yellow luminous tip, blue root
        tearGrad.addColorStop(0, 'rgba(0, 160, 255, 0.85)');
        tearGrad.addColorStop(0.4, 'rgba(255, 210, 60, 0.85)');
        tearGrad.addColorStop(0.8, 'rgba(255, 120, 20, 0.7)');
        tearGrad.addColorStop(1, 'rgba(200, 40, 0, 0)');
      } else {
        // Earth 1.0G: Bright luminous yellow/orange sooty flame
        tearGrad.addColorStop(0, 'rgba(0, 140, 255, 0.9)');
        tearGrad.addColorStop(0.2, 'rgba(255, 240, 120, 0.95)');
        tearGrad.addColorStop(0.6, 'rgba(255, 160, 20, 0.9)');
        tearGrad.addColorStop(0.9, 'rgba(255, 60, 0, 0.75)');
        tearGrad.addColorStop(1, 'rgba(120, 20, 0, 0)');
      }

      ctx.fillStyle = tearGrad;
      ctx.fill();
    }

    ctx.restore();
  }

  drawAirflowVectors() {
    const ctx = this.ctx;
    const v = this.ventilation_speed_cms;
    if (v <= 0.5) return;

    ctx.save();
    ctx.strokeStyle = 'rgba(0, 210, 255, 0.25)';
    ctx.fillStyle = 'rgba(0, 210, 255, 0.35)';
    ctx.lineWidth = 1;

    const streamOffset = (this.animTime * (v * 0.4)) % 60;
    const rows = [this.cy - 70, this.cy - 30, this.cy + 20, this.cy + 60];

    rows.forEach(y => {
      for (let x = 30 + streamOffset; x < this.canvas.width - 30; x += 60) {
        ctx.beginPath();
        ctx.moveTo(x - 20, y);
        ctx.lineTo(x, y);
        ctx.stroke();

        // Arrow head
        ctx.beginPath();
        ctx.moveTo(x, y);
        ctx.lineTo(x - 4, y - 3);
        ctx.lineTo(x - 4, y + 3);
        ctx.closePath();
        ctx.fill();
      }
    });

    ctx.restore();
  }

  updateUIOverlay() {
    const tempEl = document.getElementById('telemetryTemp');
    const gravEl = document.getElementById('telemetryGravity');
    const ventEl = document.getElementById('telemetryVent');
    const regimeEl = document.getElementById('telemetryRegime');
    const paradoxEl = document.getElementById('simParadoxAlert');

    if (tempEl) tempEl.textContent = `${Math.round(this.flame_temp_k)} K`;
    if (gravEl) gravEl.textContent = `${this.gravity_g.toFixed(2)} G`;
    if (ventEl) ventEl.textContent = `${this.ventilation_speed_cms.toFixed(1)} cm/s`;
    if (regimeEl) regimeEl.textContent = this.flame_status;

    if (paradoxEl) {
      if (this.gravity_g === 0.0 && this.ventilation_speed_cms >= 3.0 && this.ventilation_speed_cms <= 14.0) {
        paradoxEl.style.display = 'flex';
      } else {
        paradoxEl.style.display = 'none';
      }
    }
  }

  loop() {
    if (!this.isRunning) return;
    this.animTime++;

    this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

    this.drawAirflowVectors();
    this.drawFuelSource();
    this.drawFlameEnvelope();
    this.spawnCombustionParticles();
    this.updateAndDrawParticles();
    this.updateUIOverlay();

    requestAnimationFrame(this.loop);
  }
}

// Global instance attached to window for script access
window.MicrogravityFlameSimulator = MicrogravityFlameSimulator;
