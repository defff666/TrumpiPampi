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
        const defaults = { balance: 0, energy: 1000, max_energy: 1000, level: 1, multitap: 1, last_update: Date.now() / 1000 };
        this.state = saved ? JSON.parse(saved) : defaults;
        this.updateEnergy();
        console.log('Loaded state:', this.state);
    }

    saveState() {
        localStorage.setItem(`trumpiPampi_${this.chatId}`, JSON.stringify(this.state));
    }

    updateEnergy() {
        const now = Date.now() / 1000;
        const elapsed = Math.max(0, now - this.state.last_update);
        const recoveryRate = this.state.level;
        const recoveredEnergy = Math.floor(elapsed * recoveryRate);
        this.state.energy = Math.min(this.state.max_energy, this.state.energy + recoveredEnergy);
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
            this.state.last_update = Date.now() / 1000;
            this.saveState();
            return true;
        }
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
            multitap: document.getElementById('multitap'),
            main: document.getElementById('main-screen'),
            settings: document.getElementById('settings-screen'),
            tasks: document.getElementById('tasks-screen'),
            referrals: document.getElementById('referrals-screen')
        };
        this.currentScreen = 'main';
    }

    showScreen(screen) {
        Object.values(this.elements).forEach(el => el.style.display = 'none');
        this.elements[screen].style.display = 'block';
        this.currentScreen = screen;
        this.update();
    }

    update() {
        const state = this.gameState.getState();
        this.elements.balance.textContent = `💰 ${state.balance} TRUMP`;
        this.elements.energy.textContent = `⚡ ${state.energy}/${state.max_energy}`;
        this.elements.level.textContent = `Level: ${state.level}`;
        this.elements.multitap.textContent = `Multitap: x${state.multitap}`;
        if (this.currentScreen === 'settings') this.updateSettings();
        if (this.currentScreen === 'tasks') this.updateTasks();
        if (this.currentScreen === 'referrals') this.updateReferrals();
    }

    updateSettings() {
        const state = this.gameState.getState();
        this.elements.settings.innerHTML = `
            <h2>Settings</h2>
            <p>Balance: ${state.balance} TRUMP</p>
            <p>Energy: ${state.energy}/${state.max_energy}</p>
            <p>Level: ${state.level}</p>
            <p>Multitap: x${state.multitap}</p>
            <button onclick="ui.showScreen('main')">Back</button>
        `;
    }

    updateTasks() {
        fetch(`/api/tasks?chat_id=${chatId}`)
            .then(response => response.json())
            .then(data => {
                this.elements.tasks.innerHTML = `
                    <h2>Daily Tasks</h2>
                    <ul>${data.tasks.map(task => `
                        <li>${task.description} - ${task.reward} TRUMP
                            ${task.completed ? '(Completed)' : `<button onclick="completeTask(${task.id})">Complete</button>`}
                        </li>`).join('')}
                    </ul>
                    <button onclick="ui.showScreen('main')">Back</button>
                `;
            });
    }

    updateReferrals() {
        const referralLink = `https://t.me/TrumpiPampiBot?start=ref_${chatId}`;
        this.elements.referrals.innerHTML = `
            <h2>Referrals</h2>
            <p>Invite friends and earn 100 TRUMP per referral!</p>
            <p>Your link: <input type="text" value="${referralLink}" readonly></p>
            <button onclick="ui.showScreen('main')">Back</button>
        `;
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
        game.state.balance = Math.max(localStats.balance, serverStats.balance);
        game.state.energy = Math.max(localStats.energy, serverStats.energy);
        game.state.max_energy = Math.max(localStats.max_energy, serverStats.max_energy);
        game.state.level = Math.max(localStats.level, serverStats.level);
        game.state.multitap = Math.max(localStats.multitap, serverStats.multitap);
        game.state.last_update = Date.now() / 1000;
        game.saveState();
        ui.update();
        console.log('Initial stats synced from server:', serverStats);
    } catch (error) {
        console.error('Error loading initial stats:', error);
        ui.update();
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

// Завершение таска
async function completeTask(taskId) {
    try {
        const response = await fetch('/api/complete_task', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ chat_id: chatId, task_id: taskId })
        });
        if (!response.ok) throw new Error(`Task completion failed: ${response.status}`);
        const data = await response.json();
        game.state.balance += data.reward;
        game.saveState();
        ui.updateTasks();
        console.log(`Task ${taskId} completed, reward: ${data.reward}`);
    } catch (error) {
        console.error('Task completion error:', error);
    }
}

// Обработчики событий
document.getElementById('tap-btn').addEventListener('click', () => {
    if (game.tap()) ui.update();
});
document.getElementById('settings-btn').addEventListener('click', () => ui.showScreen('settings'));
document.getElementById('tasks-btn').addEventListener('click', () => ui.showScreen('tasks'));
document.getElementById('referrals-btn').addEventListener('click', () => ui.showScreen('referrals'));

window.addEventListener('unload', syncWithServer);
Telegram.WebApp.onEvent('viewportChanged', (event) => {
    if (!event.isStateStable) syncWithServer();
});
Telegram.WebApp.ready();

// Инициализация
loadInitialStats();
ui.update();
setInterval(() => {
    game.updateEnergy();
    ui.update();
}, 1000);
setInterval(syncWithServer, 300000);
