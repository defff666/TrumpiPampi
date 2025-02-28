const chatId = new URLSearchParams(window.location.search).get('chat_id');

// Предотвращаем дублирование окон
if (window.Telegram.WebApp.isExpanded) {
    window.Telegram.WebApp.close();  // Закрываем старое окно, если оно уже открыто
}

async function updateStats() {
    try {
        const response = await fetch(`/api/stats?chat_id=${chatId}`);
        console.log('Fetching stats for chat_id:', chatId);
        const data = await response.json();
        console.log('Stats response:', data);
        document.getElementById('balance').innerText = `💰 ${data.balance} TRUMP`;
        document.getElementById('energy').innerText = `⚡ ${data.energy}/${data.max_energy}`;
    } catch (error) {
        console.error('Error fetching stats:', error);
    }
}

async function tap() {
    try {
        console.log('Tap button clicked for chat_id:', chatId);
        const response = await fetch('/api/tap', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ chat_id: chatId })
        });
        const data = await response.json();
        console.log('Tap response:', data);
        document.getElementById('balance').innerText = `💰 ${data.balance} TRUMP`;
        document.getElementById('energy').innerText = `⚡ ${data.energy}/1000`;
    } catch (error) {
        console.error('Error tapping:', error);
    }
}

window.Telegram.WebApp.ready();
updateStats();
setInterval(updateStats, 5000);
