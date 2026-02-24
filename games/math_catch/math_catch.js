"use strict";


const canvas = document.getElementById("game");
const ctx = canvas.getContext("2d");

// Internal resolution (CSS can scale the canvas visually)
const W = canvas.width;
const H = canvas.height;

// Basket
const basket = {
  w: 120,
  h: 34, // thicker so we can display the current number on the bar
  x: W / 2 - 60,
  y: H - 60,
  speed: 520
};

// Balls
const BALL_VALUES = [1, 2, 3, 4, 5];        // normal (yellow)
const MULT_VALUES = [2, 3, 4];              // multiplier (green): x2, x3, x4
const NEG_VALUES  = [-1, -2, -3, -4, -5];   // negative (red): -1 to -5
const BALL_MIN_R = Math.floor(18 * 1.3);
const BALL_MAX_R = Math.floor(26 * 1.3);

// Difficulty
const TARGET_MIN = 5;
const TARGET_MAX = 11;
let spawnInterval = 0.85;          // seconds
const SPAWN_MIN = 0.35;
const SPAWN_ACCEL = 0.03;          // seconds per completed round

// Special ball spawn chances (tweak as you like)
const MULT_CHANCE = 0.12; // 12% chance for green multiplier ball
const NEG_CHANCE  = 0.15; // 15% chance for red negative ball

// State
const state = {
  phase: "target",  // "target" -> "countdown" -> "play" -> "paused"
  target: 0,
  current: 0,
  score: 0,
  countdown: 3.0,
  spawnTimer: 0
};

const balls = []; // {x,y,r,vy,value,type}  type: "normal" | "mult" | "neg"

// Input
const keys = { left: false, right: false };
window.addEventListener("keydown", (e) => {
  if (e.key === "ArrowLeft" || e.key === "a" || e.key === "A") keys.left = true;
  if (e.key === "ArrowRight" || e.key === "d" || e.key === "D") keys.right = true;
  if (e.key === "r" || e.key === "R") resetAll();
  if (e.key === "Escape") Pause();
});
window.addEventListener("keyup", (e) => {
  if (e.key === "ArrowLeft" || e.key === "a" || e.key === "A") keys.left = false;
  if (e.key === "ArrowRight" || e.key === "d" || e.key === "D") keys.right = false;
});

// Tap/click to start the round
canvas.addEventListener("click", () => {
  if (state.phase === "target") startCountdown();
});

function rand(min, max) { return Math.random() * (max - min) + min; }
function randInt(min, max) { return Math.floor(rand(min, max + 1)); }
function clamp(v, lo, hi) { return Math.max(lo, Math.min(hi, v)); }

function newTarget() {
  return randInt(TARGET_MIN, TARGET_MAX);
}

function circleRectCollide(cx, cy, r, rx, ry, rw, rh) {
  const closestX = clamp(cx, rx, rx + rw);
  const closestY = clamp(cy, ry, ry + rh);
  const dx = cx - closestX;
  const dy = cy - closestY;
  return dx * dx + dy * dy <= r * r;
}

function resetRound() {
  state.phase = "target";
  state.target = newTarget();
  state.current = 0;
  state.countdown = 3.0;
  state.spawnTimer = 0;
  balls.length = 0;
}

function resetAll() {
  spawnInterval = 0.85;
  state.score = 0;
  basket.x = W / 2 - basket.w / 2;
  resetRound();
}

function startCountdown() {
  state.phase = "countdown";
  state.countdown = 3.0;
  state.spawnTimer = 0;
  balls.length = 0;
}

function spawnBall() {
  const r = randInt(BALL_MIN_R, BALL_MAX_R);

  const roll = Math.random();
  let type = "normal";
  let value;

  if (roll < MULT_CHANCE) {
    type = "mult";
    value = MULT_VALUES[randInt(0, MULT_VALUES.length - 1)];
  } else if (roll < MULT_CHANCE + NEG_CHANCE) {
    type = "neg";
    value = NEG_VALUES[randInt(0, NEG_VALUES.length - 1)];
  } else {
    type = "normal";
    value = BALL_VALUES[randInt(0, BALL_VALUES.length - 1)];
  }

  balls.push({
    r,
    x: randInt(r, W - r),
    y: -r,
    vy: rand(140, 240),
    value,
    type
  });
}

function completeRound() {
  spawnInterval = Math.max(SPAWN_MIN, spawnInterval - SPAWN_ACCEL);
  resetRound();
}

function Pause() {
  // Toggle pause only during gameplay
  if (state.phase === "play") {
    state.phase = "paused";
    return;
  }
  if (state.phase === "paused") {
    state.phase = "play";
  }
}

// ===== Render helpers =====
function drawBackground() {
  ctx.fillStyle = "rgb(16,42,90)";
  ctx.fillRect(0, 0, W, H);

  const gx = W * 0.2, gy = H * 0.2, gr = 240;
  const grad = ctx.createRadialGradient(gx, gy, 10, gx, gy, gr);
  grad.addColorStop(0, "rgba(255,255,255,0.18)");
  grad.addColorStop(1, "rgba(255,255,255,0.00)");
  ctx.fillStyle = grad;
  ctx.fillRect(0, 0, W, H);
}

function roundRect(x, y, w, h, r) {
  const rr = Math.min(r, w / 2, h / 2);
  ctx.beginPath();
  ctx.moveTo(x + rr, y);
  ctx.arcTo(x + w, y, x + w, y + h, rr);
  ctx.arcTo(x + w, y + h, x, y + h, rr);
  ctx.arcTo(x, y + h, x, y, rr);
  ctx.arcTo(x, y, x + w, y, rr);
  ctx.closePath();
}

function drawBasket() {
  ctx.fillStyle = "rgb(255,122,24)";
  roundRect(basket.x, basket.y, basket.w, basket.h, 8);
  ctx.fill();

  // Show current number on the bar
  ctx.fillStyle = "rgb(255,255,255)";
  ctx.font = "bold 18px Arial";
  ctx.textAlign = "center";
  ctx.textBaseline = "middle";
  ctx.fillText(String(state.current), basket.x + basket.w / 2, basket.y + basket.h / 2 + 1);
  ctx.textAlign = "left";
}

function drawBall(b) {
  // Choose colors by type
  let fill = "rgb(253,224,71)";   // yellow (normal)
  let stroke = "rgb(245,158,11)";

  if (b.type === "mult") {
    fill = "rgb(74,222,128)";     // green
    stroke = "rgb(22,163,74)";
  } else if (b.type === "neg") {
    fill = "rgb(248,113,113)";    // red
    stroke = "rgb(220,38,38)";
  }

  ctx.beginPath();
  ctx.arc(b.x, b.y, b.r, 0, Math.PI * 2);
  ctx.fillStyle = fill;
  ctx.fill();
  ctx.lineWidth = 2;
  ctx.strokeStyle = stroke;
  ctx.stroke();

  // Label
  ctx.fillStyle = "rgb(11,27,58)";
  ctx.font = "bold 18px Arial";
  ctx.textAlign = "center";
  ctx.textBaseline = "middle";

  if (b.type === "mult") {
    ctx.fillText("x" + String(b.value), b.x, b.y + 1);
  } else {
    ctx.fillText(String(b.value), b.x, b.y + 1);
  }
}

function drawHUD() {
  ctx.fillStyle = "rgb(215,230,255)";
  ctx.font = "18px Arial";

  // Target centered at top
  ctx.textAlign = "center";
  ctx.fillText(`Target: ${state.target}`, W / 2, 26);

  // Score on top-right
  ctx.textAlign = "right";
  ctx.fillText(`Score: ${state.score}`, W - 16, 26);

  ctx.textAlign = "left";
}

function drawCenterText(big, small) {
  ctx.textAlign = "center";
  ctx.fillStyle = "rgb(215,230,255)";
  ctx.font = "bold 44px Arial";
  ctx.fillText(big, W / 2, H / 2 - 10);

  if (small) {
    ctx.fillStyle = "rgb(161,161,170)";
    ctx.font = "20px Arial";
    ctx.fillText(small, W / 2, H / 2 + 26);
  }
  ctx.textAlign = "left";
}

// ===== Main loop =====
let lastTs = performance.now();

function update(dt) {
  if (state.phase === "paused") {
    // Freeze everything while paused
    return;
  }
  // Move basket
  let vx = 0;
  if (keys.left) vx -= basket.speed;
  if (keys.right) vx += basket.speed;
  basket.x = clamp(basket.x + vx * dt, 0, W - basket.w);

  if (state.phase === "countdown") {
    state.countdown -= dt;
    if (state.countdown <= 0) {
      state.phase = "play";
      state.spawnTimer = 0;
      balls.length = 0;
    }
    return;
  }

  if (state.phase !== "play") {
    balls.length = 0;
    return;
  }

  // Spawn
  state.spawnTimer += dt;
  if (state.spawnTimer >= spawnInterval) {
    state.spawnTimer = 0;
    spawnBall();
  }

  // Update balls
  for (let i = balls.length - 1; i >= 0; i--) {
    const b = balls[i];
    b.y += b.vy * dt;

    // Catch
    if (circleRectCollide(b.x, b.y, b.r, basket.x, basket.y, basket.w, basket.h)) {

      if (b.type === "mult") {
        state.current *= b.value;
      } else {
        // "normal" and "neg" both add; neg values subtract
        state.current += b.value;
      }

      // Add score for every catch
      state.score += 100;

      // Floor at 0 for kid-friendly gameplay
      if (state.current < 0) state.current = 0;

      balls.splice(i, 1);

      if (state.current === state.target) {
        completeRound();
      }
      continue;
    }

    // Missed: no penalty
    if (b.y - b.r > H) {
      balls.splice(i, 1);
    }
  }
}

function render() {
  drawBackground();
  drawBasket();

  if (state.phase === "paused") {
    // Dim overlay
    ctx.fillStyle = "rgba(0,0,0,0.35)";
    ctx.fillRect(0, 0, W, H);

    // Center box
    const boxW = 520, boxH = 220;
    const boxX = W / 2 - boxW / 2;
    const boxY = H / 2 - boxH / 2;

    ctx.fillStyle = "rgb(30,30,30)";
    roundRect(boxX, boxY, boxW, boxH, 18);
    ctx.fill();

    ctx.strokeStyle = "rgb(56,56,56)";
    ctx.lineWidth = 2;
    roundRect(boxX, boxY, boxW, boxH, 18);
    ctx.stroke();

    // Text
    ctx.textAlign = "center";
    ctx.fillStyle = "rgb(215,230,255)";
    ctx.font = "bold 56px Arial";
    ctx.fillText("PAUSED", W / 2, boxY + 110);

    ctx.fillStyle = "rgb(161,161,170)";
    ctx.font = "20px Arial";
    ctx.fillText("Press ESC to resume", W / 2, boxY + 152);

    ctx.textAlign = "left";
    return;
  }

  if (state.phase === "play") {
    for (const b of balls) drawBall(b);
    drawHUD();
    return;
  }

  // Target screen
  if (state.phase === "target") {
    drawHUD();
    drawCenterText(`Target: ${state.target}`, "Click to start");
    return;
  }

  // Countdown screen
  if (state.phase === "countdown") {
    drawHUD();

    // Show target in a different color
    ctx.textAlign = "center";
    ctx.font = "bold 32px Arial";
    ctx.fillStyle = "rgb(99,102,241)"; // purple/blue accent
    ctx.fillText(`Target: ${state.target}`, W / 2, H / 2 - 90);

    // Main countdown text
    const t = Math.max(0, state.countdown);

    ctx.fillStyle = "rgb(215,230,255)";
    ctx.font = "bold 96px Arial";

    if (t > 0.5) {
      ctx.fillText(String(Math.ceil(t)), W / 2, H / 2 + 24);
    } else {
      ctx.fillText("GO!", W / 2, H / 2 + 24);
    }

    ctx.textAlign = "left";
  }
}

function loop(ts) {
  const dt = Math.min(0.05, (ts - lastTs) / 1000);
  lastTs = ts;

  update(dt);
  render();

  requestAnimationFrame(loop);
}

// Boot
resetAll();
requestAnimationFrame(loop);