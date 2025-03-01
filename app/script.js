const chatId = new URLSearchParams(window.location.search).get('chat_id');
if (!chatId) console.error('chat_id is missing');

// Модель состояния
class GameState {
    constructor(chatId) {
        this.chatId = chatId;
        this.loadState();
    }

    loadState() {
        const saved = localStorage.getItem(`trumpiPampi_${this.chatId}`);
        const defaults = { balance: 0, energy: 1000, max_energy: 1000, level: 1, multitap: 1, last_update: Date.now() };
        this.state = saved ? JSON.parse(saved) : defaults;
        this.updateEnergy(); // Восстановление энергии при загрузке
        console.log('Loaded state:', this.state);
    }

    saveState() {
        localStorage.setItem(`trumpiPampi_${this.chatId}`, JSON.stringify(this.state));
    }

    updateEnergy() {
        const now = Date.now();
        const elapsed = (now - this.state.last_update) / 1000; // Время в секундах
        const recoveryRate = this.state.level; // 1 энергия/сек на 1 уровне
        this.state.energy = Math.min(this.state.max_energy, this.state.energy + Math.floor(elapsed * recoveryRate));
        this.state.last_update = now;
        this.saveState();
    }

    tap() {
        if (this.state.energy >= this.state.multitap) {
            this.state.energy -= this.state.multitap;
            this.state.balance += this.state.multitap;
            const newLevel = 1 + Math.floor(this.state.balance / 1000);
            if (newLevel > this.state.level) {
                this.state.level = newLevel;
                this.state.max_energy = 1000 * this.state.level;
                this.state.multitap = this.state.level;
                console.log(`Leveled up to ${this.state.level}`);
            }
            this.state.last_update = Date.now();
            this.saveState();
            console.log('Tap processed:', this.state);
            return true;
        }
        console.log('Not enough energy');
        return false;
    }

    getState() {
        this.updateEnergy();
        return { ...this.state };
    }
}

// Управление UI
class UIController {
    constructor(gameState) {
        this.gameState = gameState;
        this.elements = {
            balance: document.getElementById('balance'),
            energy: document.getElementById('energy'),
            level: document.getElementById('level'),
            multitap: document.getElementById('multitap')
        };
    }

    update() {
        const state = this.gameState.getState();
        this.elements.balance.textContent = `💰 ${state.balance} TRUMP`;
        this.elements.energy.textContent = `⚡ ${state.energy}/${state.max_energy}`;
        this.elements.level.textContent = `Level: ${state.level}`;
        this.elements.multitap.textContent = `Multitap: x${state.multitap}`;
    }
}

// Инициализация
const game = new GameState(chatId);
const ui = new UIController(game);

// Загрузка начальных данных с сервера
async function loadInitialStats() {
    try {
        const response = await fetch(`/api/stats?chat_id=${chatId}`);
        if (!response.ok) throw new Error(`Stats fetch failed: ${response.status}`);
        const serverStats = await response.json();
        const localStats = game.getState();
        // Берём максимум из локального и серверного состояния
        game.state.balance = Math.max(localStats.balance, serverStats.balance);
        game.state.energy = Math.max(localStats.energy, serverStats.energy);
        game.state.max_energy = Math.max(localStats.max_energy, serverStats.max_energy);
        game.state.level = Math.max(localStats.level, serverStats.level);
        game.state.multitap = Math.max(localStats.multitap, serverStats.multitap);
        game.state.last_update = Date.now();
        game.saveState();
        ui.update();
        console.log('Initial stats synced from server:', serverStats);
    } catch (error) {
        console.error('Error loading initial stats:', error);
        ui.update(); // Используем локальные данные, если сервер недоступен
    }
}

// Синхронизация с сервером
async function syncWithServer() {
    try {
        const state = game.getState();
        const response = await fetch('/api/sync', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ chat_id: chatId, ...state })
        });
        if (!response.ok) throw new Error(`Sync failed: ${response.status}`);
        console.log('Sync successful');
    } catch (error) {
        console.error('Sync error:', error);
    }
}

// Обработчики событий
document.getElementById('tap-btn').addEventListener('click', () => {
    if (game.tap()) ui.update();
});

window.addEventListener('unload', syncWithServer);
window.Telegram.WebApp.ready();

// Инициализация и обновление
loadInitialStats();
ui.update();
setInterval(() => {
    game.updateEnergy();
    ui.update();
}, 1000); // Обновление энергии каждую секунду
setInterval(syncWithServer, 300000); // Синхронизация каждые 5 минут
