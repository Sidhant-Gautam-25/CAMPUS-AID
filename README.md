# CampusAid

> An emotionally intelligent AI companion for college students with a smart onboarding platform that makes it easy for any institution to deploy.

CampusAid is an AI-powered chatbot that helps college students navigate policies, deadlines, mental health concerns, and everyday campus life. Unlike generic chatbots, it understands each college's specific rules and responds with genuine empathy, from simple questions to crisis situations.

---

## Why CampusAid?

College life can feel overwhelming at times. It can be 2 AM with an exam tomorrow, a missed internal test, or a panic moment. Sometimes the problem is a financial issue, and the student does not know how to talk to parents or whether a fee deferral is possible. Other times the pressure builds until it feels like quitting.

Existing solutions often let students down. Emailing college staff can take days for a reply. Google provides general information that is not specific to the student's own college. ChatGPT does not know the college's policies. Friends may be asleep or may not have the right information.

CampusAid bridges that gap by knowing the college, recognizing the student's emotional state, and offering guidance that is grounded in the college's own policies.

---

## Key Features

### Emotionally Intelligent AI

CampusAid detects six emotional states: casual, confused, stressed, frustrated, distressed, and crisis. It adjusts the tone and response style based on the detected emotion, gives empathetic support, and avoids a heavy information dump unless the student is ready for it. In crisis situations, it can escalate immediately with helpline information.

### Multi-College Support

Each college receives an isolated instance with its own policies, stored in separate JSON files. This design keeps college data clean and makes it easy to add a new college by creating one new file rather than changing the application code.

### Smart Onboarding

Administrators can upload PDF or DOCX handbooks and the system will extract policies automatically. The AI categorizes policies into academic, financial, administrative, and emotional groups, streams extraction progress in real time, and allows review and approval before the policies are added.

### Document Q&A for Students

Students can upload their own study materials, such as PDFs, and ask questions about those documents. The AI uses the uploaded document as the primary context when answering questions, making responses focused and relevant.

### Bilingual Support

CampusAid detects Hindi, English, and Hinglish automatically. It matches the student's language without requiring manual switching.

### Chat Interface

The student chat interface stores conversation history in the sidebar, generates titles automatically, supports multiple chats, shows typing indicators, timestamps messages, and renders markdown.

### Admin Dashboard

The admin dashboard provides policy statistics, category filters, real-time search, delete confirmation, and instant bot updates when new policies are added.

---

## Demo Scenarios

In one scenario, a stressed student asks for help with an exam tomorrow. The bot acknowledges the anxiety and offers a time-managed study plan with next steps. In another case, a student facing a fee problem receives a response in Hinglish with practical advice and an offer to draft a fee deferral application.

If a student writes something that suggests they are in crisis, the bot responds with warmth, crisis helplines, and a gentle check-in. For onboarding, an admin can upload a 7-page handbook, and the AI can extract policies, let the admin approve them, and use the new policies immediately in student responses.

---

## Architecture

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

The data flow for chat begins when the student sends a message through the frontend. The frontend calls the Flask `/chat` endpoint with the message, the college ID, and any optional document. Flask builds the system prompt using the college policies and the AI personality, then sends the request to Groq LLaMA 3 and returns the response.

For smart onboarding, the admin uploads a PDF and Flask extracts text using PyPDF2 or python-docx. The text is split into chunks and sent to the AI with a policy extraction prompt. The AI returns structured policy data, which is streamed to the frontend while the admin reviews and approves it.

---

## Tech Stack

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

This project is designed to work on free-tier services.

---

## Project Structure

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
│   └── design-system.css     # Shared design tokens and styles
│
└── templates/
    ├── index.html            # Student chat interface
    └── admin.html            # Admin dashboard
```

---

## Local Setup

### Prerequisites

Python 3.10 or later is required. You also need a free Groq API key from [console.groq.com](https://console.groq.com).

### Installation

First clone the repository and change into the project folder.

```bash
git clone https://github.com/YourUsername/campusaid.git
cd campusaid
```

Create and activate a virtual environment.

```bash
python -m venv venv
venv\Scripts\activate      # Windows
source venv/bin/activate   # Mac/Linux
```

Install the Python dependencies.

```bash
pip install -r requirements.txt
```

Create a `.env` file in the project root with your Groq API key.

```
GROQ_API_KEY=your_groq_api_key_here
```

---

## 📝 Note for Shivam's repo

This README has been updated with the CampusAid project details and local setup instructions. The repository now contains the Flask app, admin routes, college JSON data, and frontend templates for CampusAid.


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