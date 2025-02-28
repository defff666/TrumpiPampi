const chatId = new URLSearchParams(window.location.search).get('chat_id');

// Загружаем или инициализируем локальные данные
let stats = JSON.parse(localStorage.getItem(`trumpiPampi_${chatId}`)) || {
    balance: 0,
    energy: 1000,
    max_energy: 1000,
    level: 1,
    multitap: 1,
    last_update: Date.now()
};

// Обновляем UI
function updateUI() {
    document.getElementById('balance').innerText = `💰 ${stats.balance} TRUMP`;
    document.getElementById('energy').innerText = `⚡ ${stats.energy}/${stats.max_energy}`;
    document.getElementById('level').innerText = `Level: ${stats.level}`;
    document.getElementById('multitap').innerText = `Multitap: x${stats.multitap}`;
}

// Восстановление энергии
function updateEnergy() {
    const now = Date.now();
    const elapsed = (now - stats.last_update) / 1000; // Время в секундах
    const recoveryRate = stats.level; // 1 энергия/сек на 1 уровне
    stats.energy = Math.min(stats.max_energy, stats.energy + Math.floor(elapsed * recoveryRate));
    stats.last_update = now;
    localStorage.setItem(`trumpiPampi_${chatId}`, JSON.stringify(stats));
    updateUI();
}

async function tap() {
    if (stats.energy >= stats.multitap) {
        stats.energy -= stats.multitap;
        stats.balance += stats.multitap;
        // Проверка уровня
        const newLevel = 1 + Math.floor(stats.balance / 1000);
        if (newLevel > stats.level) {
            stats.level = newLevel;
            stats.max_energy = 1000 * stats.level;
            stats.multitap = stats.level;
            console.log(`Leveled up to ${stats.level}, max_energy=${stats.max_energy}, multitap=${stats.multitap}`);
        }
        stats.last_update = Date.now();
        localStorage.setItem(`trumpiPampi_${chatId}`, JSON.stringify(stats));
        updateUI();
        console.log('Tap processed locally:', stats);
    } else {
        console.log('Not enough energy');
    }
}

async function syncWithServer() {
    try {
        console.log('Syncing with server for chat_id:', chatId);
        const response = await fetch('/api/sync', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ chat_id: chatId, ...stats })
        });
        if (!response.ok) throw new Error(`Sync failed: ${response.status}`);
        console.log('Sync successful');
    } catch (error) {
        console.error('Error syncing with server:', error);
    }
}

// Загрузка начальных данных с сервера
async function loadInitialStats() {
    try {
        console.log('Loading initial stats for chat_id:', chatId);
        const response = await fetch(`/api/stats?chat_id=${chatId}`);
        if (!response.ok) throw new Error(`Stats request failed: ${response.status}`);
        const serverStats = await response.json();
        stats = { ...stats, ...serverStats, last_update: Date.now() };
        localStorage.setItem(`trumpiPampi_${chatId}`, JSON.stringify(stats));
        updateUI();
    } catch (error) {
        console.error('Error loading initial stats:', error);
    }
}

window.Telegram.WebApp.ready();
console.log('Mini App initialized');

// Добавляем элементы для уровня и мультитапа
document.querySelector('.container').insertAdjacentHTML('beforeend', `
    <div id="level">Level: ${stats.level}</div>
    <div id="multitap">Multitap: x${stats.multitap}</div>
`);

// Синхронизация при закрытии
window.addEventListener('unload', syncWithServer);

// Инициализация и регулярное обновление
loadInitialStats();
updateUI();
setInterval(updateEnergy, 1000); // Восстановление энергии каждую секунду
setInterval(syncWithServer, 300000); // Синхронизация каждые 5 минут
