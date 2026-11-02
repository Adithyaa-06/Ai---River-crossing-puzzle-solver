// River Crossing Solver - front end (plain JavaScript, no libraries).
//
// Flow: Solve -> POST /api/solve and GET /api/compare -> store the path
// -> draw one step at a time with Previous / Next / Auto-play.

// Emoji for each name the server puts in the "left" / "right" lists.
const EMOJI = {
  Farmer: "🧑‍🌾",
  Wolf: "🐺",
  Goat: "🐐",
  Cabbage: "🥬",
  M: "🧑‍🤝‍🧑",
  C: "👹",
};

// Current solution and which step is shown.
let path = [];
let currentStep = 0;
let playTimer = null;

// Page elements.
const puzzleSelect = document.getElementById("puzzle");
const algorithmSelect = document.getElementById("algorithm");
const solveBtn = document.getElementById("solve-btn");
const prevBtn = document.getElementById("prev-btn");
const nextBtn = document.getElementById("next-btn");
const playBtn = document.getElementById("play-btn");
const resetBtn = document.getElementById("reset-btn");
const speedInput = document.getElementById("speed");
const speedLabel = document.getElementById("speed-label");
const leftBank = document.getElementById("left-bank");
const rightBank = document.getElementById("right-bank");
const boat = document.getElementById("boat");
const stepInfo = document.getElementById("step-info");
const moveLog = document.getElementById("move-log");
const errorBox = document.getElementById("error");

// ---------------------------------------------------------------------------
// Talking to the server
// ---------------------------------------------------------------------------

async function solve() {
  stopAutoPlay();
  hideError();
  solveBtn.disabled = true;

  const puzzle = puzzleSelect.value;
  const algorithm = algorithmSelect.value;

  try {
    const response = await fetch("/api/solve", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ puzzle, algorithm }),
    });
    const result = await response.json();
    if (!response.ok) {
      throw new Error(result.error || "Something went wrong");
    }

    path = result.path;
    currentStep = 0;
    showStats(result);
    buildMoveLog();
    showStep();
    loadComparison(puzzle);
  } catch (err) {
    showError(err.message);
  } finally {
    solveBtn.disabled = false;
  }
}

async function loadComparison(puzzle) {
  const response = await fetch(`/api/compare?puzzle=${encodeURIComponent(puzzle)}`);
  const data = await response.json();
  if (!response.ok) {
    showError(data.error);
    return;
  }

  const rows = [
    ["Path length", "path_length", (v) => v],
    ["Nodes expanded", "nodes_expanded", (v) => v],
    ["Nodes generated", "nodes_generated", (v) => v],
    ["Time (ms)", "time_ms", (v) => v.toFixed(3)],
  ];

  const body = document.getElementById("compare-body");
  body.innerHTML = "";
  for (const [label, key, format] of rows) {
    const tr = document.createElement("tr");
    const bfsValue = data.bfs ? format(data.bfs[key]) : "–";
    const dfsValue = data.dfs ? format(data.dfs[key]) : "–";
    tr.innerHTML = `<td>${label}</td><td>${bfsValue}</td><td>${dfsValue}</td>`;
    body.appendChild(tr);
  }
}

// ---------------------------------------------------------------------------
// Drawing
// ---------------------------------------------------------------------------

function showStats(result) {
  document.getElementById("stat-expanded").textContent = result.nodes_expanded;
  document.getElementById("stat-length").textContent = result.path_length;
  document.getElementById("stat-time").textContent = result.time_ms.toFixed(3);
}

function buildMoveLog() {
  moveLog.innerHTML = "";
  path.forEach((step, index) => {
    const li = document.createElement("li");
    li.textContent = `${index}. ${step.move}`;
    li.addEventListener("click", () => {
      stopAutoPlay();
      currentStep = index;
      showStep();
    });
    moveLog.appendChild(li);
  });
}

// Fill one bank with emojis. "Boat" is drawn separately, so it is skipped.
function drawBank(element, names) {
  element.innerHTML = "";
  for (const name of names) {
    if (name === "Boat") continue;
    const span = document.createElement("span");
    span.textContent = EMOJI[name] || name;
    span.title = name;
    element.appendChild(span);
  }
}

// The boat is on the side that holds "Boat" (missionaries puzzle)
// or the side the farmer is on (farmer puzzle).
function boatIsOnRight(step) {
  return step.right.includes("Boat") || step.right.includes("Farmer");
}

function showStep() {
  if (path.length === 0) return;
  const step = path[currentStep];

  drawBank(leftBank, step.left);
  drawBank(rightBank, step.right);
  boat.classList.toggle("right", boatIsOnRight(step));

  stepInfo.textContent = `Step ${currentStep} of ${path.length - 1}: ${step.move}`;

  // Highlight the current move in the log.
  moveLog.querySelectorAll("li").forEach((li, index) => {
    li.classList.toggle("active", index === currentStep);
  });
  const active = moveLog.children[currentStep];
  if (active) active.scrollIntoView({ block: "nearest" });

  updateButtons();
}

function updateButtons() {
  const hasPath = path.length > 0;
  prevBtn.disabled = !hasPath || currentStep === 0;
  nextBtn.disabled = !hasPath || currentStep === path.length - 1;
  playBtn.disabled = !hasPath;
  resetBtn.disabled = !hasPath;
  playBtn.textContent = playTimer ? "⏸ Pause" : "▶ Auto-play";
}

// ---------------------------------------------------------------------------
// Playback
// ---------------------------------------------------------------------------

function nextStep() {
  if (currentStep < path.length - 1) {
    currentStep++;
    showStep();
  } else {
    stopAutoPlay();
  }
}

function prevStep() {
  if (currentStep > 0) {
    currentStep--;
    showStep();
  }
}

function startAutoPlay() {
  if (currentStep === path.length - 1) currentStep = 0;   // restart from the beginning
  showStep();
  playTimer = setInterval(nextStep, Number(speedInput.value));
  updateButtons();
}

function stopAutoPlay() {
  clearInterval(playTimer);
  playTimer = null;
  updateButtons();
}

function reset() {
  stopAutoPlay();
  currentStep = 0;
  showStep();
}

// ---------------------------------------------------------------------------
// Errors
// ---------------------------------------------------------------------------

function showError(message) {
  errorBox.textContent = message;
  errorBox.hidden = false;
}

function hideError() {
  errorBox.hidden = true;
}

// ---------------------------------------------------------------------------
// Event listeners
// ---------------------------------------------------------------------------

solveBtn.addEventListener("click", solve);
nextBtn.addEventListener("click", () => { stopAutoPlay(); nextStep(); });
prevBtn.addEventListener("click", () => { stopAutoPlay(); prevStep(); });
resetBtn.addEventListener("click", reset);
playBtn.addEventListener("click", () => (playTimer ? stopAutoPlay() : startAutoPlay()));

speedInput.addEventListener("input", () => {
  speedLabel.textContent = (speedInput.value / 1000).toFixed(1) + "s";
  // Apply the new speed straight away if auto-play is running.
  if (playTimer) {
    clearInterval(playTimer);
    playTimer = setInterval(nextStep, Number(speedInput.value));
  }
});
