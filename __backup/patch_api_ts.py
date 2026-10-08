with open("frontend/lib/api.ts", "r") as f:
    text = f.read()

import re

# Add withCredentials: true
if "withCredentials: true" not in text:
    text = text.replace(
        '  headers: { "Content-Type": "application/json" },',
        '  headers: { "Content-Type": "application/json" },\n  withCredentials: true,'
    )

# Remove user_id from all methods
text = re.sub(r'export const getMe = \(.*?\) =>\n\s*api\.get\(`\/api\/auth\/me\?.*?`\);',
              r'export const getMe = () =>\n  api.get(`/api/auth/me`);', text)

text = re.sub(r'export const getWatchlists = \(.*?\) =>\n\s*api\.get\(`\/api\/watchlist\?.*?`\);',
              r'export const getWatchlists = () =>\n  api.get(`/api/watchlist`);', text)

text = re.sub(r'export const addWatchlistItem = \(.*?\) =>\n\s*api\.post\("\/api\/watchlist", \{.*?symbol, name.*?\}\);',
              r'export const addWatchlistItem = (symbol: string, name?: string) =>\n  api.post("/api/watchlist", { symbol, name });', text, flags=re.DOTALL)

text = re.sub(r'export const removeWatchlistItem = \(.*?\) =>\n\s*api\.delete\("\/api\/watchlist", \{ data: \{.*?\} \}\);',
              r'export const removeWatchlistItem = (symbol: string) =>\n  api.delete("/api/watchlist", { data: { symbol } });', text, flags=re.DOTALL)

text = re.sub(r'export const getAlerts = \(.*?\) =>\n\s*api\.get\(`\/api\/alerts\?.*?`\);',
              r'export const getAlerts = () =>\n  api.get(`/api/alerts`);', text)

# createAlert
create_alert_old = r'export const createAlert = \([\s\S]*?\) =>\n\s*api\.post\("\/api\/alerts", \{[\s\S]*?\}\);'
create_alert_new = """export const createAlert = (
  symbol: string,
  alertType: string,
  targetPrice: number,
  condition: string
) =>
  api.post("/api/alerts", {
    symbol,
    alert_type: alertType,
    target_price: targetPrice,
    condition,
  });"""
text = re.sub(create_alert_old, create_alert_new, text)

# deleteAlert
delete_alert_old = r'export const deleteAlert = \(.*?\) =>\n\s*api\.delete\("\/api\/alerts", \{ data: \{.*?\} \}\);'
delete_alert_new = 'export const deleteAlert = (alertId: string) =>\n  api.delete("/api/alerts", { data: { alert_id: alertId } });'
text = re.sub(delete_alert_old, delete_alert_new, text)

with open("frontend/lib/api.ts", "w") as f:
    f.write(text)
