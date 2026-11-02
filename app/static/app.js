
const languageSelect = document.getElementById("languageSelect");
const chatMessages = document.getElementById("chatMessages");
const messageInput = document.getElementById("messageInput");
const sendButton = document.getElementById("sendButton");
const clearButton = document.getElementById("clearButton");

const translations = {
    en: {
        eyebrow: "YOUR HEALTH. YOUR KNOWLEDGE.",
        welcomeTitle: "Hello! How can I help you today?",
        welcomeText: "Ask questions about HIV, sexual health and reproductive health. Get educational information in your preferred language.",
        assistantName: "AfyaChat Assistant",
        statusText: "Educational support",
        clearButton: "Clear chat",
        initialMessage: "Welcome! You can ask me a health education question. Please do not share private identifying information.",
        placeholder: "Type your health question...",
        sendLabel: "Send",
        inputHint: "Press Enter to send · Shift + Enter for a new line · Maximum 2,000 characters",
        safetyText: "This chatbot provides general educational information, not medical diagnosis or treatment. For personal medical advice, consult a qualified healthcare professional.",
        footerText: "Supporting informed health decisions through education.",
        you: "You",
        assistant: "AfyaChat",
        sources: "Sources",
        error: "Sorry, I could not connect to the health information service. Please try again later.",
        loading: "Thinking...",
        empty: "Please enter a question first."
    },
    sw: {
        eyebrow: "AFYA YAKO. ELIMU YAKO.",
        welcomeTitle: "Habari! Ninaweza kukusaidia vipi leo?",
        welcomeText: "Uliza maswali kuhusu VVU, afya ya uzazi na afya ya kujamiiana. Pata taarifa za kielimu kwa lugha unayoipendelea.",
        assistantName: "Msaidizi wa AfyaChat",
        statusText: "Huduma ya elimu ya afya",
        clearButton: "Futa mazungumzo",
        initialMessage: "Karibu! Unaweza kuniuliza swali kuhusu elimu ya afya. Tafadhali usishiriki taarifa binafsi zinazoweza kukutambulisha.",
        placeholder: "Andika swali lako kuhusu afya...",
        sendLabel: "Tuma",
        inputHint: "Bonyeza Enter kutuma · Shift + Enter kuanza mstari mpya · Herufi zisizozidi 2,000",
        safetyText: "Chatbot hii hutoa taarifa za jumla za kielimu, si utambuzi au matibabu. Kwa ushauri wa afya unaokuhusu, wasiliana na mtaalamu wa afya aliyehitimu.",
        footerText: "Kusaidia maamuzi sahihi ya afya kupitia elimu.",
        you: "Wewe",
        assistant: "AfyaChat",
        sources: "Vyanzo",
        error: "Samahani, imeshindikana kuunganishwa na huduma ya taarifa za afya. Tafadhali jaribu tena baadaye.",
        loading: "Inatafuta taarifa...",
        empty: "Tafadhali andika swali kwanza."
    }
};

let currentLanguage = "en";
let isSending = false;

function addMessage(role, text, sources = [], safetyNotice = "") {
    const t = translations[currentLanguage];

    const wrapper = document.createElement("div");
    wrapper.className = role === "user"
        ? "message user-message"
        : "message assistant-message";

    const avatar = document.createElement("div");
    avatar.className = "avatar";
    avatar.textContent = role === "user" ? "●" : "✚";

    const content = document.createElement("div");
    content.className = "message-content";

    const bubble = document.createElement("div");
    bubble.className = "message-bubble";
    bubble.textContent = text;

    const time = document.createElement("span");
    time.className = "message-time";
    time.textContent = role === "user" ? t.you : t.assistant;

    content.appendChild(bubble);

    if (sources.length > 0) {
        const sourceContainer = document.createElement("div");
        sourceContainer.className = "sources";

        const heading = document.createElement("strong");
        heading.textContent = t.sources;
        sourceContainer.appendChild(heading);

        sources.forEach(source => {
            const link = document.createElement("a");

            try {
                const url = new URL(source.url);
                if (url.protocol !== "https:" && url.protocol !== "http:") {
                    return;
                }

                link.href = url.href;
                link.target = "_blank";
                link.rel = "noopener noreferrer";
                link.textContent = source.title || source.organization || url.hostname;
                sourceContainer.appendChild(link);
            } catch {
                // Do not display invalid source URLs.
            }
        });

        if (sourceContainer.children.length > 1) {
            content.appendChild(sourceContainer);
        }
    }

    if (safetyNotice) {
        const safety = document.createElement("div");
        safety.className = "response-safety";
        safety.textContent = safetyNotice;
        content.appendChild(safety);
    }

    content.appendChild(time);
    wrapper.appendChild(avatar);
    wrapper.appendChild(content);
    chatMessages.appendChild(wrapper);

    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function updateLanguage(language) {
    currentLanguage = language;
    const t = translations[language];

    document.documentElement.lang = language;
    document.getElementById("eyebrow").textContent = t.eyebrow;
    document.getElementById("welcomeTitle").textContent = t.welcomeTitle;
    document.getElementById("welcomeText").textContent = t.welcomeText;
    document.getElementById("assistantName").textContent = t.assistantName;
    document.getElementById("statusText").textContent = t.statusText;
    document.getElementById("clearButton").textContent = t.clearButton;
    document.getElementById("initialMessage").textContent = t.initialMessage;
    document.getElementById("messageInput").placeholder = t.placeholder;
    document.getElementById("sendLabel").textContent = t.sendLabel;
    document.getElementById("inputHint").textContent = t.inputHint;
    document.getElementById("safetyText").textContent = t.safetyText;
    document.getElementById("footerText").textContent = t.footerText;
}

async function sendMessage() {
    const message = messageInput.value.trim();

    if (!message) {
        messageInput.focus();
        return;
    }

    if (isSending) return;

    isSending = true;
    sendButton.disabled = true;

    addMessage("user", message);
    messageInput.value = "";

    const t = translations[currentLanguage];
    const loadingElement = document.createElement("div");
    loadingElement.className = "message assistant-message";
    loadingElement.id = "loadingMessage";

    const loadingBubble = document.createElement("div");
    loadingBubble.className = "message-bubble";
    loadingBubble.textContent = t.loading;

    loadingElement.appendChild(loadingBubble);
    chatMessages.appendChild(loadingElement);
    chatMessages.scrollTop = chatMessages.scrollHeight;

    try {
        const response = await fetch("/api/v1/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                message: message,
                language: currentLanguage
            })
        });

        if (!response.ok) {
            throw new Error("Chat service returned an error.");
        }

        const data = await response.json();

        if (!data || typeof data.answer !== "string") {
            throw new Error("Invalid response from chat service.");
        }

        addMessage(
            "assistant",
            data.answer,
            Array.isArray(data.sources) ? data.sources : [],
            data.safety_notice || ""
        );
    } catch (error) {
        addMessage("assistant", translations[currentLanguage].error);
    } finally {
        document.getElementById("loadingMessage")?.remove();
        isSending = false;
        sendButton.disabled = false;
        messageInput.focus();
    }
}

function clearChat() {
    const t = translations[currentLanguage];

    chatMessages.innerHTML = `
        <div class="message assistant-message">
            <div class="avatar">✚</div>
            <div class="message-content">
                <div class="message-bubble" id="initialMessage"></div>
                <span class="message-time">AfyaChat</span>
            </div>
        </div>
    `;

    document.getElementById("initialMessage").textContent = t.initialMessage;
}

sendButton.addEventListener("click", sendMessage);

messageInput.addEventListener("keydown", event => {
    if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
    }
});

clearButton.addEventListener("click", clearChat);

languageSelect.addEventListener("change", event => {
    updateLanguage(event.target.value);
});

updateLanguage("en");
