(function() {
  // Only target chart pages
  if (!window.location.pathname.includes('/chart')) {
    return;
  }

  console.log("🚀 Kronos TradingView Bridge Initializing...");

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

      <div id="advisory-box" style="display:none; font-size:10px; line-height:1.4; padding:8px; background:rgba(0,0,0,0.25); border:1px dashed rgba(255,255,255,0.08); border-radius:6px; color:#cbd5e1; max-height:85px; overflow-y:auto; word-break:break-word;">
        <i>💡 Advisor View:</i> <span id="kronos-explanation"></span>
      </div>

      <button class="kronos-btn" id="btn-predict">Generate Kronos Forecast</button>

      <div class="kronos-btn-group">
        <button class="kronos-btn btn-buy" id="btn-buy">Market BUY</button>
        <button class="kronos-btn btn-sell" id="btn-sell">Market SELL</button>
      </div>
    </div>
    <div class="warning-banner">⚠️ MOCK PAPER TRADING MODE ONLY</div>
  `;

  // Safely inject sidebar once DOM is fully accessible
  function injectUI() {
    if (document.body) {
      document.body.appendChild(sidebar);
      setupWidgetEvents();
    } else {
      setTimeout(injectUI, 100);
    }
  }

  injectUI();

  // Setup widget interactivity
  function setupWidgetEvents() {
    let header = document.getElementById('kronos-drag-handle');
    let toggleBtn = document.getElementById('kronos-toggle');
    header.addEventListener('click', (e) => {
      if(e.target === toggleBtn || e.target.id === "kronos-toggle"){
        sidebar.classList.toggle('collapsed');
        toggleBtn.textContent = sidebar.classList.contains('collapsed') ? '➕' : '➖';
      }
    });

    setInterval(updateTickerInfo, 2000);
    setInterval(refreshPortfolio, 5000);
    setTimeout(refreshPortfolio, 1000);

    document.getElementById('btn-predict').addEventListener('click', generateForecast);
    document.getElementById('btn-buy').addEventListener('click', () => submitManualOrder('BUY'));
    document.getElementById('btn-sell').addEventListener('click', () => submitManualOrder('SELL'));
  }

  // Robustly retrieve active symbol and timeframe
  function updateTickerInfo() {
    let symbol = "";

    // 1. Target search bar text (Direct DOM element on TV chart)
    let symbolBtn = document.getElementById('header-toolbar-symbol-search');
    if (symbolBtn) {
      symbol = symbolBtn.textContent.trim();
    }

    // 2. Target page title as fallback
    if (!symbol || symbol === "TradingView" || symbol.includes("Chart")) {
      let title = document.title;
      symbol = title.split(/[\s]/)[0];
    }

    // Clean up junk parses
    if (symbol && (symbol === "TradingView" || symbol.includes("Chart") || symbol.length > 10)) {
      symbol = "";
    }

    let interval = "1h";
    let intervalEl = document.getElementById('header-toolbar-intervals');
    if (intervalEl) {
      interval = intervalEl.textContent.trim();
    }

    if (symbol) {
      document.getElementById('active-symbol').textContent = symbol;
    }
    document.getElementById('active-timeframe').textContent = interval;
    return { symbol, interval };
  }

  // Refresh Cash & Positions from local API
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

  // Generate forecast
  async function generateForecast() {
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

        if (data.explanation) {
          document.getElementById('advisory-box').style.display = 'block';
          document.getElementById('kronos-explanation').textContent = data.explanation;
        } else {
          document.getElementById('advisory-box').style.display = 'none';
        }

        drawCanvasPredict(data.history, data.prediction);
        drawOverlayPredict(data.history, data.prediction, data.entry_price, data.take_profit, data.stop_loss, data.signal);
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
  }

  // Draw candlestick predictions on HTML Canvas
  function drawCanvasPredict(history, prediction) {
    let canvas = document.getElementById('forecast-canvas');
    let ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    document.getElementById('chart-placeholder').style.display = 'none';

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

    // Draw division line
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

  // Manual orders
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

  // Draw glowing forecast overlay on TradingView chart container
  function drawOverlayPredict(history, prediction, entryPrice, takeProfit, stopLoss, signal) {
    const containers = document.querySelectorAll('.chart-container, .chart-widget, .layout__area--center');
    if (!containers || containers.length === 0) return;

    const chartContainer = containers[0];

    // Ensure relative positioning for absolute centering of child elements
    const currentStyle = window.getComputedStyle(chartContainer);
    if (currentStyle.position === 'static') {
      chartContainer.style.position = 'relative';
    }

    let overlay = document.getElementById('kronos-chart-overlay');
    if (!overlay) {
      overlay = document.createElement('canvas');
      overlay.id = 'kronos-chart-overlay';
      overlay.style.position = 'absolute';
      overlay.style.top = '0';
      overlay.style.left = '0';
      overlay.style.width = '100%';
      overlay.style.height = '100%';
      overlay.style.pointerEvents = 'none';
      overlay.style.zIndex = '5'; // Above TV candles but below sidebar
      chartContainer.appendChild(overlay);
    }

    const ctx = overlay.getContext('2d');
    const dpr = window.devicePixelRatio || 1;
    const width = chartContainer.clientWidth;
    const height = chartContainer.clientHeight;

    overlay.width = width * dpr;
    overlay.height = height * dpr;
    overlay.style.width = `${width}px`;
    overlay.style.height = `${height}px`;
    ctx.scale(dpr, dpr);

    ctx.clearRect(0, 0, width, height);

    // Position forecast details in the right-hand offset
    const rightMargin = 140;
    const startX = width - rightMargin;
    const predLen = prediction.length;
    const candleWidth = Math.max(3, (rightMargin - 20) / predLen);

    const highs = prediction.map(p => p.high);
    const lows = prediction.map(p => p.low);
    const maxVal = Math.max(...highs, entryPrice, takeProfit);
    const minVal = Math.min(...lows, entryPrice, stopLoss);
    const range = maxVal - minVal || 1;

    // Map price to local Y coordinates
    const padY = 50;
    const chartH = height - (padY * 2);
    function priceToY(price) {
      return padY + chartH - ((price - minVal) / range) * chartH;
    }

    // 1. Draw Historical Separator line
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.4)';
    ctx.setLineDash([4, 4]);
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(startX, 10);
    ctx.lineTo(startX, height - 10);
    ctx.stroke();

    ctx.fillStyle = 'rgba(255, 255, 255, 0.7)';
    ctx.font = '10px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto';
    ctx.fillText('Forecast Boundary', startX - 100, 20);

    // 2. Draw prediction candlesticks
    ctx.setLineDash([]);
    for (let i = 0; i < predLen; i++) {
      let p = prediction[i];
      let x = startX + (i * candleWidth) + candleWidth/2;

      let yOpen = priceToY(p.open);
      let yClose = priceToY(p.close);
      let yHigh = priceToY(p.high);
      let yLow = priceToY(p.low);

      let isBull = p.close >= p.open;
      let color = isBull ? 'rgba(74, 222, 128, 0.85)' : 'rgba(248, 113, 113, 0.85)';
      ctx.strokeStyle = color;
      ctx.fillStyle = isBull ? 'rgba(74, 222, 128, 0.25)' : 'rgba(248, 113, 113, 0.25)';
      ctx.lineWidth = 1.2;

      // Draw wick
      ctx.beginPath();
      ctx.moveTo(x, yHigh);
      ctx.lineTo(x, yLow);
      ctx.stroke();

      // Draw body
      let yTop = Math.min(yOpen, yClose);
      let yBottom = Math.max(yOpen, yClose);
      let bodyH = Math.max(yBottom - yTop, 2);

      ctx.beginPath();
      ctx.rect(x - candleWidth/3, yTop, (candleWidth/3)*2, bodyH);
      ctx.fill();
      ctx.stroke();
    }

    // 3. Draw horizontal target bands (TP / SL / Entry)
    const yEntry = priceToY(entryPrice);
    const yTp = priceToY(takeProfit);
    const ySl = priceToY(stopLoss);

    // Entry Line
    ctx.strokeStyle = 'rgba(96, 165, 250, 0.5)'; // Blue
    ctx.lineWidth = 1;
    ctx.setLineDash([2, 2]);
    ctx.beginPath();
    ctx.moveTo(0, yEntry);
    ctx.lineTo(width, yEntry);
    ctx.stroke();
    ctx.fillStyle = '#60a5fa';
    ctx.fillText(`Kronos Entry: ${entryPrice.toFixed(2)}`, 20, yEntry - 4);

    // Take Profit Line
    ctx.strokeStyle = 'rgba(52, 211, 153, 0.5)'; // Green
    ctx.lineWidth = 1.2;
    ctx.setLineDash([5, 3]);
    ctx.beginPath();
    ctx.moveTo(0, yTp);
    ctx.lineTo(width, yTp);
    ctx.stroke();
    ctx.fillStyle = '#34d399';
    ctx.fillText(`Target Take-Profit (TP): ${takeProfit.toFixed(2)}`, 20, yTp - 4);

    // Stop Loss Line
    ctx.strokeStyle = 'rgba(248, 113, 113, 0.5)'; // Red
    ctx.lineWidth = 1.2;
    ctx.setLineDash([5, 3]);
    ctx.beginPath();
    ctx.moveTo(0, ySl);
    ctx.lineTo(width, ySl);
    ctx.stroke();
    ctx.fillStyle = '#f87171';
    ctx.fillText(`Trailing Stop-Loss (SL): ${stopLoss.toFixed(2)}`, 20, ySl - 4);

    // 4. Outlook indicator display HUD
    ctx.setLineDash([]);
    ctx.fillStyle = 'rgba(14, 18, 30, 0.85)';
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.08)';
    ctx.lineWidth = 1;

    // Draw status box in top left of chart area (compatible rounded rect)
    const boxW = 200;
    const boxH = 55;
    const bx = 15;
    const by = 40;
    const br = 8;
    ctx.beginPath();
    ctx.moveTo(bx + br, by);
    ctx.lineTo(bx + boxW - br, by);
    ctx.arcTo(bx + boxW, by, bx + boxW, by + br, br);
    ctx.lineTo(bx + boxW, by + boxH - br);
    ctx.arcTo(bx + boxW, by + boxH, bx + boxW - br, by + boxH, br);
    ctx.lineTo(bx + br, by + boxH);
    ctx.arcTo(bx, by + boxH, bx, by + boxH - br, br);
    ctx.lineTo(bx, by + br);
    ctx.arcTo(bx, by, bx + br, by, br);
    ctx.closePath();
    ctx.fill();
    ctx.stroke();

    ctx.fillStyle = '#fff';
    ctx.font = 'bold 11px sans-serif';
    ctx.fillText(`Kronos Forecast: ${signal}`, 25, 58);
    ctx.fillStyle = signal === 'BUY' ? '#34d399' : (signal === 'SELL' ? '#f87171' : '#9ca3af');
    ctx.font = '9px sans-serif';
    ctx.fillText(`Directional bias target calculated.`, 25, 75);
    ctx.fillStyle = '#71717a';
    ctx.fillText(`Mock Trading Mode Live.`, 25, 87);
  }
})();
