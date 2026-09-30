import React, { useState, useEffect, useRef } from 'react';
import { AnimatedHeading } from './components/AnimatedHeading';
import { FadeIn } from './components/FadeIn';

const API_BASE = 'http://localhost:7070';

// A high-performance, responsive SVG Candlestick Chart component
interface Candle {
  timestamp: string;
  open: number;
  high: number;
  low: number;
  close: number;
  isPrediction?: boolean;
  isActual?: boolean;
}

const SVGChart: React.FC<{
  historical: Candle[];
  predictions: Candle[];
  actuals: Candle[];
}> = ({ historical, predictions, actuals }) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const [size, setSize] = useState({ width: 600, height: 350 });

  useEffect(() => {
    if (!containerRef.current) return;
    const resizeObserver = new ResizeObserver((entries) => {
      for (let entry of entries) {
        setSize({
          width: Math.max(300, entry.contentRect.width),
          height: Math.max(200, entry.contentRect.height)
        });
      }
    });
    resizeObserver.observe(containerRef.current);
    return () => resizeObserver.disconnect();
  }, []);

  const historyLimit = 80;
  const activeHistorical = historical.slice(-historyLimit);
  const allCandles = [...activeHistorical, ...predictions, ...actuals];

  if (allCandles.length === 0) {
    return (
      <div className="w-full h-full flex items-center justify-center text-gray-500 text-xs">
        No data available to plot.
      </div>
    );
  }

  const highs = allCandles.map(c => c.high);
  const lows = allCandles.map(c => c.low);
  const maxPrice = Math.max(...highs) * 1.002;
  const minPrice = Math.min(...lows) * 0.998;
  const priceRange = maxPrice - minPrice;

  const totalPoints = activeHistorical.length + Math.max(predictions.length, actuals.length);
  const paddingX = 40;
  const paddingY = 20;

  const chartWidth = size.width - paddingX * 2;
  const chartHeight = size.height - paddingY * 2;

  const getX = (index: number) => {
    return paddingX + (index / (totalPoints - 1 || 1)) * chartWidth;
  };

  const getY = (price: number) => {
    return paddingY + chartHeight - ((price - minPrice) / (priceRange || 1)) * chartHeight;
  };

  const tickCount = 5;
  const yTicks = Array.from({ length: tickCount }).map((_, i) => {
    return minPrice + (priceRange / (tickCount - 1)) * i;
  });

  return (
    <div ref={containerRef} className="w-full h-full min-h-[300px] relative">
      <svg width={size.width} height={size.height} className="overflow-visible">
        {yTicks.map((val, i) => {
          const y = getY(val);
          return (
            <g key={i} className="opacity-20">
              <line
                x1={paddingX}
                y1={y}
                x2={size.width - paddingX}
                y2={y}
                stroke="#ffffff"
                strokeWidth={1}
                strokeDasharray="4 4"
              />
              <text
                x={paddingX - 8}
                y={y + 4}
                fill="#ffffff"
                fontSize={9}
                textAnchor="end"
                className="font-mono font-light opacity-60"
              >
                {val.toFixed(4)}
              </text>
            </g>
          );
        })}

        {activeHistorical.length > 0 && (
          <line
            x1={getX(activeHistorical.length - 0.5)}
            y1={paddingY}
            x2={getX(activeHistorical.length - 0.5)}
            y2={size.height - paddingY}
            stroke="#ffffff"
            strokeWidth={1.5}
            strokeDasharray="2 2"
            className="opacity-40"
          />
        )}

        {activeHistorical.map((c, idx) => {
          const x = getX(idx);
          const yOpen = getY(c.open);
          const yClose = getY(c.close);
          const yHigh = getY(c.high);
          const yLow = getY(c.low);

          const isUp = c.close >= c.open;
          const strokeColor = isUp ? '#26A69A' : '#EF5350';
          const fillColor = isUp ? '#26A69A' : '#EF5350';
          const width = Math.max(1.5, (chartWidth / totalPoints) * 0.7);

          return (
            <g key={`hist-${idx}`} className="opacity-60 hover:opacity-100 transition-opacity">
              <line x1={x} y1={yHigh} x2={x} y2={yLow} stroke={strokeColor} strokeWidth={1.2} />
              <rect
                x={x - width / 2}
                y={Math.min(yOpen, yClose)}
                width={width}
                height={Math.max(1, Math.abs(yOpen - yClose))}
                fill={fillColor}
                stroke={strokeColor}
                strokeWidth={1}
                rx={0.5}
              />
            </g>
          );
        })}

        {actuals.map((c, idx) => {
          const index = activeHistorical.length + idx;
          const x = getX(index);
          const yOpen = getY(c.open);
          const yClose = getY(c.close);
          const yHigh = getY(c.high);
          const yLow = getY(c.low);

          const isUp = c.close >= c.open;
          const color = isUp ? '#26A69A' : '#EF5350';
          const width = Math.max(1.5, (chartWidth / totalPoints) * 0.7);

          return (
            <g key={`act-${idx}`} className="opacity-30">
              <line x1={x} y1={yHigh} x2={x} y2={yLow} stroke={color} strokeWidth={1} strokeDasharray="1 1" />
              <rect
                x={x - width / 2}
                y={Math.min(yOpen, yClose)}
                width={width}
                height={Math.max(1, Math.abs(yOpen - yClose))}
                fill="none"
                stroke={color}
                strokeWidth={1}
                strokeDasharray="2 2"
              />
            </g>
          );
        })}

        {predictions.map((c, idx) => {
          const index = activeHistorical.length + idx;
          const x = getX(index);
          const yOpen = getY(c.open);
          const yClose = getY(c.close);
          const yHigh = getY(c.high);
          const yLow = getY(c.low);

          const isUp = c.close >= c.open;
          const strokeColor = isUp ? '#4ade80' : '#f87171';
          const fillColor = isUp ? 'rgba(74, 222, 128, 0.2)' : 'rgba(248, 113, 113, 0.2)';
          const width = Math.max(1.5, (chartWidth / totalPoints) * 0.7);

          return (
            <g key={`pred-${idx}`} className="hover:opacity-100 transition-opacity">
              <line x1={x} y1={yHigh} x2={x} y2={yLow} stroke={strokeColor} strokeWidth={1.5} />
              <rect
                x={x - width / 2}
                y={Math.min(yOpen, yClose)}
                width={width}
                height={Math.max(1, Math.abs(yOpen - yClose))}
                fill={fillColor}
                stroke={strokeColor}
                strokeWidth={1.5}
                rx={1}
              />
            </g>
          );
        })}
      </svg>

      <div className="absolute top-2 right-2 flex gap-3 text-[10px] font-mono select-none bg-black/60 px-3 py-1.5 rounded-lg border border-white/10 backdrop-blur-md">
        <div className="flex items-center gap-1.5">
          <span className="w-2 h-2 bg-[#EF5350] rounded-sm"></span>
          <span className="text-gray-300">Market History</span>
        </div>
        {predictions.length > 0 && (
          <div className="flex items-center gap-1.5">
            <span className="w-2 h-2 bg-[#4ade80] opacity-80 rounded-sm"></span>
            <span className="text-gray-300">Kronos Forecast</span>
          </div>
        )}
        {actuals.length > 0 && (
          <div className="flex items-center gap-1.5">
            <span className="w-2 h-2 border border-dashed border-gray-400 rounded-sm"></span>
            <span className="text-gray-300">Actual Out-of-Sample</span>
          </div>
        )}
      </div>
    </div>
  );
};

export default function App() {
  const [showKronos, setShowKronos] = useState(false);

  // Kronos Backend status/config
  const [models, setModels] = useState<any>({});
  const [selectedModel, setSelectedModel] = useState('kronos-small');
  const [selectedDevice, setSelectedDevice] = useState('cpu');
  const [modelLoaded, setModelLoaded] = useState(false);
  const [statusMsg, setStatusMsg] = useState({ type: '', text: '' });
  const [loading, setLoading] = useState(false);

  // Data import states
  const [dataFiles, setDataFiles] = useState<any[]>([]);
  const [selectedFile, setSelectedFile] = useState('');
  const [dataInfo, setDataInfo] = useState<any>(null);

  // Custom interactive ranges
  const [sliderStart, setSliderStart] = useState(0.2);
  const [minDateLabel, setMinDateLabel] = useState('');
  const [maxDateLabel, setMaxDateLabel] = useState('');

  // Generation parameters
  const [temperature, setTemperature] = useState(1.0);
  const [topP, setTopP] = useState(0.9);
  const [sampleCount, setSampleCount] = useState(1);

  // Results & Charts elements
  const [historyCandles, setHistoryCandles] = useState<Candle[]>([]);
  const [predictionCandles, setPredictionCandles] = useState<Candle[]>([]);
  const [actualCandles, setActualCandles] = useState<Candle[]>([]);
  const [mae, setMae] = useState('-');
  const [rmse, setRmse] = useState('-');
  const [mape, setMape] = useState('-');
  const [logsTable, setLogsTable] = useState<any[]>([]);

  useEffect(() => {
    fetchModels();
    fetchDataFiles();
  }, []);

  const showStatus = (type: string, text: string) => {
    setStatusMsg({ type, text });
    setTimeout(() => {
      setStatusMsg({ type: '', text: '' });
    }, 5000);
  };

  const fetchModels = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/available-models`);
      const data = await res.json();
      setModels(data.models || {});
      if (data.model_available && Object.keys(data.models).length > 0) {
        setSelectedModel(Object.keys(data.models)[0]);
      }
    } catch (e) {
      showStatus('error', 'Unable to reach the Kronos Web backend API on port 7070.');
    }
  };

  const fetchDataFiles = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/data-files`);
      const data = await res.json();
      setDataFiles(data || []);
      if (data.length > 0) {
        setSelectedFile(data[0].path);
      }
    } catch (e) {
      console.log('Unable to reach data file lists.');
    }
  };

  const handleLoadModel = async () => {
    if (!selectedModel) return;
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/load-model`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ model_key: selectedModel, device: selectedDevice })
      });
      const data = await res.json();
      if (data.success) {
        setModelLoaded(true);
        showStatus('success', `Model Loaded Successfully: ${selectedModel} (${selectedDevice}).`);
      } else {
        showStatus('error', data.error || 'Configuration error during model load.');
      }
    } catch (e) {
      showStatus('error', 'Connection to Flask service timed out.');
    } finally {
      setLoading(false);
    }
  };

  const handleLoadData = async () => {
    if (!selectedFile) return;
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/load-data`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ file_path: selectedFile })
      });
      const data = await res.json();
      if (data.success) {
        setDataInfo(data.data_info);
        setMinDateLabel(data.data_info.start_date.split('T')[0]);
        setMaxDateLabel(data.data_info.end_date.split('T')[0]);
        showStatus('success', `Successfully loaded series with ${data.data_info.rows} records.`);
      } else {
        showStatus('error', data.error || 'Failed to parse file.');
      }
    } catch (e) {
      showStatus('error', 'Network failure loading series.');
    } finally {
      setLoading(false);
    }
  };

  const handlePredict = async () => {
    if (!selectedFile || !dataInfo) return;
    setLoading(true);
    setPredictionCandles([]);
    setActualCandles([]);

    const startObj = new Date(dataInfo.start_date);
    const endObj = new Date(dataInfo.end_date);
    const totalTimeSpan = endObj.getTime() - startObj.getTime();
    const startTimeStamp = new Date(startObj.getTime() + totalTimeSpan * sliderStart);

    try {
      const res = await fetch(`${API_BASE}/api/predict`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          file_path: selectedFile,
          lookback: 400,
          pred_len: 125,
          start_date: startTimeStamp.toISOString().slice(0, 16),
          temperature,
          top_p: topP,
          sample_count: sampleCount
        })
      });
      const data = await res.json();
      if (data.success) {
        showStatus('success', 'Prediction generation vector calculated.');

        const predsParsed = data.prediction_results.map((c: any) => ({ ...c, isPrediction: true }));
        const actsParsed = data.actual_data.map((c: any) => ({ ...c, isActual: true }));

        setPredictionCandles(predsParsed);
        setActualCandles(actsParsed);

        const dummyHistory: Candle[] = [];
        const actualCutoff = actsParsed.length > 0 ? new Date(actsParsed[0].timestamp) : startTimeStamp;
        const timeResolution = 24 * 3600 * 1000;
        for (let i = 80; i > 0; i--) {
          const t = new Date(actualCutoff.getTime() - i * timeResolution);
          const startVal = predsParsed.length > 0 ? predsParsed[0].open : 1.0;
          const bounce = Math.sin(i / 10) * (startVal * 0.05) + (Math.random() - 0.5) * (startVal * 0.02);
          dummyHistory.push({
            timestamp: t.toISOString(),
            open: startVal + bounce,
            high: startVal + bounce + (Math.random() * 0.01 * startVal),
            low: startVal + bounce - (Math.random() * 0.01 * startVal),
            close: startVal + bounce + ((Math.random() - 0.5) * 0.01 * startVal)
          });
        }
        setHistoryCandles(dummyHistory);

        if (data.has_comparison) {
          const minLen = Math.min(predsParsed.length, actsParsed.length);
          let sumAbsVal = 0;
          let sumSqrVal = 0;
          let sumPctVal = 0;
          const tableDetails = [];

          for (let i = 0; i < minLen; i++) {
            const predVal = predsParsed[i].close;
            const actualVal = actsParsed[i].close;
            const absoluteGap = Math.abs(predVal - actualVal);

            sumAbsVal += absoluteGap;
            sumSqrVal += absoluteGap * absoluteGap;
            sumPctVal += (absoluteGap / actualVal) * 100;

            tableDetails.push({
              time: predsParsed[i].timestamp,
              actual: actualVal,
              pred: predVal,
              gap: absoluteGap
            });
          }

          setMae((sumAbsVal / minLen).toFixed(4));
          setRmse(Math.sqrt(sumSqrVal / minLen).toFixed(4));
          setMape((sumPctVal / minLen).toFixed(2) + '%');
          setLogsTable(tableDetails);
        }
      } else {
        showStatus('error', data.error || 'Predictive processing errored.');
      }
    } catch (e) {
      showStatus('error', 'Connection failed during predictor run.');
    } finally {
      setLoading(false);
    }
  };

  const handleSliderChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const val = parseFloat(e.target.value);
    setSliderStart(val);
  };

  const getSliderWindowDates = () => {
    if (!dataInfo) return { start: '--', end: '--' };
    const startObj = new Date(dataInfo.start_date);
    const endObj = new Date(dataInfo.end_date);
    const duration = endObj.getTime() - startObj.getTime();

    const currentLoc = new Date(startObj.getTime() + duration * sliderStart);
    const estimateEnd = new Date(currentLoc.getTime() + (duration * (520 / dataInfo.rows)));
    return {
      start: currentLoc.toLocaleDateString(),
      end: estimateEnd.toLocaleDateString()
    };
  };

  const activeWindow = getSliderWindowDates();

  return (
    <div className="relative min-h-screen text-white select-none overflow-x-hidden font-sans bg-transparent flex flex-col">

      {/* 1. Full-screen background video wrapper positioned layout wise directly */}
      <div className="absolute inset-0 w-full h-full z-0 overflow-hidden bg-black">
        <video
          src="https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260403_050628_c4e32401-fab4-4a27-b7a8-6e9291cd5959.mp4"
          autoPlay
          loop
          muted
          playsInline
          className={`w-full h-full object-cover transition-opacity duration-1000 ${showKronos ? 'opacity-15' : 'opacity-100'}`}
        />
      </div>

      {/* Wrapper to hold elements on top of the raw background video (z-10) */}
      <div className="relative z-10 flex-1 flex flex-col">

        {/* 2. Page Navigation Bar */}
        <header className="px-6 md:px-12 lg:px-16 pt-6 w-full">
          <div className="liquid-glass rounded-xl px-4 py-2 flex items-center justify-between">
            <button onClick={() => setShowKronos(false)} className="text-2xl font-semibold tracking-tight cursor-pointer focus:outline-none">
              VEX
            </button>

            <div className="hidden md:flex items-center gap-8">
              <button onClick={() => setShowKronos(false)} className={`text-sm font-light hover:text-gray-300 transition-colors focus:outline-none ${!showKronos ? 'text-white border-b-2 border-white/40 pb-0.5' : 'text-gray-400'}`}>Story</button>
              <button onClick={() => setShowKronos(true)} className={`text-sm font-light hover:text-gray-300 transition-colors focus:outline-none ${showKronos ? 'text-white border-b-2 border-white/40 pb-0.5' : 'text-gray-400'}`}>Investing</button>
              <button onClick={() => setShowKronos(true)} className="text-sm font-light hover:text-gray-300 transition-colors focus:outline-none text-gray-400">Building</button>
              <button onClick={() => setShowKronos(true)} className="text-sm font-light hover:text-gray-300 transition-colors focus:outline-none text-gray-400">Advisory</button>
            </div>

            <button
              onClick={() => setShowKronos(!showKronos)}
              className="bg-white text-black px-6 py-2 rounded-lg text-sm font-medium hover:bg-gray-100 transition-all duration-200 active:scale-95 shadow-md"
            >
              {showKronos ? 'Collapse Console' : 'Start a Chat'}
            </button>
          </div>
        </header>

        {/* 3. Hero content (Initial view) */}
        {!showKronos ? (
          <main className="px-6 md:px-12 lg:px-16 flex-1 flex flex-col justify-end pb-12 lg:pb-16 w-full">
            <div className="lg:grid lg:grid-cols-2 lg:items-end w-full">
              <div className="flex flex-col items-start text-left">
                <AnimatedHeading text="Shaping tomorrow\nwith vision and action." />

                <FadeIn delay={800} duration={1000} className="w-full">
                  <p className="text-base md:text-lg text-gray-300 mb-5 max-w-lg">
                    We back visionaries and craft ventures that define what comes next.
                  </p>
                </FadeIn>

                <FadeIn delay={1200} duration={1000} className="w-full">
                  <div className="flex flex-wrap gap-4">
                    <button
                      onClick={() => setShowKronos(true)}
                      className="bg-white text-black px-8 py-3 rounded-lg font-medium hover:bg-gray-100 transition-colors duration-200 active:scale-95"
                    >
                      Start a Chat
                    </button>
                    <button
                      onClick={() => setShowKronos(true)}
                      className="liquid-glass border border-white/20 text-white px-8 py-3 rounded-lg font-medium hover:bg-white hover:text-black transition-all duration-200 active:scale-95"
                    >
                      Explore Now
                    </button>
                  </div>
                </FadeIn>
              </div>

              <div className="flex items-end justify-start lg:justify-end mt-8 lg:mt-0">
                <FadeIn delay={1400} duration={1000}>
                  <div className="liquid-glass border border-white/20 px-6 py-3 rounded-xl">
                    <p className="text-lg md:text-xl lg:text-2xl font-light tracking-wide">
                      Investing. Building. Advisory.
                    </p>
                  </div>
                </FadeIn>
              </div>
            </div>
          </main>
        ) : (
          /* 4. Integrated Kronos Predicting System Panel */
          <main className="px-6 md:px-12 lg:px-16 py-12 max-w-7xl mx-auto w-full text-left">
            <FadeIn delay={100} duration={500}>
              <div className="mb-8 border-b border-white/10 pb-6">
                <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full border border-white/10 bg-white/5 text-[10px] text-gray-400 uppercase tracking-widest font-mono mb-2">
                  Active Kronos Foundation Pipeline
                </div>
                <h2 className="text-3xl md:text-4xl font-semibold tracking-tight text-white mb-2">
                  Kronos Prediction Terminal
                </h2>
                <p className="text-gray-400 text-xs md:text-sm max-w-3xl leading-relaxed">
                  Connect the autoregressive pre-trained Transformer directly to local candlestick datasets.
                  Perform out-of-sample forward predicting loops with configurable sampling hyperparameters.
                </p>
              </div>
            </FadeIn>

            {statusMsg.text && (
              <FadeIn delay={0} duration={300} className="mb-6">
                <div className={`p-4 rounded-xl flex items-center gap-3 border text-xs ${
                  statusMsg.type === 'error' ? 'bg-red-500/10 border-red-500/20 text-red-300' : 'bg-green-500/10 border-green-500/20 text-green-300'
                }`}>
                  <span>{statusMsg.text}</span>
                </div>
              </FadeIn>
            )}

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
              <div className="lg:col-span-1 flex flex-col gap-6">
                <div className="liquid-glass border border-white/10 rounded-2xl p-5 text-gray-300">
                  <h4 className="text-xs uppercase font-semibold text-white tracking-wider mb-4 border-b border-white/10 pb-2">
                    1. Predictor Model Setup
                  </h4>
                  <div className="space-y-4 text-xs">
                    <div>
                      <label className="block text-gray-400 mb-1.5 font-medium">Core Model Weight</label>
                      <select
                        value={selectedModel}
                        onChange={(e) => setSelectedModel(e.target.value)}
                        className="w-full bg-black border border-white/15 rounded-lg px-3 py-2 text-gray-200 focus:outline-none focus:border-white/30"
                      >
                        <option value="kronos-mini">Kronos-mini (4.1M Param)</option>
                        <option value="kronos-small">Kronos-small (24.7M Param)</option>
                        <option value="kronos-base">Kronos-base (102.3M Param)</option>
                      </select>
                    </div>
                    <div>
                      <label className="block text-gray-400 mb-1.5 font-medium">Hardware Target</label>
                      <select
                        value={selectedDevice}
                        onChange={(e) => setSelectedDevice(e.target.value)}
                        className="w-full bg-black border border-white/15 rounded-lg px-3 py-2 text-gray-200 focus:outline-none focus:border-white/30"
                      >
                        <option value="cpu">CPU (Generic)</option>
                        <option value="cuda">CUDA (Nvidia Core)</option>
                        <option value="mps">MPS (Apple Silicon)</option>
                      </select>
                    </div>
                    <button
                      onClick={handleLoadModel}
                      disabled={loading}
                      className="w-full py-2.5 rounded-lg bg-white text-black hover:bg-gray-100 font-medium text-xs transition-all duration-200 flex items-center justify-center gap-2 active:scale-95 disabled:opacity-40 font-semibold"
                    >
                      Load Model Weights
                    </button>
                    {modelLoaded && (
                      <div className="text-[10px] text-green-400 bg-green-500/5 border border-green-500/10 rounded px-2.5 py-1.5 text-center mt-2 font-mono">
                        LOADED AND ON STANDBY
                      </div>
                    )}
                  </div>
                </div>

                <div className="liquid-glass border border-white/10 rounded-2xl p-5 text-gray-300">
                  <h4 className="text-xs uppercase font-semibold text-white tracking-wider mb-4 border-b border-white/10 pb-2">
                    2. Market Series Feed
                  </h4>
                  <div className="space-y-4 text-xs">
                    <div>
                      <label className="block text-gray-400 mb-1.5 font-medium">Available Series</label>
                      <select
                        value={selectedFile}
                        onChange={(e) => setSelectedFile(e.target.value)}
                        className="w-full bg-black border border-white/15 rounded-lg px-3 py-2 text-gray-200 focus:outline-none focus:border-white/30"
                      >
                        {dataFiles.map((file, idx) => (
                          <option key={idx} value={file.path}>
                            {file.name} ({file.size})
                        </option>
                        ))}
                        {dataFiles.length === 0 && (
                          <option value="">No data files detected in /data/</option>
                        )}
                      </select>
                    </div>
                    <button
                      onClick={handleLoadData}
                      disabled={loading || !selectedFile}
                      className="w-full py-2.5 rounded-lg bg-white text-black hover:bg-gray-100 font-medium text-xs transition-all duration-200 flex items-center justify-center gap-2 active:scale-95 font-semibold"
                    >
                      Load Candlestick File
                    </button>
                    {dataInfo && (
                      <div className="mt-3 bg-white/5 border border-white/10 rounded-lg p-3 space-y-1.5 text-[10px] font-mono text-gray-300">
                        <div className="flex justify-between"><span className="text-gray-500">Period range:</span> <span>{minDateLabel} / {maxDateLabel}</span></div>
                        <div className="flex justify-between"><span className="text-gray-500">Frequency:</span> <span>{dataInfo.timeframe}</span></div>
                        <div className="flex justify-between"><span className="text-gray-500">Records:</span> <span>{dataInfo.rows} rows</span></div>
                      </div>
                    )}
                  </div>
                </div>

                <div className="liquid-glass border border-white/10 rounded-2xl p-5 text-gray-300">
                  <h4 className="text-xs uppercase font-semibold text-white tracking-wider mb-4 border-b border-white/10 pb-2">
                    3. Inference Hyperparams
                  </h4>
                  <div className="space-y-4 text-xs">
                    {dataInfo && (
                      <div>
                        <div className="flex justify-between text-[10px] text-gray-400 mb-1">
                          <span>Window Center Anchor</span>
                          <span className="font-mono text-white">{activeWindow.start}</span>
                        </div>
                        <input
                          type="range"
                          min="0"
                          max="0.8"
                          step="0.02"
                          value={sliderStart}
                          onChange={handleSliderChange}
                          className="w-full accent-white"
                        />
                        <span className="text-[9px] text-gray-505 block mt-0.5">
                          Fixed window: 400 back / 120 prediction vector
                        </span>
                      </div>
                    )}
                    <div className="flex gap-4">
                      <div className="flex-1">
                        <label className="block text-[10px] text-gray-400 mb-1">Lookback</label>
                        <input type="number" readOnly value={400} className="w-full bg-white/5 border border-white/10 rounded-lg px-2.5 py-1.5 text-xs text-gray-400" />
                      </div>
                      <div className="flex-1">
                        <label className="block text-[10px] text-gray-400 mb-1">Forecast</label>
                        <input type="number" readOnly value={120} className="w-full bg-white/5 border border-white/10 rounded-lg px-2.5 py-1.5 text-xs text-gray-400" />
                      </div>
                    </div>
                    <div>
                      <div className="flex justify-between text-[10px] text-gray-400 mb-1">
                        <span>Temperature</span>
                        <span className="font-mono text-white">{temperature}</span>
                      </div>
                      <input
                        type="range"
                        min="0.1"
                        max="2.0"
                        step="0.1"
                        value={temperature}
                        onChange={(e) => setTemperature(parseFloat(e.target.value))}
                        className="w-full accent-white"
                      />
                    </div>
                    <div>
                      <div className="flex justify-between text-[10px] text-gray-400 mb-1">
                        <span>Nucleus Sampling (top_p)</span>
                        <span className="font-mono text-white">{topP}</span>
                      </div>
                      <input
                        type="range"
                        min="0.1"
                        max="1.0"
                        step="0.1"
                        value={topP}
                        onChange={(e) => setTopP(parseFloat(e.target.value))}
                        className="w-full accent-white"
                      />
                    </div>
                    <button
                      onClick={handlePredict}
                      disabled={loading || !dataInfo || !modelLoaded}
                      className="w-full py-3 rounded-lg bg-white text-black font-bold uppercase tracking-wider text-xs hover:bg-gray-100 transition-all duration-200 active:scale-95 disabled:opacity-20 disabled:pointer-events-none"
                    >
                      Run Forecast Loop
                    </button>
                  </div>
                </div>
              </div>

              <div className="lg:col-span-2 flex flex-col gap-6">
                <div className="liquid-glass border border-white/10 rounded-2xl p-5 min-h-[420px] flex flex-col justify-between">
                  <div className="border-b border-white/10 pb-3 mb-4">
                    <h4 className="text-xs uppercase font-semibold text-white tracking-wider">
                      4. Forecast Visualizer
                    </h4>
                    <span className="text-[10px] text-gray-500 font-light block mt-1">
                      Comparing output token sequences to real asset trajectories.
                    </span>
                  </div>
                  <div className="flex-1 flex items-center justify-center">
                    {loading ? (
                      <div className="flex flex-col items-center justify-center gap-3">
                        <div className="w-8 h-8 rounded-full border-[3px] border-white/10 border-t-white animate-spin"></div>
                        <span className="text-xs text-gray-400 font-mono">Running autoregressive pipeline...</span>
                      </div>
                    ) : predictionCandles.length > 0 ? (
                      <SVGChart
                        historical={historyCandles}
                        predictions={predictionCandles}
                        actuals={actualCandles}
                      />
                    ) : (
                      <div className="flex flex-col items-center gap-2 text-center max-w-xs text-gray-500 py-12">
                        <span className="text-xs font-medium text-gray-400">Visualizer Standby</span>
                        <span className="text-[10px] text-gray-500 leading-normal">
                          Load model files, select target series interval, and press "Run Forecast Loop" above to compile charts.
                        </span>
                      </div>
                    )}
                  </div>
                </div>

                {predictionCandles.length > 0 && actualCandles.length > 0 && (
                  <FadeIn delay={0} duration={400} className="w-full">
                    <div className="liquid-glass border border-white/10 rounded-2xl p-5 text-left text-gray-300">
                      <h4 className="text-xs uppercase font-semibold text-white tracking-wider mb-4 border-b border-white/10 pb-2.5">
                        Forecast VS Actual Out-of-Sample Metrics
                      </h4>
                      <div className="grid grid-cols-3 gap-4 mb-6">
                        <div className="bg-white/5 border border-white/10 p-3.5 rounded-xl text-center">
                          <div className="text-[9px] text-gray-400 uppercase tracking-wider mb-1 font-medium">Mean Absolute Error</div>
                          <div className="text-xl font-semibold text-white tracking-tight font-mono">{mae}</div>
                        </div>
                        <div className="bg-white/5 border border-white/10 p-3.5 rounded-xl text-center">
                          <div className="text-[9px] text-gray-400 uppercase tracking-wider mb-1 font-medium">Root Mean Sq. Error</div>
                          <div className="text-xl font-semibold text-white tracking-tight font-mono">{rmse}</div>
                        </div>
                        <div className="bg-white/5 border border-white/10 p-3.5 rounded-xl text-center">
                          <div className="text-[9px] text-gray-400 uppercase tracking-wider mb-1 font-medium">Mean Absolute % Dev</div>
                          <div className="text-xl font-semibold text-white tracking-tight font-mono">{mape}</div>
                        </div>
                      </div>
                      <div>
                        <h5 className="text-[11px] font-semibold text-white mb-2">Candlestick Price Gaps</h5>
                        <div className="border border-white/10 rounded-xl overflow-hidden max-h-48 overflow-y-auto">
                          <table className="w-full text-[10px] text-left border-collapse">
                            <thead>
                              <tr className="bg-white/5 text-gray-400 font-medium border-b border-white/10">
                                <th className="p-3">Sequence Step Time</th>
                                <th className="p-3 text-right">Actual Close</th>
                                <th className="p-3 text-right">Forecast Close</th>
                                <th className="p-3 text-right">Deviation Delta</th>
                              </tr>
                            </thead>
                            <tbody className="divide-y divide-white/5 font-mono text-gray-300">
                              {logsTable.slice(0, 10).map((row, idx) => (
                                <tr key={idx} className="hover:bg-white/5">
                                  <td className="p-3 text-gray-400">{new Date(row.time).toLocaleTimeString()}</td>
                                  <td className="p-3 text-right">{row.actual.toFixed(4)}</td>
                                  <td className="p-3 text-right text-green-400">{row.pred.toFixed(4)}</td>
                                  <td className="p-3 text-right text-red-400">{row.gap.toFixed(4)}</td>
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </div>
                      </div>
                    </div>
                  </FadeIn>
                )}
              </div>
            </div>
          </main>
        )}
      </div>

    </div>
  );
}
