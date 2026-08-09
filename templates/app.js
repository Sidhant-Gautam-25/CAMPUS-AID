// CampusAid Interactive Client Controller
document.addEventListener("DOMContentLoaded", () => {
    // DOM Elements
    const chatMessagesContainer = document.getElementById("chat-messages");
    const scenarioButtons = document.querySelectorAll(".scenario-btn");
    const chatInput = document.getElementById("chat-input");
    const sendTrigger = document.getElementById("send-trigger");
    const progressBar = document.getElementById("main-progress-bar");
    const completionPercentage = document.getElementById("completion-percentage");
    const milestoneCards = document.querySelectorAll(".milestone-card");
    // Pre-defined Scenario Data
    const conversations = {
        "attendance-fee": {
            userQuery: "My attendance is 63% and I need fee deferral.",
            botResponse: "Your attendance is below the required threshold of 75%. You may apply for attendance relaxation under special cases (e.g., medical leave or college representation) via the Academic Dean's portal.\n\nFor the fee deferral, you can submit a formal deferment form to the accounts department. Be sure to file it before the payment due date to prevent late fees from accumulating."
        },
        "scholarship": {
            userQuery: "Are there any active scholarships for engineering?",
            botResponse: "Yes! Currently, the Merit-Cum-Means (MCM) Scholarship and the Academic Excellence Waiver are open for applications. The deadline is next Friday.\n\nTo apply, you will need to upload your latest semester transcript (minimum CGPA 8.0) and household income declaration under the 'Financial Aid' tab on your dashboard."
        },
        "grievance": {
            userQuery: "How do I register a grievance about the hostel mess?",
            botResponse: "You can file an official grievance ticket using our 'Grievance Support' menu. CampusAid will automatically categorize the mess quality issue and assign it to the Hostel Warden.\n\nA ticket number will be generated immediately, and you can track the warden's feedback and resolution progress in real-time."
        }
    };
    let typingTimer = null;
    // Initialize conversation with bot greeting
    function initChat() {
        chatMessagesContainer.innerHTML = "";
        
        // Add default bot greeting
        appendMessage("bot", "Hello! I'm CampusAid, your AI-powered campus assistant. Select a scenario on the left to see how I process complex student queries.");
        
        // Simulate a minor completion bar animation on load
        setTimeout(() => {
            progressBar.style.width = "30%";
        }, 500);
    }
    // Append standard message to UI
    function appendMessage(sender, text) {
        const messageDiv = document.createElement("div");
        messageDiv.classList.add("chat-message", sender);
        
        const avatar = document.createElement("div");
        avatar.classList.add("avatar-wrapper");
        avatar.innerText = sender === "user" ? "" : "";
        
        const bubble = document.createElement("div");
        bubble.classList.add("message-bubble");
        
        // Convert newlines to breaks for clean formatting
        bubble.innerHTML = text.replace(/\n/g, "<br>");
        
        messageDiv.appendChild(avatar);
        messageDiv.appendChild(bubble);
        chatMessagesContainer.appendChild(messageDiv);
        
        // Scroll to bottom
        chatMessagesContainer.scrollTop = chatMessagesContainer.scrollHeight;
        
        return bubble;
    }
    // Append typing loader indicator
    function appendTypingIndicator() {
        const messageDiv = document.createElement("div");
        messageDiv.classList.add("chat-message", "bot", "typing-indicator-wrapper");
        
        const avatar = document.createElement("div");
        avatar.classList.add("avatar-wrapper");
        avatar.innerText = "";
        
        const bubble = document.createElement("div");
        bubble.classList.add("message-bubble");
        
        const loader = document.createElement("div");
        loader.classList.add("typing-dot-loader");
        loader.innerHTML = "<span></span><span></span><span></span>";
        
        bubble.appendChild(loader);
        messageDiv.appendChild(avatar);
        messageDiv.appendChild(bubble);
        chatMessagesContainer.appendChild(messageDiv);
        
        chatMessagesContainer.scrollTop = chatMessagesContainer.scrollHeight;
        return messageDiv;
    }
    // Typewriter printout function
    function runTypewriter(element, text, speed = 15) {
        let index = 0;
        element.innerHTML = "";
        
        return new Promise((resolve) => {
            function type() {
                if (index < text.length) {
                    const char = text.charAt(index);
                    if (char === "\n") {
                        element.innerHTML += "<br>";
                    } else {
                        element.innerHTML += char;
                    }
                    index++;
                    chatMessagesContainer.scrollTop = chatMessagesContainer.scrollHeight;
                    typingTimer = setTimeout(type, speed);
                } else {
                    resolve();
                }
            }
            type();
        });
    }
    // Trigger full scenario flow
    async function triggerScenario(scenarioKey) {
        // Clear any ongoing typewriter timers
        if (typingTimer) {
            clearTimeout(typingTimer);
        }
        const data = conversations[scenarioKey];
        if (!data) return;
        // Clear chat body and render greeting again (or just print selected scenario)
        chatMessagesContainer.innerHTML = "";
        
        // 1. User sends message
        appendMessage("user", data.userQuery);
        
        // Disable other buttons during execution
        scenarioButtons.forEach(btn => btn.setAttribute("disabled", "true"));
        
        // 2. Wait 800ms and show bot typing indicator
        await new Promise(r => setTimeout(r, 600));
        const indicator = appendTypingIndicator();
        
        // 3. Wait 1200ms and replace typing indicator with typewriting response
        await new Promise(r => setTimeout(r, 1000));
        if (indicator && indicator.parentNode) {
            indicator.parentNode.removeChild(indicator);
        }
        
        const responseBubble = appendMessage("bot", "");
        await runTypewriter(responseBubble, data.botResponse);
        
        // Re-enable controls
        scenarioButtons.forEach(btn => btn.removeAttribute("disabled"));
    }
    // Event listeners for scenario clicks
    scenarioButtons.forEach(button => {
        button.addEventListener("click", () => {
            // Remove active status from all and add to clicked
            scenarioButtons.forEach(btn => btn.classList.remove("active"));
            button.classList.add("active");
            
            const scenario = button.getAttribute("data-scenario");
            triggerScenario(scenario);
        });
    });
    // Milestone completion interactive simulation
    milestoneCards.forEach((card, idx) => {
        card.addEventListener("click", () => {
            // Toggle completed status for demo interactivity
            if (card.classList.contains("pending")) {
                card.classList.remove("pending");
                card.classList.add("completed");
                card.innerHTML = card.innerHTML.replace(`<div class="milestone-number">0${idx+1}</div>`, `<div class="milestone-check"></div>`);
                
                // Recalculate and update completion percentage dynamically
                updateProgress();
            }
        });
    });
    function updateProgress() {
        const completedCount = document.querySelectorAll(".milestone-card.completed").length;
        const total = milestoneCards.length;
        const percent = Math.round((completedCount / total) * 100);
        
        progressBar.style.width = `${percent}%`;
        completionPercentage.innerText = `${percent}%`;
    }
    // Scroll Fade-In animation observer
    const cards = document.querySelectorAll(".feature-card, .capability-node, .progress-container");
    const observerOptions = {
        threshold: 0.1,
        rootMargin: "0px 0px -50px 0px"
    };
    const revealObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = "1";
                entry.target.style.transform = "translateY(0)";
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);
    cards.forEach(card => {
        card.style.opacity = "0";
        card.style.transform = "translateY(25px)";
        card.style.transition = "opacity 0.6s cubic-bezier(0.16, 1, 0.3, 1), transform 0.6s cubic-bezier(0.16, 1, 0.3, 1)";
        revealObserver.observe(card);
    });
    // Start
    initChat();
    
    // Automatically trigger first scenario shortly after load for visual wow factor
    setTimeout(() => {
        triggerScenario("attendance-fee");
    }, 1500);
});