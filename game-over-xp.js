/**
 * game-over-xp.js
 * Drop this script into any game page. Call showGameOverXP() when the game ends.
 *
 * Usage:
 *   <script src="../../game-over-xp.js"></script>
 *   <script>
 *     // when your game ends:
 *     showGameOverXP({ gameId: "math-catch", score: 1450, xpEarned: 300 });
 *   </script>
 *
 * The overlay injects its own CSS — no stylesheet needed.
 * Clicking "Back to Dashboard" navigates to /student-dashboard.php.
 */

(function () {
  // ── Inject styles ────────────────────────────────────────────────────────
  const STYLE = `
    #xp-overlay *{box-sizing:border-box;margin:0;padding:0}
    #xp-overlay{
      position:fixed;inset:0;z-index:99999;
      display:flex;align-items:center;justify-content:center;
      background:rgba(7,10,19,.88);
      backdrop-filter:blur(6px);
      font-family:ui-sans-serif,system-ui,-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;
      color:#fff;
      opacity:0;transition:opacity .35s ease;
    }
    #xp-overlay.visible{opacity:1}
    .xpo-card{
      background:rgba(255,255,255,.05);
      border:1px solid rgba(255,255,255,.11);
      border-radius:22px;
      padding:36px 40px;
      width:min(460px,92vw);
      text-align:center;
      transform:translateY(22px);
      transition:transform .4s cubic-bezier(.22,1,.36,1);
      box-shadow:0 24px 60px rgba(0,0,0,.55);
    }
    #xp-overlay.visible .xpo-card{transform:translateY(0)}
    .xpo-icon{font-size:52px;line-height:1;margin-bottom:12px}
    .xpo-title{font-size:26px;font-weight:800;letter-spacing:.02em;margin-bottom:4px}
    .xpo-score{font-size:14px;color:rgba(255,255,255,.55);margin-bottom:26px}
    .xpo-score strong{color:rgba(255,255,255,.85);font-size:16px}

    /* XP bar */
    .xpo-xp-label{
      display:flex;justify-content:space-between;align-items:baseline;
      font-size:12px;color:rgba(255,255,255,.55);margin-bottom:8px;
    }
    .xpo-xp-label .lvl{font-size:13px;color:#fff;font-weight:700}
    .xpo-bar-track{
      height:14px;background:rgba(255,255,255,.10);
      border-radius:999px;overflow:hidden;margin-bottom:6px;
    }
    .xpo-bar-fill{
      height:100%;width:0%;border-radius:999px;
      background:linear-gradient(90deg,#4F5DFF,#818CF8);
      transition:width .9s cubic-bezier(.22,1,.36,1);
    }
    .xpo-bar-foot{font-size:11px;color:rgba(255,255,255,.40);margin-bottom:20px}
    .xpo-earned{
      display:inline-flex;align-items:center;gap:6px;
      padding:8px 18px;border-radius:999px;
      background:rgba(79,93,255,.18);
      border:1px solid rgba(79,93,255,.35);
      font-size:14px;font-weight:700;color:#818CF8;
      margin-bottom:22px;
    }

    /* Level-up banner */
    .xpo-levelup{
      background:linear-gradient(135deg,rgba(245,158,11,.18),rgba(245,158,11,.06));
      border:1px solid rgba(245,158,11,.40);
      border-radius:14px;padding:12px 16px;
      font-size:13px;color:#FCD34D;
      margin-bottom:20px;
      display:none;
    }
    .xpo-levelup.show{display:block}
    .xpo-levelup strong{font-size:16px;display:block;margin-bottom:2px}

    /* Buttons */
    .xpo-actions{display:flex;gap:10px;justify-content:center;flex-wrap:wrap}
    .xpo-btn{
      border:1px solid rgba(255,255,255,.13);
      background:rgba(255,255,255,.07);
      color:#fff;padding:11px 22px;border-radius:14px;
      cursor:pointer;font-size:13px;font-weight:600;letter-spacing:.06em;
      transition:.15s ease;
    }
    .xpo-btn:hover{background:rgba(255,255,255,.12);transform:translateY(-1px)}
    .xpo-btn.primary{
      background:rgba(79,93,255,.85);
      border-color:rgba(79,93,255,.55);
    }
    .xpo-btn.primary:hover{background:rgba(79,93,255,.95)}

    /* Error state */
    .xpo-error{
      font-size:12px;color:rgba(239,68,68,.8);margin-top:14px;
    }
    /* Loading spinner */
    .xpo-spinner{
      width:32px;height:32px;border-radius:50%;
      border:3px solid rgba(255,255,255,.12);
      border-top-color:#4F5DFF;
      animation:xpo-spin .7s linear infinite;
      margin:20px auto;
    }
    @keyframes xpo-spin{to{transform:rotate(360deg)}}
  `;

  function injectStyles() {
    if (document.getElementById("xpo-styles")) return;
    const s = document.createElement("style");
    s.id = "xpo-styles";
    s.textContent = STYLE;
    document.head.appendChild(s);
  }

  // ── XP math (must match PHP logic) ──────────────────────────────────────
  function xpToLevel(xp) { return Math.floor(xp / 1000) + 1; }
  function xpProgress(xp) { return xp % 1000; }
  function getRankTitle(level) {
    if (level >= 7) return "Elite Cadet";
    if (level >= 5) return "Senior Cadet";
    if (level >= 3) return "Cadet";
    return "Junior Cadet";
  }

  // ── Build overlay DOM ────────────────────────────────────────────────────
  function buildOverlay() {
    const el = document.createElement("div");
    el.id = "xp-overlay";
    el.innerHTML = `
      <div class="xpo-card">
        <div class="xpo-icon">🏆</div>
        <div class="xpo-title">Game Over!</div>
        <div class="xpo-score" id="xpo-score-line">Loading results…</div>
        <div class="xpo-spinner" id="xpo-spinner"></div>
        <div id="xpo-results" style="display:none">
          <div class="xpo-earned" id="xpo-earned-badge">+0 XP</div>
          <div class="xpo-levelup" id="xpo-levelup">
            <strong>⭐ LEVEL UP!</strong>
            <span id="xpo-levelup-text"></span>
          </div>
          <div class="xpo-xp-label">
            <span class="lvl" id="xpo-level">Level 1</span>
            <span id="xpo-xp-right">0 / 1000 XP</span>
          </div>
          <div class="xpo-bar-track">
            <div class="xpo-bar-fill" id="xpo-bar"></div>
          </div>
          <div class="xpo-bar-foot" id="xpo-bar-foot">0 XP to next level</div>
          <div class="xpo-actions">
            <button class="xpo-btn" id="xpo-replay">PLAY AGAIN</button>
            <button class="xpo-btn primary" id="xpo-dashboard">BACK TO DASHBOARD</button>
          </div>
        </div>
        <div class="xpo-error" id="xpo-error"></div>
      </div>
    `;
    document.body.appendChild(el);

    // Force reflow then fade in
    requestAnimationFrame(() => {
      requestAnimationFrame(() => el.classList.add("visible"));
    });

    return el;
  }

  // ── Animate XP bar ───────────────────────────────────────────────────────
  function animateXP(xpBefore, xpAfter, leveledUp) {
    const bar      = document.getElementById("xpo-bar");
    const levelEl  = document.getElementById("xpo-level");
    const xpRight  = document.getElementById("xpo-xp-right");
    const barFoot  = document.getElementById("xpo-bar-foot");

    const PER_LEVEL = 1000;

    if (!leveledUp) {
      // Simple: animate from old progress to new progress within same level
      const startPct = (xpProgress(xpBefore) / PER_LEVEL) * 100;
      const endPct   = (xpProgress(xpAfter)  / PER_LEVEL) * 100;
      const level    = xpToLevel(xpAfter);

      levelEl.textContent = `Level ${level} — ${getRankTitle(level)}`;
      xpRight.textContent = `${xpProgress(xpAfter)} / ${PER_LEVEL} XP`;
      barFoot.textContent = `${PER_LEVEL - xpProgress(xpAfter)} XP to next level`;

      bar.style.width = startPct + "%";
      requestAnimationFrame(() => {
        setTimeout(() => { bar.style.width = endPct + "%"; }, 80);
      });
    } else {
      // Level-up animation: fill bar to 100%, flash, then show new level progress
      const startPct = (xpProgress(xpBefore) / PER_LEVEL) * 100;
      const newLevel = xpToLevel(xpAfter);
      const endPct   = (xpProgress(xpAfter)  / PER_LEVEL) * 100;

      levelEl.textContent = `Level ${newLevel - 1} → ${newLevel}`;
      bar.style.width = startPct + "%";

      // Phase 1: fill to 100%
      setTimeout(() => {
        bar.style.transition = "width .6s cubic-bezier(.22,1,.36,1)";
        bar.style.width = "100%";
      }, 80);

      // Phase 2: flash gold, reset, show new level
      setTimeout(() => {
        bar.style.background = "linear-gradient(90deg,#F59E0B,#FCD34D)";
        bar.style.transition = "none";
        bar.style.width = "0%";

        levelEl.textContent = `Level ${newLevel} — ${getRankTitle(newLevel)}`;
        xpRight.textContent = `${xpProgress(xpAfter)} / ${PER_LEVEL} XP`;
        barFoot.textContent = `${PER_LEVEL - xpProgress(xpAfter)} XP to next level`;

        // Phase 3: animate in new level's progress
        setTimeout(() => {
          bar.style.transition = "width .8s cubic-bezier(.22,1,.36,1)";
          bar.style.width = endPct + "%";
        }, 120);
      }, 780);
    }
  }

  // ── Main public function ─────────────────────────────────────────────────
  /**
   * @param {object} opts
   * @param {string} opts.gameId     - matches game_id in missions list e.g. "math-catch"
   * @param {number} opts.score      - raw game score
   * @param {number} opts.xpEarned   - XP to award (server caps at 1000)
   * @param {string} [opts.replayUrl]- URL to reload for replay (defaults to location.reload)
   * @param {string} [opts.dashUrl]  - URL for dashboard button (default: /student-dashboard.php)
   */
  window.showGameOverXP = async function (opts = {}) {
    injectStyles();

    const {
      gameId,
      score      = 0,
      xpEarned   = 0,
      replayUrl  = null,
      dashUrl    = "/ArcadeAppDevProj/student-dashboard.php",
    } = opts;

    const overlay = buildOverlay();

    // Score line
    document.getElementById("xpo-score-line").innerHTML =
      `Final score: <strong>${score.toLocaleString()}</strong>`;

    // ── Call backend ───────────────────────────────────────────────────────
    let result = null;
    try {
      const res = await fetch("/ArcadeAppDevProj/save_game_result.php", {
        method:  "POST",
        headers: { "Content-Type": "application/json" },
        body:    JSON.stringify({ game_id: gameId, score, xp_earned: xpEarned }),
      });

      if (res.status === 401) {
        // Not logged in — still show overlay but skip XP
        document.getElementById("xpo-spinner").style.display = "none";
        document.getElementById("xpo-error").textContent =
          "Sign in to save your progress!";
        document.getElementById("xpo-results").style.display = "block";
        document.getElementById("xpo-earned-badge").textContent = `+${xpEarned} XP (not saved)`;
        setupButtons(overlay, replayUrl, dashUrl);
        return;
      }

      result = await res.json();
    } catch (err) {
      document.getElementById("xpo-spinner").style.display = "none";
      document.getElementById("xpo-error").textContent =
        "Could not reach server. Score not saved.";
      document.getElementById("xpo-results").style.display = "block";
      setupButtons(overlay, replayUrl, dashUrl);
      return;
    }

    // ── Render results ─────────────────────────────────────────────────────
    document.getElementById("xpo-spinner").style.display = "none";
    document.getElementById("xpo-results").style.display = "block";

    if (result.status !== "ok") {
      document.getElementById("xpo-error").textContent =
        result.message || "Error saving result.";
      setupButtons(overlay, replayUrl, dashUrl);
      return;
    }

    // XP earned badge
    document.getElementById("xpo-earned-badge").textContent =
      `+${result.xp_earned} XP earned`;

    // Level-up banner
    if (result.leveled_up) {
      const banner = document.getElementById("xpo-levelup");
      banner.classList.add("show");
      document.getElementById("xpo-levelup-text").textContent =
        `${getRankTitle(result.level_before)} → ${getRankTitle(result.level_after)}`;
    }

    // Animate bar
    animateXP(result.xp_before, result.xp_after, result.leveled_up);

    setupButtons(overlay, replayUrl, dashUrl);
  };

  function setupButtons(overlay, replayUrl, dashUrl) {
    document.getElementById("xpo-replay").addEventListener("click", () => {
      overlay.remove();
      if (replayUrl) {
        window.location.href = replayUrl;
      } else {
        window.location.reload();
      }
    });
    document.getElementById("xpo-dashboard").addEventListener("click", () => {
      window.location.href = dashUrl;
    });
  }
})();