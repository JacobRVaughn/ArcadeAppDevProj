// catch_stars.js
"use strict";

// ====== Canvas setup ======
const canvas = document.getElementById("game");
if (!canvas) {
  throw new Error("Canvas with id='game' not found. Add <canvas id='game'></canvas> to the page.");
}
const ctx = canvas.getContext("2d");

// ====== Game state ======
const state = {
  score: 0,
  lives: 3,
  running: true,
  lastTime: 0,
  spawnTimer: 0,
  spawnInterval: 900 // ms between star spawns (will speed up)
};

// ====== Player (basket) ======
const basket = {
  w: 110,
  h: 20,
  x: canvas.width / 2 - 55,
  y: canvas.height - 45,
  speed: 420, // pixels/sec
  vx: 0
};

// ====== Falling objects ======
const stars = []; // each star: {x,y,r,vy}

function rand(min, max) {
  return Math.random() * (max - min) + min;
}

function spawnStar() {
  const r = rand(10, 16);
  stars.push({
    x: rand(r, canvas.width - r),
    y: -r,
    r,
    vy: rand(130, 220) + state.score * 2
  });
}

// ====== Input handling ======
const keys = { left: false, right: false };

function onKeyDown(e) {
  const k = e.key.toLowerCase();
  if (e.key === "ArrowLeft" || k === "a") keys.left = true;
  if (e.key === "ArrowRight" || k === "d") keys.right = true;
  if (k === "r") resetGame();
}

function onKeyUp(e) {
  const k = e.key.toLowerCase();
  if (e.key === "ArrowLeft" || k === "a") keys.left = false;
  if (e.key === "ArrowRight" || k === "d") keys.right = false;
}

window.addEventListener("keydown", onKeyDown);
window.addEventListener("keyup", onKeyUp);

canvas.addEventListener("click", () => {
  if (!state.running) resetGame();
});

// ====== Helpers ======
function resetGame() {
  state.score = 0;
  state.lives = 3;
  state.running = true;
  state.spawnTimer = 0;
  state.spawnInterval = 900;
  stars.length = 0;
  basket.x = canvas.width / 2 - basket.w / 2;
  basket.vx = 0;
}

function circleRectCollision(cx, cy, cr, rx, ry, rw, rh) {
  const closestX = Math.max(rx, Math.min(cx, rx + rw));
  const closestY = Math.max(ry, Math.min(cy, ry + rh));
  const dx = cx - closestX;
  const dy = cy - closestY;
  return (dx * dx + dy * dy) <= cr * cr;
}

// ====== Update loop ======
function update(dt) {
  if (!state.running) return;

  basket.vx = 0;
  if (keys.left) basket.vx = -basket.speed;
  if (keys.right) basket.vx = basket.speed;

  basket.x += basket.vx * dt;
  basket.x = Math.max(0, Math.min(canvas.width - basket.w, basket.x));

  state.spawnTimer += dt * 1000;
  if (state.spawnTimer >= state.spawnInterval) {
    state.spawnTimer = 0;
    spawnStar();
    state.spawnInterval = Math.max(350, state.spawnInterval - 8);
  }

  for (let i = stars.length - 1; i >= 0; i--) {
    const s = stars[i];
    s.y += s.vy * dt;

    if (circleRectCollision(s.x, s.y, s.r, basket.x, basket.y, basket.w, basket.h)) {
      state.score += 1;
      stars.splice(i, 1);
      continue;
    }

    if (s.y - s.r > canvas.height) {
      state.lives -= 1;
      stars.splice(i, 1);

      if (state.lives <= 0) state.running = false;
    }
  }
}

// ====== Render ======
function drawBackground() {
  ctx.fillStyle = "#102a5a";
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  const g = ctx.createRadialGradient(
    canvas.width * 0.2, canvas.height * 0.2, 40,
    canvas.width * 0.2, canvas.height * 0.2, 320
  );
  g.addColorStop(0, "rgba(255,255,255,0.10)");
  g.addColorStop(1, "rgba(255,255,255,0)");
  ctx.fillStyle = g;
  ctx.fillRect(0, 0, canvas.width, canvas.height);
}

function drawStar(x, y, r) {
  ctx.save();
  ctx.translate(x, y);
  ctx.fillStyle = "#ffef7a";
  ctx.beginPath();
  for (let i = 0; i < 5; i++) {
    const a = (i * 2 * Math.PI) / 5 - Math.PI / 2;
    ctx.lineTo(Math.cos(a) * r, Math.sin(a) * r);
    const b = a + Math.PI / 5;
    ctx.lineTo(Math.cos(b) * (r * 0.45), Math.sin(b) * (r * 0.45));
  }
  ctx.closePath();
  ctx.fill();

  ctx.globalAlpha = 0.35;
  ctx.beginPath();
  ctx.arc(0, 0, r * 1.5, 0, Math.PI * 2);
  ctx.fill();
  ctx.restore();
}

function drawBasket() {
  ctx.fillStyle = "#ff7a18";
  ctx.fillRect(basket.x, basket.y, basket.w, basket.h);

  ctx.fillStyle = "#ffd2b3";
  ctx.fillRect(basket.x + 10, basket.y - 10, basket.w - 20, 8);

  ctx.fillStyle = "rgba(255,255,255,0.9)";
  ctx.fillRect(basket.x + 28, basket.y + 6, 10, 5);
  ctx.fillRect(basket.x + basket.w - 38, basket.y + 6, 10, 5);
}

function drawHUD() {
  ctx.fillStyle = "#d7e6ff";
  ctx.font = "18px Arial";
  ctx.fillText(`Score: ${state.score}`, 18, 28);
  ctx.fillText(`Lives: ${state.lives}`, 18, 52);
}

function drawGameOver() {
  ctx.save();
  ctx.fillStyle = "rgba(0,0,0,0.45)";
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  ctx.fillStyle = "#ffffff";
  ctx.font = "bold 40px Arial";
  ctx.textAlign = "center";
  ctx.fillText("Game Over", canvas.width / 2, canvas.height / 2 - 20);

  ctx.font = "20px Arial";
  ctx.fillText(`Final Score: ${state.score}`, canvas.width / 2, canvas.height / 2 + 18);

  ctx.font = "16px Arial";
  ctx.fillText("Press R to restart (or click)", canvas.width / 2, canvas.height / 2 + 50);
  ctx.restore();
}

function render() {
  drawBackground();
  for (const s of stars) drawStar(s.x, s.y, s.r);
  drawBasket();
  drawHUD();
  if (!state.running) drawGameOver();
}

// ====== Main loop ======
function loop(timestamp) {
  const dt = Math.min(0.033, (timestamp - state.lastTime) / 1000 || 0);
  state.lastTime = timestamp;

  update(dt);
  render();
  requestAnimationFrame(loop);
}

// Start
resetGame();
requestAnimationFrame(loop);