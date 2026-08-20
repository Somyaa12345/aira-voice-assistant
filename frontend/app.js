// Aira Voice Assistant Frontend Client
const API_BASE = "";

// DOM Elements
const micBtn = document.getElementById("micBtn");
const micBtnText = document.getElementById("micBtnText");
const airaOrb = document.getElementById("airaOrb");
const voiceStatus = document.getElementById("voiceStatus");
const chatInput = document.getElementById("chatInput");
const sendBtn = document.getElementById("sendBtn");
const messagesContainer = document.getElementById("messagesContainer");
const notesContainer = document.getElementById("notesContainer");
const memoryContainer = document.getElementById("memoryContainer");

let mediaRecorder = null;
let audioChunks = [];
let isRecording = false;
let currentAudio = null;

// Initialize Web App
document.addEventListener("DOMContentLoaded", () => {
    fetchMemoryAndNotes();
    setupEventListeners();
});

function setupEventListeners() {
    micBtn.addEventListener("click", toggleRecording);
    sendBtn.addEventListener("click", () => handleSendText());
    chatInput.addEventListener("keypress", (e) => {
        if (e.key === "Enter") handleSendText();
    });
}

// Toggle Mic Recording
async function toggleRecording() {
    if (!isRecording) {
        startRecording();
    } else {
        stopRecording();
    }
}

async function startRecording() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        
        let mimeType = "audio/webm;codecs=opus";
        if (!MediaRecorder.isTypeSupported(mimeType)) {
            mimeType = MediaRecorder.isTypeSupported("audio/webm") ? "audio/webm" : "";
        }

        mediaRecorder = mimeType ? new MediaRecorder(stream, { mimeType }) : new MediaRecorder(stream);
        audioChunks = [];

        mediaRecorder.ondataavailable = (event) => {
            if (event.data.size > 0) audioChunks.push(event.data);
        };

        mediaRecorder.onstop = async () => {
            const actualType = mediaRecorder.mimeType || "audio/webm";
            const audioBlob = new Blob(audioChunks, { type: actualType });
            await processVoiceBlob(audioBlob, actualType);
        };

        mediaRecorder.start(250); // Collect data chunks every 250ms
        isRecording = true;
        micBtn.classList.add("recording");
        micBtnText.textContent = "Listening... (Click to Stop)";
        airaOrb.className = "aira-orb-large listening";
        voiceStatus.textContent = "Listening to your voice...";
    } catch (err) {
        console.error("Microphone permission denied or error:", err);
        alert("Microphone access is required for voice interaction.");
    }
}

function stopRecording() {
    if (mediaRecorder && isRecording) {
        mediaRecorder.stop();
        isRecording = false;
        micBtn.classList.remove("recording");
        micBtnText.textContent = "Processing...";
        airaOrb.className = "aira-orb-large";
        voiceStatus.textContent = "Processing speech with Whisper & Ollama...";
    }
}

// Send Recorded Voice Blob to Backend
async function processVoiceBlob(blob, mimeType = "audio/webm") {
    const formData = new FormData();
    const ext = mimeType.includes("webm") ? "webm" : (mimeType.includes("ogg") ? "ogg" : "wav");
    formData.append("file", blob, `user_recording.${ext}`);
    formData.append("session_id", "default");

    try {
        const response = await fetch(`${API_BASE}/api/voice/process`, {
            method: "POST",
            body: formData
        });

        if (!response.ok) throw new Error("Server error during voice processing");

        let transcribedText = "";
        let assistantReply = "";
        let toolCalls = [];

        try {
            const data = await response.json();
            transcribedText = data.user_text || "Voice Input";
            assistantReply = data.assistant_reply || "";
            toolCalls = data.tool_calls || [];
        } catch (e) {
            const transcribedRaw = response.headers.get("X-Transcribed-Text") || "Voice Input";
            const assistantRaw = response.headers.get("X-Assistant-Reply") || "";
            transcribedText = decodeURIComponent(transcribedRaw);
            assistantReply = decodeURIComponent(assistantRaw);
        }

        // Add message bubbles
        appendMessage("user", transcribedText);
        appendMessage("assistant", assistantReply, toolCalls);

        // Speak Response using Indian Female Web Speech Synthesis (Instant!)
        speakText(assistantReply);

        voiceStatus.textContent = "Click 'Start Speaking' or type below";
        micBtnText.textContent = "Start Speaking";
        fetchMemoryAndNotes();

    } catch (err) {
        console.error("Error processing voice:", err);
        voiceStatus.textContent = "Error processing voice request.";
        micBtnText.textContent = "Start Speaking";
    }
}

// Send Text Message
async function handleSendText(overrideQuery = null) {
    const text = overrideQuery || chatInput.value.trim();
    if (!text) return;

    chatInput.value = "";
    appendMessage("user", text);
    voiceStatus.textContent = "Aira is thinking...";
    airaOrb.className = "aira-orb-large listening";

    try {
        const response = await fetch(`${API_BASE}/api/chat`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                query: text,
                session_id: "default",
                synthesize_audio: true
            })
        });

        const data = await response.json();
        airaOrb.className = "aira-orb-large speaking";

        appendMessage("assistant", data.assistant_reply, data.tool_calls);
        speakText(data.assistant_reply);
        voiceStatus.textContent = "Click 'Start Speaking' or type below";

        fetchMemoryAndNotes();
        setTimeout(() => { airaOrb.className = "aira-orb-large"; }, 2000);

    } catch (err) {
        console.error("Chat error:", err);
        appendMessage("assistant", "Sorry, I encountered an error connecting to my backend.");
        airaOrb.className = "aira-orb-large";
    }
}

function sendQuickQuery(queryText) {
    handleSendText(queryText);
}

// UI Helper Functions
function appendMessage(role, content, toolCalls = null) {
    const bubble = document.createElement("div");
    bubble.className = `message-bubble ${role}`;
    bubble.innerHTML = content;

    if (toolCalls && toolCalls.length > 0) {
        toolCalls.forEach(tc => {
            const toolDiv = document.createElement("div");
            toolDiv.className = "tool-card";
            
            const targetUrl = tc.result && tc.result.url ? tc.result.url : null;
            if (targetUrl) {
                toolDiv.innerHTML = `🛠 Tool Executed: <strong>${tc.tool}</strong> → <a href="${targetUrl}" target="_blank" style="color:#67e8f9;text-decoration:underline;">${targetUrl}</a>`;
                // Open URL in new browser tab client-side
                try { window.open(targetUrl, '_blank'); } catch(e) { console.log(e); }
            } else {
                toolDiv.textContent = `🛠 Tool Executed: ${tc.tool} ${JSON.stringify(tc.args)}`;
            }
            bubble.appendChild(toolDiv);
        });
    }

    messagesContainer.appendChild(bubble);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

function getIndianFemaleVoice() {
    if (!('speechSynthesis' in window)) return null;
    const voices = window.speechSynthesis.getVoices();
    if (!voices || voices.length === 0) return null;

    // 1. Strict priority: Indian English (en-IN) female voice
    let selected = voices.find(v => (v.lang === "en-IN" || v.lang === "en_IN" || v.name.includes("India")) &&
        (v.name.includes("Female") || v.name.includes("Heera") || v.name.includes("Neerja") || v.name.includes("Veena") || v.name.includes("Kalpana") || v.name.includes("Google")));
    
    // 2. Fallback to any en-IN voice
    if (!selected) {
        selected = voices.find(v => v.lang === "en-IN" || v.lang === "en_IN" || v.name.includes("India"));
    }
    
    // 3. Fallback to female voice
    if (!selected) {
        selected = voices.find(v => v.name.includes("Female") || v.name.includes("Zira"));
    }

    return selected || voices[0];
}

function speakText(text) {
    if ('speechSynthesis' in window) {
        window.speechSynthesis.cancel();
        const utterance = new SpeechSynthesisUtterance(text);
        
        const indianVoice = getIndianFemaleVoice();
        if (indianVoice) {
            utterance.voice = indianVoice;
            utterance.lang = indianVoice.lang || "en-IN";
            console.log("Selected Indian English Voice:", indianVoice.name, indianVoice.lang);
        } else {
            utterance.lang = "en-IN";
        }
        
        utterance.rate = 0.95; // Natural speaking pace for Hindi accent
        utterance.pitch = 1.05; // Natural female pitch
        airaOrb.className = "aira-orb-large speaking";
        utterance.onend = () => { airaOrb.className = "aira-orb-large"; };
        utterance.onerror = () => { airaOrb.className = "aira-orb-large"; };
        window.speechSynthesis.speak(utterance);
    }
}

// Pre-load voices on browser load
if ('speechSynthesis' in window) {
    window.speechSynthesis.onvoiceschanged = () => { getIndianFemaleVoice(); };
}

function playAudio(audioUrl, fallbackText = "") {
    if (currentAudio) currentAudio.pause();
    airaOrb.className = "aira-orb-large speaking";
    currentAudio = new Audio(audioUrl);

    currentAudio.onended = () => {
        airaOrb.className = "aira-orb-large";
    };

    currentAudio.onerror = () => {
        console.log("Audio element failed, using Web Speech Synthesis fallback");
        if (fallbackText) speakText(fallbackText);
    };

    currentAudio.play().catch(e => {
        console.log("Autoplay audio error, falling back to SpeechSynthesis:", e);
        if (fallbackText) speakText(fallbackText);
    });
}

async function fetchMemoryAndNotes() {
    try {
        const [notesRes, memRes] = await Promise.all([
            fetch(`${API_BASE}/api/memory/notes`),
            fetch(`${API_BASE}/api/memory/memories`)
        ]);

        if (notesRes.ok) {
            const notes = await notesRes.json();
            notesContainer.innerHTML = notes.length === 0 ? '<div class="item-badge">No notes saved yet</div>' : '';
            notes.forEach(n => {
                const item = document.createElement("div");
                item.className = "item-badge";
                item.textContent = `📌 ${n.title}: ${n.content}`;
                notesContainer.appendChild(item);
            });
        }

        if (memRes.ok) {
            const mems = await memRes.json();
            memoryContainer.innerHTML = mems.length === 0 ? '<div class="item-badge">Memory active</div>' : '';
            mems.forEach(m => {
                const item = document.createElement("div");
                item.className = "item-badge";
                item.textContent = `💡 ${m.key}: ${m.value}`;
                memoryContainer.appendChild(item);
            });
        }
    } catch (e) {
        console.log("Memory sync:", e);
    }
}
