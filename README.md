# 🎓 CampusAid

> An emotionally intelligent AI companion for college students — with a smart onboarding platform that makes it easy for any institution to deploy.

CampusAid is an AI-powered chatbot that helps college students navigate policies, deadlines, mental health struggles, and everyday college life. Unlike generic chatbots, it understands each college's specific rules and responds with genuine empathy — from casual questions to crisis moments.

---

## ✨ Why CampusAid?

Every college student has been here:

- It's 2 AM. Exam tomorrow. Missed the last internal test. Panicking.
- Financial trouble. Can't tell parents. Don't know if fee deferral is even an option.
- Overwhelmed. Feel like quitting. No one to talk to.

Existing solutions fail:

- **Email admin?** Days for a reply.
- **Google?** Generic advice, not your college.
- **ChatGPT?** Doesn't know your specific policies.
- **Friends?** Might be sleeping. Or don't know either.

**CampusAid is the missing layer** — an AI that knows YOUR college, understands YOUR emotions, and helps YOU take the next step.

---

## 🚀 Key Features

### 🧠 Emotionally Intelligent AI

- Detects 6 emotional states: casual, confused, stressed, frustrated, distressed, crisis
- Adjusts tone and response style based on detected emotion
- Empathetic first-aid before information dumps
- Automatic crisis escalation with helpline numbers (iCall, Vandrevala Foundation)

### 🌍 Multi-College Support

- Each college gets an isolated instance with its own policies
- Clean architecture: one JSON file per college
- Adding a new college = one file, zero code changes

### 📥 Smart Onboarding (Centerpiece Feature)

- Admins drag-and-drop PDF/DOCX handbooks
- AI extracts every policy automatically
- Auto-categorization (academic, financial, administrative, emotional)
- Live progress streaming during extraction
- Review and approve with one click
- Smart duplicate detection

### 📄 Document Q&A for Students

- Students upload their own study materials (PDFs)
- Ask questions about their assignments, notes, syllabi
- AI answers using the uploaded document as primary context

### 🌐 Bilingual Support

- Auto-detects Hindi, English, and Hinglish
- Matches student's language per message
- No manual switching needed

### 💬 ChatGPT-Style Interface

- Persistent chat history in sidebar
- Auto-generated conversation titles
- Multi-chat support with document per conversation
- Real-time typing indicators
- Message timestamps
- Markdown rendering
- Dark mode

### 🛡️ Admin Dashboard

- Live policy statistics
- Filter policies by category
- Real-time search
- Delete with confirmation
- Instant bot updates after changes

---

## 🎬 Demo Scenarios

**Scenario 1 — Stressed Student**

> Student: "My exam is in 2 days and I've studied nothing. I'm panicking."
>
> Bot: Acknowledges the anxiety, provides a time-blocked study plan, offers to help further.

**Scenario 2 — Financial Crisis**

> Student: "Bhai fees nahi de paunga is baar"
>
> Bot: Responds in Hinglish, offers fee deferral information, drafts an application letter on request.

**Scenario 3 — Crisis Moment**

> Student: "Nothing matters anymore. I want to quit everything."
>
> Bot: Immediate empathetic response with crisis helplines (iCall, Vandrevala), no judgment, soft check-in.

**Scenario 4 — Smart Onboarding (The Wow Moment)**

> Admin drops a 7-page college handbook PDF.
>
> AI extracts 24 policies in ~2 minutes with live progress bar.
>
> Admin approves. Bot immediately uses new policies. Student asks a question about the newly added content. Bot answers with fresh knowledge.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────┐
│           STUDENT INTERFACE                 │
│  Chat UI • History • Document Upload        │
└────────────────┬────────────────────────────┘
                 │
                 ↓
┌─────────────────────────────────────────────┐
│           FLASK BACKEND                     │
│  Routing • Session • Business Logic         │
└────────┬────────────────────────┬───────────┘
         │                        │
         ↓                        ↓
┌────────────────────┐  ┌──────────────────────┐
│   AI LAYER         │  │  KNOWLEDGE LAYER     │
│  Groq + LLaMA 3    │  │  College JSONs       │
│  Emotion Detection │  │  System Prompts      │
│  Crisis Safety     │  │  Policy Store        │
└────────────────────┘  └──────────────────────┘
                                 ↑
                                 │
┌─────────────────────────────────────────────┐
│           ADMIN INTERFACE                   │
│  Upload • Extract • Review • Manage         │
└─────────────────────────────────────────────┘
```

**Data Flow — Chat:**

1. Student sends message → Frontend
2. Frontend calls Flask `/chat` with message + college_id + optional document
3. Flask builds system prompt with college policies + AI personality
4. Groq LLaMA 3 processes and returns empathetic response
5. Reply streamed back to student

**Data Flow — Smart Onboarding:**

1. Admin uploads PDF → Flask extracts text (PyPDF2/python-docx)
2. Text split into ~3000-char chunks (rate-limit safe)
3. Each chunk sent to AI with policy extraction prompt
4. AI returns structured JSON with categorized policies
5. Server-Sent Events (SSE) stream progress to frontend in real-time
6. Admin reviews → approves → merged into college JSON
7. System prompt regenerated → bot uses new policies immediately

---

## 🛠️ Tech Stack

| Layer | Technology |
| ----- | ---------- |
| Backend | Python 3, Flask |
| AI Engine | Groq API + LLaMA 3.1 8B Instant |
| Document Parsing | PyPDF2, python-docx |
| Frontend | Vanilla HTML/CSS/JavaScript |
| Storage | JSON files (per college) + localStorage (chat history) |
| Streaming | Server-Sent Events (SSE) |
| Font | Inter (Google Fonts) |
| Deployment | Render (free tier) |

**Zero paid services. Everything runs on free tiers.**

---

## 📂 Project Structure

```
campusaid/
├── app.py                    # Main Flask app + chat endpoints
├── admin.py                  # Admin dashboard routes (separated for clarity)
├── requirements.txt          # Python dependencies
├── .env                      # API keys (never committed)
├── .gitignore
│
├── colleges/                 # Multi-tenant data layer
│   ├── abc_college.json      # ABC College policies + config
│   └── xyz_institute.json    # XYZ Institute policies + config
│
├── static/
│   └── design-system.css     # Shared design tokens (colors, fonts, spacing)
│
└── templates/
    ├── index.html            # Student chat interface
    └── admin.html            # Admin dashboard
```

---

## 🚀 Local Setup

### Prerequisites

- Python 3.10+
- Free Groq API key from [console.groq.com](https://console.groq.com)

### Installation

**1. Clone the repository**

```bash
git clone https://github.com/YourUsername/campusaid.git
cd campusaid
```

**2. Create virtual environment**

```bash
python -m venv venv
venv\Scripts\activate      # Windows
source venv/bin/activate   # Mac/Linux
```

**3. Install dependencies**

```bash
pip install -r requirements.txt
```

**4. Set up environment variables**

Create a `.env` file in the root:

```
GROQ_API_KEY=your_groq_api_key_here
```

**5. Run the app**

```bash
python app.py
```

**6. Open in browser**

- Student view: `http://localhost:5000`
- Admin dashboard: `http://localhost:5000/admin/abc_college`

---

## 🎯 Design Decisions & Tradeoffs

Building this in limited time meant making hard choices. Here's the honest breakdown:

### What I Chose To Build

- ✅ Deep emotional intelligence (competing chatbots feel robotic)
- ✅ Live document extraction (biggest differentiator)
- ✅ Multi-college architecture (proves platform scalability)
- ✅ Bilingual support (Indian college reality)

### What I Deliberately Skipped

- ❌ User authentication — Out of scope. Colleges would integrate their existing SSO in production.
- ❌ LMS integration — Requires college API access that isn't accessible in short timeframes. Manual document upload proves the concept.
- ❌ Vector database / RAG — Groq's context window is sufficient for policy databases up to 8000 chars.
- ❌ Faculty features — Different product entirely. Roadmap item.
- ❌ Custom AI training — Prompt engineering + LLaMA 3 handles the domain well.

### Trade-offs I Accept

- ⚠️ Free tier rate limits (6000 TPM) — Handled via smart chunking with delays
- ⚠️ Chat history in localStorage — Simpler than DB, sufficient for demo
- ⚠️ Manual college onboarding — But 60 seconds via PDF drop, not a real limitation

---

## 🎨 UI Highlights

- **Design System** — All colors, fonts, spacing defined once, used everywhere
- **Inter Font** — The typography of choice for modern products (Vercel, Notion, GitHub)
- **Semantic Colors** — Category-coded badges, status-based notifications
- **Dark Mode** — Persistent across sessions, works on both chat and admin
- **Micro-interactions** — Hover states, fade-ins, smooth transitions
- **Empty States** — Suggestion cards guide new users
- **Real-time Feedback** — Live typing dots, progress bars, streaming updates

---

## 🔮 Future Roadmap

**Short Term**

- Mobile responsive design
- Chat embedding as an iframe widget for LMS integration
- Search across chat history
- Export conversations as PDF

**Medium Term**

- College admin authentication (SSO)
- Faculty-facing features (assignment analysis, question bank generation)
- Voice input for accessibility
- WhatsApp integration

**Long Term**

- Real LMS API integrations (Moodle, Blackboard, Google Classroom)
- Anonymous mental health analytics for college counselors
- Multi-language expansion (Tamil, Marathi, Bengali)
- Fine-tuned model specifically for Indian college contexts

---

## 📊 By The Numbers

- **6 emotional states** — Detected and handled
- **4 policy categories** — Auto-classified
- **24 policies** — Extractable from a 7-page PDF in ~2 minutes
- **0 credit card required** — Full stack runs on free tiers

---

## 📝 License

MIT License — free to use, modify, and adapt.

Please give credit if you build on this. And if you're using it for your college — reach out. I'd love to hear about it.

---

## 💌 Contact

Built with 💙 for every student who's ever felt alone at 2 AM.

If you want to collaborate, ask questions, or share how you're using CampusAid:

- GitHub: [https://github.com/Shivam-4039]
- LinkedIn: [https://www.linkedin.com/in/shivam-aditya-singh-24a203244/]
- Email: [shivamaditya_singh25@mru.ac.in]

---

**CampusAid — because no student should have to figure it out alone.** 🎓✨