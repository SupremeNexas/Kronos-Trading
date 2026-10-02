import axios from "axios";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:7070";

const api = axios.create({
  baseURL: API_BASE,
  timeout: 30000,
  headers: { "Content-Type": "application/json" },
});

// Health
export const getHealth = () => api.get("/health");

// Auth
export const login = (email: string, password: string) =>
  api.post("/api/auth/login", { email, password });

export const register = (email: string, password: string, name: string) =>
  api.post("/api/auth/register", { email, password, name });

export const loginDemo = () => api.post("/api/auth/demo");

export const getMe = (userId: string) =>
  api.get(`/api/auth/me?user_id=${userId}`);

// Market
export const getMarketOverview = () => api.get("/api/market/overview");
export const getMarketTrending = () => api.get("/api/market/trending");
export const getMarketQuote = (symbol: string) =>
  api.get(`/api/market/quote?symbol=${symbol}`);
export const getMarketBars = (symbol: string, timeframe = "1d", limit = 300) =>
  api.get(`/api/market/bars?symbol=${symbol}&timeframe=${timeframe}&limit=${limit}`);
export const searchSymbols = (q: string) =>
  api.get(`/api/market/search?q=${q}`);

// Forecast
export const getForecast = (symbol: string, interval = "1d", horizon = 20) =>
  api.post("/api/forecast", { symbol, interval, horizon });

// Backtest
export const runBacktest = (symbol: string, timeframe = "1d", horizon = 10) =>
  api.post("/api/backtest", { symbol, timeframe, horizon });

// Research
export const runResearch = (symbol: string) =>
  api.post("/api/research/run", { symbol });
export const getLatestResearch = (symbol: string) =>
  api.get(`/api/research/latest?symbol=${symbol}`);

// News
export const getNewsFeed = () => api.get("/api/news/feed");

// Watchlist
export const getWatchlists = (userId: string) =>
  api.get(`/api/watchlist?user_id=${userId}`);
export const addWatchlistItem = (userId: string, symbol: string, name?: string) =>
  api.post("/api/watchlist", { user_id: userId, symbol, name });
export const removeWatchlistItem = (userId: string, symbol: string) =>
  api.delete("/api/watchlist", { data: { user_id: userId, symbol } });

// Alerts
export const getAlerts = (userId: string) =>
  api.get(`/api/alerts?user_id=${userId}`);
export const createAlert = (
  userId: string,
  symbol: string,
  alertType: string,
  targetPrice: number,
  condition: string
) =>
  api.post("/api/alerts", {
    user_id: userId,
    symbol,
    alert_type: alertType,
    target_price: targetPrice,
    condition,
  });
export const deleteAlert = (userId: string, alertId: string) =>
  api.delete("/api/alerts", { data: { user_id: userId, alert_id: alertId } });

// Portfolio
export const getPortfolio = () => api.get("/api/portfolio");

// Trading
export const getTradingAccount = () => api.get("/api/trading/account");
export const getTradingPositions = () => api.get("/api/trading/positions");
export const placeOrder = (order: {
  symbol: string;
  side: string;
  quantity: number;
  order_type: string;
  price: number;
}) => api.post("/api/trading/place-order", order);

// Model
export const getModelStatus = () => api.get("/api/model-status");
export const getAvailableModels = () => api.get("/api/available-models");

export default api;
