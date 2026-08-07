from flask import Flask, render_template, request, jsonify
from groq import Groq
from dotenv import load_dotenv
import os
import json
import glob
from PyPDF2 import PdfReader
from admin import register_admin_routes

# Setup
load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

app = Flask(__name__)

# Load all colleges from /colleges folder
def load_all_colleges():
    colleges = {}
    college_files = glob.glob("colleges/*.json")
    for filepath in college_files:
        with open(filepath, "r", encoding="utf-8") as f:
            college_data = json.load(f)
            colleges[college_data["id"]] = college_data
    return colleges

# Convert a college's policies into readable text for the AI
def build_policy_text(college_data):
    policy_text = ""
    policies = college_data.get("policies", {})
    for key, section in policies.items():
        policy_text += f"\n{section['title'].upper()} (category: {section['category']}):\n"
        for rule in section['rules']:
            policy_text += f"- {rule}\n"
    return policy_text

# Build a system prompt for a specific college
def build_system_prompt(college_data):
    college_policy = build_policy_text(college_data)
    college_name = college_data.get("name", "the College")
    office_contact = college_data.get("office_contact", "the college office")

    return f"""
You are CampusAid, a digital senior at {college_name} who genuinely cares about students.

You are NOT a chatbot. You are NOT a search engine. You are NOT a help desk.

You are the friend a student wishes they had at 2 AM when everything feels impossible.

═══════════════════════════════════════════
YOUR CORE PERSONALITY
═══════════════════════════════════════════

- You speak like a thoughtful senior, not a corporate assistant.
- You're warm but not fake. Direct but not cold.
- You take problems seriously. You don't trivialize.
- You believe every student deserves to feel less alone.

═══════════════════════════════════════════
HOW YOU MUST THINK BEFORE EVERY RESPONSE
═══════════════════════════════════════════

STEP 1 — DETECT EMOTION (silently):
- CASUAL: quick question, no stress
- CONFUSED: doesn't understand a process
- STRESSED: worried, anxious, under pressure
- FRUSTRATED: angry, fed up with the system
- DISTRESSED: deep emotional pain, hopelessness
- CRISIS: mentions self-harm, suicide, "can't go on"

STEP 2 — CATEGORIZE QUERY (silently):
- ACADEMIC | FINANCIAL | ADMINISTRATIVE | EMOTIONAL | MIXED

STEP 3 — CHOOSE RESPONSE APPROACH:
- CASUAL → brief and friendly
- CONFUSED → patient walkthrough
- STRESSED → acknowledge feeling FIRST, then guide
- FRUSTRATED → validate, then offer real options
- DISTRESSED → empathy first, NO info dump, gentle support
- CRISIS → immediate helpline + warmth + call to action

═══════════════════════════════════════════
THE SOUL RULES (THIS IS WHAT MAKES YOU DIFFERENT)
═══════════════════════════════════════════

RULE 1 — EMOTIONAL FIRST-AID:
For any emotional message, ACKNOWLEDGE the feeling before giving any information.

RULE 2 — STEP-BY-STEP ACTION PLANS (when needed):
For complex queries, break the answer into clear steps with time estimates.
For CASUAL queries (simple factual questions), keep the answer SHORT — 1-3 sentences max. No steps. No long plans. Just the answer.
Only use step-by-step format when the student is doing something complex (applying, drafting, planning).

RULE 3 — DRAFT IT FOR THEM:
If the student needs to write a letter, email, or application — OFFER TO DRAFT IT.
If they say yes, write a complete, properly formatted draft they can use directly.

RULE 4 — STAY WITH THEM:
After every response, leave a gentle door open when it fits naturally.
Never push. Just leave the door open.

RULE 5 — LANGUAGE MATCHING:
ALWAYS reply in the SAME language as the student's MOST RECENT message.
Don't carry over from previous messages. Match only the latest one.

RULE 6 — NEVER LABEL EMOTIONS IN YOUR REPLY:
Your detection is internal only.
NEVER write words like CASUAL, STRESSED, EMOTIONAL, CRISIS, ACADEMIC, FINANCIAL in your response.

RULE 7 — POLICY HONESTY:
Answer ONLY based on the college policy below.
If a question is outside the policy, say: "This needs to be handled by the college office directly. {office_contact}. I can help you prep what to ask, if you want."
NEVER make up rules.

RULE 8 — CRISIS PROTOCOL (NON-NEGOTIABLE):
If you detect CRISIS, drop everything else. Lead with:
- Warmth and presence ("I'm here. You're not alone.")
- Immediate helplines:
  * iCall: 9152987821 (24/7)
  * Vandrevala Foundation: 1860-2662-345 (24/7 free)
- A gentle nudge to reach out and a soft check-in.

═══════════════════════════════════════════
HOW YOU WRITE
═══════════════════════════════════════════

- Short paragraphs. Easy to read on a phone.
- Use occasional emojis only when it fits the tone (💙 for warmth, never for casual questions).
- Avoid corporate phrases: "As per policy", "Kindly note", "We regret to inform"
- Use human phrases: "Hey, here's the deal", "Let's break this down", "I got you"
- Bold key actions, not headers.

═══════════════════════════════════════════
WHAT THE STUDENT SHOULD FEEL AFTER YOUR REPLY
═══════════════════════════════════════════

Every response should leave them feeling ONE of these:
1. "Okay, I know exactly what to do next."
2. "I'm not alone in this."
3. "Someone gets it."

═══════════════════════════════════════════
{college_name.upper()} POLICY DATABASE
═══════════════════════════════════════════
{college_policy}
"""

# Load all colleges once at startup
COLLEGES = load_all_colleges()

# Pre-build system prompts for each college (efficient — no rebuilding per request)
SYSTEM_PROMPTS = {college_id: build_system_prompt(college_data) for college_id, college_data in COLLEGES.items()}

# Default college (used when none specified)
DEFAULT_COLLEGE = "abc_college"

# Store conversation per session (simple for now)
# No longer using global state - frontend manages chats now

# Home page
@app.route("/")
def home():
    return render_template("landing.html")

@app.route("/chat")
def chat_page():
    return render_template("index.html")

@app.route("/admin")
def admin_login_page():
    return render_template("admin_login.html")
# Chat endpoint
# Generate a short title for a conversation
@app.route("/generate_title", methods=["POST"])
def generate_title():
    data = request.json
    user_message = data.get("message", "").strip()

    if not user_message:
        return jsonify({"title": "New Chat"})

    try:
        response = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a title generator. Generate a SHORT (3-5 words max) descriptive title for a conversation that starts with the user's message. Return ONLY the title text, no quotes, no punctuation at the end. Examples: 'Fee Deferral Help', 'Exam Stress Support', 'Scholarship Application', 'Hostel Rules Query', 'Missed Exam Issue'."
                },
                {
                    "role": "user",
                    "content": f"Generate a title for a conversation starting with: \"{user_message}\""
                }
            ],
            model="llama-3.1-8b-instant",
            max_tokens=20
        )

        title = response.choices[0].message.content.strip().strip('"').strip("'")
        return jsonify({"title": title or "New Chat"})
    except Exception as e:
        return jsonify({"title": "New Chat"})
@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_message = data.get("message", "").strip()
    history = data.get("history", [])
    # Clean history: keep only role + content (strip timestamps or other fields)
    history = [{"role": m.get("role"), "content": m.get("content")} for m in history if m.get("role") and m.get("content")]
    document = data.get("document", None)
    college_id = data.get("college_id", DEFAULT_COLLEGE)

    if not user_message:
        return jsonify({"reply": "Please type something to chat."})

    # Get the system prompt for the selected college
    current_prompt = SYSTEM_PROMPTS.get(college_id, SYSTEM_PROMPTS[DEFAULT_COLLEGE])

    # If a document is attached to this chat, add it to context
    if document and document.get("content"):
        current_prompt += f"""

═══════════════════════════════════════════
🔴 STUDENT'S UPLOADED DOCUMENT — TOP PRIORITY 🔴
═══════════════════════════════════════════

The student has uploaded a document titled: "{document['name']}"

CRITICAL RULES FOR HANDLING UPLOADED DOCUMENT:

1. When the student asks ANYTHING about "this document", "this PDF", "this file", "summarize", "what is this about", "main topics", "key points" — they mean THE UPLOADED DOCUMENT BELOW. NOT your instructions. NOT the college policies.

2. The uploaded document is the student's CURRENT FOCUS. Treat it as the most important context.

3. NEVER summarize your own instructions or rules. NEVER summarize the college policy database. Only summarize/explain the uploaded document content.

4. If the question is clearly about college policy (fees, attendance, etc.) and unrelated to the document, then use college policy.

5. If unclear, ASSUME the student is asking about the uploaded document.

DOCUMENT CONTENT BELOW:
─────────────────────────────────────────
{document['content'][:8000]}
─────────────────────────────────────────
END OF DOCUMENT CONTENT
"""

    # Build message list with history from frontend
    messages = [{"role": "system", "content": current_prompt}]
    messages.extend(history)
    messages.append({"role": "user", "content": user_message})

    response = client.chat.completions.create(
        messages=messages,
        model="llama-3.1-8b-instant"
    )

    reply = response.choices[0].message.content

    return jsonify({"reply": reply})

# Upload PDF endpoint
@app.route("/upload", methods=["POST"])
def upload():
    if "file" not in request.files:
        return jsonify({"status": "error", "message": "No file uploaded"})

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"status": "error", "message": "No file selected"})

    if not file.filename.lower().endswith(".pdf"):
        return jsonify({"status": "error", "message": "Only PDF files are supported"})

    try:
        reader = PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"

        if not text.strip():
            return jsonify({"status": "error", "message": "Could not read text from this PDF"})

        return jsonify({
            "status": "success",
            "message": f"Got it! I've read '{file.filename}'. Ask me anything about it.",
            "filename": file.filename,
            "content": text.strip()
        })
    except Exception as e:
        return jsonify({"status": "error", "message": f"Error reading PDF: {str(e)}"})


@app.route("/remove_document", methods=["POST"])
def remove_document():
    # Document management now handled by frontend
    return jsonify({"status": "removed"})

    # Get list of available colleges
@app.route("/colleges", methods=["GET"])
def get_colleges():
    colleges_list = []
    for college_id, data in COLLEGES.items():
        colleges_list.append({
            "id": college_id,
            "name": data.get("name", "Unknown"),
            "tagline": data.get("tagline", ""),
            "colors": data.get("colors", {"primary": "#2563eb", "primary_dark": "#1e40af"})
        })
    return jsonify({"colleges": colleges_list})

@app.route("/reset", methods=["POST"])
def reset():
    # Chat management now handled by frontend
    return jsonify({"status": "reset"})

# Register admin routes from admin.py
register_admin_routes(
    app,
    client,
    COLLEGES,
    SYSTEM_PROMPTS,
    build_system_prompt,
    load_all_colleges
)
# Run the app
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)