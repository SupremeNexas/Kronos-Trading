// Injected Panel Setup
let sidebar = document.createElement('div');
sidebar.id = 'kronos-tv-sidebar';
sidebar.innerHTML = `
  <div class="kronos-header" id="kronos-drag-handle">
    <span class="kronos-title">📈 Kronos Forecast Client</span>
    <span id="kronos-toggle" style="cursor:pointer">➖</span>
  </div>
  <div class="kronos-body">
    <div class="kronos-info-row">
      <span>Active Asset:</span>
      <span id="active-symbol" style="font-weight:bold;color:#ffeb3b">LOADING</span>
    </div>
    <div class="kronos-info-row">
      <span>Interval:</span>
      <span id="active-timeframe" style="font-weight:bold">LOADING</span>
    </div>

    <div class="kronos-chart-area" id="forecast-canvas-container">
      <canvas id="forecast-canvas" width="280" height="170" style="position:absolute;top:5px;left:5px;"></canvas>
      <span id="chart-placeholder" style="font-size:11px;color:#787b86">Click Predict to render candles</span>
    </div>

    <div class="kronos-stats-box">
      <div style="font-weight:bold;margin-bottom:5px;display:flex;justify-content:space-between">
        <span>Signal: <span id="trade-signal" style="color:#d1d4dc">HOLD</span></span>
        <span>Cash: $<span id="lbl-cash">100,000</span></span>
      </div>
      <div style="display:flex;justify-content:space-between">
        <span>Position: <span id="lbl-pos">0</span></span>
        <label style="font-size:11px; cursor:pointer;">
          <input type="checkbox" id="auto-trade-chk"> Auto-Trade
        </label>
      </div>
    </div>

    <button class="kronos-btn" id="btn-predict">Generate Kronos Forecast</button>

    <div class="kronos-btn-group">
      <button class="kronos-btn btn-buy" id="btn-buy">Market BUY</button>
      <button class="kronos-btn btn-sell" id="btn-sell">Market SELL</button>
    </div>
  </div>
  <div class="warning-banner">⚠️ MOCK PAPER TRADING MODE ONLY</div>
`;
document.body.appendChild(sidebar);

// Setup collapse toggler
let header = document.getElementById('kronos-drag-handle');
let toggleBtn = document.getElementById('kronos-toggle');
header.addEventListener('click', (e) => {
  if(e.target === toggleBtn || e.target.id === "kronos-toggle"){
    sidebar.classList.toggle('collapsed');
    toggleBtn.textContent = sidebar.classList.contains('collapsed') ? '➕' : '➖';
  }
});

// Update asset info
function updateTickerInfo() {
  let title = document.title;
  let symbol = title.split(/[\s]/)[0];

  let interval = "1h";
  let intervalEl = document.getElementById('header-toolbar-intervals');
  if (intervalEl) {
    interval = intervalEl.textContent.trim();
  }

  if (symbol && symbol !== "TradingView" && !symbol.includes("Chart")) {
    document.getElementById('active-symbol').textContent = symbol;
  }
  document.getElementById('active-timeframe').textContent = interval;
  return { symbol, interval };
}

setInterval(updateTickerInfo, 2000);

// Fetch cash & positions
async function refreshPortfolio() {
  try {
    let res = await fetch('http://localhost:7070/api/portfolio');
    let data = await res.json();
    document.getElementById('lbl-cash').textContent = Math.round(data.cash).toLocaleString();
    let symbol = document.getElementById('active-symbol').textContent;
    let pos = data.positions[symbol] || data.positions[symbol + "T"] || {quantity: 0};
    document.getElementById('lbl-pos').textContent = parseFloat(pos.quantity).toFixed(4);
  } catch(err) {
    console.warn("Failed to connect to local server portfolio API");
  }
}

setInterval(refreshPortfolio, 5000);
setTimeout(refreshPortfolio, 1000);

// Draw candlestick charts on HTML canvas
function drawCanvasPredict(history, prediction) {
  let canvas = document.getElementById('forecast-canvas');
  let ctx = canvas.getContext('2d');
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  document.getElementById('chart-placeholder').style.display = 'none';

  // Keep last 40 history points + prediction points for visual clarity
  let cleanHistory = history.slice(-40);
  let all = [];
  cleanHistory.forEach(d => all.push({o: d.open, h: d.high, l: d.low, c: d.close, isPred: false}));
  prediction.forEach(d => all.push({o: d.open, h: d.high, l: d.low, c: d.close, isPred: true}));

  let prices = all.flatMap(d => [d.o, d.h, d.l, d.c]);
  let min = Math.min(...prices);
  let max = Math.max(...prices);
  let range = max - min || 1;

  let pad = 10;
  let chartH = canvas.height - 2 * pad;
  let chartW = canvas.width;
  let spacing = chartW / all.length;
  let barW = spacing * 0.7;

  // Draw division line between history and prediction
  let splitIdx = cleanHistory.length;
  let splitX = splitIdx * spacing;
  ctx.strokeStyle = 'rgba(255,255,255,0.15)';
  ctx.setLineDash([4, 4]);
  ctx.lineWidth = 1;
  ctx.beginPath();
  ctx.moveTo(splitX, 0);
  ctx.lineTo(splitX, canvas.height);
  ctx.stroke();
  ctx.setLineDash([]); // Reset

  for(let i=0; i<all.length; i++) {
    let d = all[i];
    let x = i * spacing + spacing / 2;

    let yOpen = canvas.height - pad - ((d.o - min) / range) * chartH;
    let yClose = canvas.height - pad - ((d.c - min) / range) * chartH;
    let yHigh = canvas.height - pad - ((d.h - min) / range) * chartH;
    let yLow = canvas.height - pad - ((d.l - min) / range) * chartH;

    let isBull = d.c >= d.o;
    let color;

    if (d.isPred) {
      color = isBull ? 'rgba(38, 166, 154, 0.9)' : 'rgba(239, 83, 80, 0.9)';
      ctx.strokeStyle = color;
      ctx.fillStyle = isBull ? 'rgba(38, 166, 154, 0.15)' : 'rgba(239, 83, 80, 0.15)';
      ctx.lineWidth = 1.5;
    } else {
      color = isBull ? '#26a69a' : '#ef5350';
      ctx.strokeStyle = color;
      ctx.fillStyle = color;
      ctx.lineWidth = 1;
    }

    // Draw Wick
    ctx.beginPath();
    ctx.moveTo(x, yHigh);
    ctx.lineTo(x, yLow);
    ctx.stroke();

    // Draw Body
    let yTop = Math.min(yOpen, yClose);
    let yBottom = Math.max(yOpen, yClose);
    let bodyH = Math.max(yBottom - yTop, 1.5);

    ctx.beginPath();
    ctx.rect(x - barW / 2, yTop, barW, bodyH);
    ctx.fill();
    ctx.stroke();
  }
}

// Predict Trigger
document.getElementById('btn-predict').addEventListener('click', async () => {
  let btn = document.getElementById('btn-predict');
  btn.disabled = true;
  btn.textContent = "Forecasting...";

  let { symbol, interval } = updateTickerInfo();
  let autoTrade = document.getElementById('auto-trade-chk').checked;

  try {
    let res = await fetch('http://localhost:7070/api/predict_tv', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ symbol, timeframe: interval, auto_trade: autoTrade })
    });
    let data = await res.json();

    if (data.success) {
      document.getElementById('trade-signal').textContent = data.signal;
      let sigColor = data.signal === "BUY" ? "#26a69a" : data.signal === "SELL" ? "#ef5350" : "#d1d4dc";
      document.getElementById('trade-signal').style.color = sigColor;

      drawCanvasPredict(data.history, data.prediction);
      refreshPortfolio();
    } else {
      alert("Forecast Failed: " + data.error);
    }
  } catch(err) {
    alert("Cannot connect to local Flask server on http://localhost:7070");
  } finally {
    btn.disabled = false;
    btn.textContent = "Generate Kronos Forecast";
  }
});

// Manual Order placement UI helpers
async function submitManualOrder(action) {
  let { symbol } = updateTickerInfo();
  let price = prompt("Enter Execution Price (e.g. Current Price):", "");
  let qty = prompt("Enter Order Quantity:", "");
  if(!price || !qty) return;

  try {
    let res = await fetch('http://localhost:7070/api/trade_tv', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ symbol, action, quantity: parseFloat(qty), price: parseFloat(price) })
    });
    let data = await res.json();
    if(data.success){
      alert(data.message);
      refreshPortfolio();
    } else {
      alert("Order Error: " + data.error);
    }
  } catch(err) {
    alert("Failed to submit manual order");
  }
}

document.getElementById('btn-buy').addEventListener('click', () => submitManualOrder('BUY'));
document.getElementById('btn-sell').addEventListener('click', () => submitManualOrder('SELL'));
