const chatId = new URLSearchParams(window.location.search).get('chat_id');

// Предотвращаем дубли через уникальный ключ сессии
const sessionKey = `trumpiPampiSession_${chatId}`;
const isActiveSession = localStorage.getItem(sessionKey);
if (isActiveSession && window.Telegram.WebApp.isExpanded) {
    console.log('Closing duplicate Mini App instance');
    window.Telegram.WebApp.close();
} else {
    localStorage.setItem(sessionKey, 'active');
    console.log('New session started for chat_id:', chatId);
}

// Очищаем сессию при закрытии
window.addEventListener('unload', () => {
    localStorage.removeItem(sessionKey);
});

async function updateStats() {
    try {
        console.log('Fetching stats for chat_id:', chatId);
        const response = await fetch(`/api/stats?chat_id=${chatId}`);
        if (!response.ok) throw new Error(`Stats request failed: ${response.status}`);
        const data = await response.json();
        console.log('Stats response:', data);
        document.getElementById('balance').innerText = `💰 ${data.balance} TRUMP`;
        document.getElementById('energy').innerText = `⚡ ${data.energy}/${data.max_energy}`;
        document.getElementById('level').innerText = `Level: ${data.level}`;
        document.getElementById('multitap').innerText = `Multitap: x${data.multitap}`;
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
        document.getElementById('energy').innerText = `⚡ ${data.energy}/1000`;  // Временный показ до updateStats
        updateStats();  // Обновляем сразу
    } catch (error) {
        console.error('Error tapping:', error);
    }
}

window.Telegram.WebApp.ready();
console.log('Mini App initialized');

// Добавляем элементы для уровня и мультитапа
document.querySelector('.container').insertAdjacentHTML('beforeend', `
    <div id="level">Level: 1</div>
    <div id="multitap">Multitap: x1</div>
`);

updateStats();
setInterval(updateStats, 1000);  // Ускорим до 1 сек для плавного восстановления энергии
