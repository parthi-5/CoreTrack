let currentUserId = localStorage.getItem("activeSaaSUser") || null;
let isLoginMode = true;
const API_BASE_URL = "https://coretrack-backend-ftor.onrender.com/";
window.onload = function() {
    renderAppLayoutState();
};

function toggleProfileView(showProfile){
    const grid=document.querySelector(".dashboard-grid");
    const profileView = document.getElementById("userProfileView");

    if (showProfile) {
        grid.style.display = "none";
        profileView.style.display = "block";
        populateProfileData();
    } else {
        profileView.style.display = "none";
        grid.style.display = "grid";
    }
}

function populateProfileData(){
    if (!currentUserId) return;
    document.getElementById("profileIdField").innerText=`#${currentUserId}`;
    fetch(`${API_BASE_URL}user/profile?user_id=${currentUserId}`)
    .then(response => response.json())
    .then(data => {
        const emailField = document.getElementById("profileEmailField");
        const headerNameField= document.getElementById("profileHeaderName");
        if (data.status === "success") {
            document.getElementById("profileEmailField").innerText = data.email;
            document.getElementById("profileNameInput").value = data.name;
            document.getElementById("profileHeaderName").innerText = data.name;
        }
    })
    .catch(error => console.error("Telemetry map fetch fault:", error));
}

function togglePasswordVisibility() {
    const passwordField = document.getElementById("authPassword");
    const checkbox = document.getElementById("showPasswordCheckbox");
    
    if (checkbox.checked) {
        passwordField.type = "text";
    } else {
        passwordField.type = "password";
    }
}

function updateProfileNameAction() {
    const freshNameValue = document.getElementById("profileNameInput").value;
    if (freshNameValue.trim() === "") return;

    fetch(`${API_BASE_URL}user/profile/update`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_id: parseInt(currentUserId), new_name: freshNameValue })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === "success") {
            document.getElementById("profileHeaderName").innerText = data.updated_name;
        }
    })
    .catch(error => console.error("Identity update failure caught:", error));
}

function renderAppLayoutState() {
    const authPanel = document.getElementById("authPanel");
    const mainDashboard = document.getElementById("mainDashboard");

    if (currentUserId && currentUserId !== "null") {
        authPanel.style.display = "none";
        mainDashboard.style.display = "block";
        
        logMetricsAction();
        loadJournalHistoryStream();
    } else {
        mainDashboard.style.display = "none";
        authPanel.style.display = "block";
    }
}

function handleLogout() {
    localStorage.removeItem("activeSaaSUser");
    currentUserId = null;
    renderAppLayoutState();
    toggleProfileView(false); 
}

function toggleAuthMode() {
    isLoginMode = !isLoginMode;
    const title = document.getElementById("authTitle");
    const desc = document.getElementById("authDesc");
    const mainBtn = document.getElementById("mainAuthBtn");
    const toggleBtn = document.getElementById("toggleAuthBtn");
    const nameWrapper=document.getElementById("authNameWrapper");

    if (isLoginMode) {
        title.innerText = "Account Login";
        desc.innerText = "Please log in to synchronize your telemetry networks.";
        mainBtn.innerText = "Login";
        toggleBtn.innerText = "Sign Up";
        nameWrapper.style.display="none";
    } else {
        title.innerText = "Create SaaS Account";
        desc.innerText = "Register your private profile inside the global distributed cluster.";
        mainBtn.innerText = "Register Now";
        toggleBtn.innerText = "Back to Login";
        nameWrapper.style.display="block";
    }
    document.getElementById("showPasswordCheckbox").checked = false;
    document.getElementById("authPassword").type = "password";
}


function handleAuthAction() {
    const email = document.getElementById("authEmail").value;
    const password = document.getElementById("authPassword").value;
    const name = document.getElementById("authName").value;

    if (!email || !password) return;

    const endpoint = isLoginMode ? "login" : "register";
    
    const payload = { email: email, password: password };
    if (!isLoginMode) {
        payload.name = name || "Anonymous Developer";
    }

    fetch(`${API_BASE_URL}${endpoint}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === "error" || data.detail) {
            console.error("Auth rejection payload structural trace:", data);
        } else {
            if (isLoginMode) {
                localStorage.setItem("activeSaaSUser", data.user_id);
                currentUserId = data.user_id;
                renderAppLayoutState(); 
            } else {
                toggleAuthMode(); 
            }
        }
    })
    .catch(error => console.error("Network interface jam caught:", error));
}

function loadJournalHistoryStream() {
    if (!currentUserId) return;

    fetch(`${API_BASE_URL}journal?user_id=${currentUserId}`)
    .then(response => response.json())
    .then(entriesList => {
        const historyContainer = document.getElementById("journalHistoryStream");
        if (!historyContainer) return;

        historyContainer.innerHTML = "";

        if (entriesList.length === 0) {
            historyContainer.innerHTML = `<div style="color: #52525b; font-size: 0.85rem; font-style: italic;">No logs saved in this session vault yet...</div>`;
            return;
        }

        entriesList.reverse().forEach(entry => {
            const entryBlock = document.createElement("div");
            entryBlock.style.background = "#27272a";
            entryBlock.style.padding = "10px";
            entryBlock.style.borderRadius = "6px";
            entryBlock.style.borderLeft = entry.mood === "Happy" ? "4px solid #10b981" : "4px solid #f59e0b";
            
            entryBlock.innerHTML = `
                <div style="font-size: 0.85rem; color: #fff; line-height: 1.4;">"${entry.content}"</div>
                <div style="font-size: 0.75rem; color: #a1a1aa; margin-top: 4px; font-weight: bold;">AI Mood: ${entry.mood}</div>
            `;
            historyContainer.appendChild(entryBlock);
        });
    })
    .catch(error => console.error("History aggregator fetch crash caught:", error));
}

function logJournalAction() {
    const inputElement = document.getElementById("journalInput");
    const userText = inputElement.value;

    if (userText.trim() === "") return;

    fetch(`${API_BASE_URL}journal`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ content: userText, user_id: currentUserId })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === "success") {
            inputElement.value = ""; 
            logMetricsAction();      
            loadJournalHistoryStream(); 
        }
    })
    .catch(error => console.error("Submission stream network drop caught:", error));
}

function logMetricsAction() {
    if (!currentUserId || currentUserId === "null") return;

    fetch(`${API_BASE_URL}journal/analytics?user_id=${currentUserId}`)
    .then(response => response.json())
    .then(data => {
        const totalDisplayElement = document.getElementById("analyticsTotal");
        const anxietyDisplayElement = document.getElementById("analyticsAnxiety");

        if (!data.metrics || data.total_days_tracked === 0) {
            if (totalDisplayElement) totalDisplayElement.innerText = "0 Days";
            if (anxietyDisplayElement) anxietyDisplayElement.innerText = "0%";
            return;
        }

        if (totalDisplayElement) totalDisplayElement.innerText = `${data.total_days_tracked} Days`;
        if (anxietyDisplayElement) anxietyDisplayElement.innerText = data.metrics.anxiety_rate;
    })
    .catch(error => console.error("Silent calculation error handled:", error));
}

function logHabitAction() {
    fetch(`${API_BASE_URL}habits/log`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name: "Coding Sprint", user_id: currentUserId })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === "success") {
            const streakElement = document.getElementById("habitStreak");
            if (streakElement) streakElement.innerText = `${data.current_streak} Days`;
        }
    })
    .catch(error => console.error("Silent habit crash caught:", error));
}