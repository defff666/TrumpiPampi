const chatId = new URLSearchParams(window.location.search).get('chat_id');

// Проверяем, запущено ли уже приложение ранее
let isFirstLaunch = localStorage.getItem('trumpiPampiFirstLaunch') === null;
if (!isFirstLaunch && window.Telegram.WebApp.isExpanded) {
    console.log('Closing duplicate Mini App instance');
    window.Telegram.WebApp.close();
} else {
    localStorage.setItem('trumpiPampiFirstLaunch', 'true');
    console.log('First launch detected, keeping Mini App open');
}

async function updateStats() {
    try {
        console.log('Fetching stats for chat_id:', chatId);
        const response = await fetch(`/api/stats?chat_id=${chatId}`);
        if (!response.ok) throw new Error(`Stats request failed: ${response.status}`);
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
        if (!response.ok) throw new Error(`Tap request failed: ${response.status}`);
        const data = await response.json();
        console.log('Tap response:', data);
        document.getElementById('balance').innerText = `💰 ${data.balance} TRUMP`;
        document.getElementById('energy').innerText = `⚡ ${data.energy}/1000`;
    } catch (error) {
        console.error('Error tapping:', error);
    }
}

window.Telegram.WebApp.ready();
console.log('Mini App initialized');
updateStats();
setInterval(updateStats, 5000);
