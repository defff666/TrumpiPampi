const chatId = new URLSearchParams(window.location.search).get('chat_id');

async function updateStats() {
    const response = await fetch(`/api/stats?chat_id=${chatId}`);
    const data = await response.json();
    document.getElementById('balance').innerText = `💰 ${data.balance} TRUMP`;
    document.getElementById('energy').innerText = `⚡ ${data.energy}/${data.max_energy}`;
}

async function tap() {
    const response = await fetch('/api/tap', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ chat_id: chatId })
    });
    const data = await response.json();
    document.getElementById('balance').innerText = `💰 ${data.balance} TRUMP`;
    document.getElementById('energy').innerText = `⚡ ${data.energy}/1000`;
}

window.Telegram.WebApp.ready();
updateStats();
setInterval(updateStats, 5000); // Обновление каждые 5 сек
