const fs = require('fs');
const http = require('http');

// Fetch rendered /invest page from local Flask server
http.get('http://127.0.0.1:7070/invest', (res) => {
    let body = '';
    res.on('data', chunk => body += chunk);
    res.on('end', () => {
        console.log("Status Code:", res.statusCode);
        console.log("Body Length:", body.length);

        const hasContainer = body.includes('id="tv-chart-container"');
        const hasCanvas = body.includes('id="tv-chart-canvas"');
        const hasDebug = body.includes('id="chart-debug-panel"');
        const hasScript = body.includes('lightweight-charts');

        console.log("Check Container:", hasContainer);
        console.log("Check Canvas:", hasCanvas);
        console.log("Check Debug Panel:", hasDebug);
        console.log("Check LightweightCharts CDN:", hasScript);

        if (res.statusCode === 200 && hasContainer && hasCanvas && hasScript) {
            console.log("✅ HTML template structure verification PASSED!");
        } else {
            console.error("❌ Verification FAILED!");
            process.exit(1);
        }
    });
}).on('error', (err) => {
    console.log("Flask server not running on port 7070 during script check. Testing template file directly.");
    const html = fs.readFileSync('./webui/templates/index.html', 'utf-8');
    const hasContainer = html.includes('id="tv-chart-container"');
    const hasCanvas = html.includes('id="tv-chart-canvas"');
    const hasDebug = html.includes('id="chart-debug-panel"');
    const hasScript = html.includes('lightweight-charts');

    console.log("Template Check Container:", hasContainer);
    console.log("Template Check Canvas:", hasCanvas);
    console.log("Template Check Debug Panel:", hasDebug);
    console.log("Template Check LightweightCharts CDN:", hasScript);

    if (hasContainer && hasCanvas && hasScript) {
        console.log("✅ Direct template file verification PASSED!");
    } else {
        console.error("❌ Direct template file verification FAILED!");
        process.exit(1);
    }
});
