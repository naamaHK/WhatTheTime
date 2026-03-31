const HOURS_HEB = {
    1: "אַחַת", 2: "שְׁתַּיִם", 3: "שָׁלֹשׁ", 4: "אַרְבַּע",
    5: "חָמֵשׁ", 6: "שֵׁשׁ", 7: "שֶׁבַע", 8: "שְׁמֹנֶה",
    9: "תֵּשַׁע", 10: "עֶשֶׂר", 11: "אַחַת עֶשְׂרֵה", 12: "שְׁתֵּים עֶשְׂרֵה"
};

const MINUTES_HEB = {
    5: "חָמֵשׁ", 10: "עֶשֶׂר", 20: "עֶשְׂרִים", 25: "עֶשְׂרִים וְחָמֵשׁ"
};

const ALL_TIMES = [];
for (let h = 1; h <= 12; h++) {
    [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55].forEach(m => {
        ALL_TIMES.push({ h, m });
    });
}

const PRAISES = [
    "🎉 כׇּל הַכָּבוֹד! עֲנִיתֶם נָכוֹן! אַתֶּם מַדְהִימִים! 🌟",
    "⭐ יָפֶה מְאֹד! קְרָאתֶם אֶת הַשָּׁעוֹן נָכוֹן! 🎊",
    "🏆 וָאוּ! נָכוֹן לְגַמְרֵי! אַתֶּם גְּאוֹנִים! 🎉",
    "🌈 מְצֻיָּן! כׇּל הַכָּבוֹד לָכֶם! ⭐",
    "🎯 נָכוֹן! אַתֶּם מַמָּשׁ טוֹבִים בָּזֶה! 🥳"
];

let currentMode = 1;
let currentHour = 0;
let currentMinute = 0;
let guessesLeft = 3;
let correctIdx = 0;
const MAX_GUESSES = 3;
let timeOptsLeft = 60;
let uiTimerId = null;

// Web Audio Context for sounds
const AudioContext = window.AudioContext || window.webkitAudioContext;
let audioCtx = null;

function playTone(freq, type, duration, vol=0.1) {
    if (!audioCtx) audioCtx = new AudioContext();
    if (audioCtx.state === 'suspended') audioCtx.resume();
    const osc = audioCtx.createOscillator();
    const gain = audioCtx.createGain();
    osc.type = type;
    osc.frequency.setValueAtTime(freq, audioCtx.currentTime);
    gain.gain.setValueAtTime(vol, audioCtx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + duration);
    osc.connect(gain);
    gain.connect(audioCtx.destination);
    osc.start();
    osc.stop(audioCtx.currentTime + duration);
}

function playSuccessSound() {
    playTone(523.25, 'sine', 0.1); // C5
    setTimeout(() => playTone(659.25, 'sine', 0.1), 100); // E5
    setTimeout(() => playTone(783.99, 'sine', 0.2), 200); // G5
}

function playFailSound() {
    playTone(300, 'triangle', 0.2);
    setTimeout(() => playTone(250, 'triangle', 0.4), 150);
}

function timeToHebrew(hour, minute) {
    const h = HOURS_HEB[hour];
    const nextHour = HOURS_HEB[(hour % 12) + 1];

    if (minute === 0) return h;
    if (minute === 15) return `${h} וָרֶבַע`;
    if (minute === 30) return `${h} וָחֵצִי`;
    if (minute === 45) return `רֶבַע לְ${nextHour}`;
    
    if (minute <= 25) {
        const m = MINUTES_HEB[minute];
        return `${h} וְ${m} דַּקּוֹת`;
    } else {
        const back = 60 - minute;
        const m = MINUTES_HEB[back];
        return `${m} דַּקּוֹת לְ${nextHour}`;
    }
}

// Drawing the clock
function drawClock(hour, minute) {
    const canvas = document.getElementById("clockCanvas");
    const ctx = canvas.getContext("2d");
    const cx = canvas.width / 2;
    const cy = canvas.height / 2;
    const r = cx - 15;

    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Face
    ctx.beginPath();
    ctx.arc(cx, cy, r, 0, 2 * Math.PI);
    ctx.fillStyle = "white";
    ctx.fill();
    ctx.lineWidth = 6;
    ctx.strokeStyle = "#2C3E50";
    ctx.stroke();

    // Tick marks
    for (let i = 0; i < 60; i++) {
        const angle = (i * 6 - 90) * (Math.PI / 180);
        const isHour = i % 5 === 0;
        const ir = isHour ? r - 20 : r - 10;
        
        ctx.beginPath();
        ctx.moveTo(cx + ir * Math.cos(angle), cy + ir * Math.sin(angle));
        ctx.lineTo(cx + (r - 4) * Math.cos(angle), cy + (r - 4) * Math.sin(angle));
        ctx.strokeStyle = "#95A5A6";
        ctx.lineWidth = isHour ? 3 : 1.5;
        ctx.stroke();
    }

    // Numbers
    ctx.font = "bold 22px 'Rubik', sans-serif";
    ctx.fillStyle = "#2C3E50";
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    for (let i = 1; i <= 12; i++) {
        const angle = (i * 30 - 90) * (Math.PI / 180);
        const nr = r - 35;
        ctx.fillText(i.toString(), cx + nr * Math.cos(angle), cy + nr * Math.sin(angle));
    }

    // Hour hand
    const ha = ((hour % 12) * 30 + minute * 0.5 - 90) * (Math.PI / 180);
    ctx.beginPath();
    ctx.moveTo(cx, cy);
    ctx.lineTo(cx + r * 0.5 * Math.cos(ha), cy + r * 0.5 * Math.sin(ha));
    ctx.strokeStyle = "#2C3E50";
    ctx.lineWidth = 10;
    ctx.lineCap = "round";
    ctx.stroke();

    // Minute hand
    const ma = (minute * 6 - 90) * (Math.PI / 180);
    ctx.beginPath();
    ctx.moveTo(cx, cy);
    ctx.lineTo(cx + r * 0.75 * Math.cos(ma), cy + r * 0.75 * Math.sin(ma));
    ctx.strokeStyle = "#E74C3C";
    ctx.lineWidth = 6;
    ctx.lineCap = "round";
    ctx.stroke();

    // Center dot
    ctx.beginPath();
    ctx.arc(cx, cy, 10, 0, 2 * Math.PI);
    ctx.fillStyle = "#2C3E50";
    ctx.fill();
    ctx.lineWidth = 3;
    ctx.strokeStyle = "white";
    ctx.stroke();
}

// Navigation & Initialization
function showMenu() {
    document.getElementById("view-menu").classList.add("active-view");
    document.getElementById("view-game").classList.remove("active-view");
}

function startGame(mode) {
    currentMode = mode;
    document.getElementById("view-menu").classList.remove("active-view");
    document.getElementById("view-game").classList.add("active-view");
    
    document.getElementById("mode1-inputs").classList.toggle("hidden", mode !== 1);
    document.getElementById("btn-check").classList.toggle("hidden", mode !== 1);
    document.getElementById("mode2-choices").classList.toggle("hidden", mode !== 2);
    
    const instr = mode === 1 ? "הִסְתַּכְּלוּ עַל הַשָּׁעוֹן וּכְתְבוּ אֶת הַשָּׁעָה!" : "בְּחַר אֶת הַשָּׁעָה הַנְּכוֹנָה:";
    document.getElementById("game-instructions").textContent = instr;
    
    newQuestion();
}

function updateLives() {
    const hearts = "❤️".repeat(guessesLeft) + "🖤".repeat(MAX_GUESSES - Math.max(0, guessesLeft));
    document.getElementById("lives-display").textContent = `נִסְיוֹנוֹת: ${hearts}`;
}

function shakeApp() {
    const app = document.getElementById("app-container");
    app.classList.remove("shake");
    void app.offsetWidth; // trigger reflow
    app.classList.add("shake");
}

function newQuestion() {
    const time = ALL_TIMES[Math.floor(Math.random() * ALL_TIMES.length)];
    currentHour = time.h;
    currentMinute = time.m;
    guessesLeft = MAX_GUESSES;
    updateLives();
    
    document.getElementById("btn-read").disabled = true;
    const fb = document.getElementById("feedback-msg");
    fb.textContent = "";
    fb.className = "feedback";
    
    drawClock(currentHour, currentMinute);
    
    clearTimeout(uiTimerId);
    document.getElementById("read-timer").classList.add("hidden");
    document.getElementById("btn-read-opts").classList.add("hidden");
    if (currentMode === 2) {
        timeOptsLeft = 60;
        document.getElementById("read-timer").classList.remove("hidden");
        updateTimer();
    }
    
    if (currentMode === 1) {
        const inpM = document.getElementById("input-minutes");
        const inpH = document.getElementById("input-hours");
        inpM.value = ""; inpH.value = "";
        inpM.disabled = false; inpH.disabled = false;
        inpH.focus();
    } else {
        setupMode2();
    }
}

// Auto-advance logic for Hours -> Minutes
document.getElementById("input-hours").addEventListener("keyup", (e) => {
    if (["Backspace", "Delete", "Enter", "Tab"].includes(e.key)) return;
    const val = e.target.value.trim();
    if (!val) return;
    if (val.length >= 2 || (val.length === 1 && "3456789".includes(val))) {
        document.getElementById("input-minutes").focus();
    }
});

// Mode 1 Check
function checkAnswerMode1() {
    if (guessesLeft <= 0) return;
    
    const inpH = document.getElementById("input-hours");
    const inpM = document.getElementById("input-minutes");
    const h = parseInt(inpH.value);
    const m = parseInt(inpM.value);
    const fb = document.getElementById("feedback-msg");
    
    if (isNaN(h) || isNaN(m)) {
        fb.textContent = "❓ אָנָּא הַכְנֵס מִסְפָּרִים בִּלְבַד!";
        fb.className = "feedback error";
        return;
    }
    
    if (h === currentHour && m === currentMinute) {
        guessesLeft = 0;
        updateLives();
        playSuccessSound();
        fb.textContent = PRAISES[Math.floor(Math.random() * PRAISES.length)];
        fb.className = "feedback success";
        inpH.disabled = true; inpM.disabled = true;
        document.getElementById("btn-read").disabled = false;
    } else {
        guessesLeft--;
        playFailSound();
        updateLives();
        shakeApp();
        if (guessesLeft === 0) {
            fb.textContent = `😔 לֹא נוֹרָא! התְּשׁוּבָה הַנְּכוֹנָה: ${currentHour}:${currentMinute.toString().padStart(2, '0')} · ${timeToHebrew(currentHour, currentMinute)}`;
            fb.className = "feedback error";
            inpH.disabled = true; inpM.disabled = true;
            document.getElementById("btn-read").disabled = false;
        } else {
            fb.textContent = "💪 נַסוּ שׁוּב! אַתֶם יְכוֹלִים! 😊";
            fb.className = "feedback error";
        }
    }
}

// Enter Key triggers check in Mode 1
document.getElementById("input-hours").addEventListener("keypress", (e) => { if (e.key === "Enter") checkAnswerMode1(); });
document.getElementById("input-minutes").addEventListener("keypress", (e) => { if (e.key === "Enter") checkAnswerMode1(); });

// Mode 2 Logic
function setupMode2() {
    let pool = ALL_TIMES.filter(t => t.h !== currentHour || t.m !== currentMinute);
    // shuffle pool
    for (let i = pool.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [pool[i], pool[j]] = [pool[j], pool[i]];
    }
    
    const options = [{h: currentHour, m: currentMinute}, ...pool.slice(0, 3)];
    // shuffle options
    for (let i = options.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [options[i], options[j]] = [options[j], options[i]];
    }
    
    for (let i = 0; i < 4; i++) {
        const btn = document.getElementById(`choice${i}`);
        btn.textContent = `${i + 1}. ${timeToHebrew(options[i].h, options[i].m)}`;
        btn.disabled = false;
        btn.className = "choice-btn";
        if (options[i].h === currentHour && options[i].m === currentMinute) {
            correctIdx = i;
        }
    }
}

function makeGuess(idx) {
    if (guessesLeft <= 0) return;
    const fb = document.getElementById("feedback-msg");
    const btn = document.getElementById(`choice${idx}`);
    
    if (idx === correctIdx) {
        guessesLeft = 0;
        updateLives();
        playSuccessSound();
        btn.classList.add("correct");
        fb.textContent = PRAISES[Math.floor(Math.random() * PRAISES.length)];
        fb.className = "feedback success";
        document.getElementById("btn-read").disabled = false;
        
        for (let i = 0; i < 4; i++) {
            document.getElementById(`choice${i}`).disabled = true;
        }
    } else {
        guessesLeft--;
        playFailSound();
        updateLives();
        shakeApp();
        btn.classList.add("wrong");
        btn.disabled = true;
        
        if (guessesLeft === 0) {
            fb.textContent = `😔 לֹא נוֹרָא! התְּשׁוּבָה הַנְּכוֹנָה: ${timeToHebrew(currentHour, currentMinute)}`;
            fb.className = "feedback error";
            document.getElementById(`choice${correctIdx}`).classList.add("correct");
            for (let i = 0; i < 4; i++) {
                document.getElementById(`choice${i}`).disabled = true;
            }
            document.getElementById("btn-read").disabled = false;
        } else {
            fb.textContent = "💪 נַסוּ שׁוּב! אַתֶם יְכוֹלִים! 😊";
            fb.className = "feedback error";
        }
    }
}

// Text to Speech
function readAloud() {
    if (currentHour === 0) return;
    const text = timeToHebrew(currentHour, currentMinute);
    const msg = new SpeechSynthesisUtterance(text);
    msg.lang = 'he-IL';
    // try to find Carmit or another Hebrew voice
    const voices = window.speechSynthesis.getVoices();
    const hebrewVoice = voices.find(v => v.lang.includes('he')) || voices.find(v => v.name.includes('Carmit'));
    if (hebrewVoice) msg.voice = hebrewVoice;
    
    window.speechSynthesis.speak(msg);
}

function readAllOptions() {
    let parts = [];
    const words = ["אֶפְשָׁרוּת אַחַת", "אֶפְשָׁרוּת שְׁנִיָּה", "אֶפְשָׁרוּת שְׁלִישִׁית", "אֶפְשָׁרוּת רְבִיעִית"];
    for(let i=0; i<4; i++) {
        const cleanText = document.getElementById('choice'+i).textContent.replace(/^\\d+\\.\\s*/, '');
        parts.push(`${words[i]}, ${cleanText}`);
    }
    const text = parts.join(". ");
    const msg = new SpeechSynthesisUtterance(text);
    msg.lang = 'he-IL';
    const voices = window.speechSynthesis.getVoices();
    const hebrewVoice = voices.find(v => v.lang.includes('he')) || voices.find(v => v.name.includes('Carmit'));
    if (hebrewVoice) msg.voice = hebrewVoice;
    window.speechSynthesis.speak(msg);
}

function updateTimer() {
    if (timeOptsLeft > 0) {
        document.getElementById("read-timer").textContent = `⏳ ${timeOptsLeft}`;
        timeOptsLeft--;
        uiTimerId = setTimeout(updateTimer, 1000);
    } else {
        document.getElementById("read-timer").classList.add("hidden");
        if (guessesLeft > 0 && currentMode === 2) {
            document.getElementById("btn-read-opts").classList.remove("hidden");
        }
    }
}

// Initialize voices cleanly for Chrome
if (window.speechSynthesis.onvoiceschanged !== undefined) {
    window.speechSynthesis.onvoiceschanged = () => window.speechSynthesis.getVoices();
}
