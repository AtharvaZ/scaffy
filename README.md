# Scaffy

**AI-powered assignment scaffolder that breaks down programming assignments into manageable tasks**

Scaffy is an intelligent learning tool that helps students tackle programming assignments by breaking them down into smaller, manageable tasks with starter code, hints, and live code execution.

## 🚀 Features

- **Assignment Parsing**: Upload PDFs or paste assignment text to automatically break down complex assignments into ordered tasks with dependencies
- **Starter Code Generation**: Get AI-generated starter code templates with TODOs and concept examples tailored to your experience level
- **Live Code Execution**: Run Python and JavaScript code directly in the browser using Piston API with real-time output and error handling
- **Progressive Hints**: Get contextual hints that become more specific as you ask for help multiple times
- **Concept Examples**: On-demand examples of programming concepts in your known language to help bridge to the target language
- **PDF Upload**: Extract text from assignment PDFs automatically
- **Dark Mode**: Beautiful dark/light theme support
- **Interactive UI**: Modern, responsive interface with animations and progress indicators

## 🛠️ Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **Anthropic Claude API** - AI agent for parsing, code generation, and hints
- **Piston API** - Code execution service for running Python, JavaScript, and other languages
- **Uvicorn** - ASGI server
- **pdfplumber** - PDF text extraction
- **Pydantic** - Data validation and settings management

### Frontend
- **React 18** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool and dev server
- **React Router** - Client-side routing
- **Monaco Editor** - Code editor (VS Code editor in the browser)
- **Tailwind CSS** - Utility-first CSS framework
- **Zustand** - State management
- **Three.js** - 3D animations

## 📁 Project Structure

```
Scaffy_frontend/
├── backend/                 # Python FastAPI backend
│   ├── agents/             # AI agents for different tasks
│   │   ├── parser_agent.py         # Breaks down assignments
│   │   ├── codegen_agent.py        # Generates starter code
│   │   ├── live_helper.py          # Provides hints
│   │   └── concept_example.py      # Generates concept examples
│   ├── services/           # Core services
│   │   ├── anthropic_client.py     # Claude API client
│   │   ├── code_runner.py          # Code execution service (Piston API)
│   │   └── pdf_extractor.py        # PDF text extraction
│   ├── pyd_models/         # Pydantic schemas
│   │   └── schemas.py              # API request/response models
│   ├── utils/              # Utility functions
│   │   ├── agent_prompts.py        # AI prompts
│   │   └── json_parser.py          # JSON extraction utilities
│   └── main.py             # FastAPI application entry point
│
├── frontend/               # React TypeScript frontend
│   ├── src/
│   │   ├── api/            # API client and endpoints
│   │   ├── components/     # React components
│   │   │   ├── CodeEditor.tsx      # Monaco editor wrapper
│   │   │   ├── ChatBot.tsx         # AI chat interface
│   │   │   ├── PDFUploadZone.tsx   # PDF upload component
│   │   │   └── ui/                 # Reusable UI components
│   │   ├── pages/          # Page components
│   │   │   ├── LandingPage.tsx     # Home page
│   │   │   ├── TaskPage.tsx        # Task breakdown view
│   │   │   └── EditorPage.tsx      # Code editor page
│   │   ├── store/          # Zustand state management
│   │   └── types/          # TypeScript type definitions
│   └── package.json
│
└── README.md
```

## 🏃 Getting Started

### Prerequisites

- **Python 3.8+** (for backend)
- **Node.js 18+** and **npm** (for frontend - required for React and Vite build tools)
- **Anthropic API Key** - Get one from [Anthropic Console](https://console.anthropic.com/)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Scaffy_frontend
   ```

2. **Set up the backend**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Set up the frontend**
   ```bash
   cd ../frontend
   npm install
   ```

4. **Configure environment variables**

   Create a `.env` file in the `backend/` directory:
   ```env
   ANTHROPIC_API_KEY=your_anthropic_api_key_here
   ```

   Create a `.env` file in the `frontend/` directory (optional, defaults to `http://localhost:8000`):
   ```env
   VITE_API_BASE_URL=http://localhost:8000
   ```

### Running the Application

1. **Start the backend server**
   ```bash
   cd backend
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   python main.py
   ```
   The backend will run on `http://localhost:8000`

2. **Start the frontend development server** (in a new terminal)
   ```bash
   cd frontend
   npm run dev
   ```
   The frontend will run on `http://localhost:5173` (or another port if 5173 is busy)

3. **Open your browser**
   Navigate to `http://localhost:5173` to use the application

## 📡 API Endpoints

### Health Check
- `GET /` - Simple health check
- `GET /health` - Detailed health check with agent status

### Assignment Processing
- `POST /parse-assignment` - Break down assignment into tasks
- `POST /generate-starter-code` - Generate starter code for a task
- `POST /extract-pdf-text` - Extract text from uploaded PDF

### Learning Support
- `POST /get-hint` - Get contextual hint for current task
- `POST /get-concept-example` - Get example of a programming concept

### Code Execution
- `POST /run-code` - Execute Python or JavaScript code (powered by Piston API)

See the FastAPI docs at `http://localhost:8000/docs` for detailed API documentation.

## 🎯 How It Works

1. **Upload or Paste Assignment**: Students provide their assignment (PDF or text)
2. **Task Breakdown**: AI agent analyzes the assignment and creates an ordered list of tasks with dependencies
3. **Starter Code**: For each task, AI generates starter code with TODOs and concept examples
4. **Code & Learn**: Students work through tasks in the integrated code editor
5. **Get Help**: When stuck, students can ask for hints that become progressively more specific
6. **Run & Test**: Execute code directly in the browser to see results and catch errors early

## 🔧 Development

### Backend Development
```bash
cd backend
source venv/bin/activate
python main.py  # Runs with auto-reload enabled
```

### Frontend Development
```bash
cd frontend
npm run dev     # Development server with hot reload
npm run build   # Production build
npm run preview # Preview production build
```

### Code Style
- Backend: Follow PEP 8 Python style guide
- Frontend: TypeScript with ESLint configuration

## 📝 Environment Variables

### Backend (.env)
- `ANTHROPIC_API_KEY` (required) - Your Anthropic API key for Claude
- `PISTON_API_URL` (optional) - Piston API endpoint, defaults to `https://emkc.org/api/v2/piston`

### Frontend (.env)
- `VITE_API_BASE_URL` (optional) - Backend API URL, defaults to `http://localhost:8000`

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

MIT License

## �� Acknowledgments

- Built with [Anthropic Claude](https://www.anthropic.com/) for AI capabilities
- Code execution powered by [Piston API](https://emkc.org/) (Engineer Man's Code Execution API)
- UI components inspired by modern design systems
- Code editor powered by [Monaco Editor](https://microsoft.github.io/monaco-editor/)

---

**Made with ❤️ for students learning to code**
