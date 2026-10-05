import re

with open("frontend/app/terminal/page.tsx", "r") as f:
    content = f.read()

# We want to replace the payload of the axios.post call in handlePlaceOrder
old_post = """const res = await axios.post('/api/trading/place-order', {
        symbol,
        side,
        quantity,
        order_type: orderType,
        price: orderType === 'Limit' ? limitPrice : 0,
        analysis_id: forecast?.analysis_id
      });"""

new_post = """const payload = {
        symbol,
        side,
        quantity,
        order_type: orderType,
        price: orderType === 'Limit' ? limitPrice : 0,
        analysis_id: forecast?.analysis_id,
        strategy: strategyParam || undefined,
        signal_scan_id: scanIdParam || undefined,
        signal_score: scoreParam || undefined,
        volume_ratio: volParam || undefined,
        attention_score: attentionParam || undefined,
        momentum_7d: momentumParam || undefined,
        decision: strategyParam ? "MANUAL_TRADE" : undefined
      };
      const res = await axios.post('/api/trading/place-order', payload);"""

content = content.replace(old_post, new_post)
with open("frontend/app/terminal/page.tsx", "w") as f:
    f.write(content)
print("Updated handlePlaceOrder.")
