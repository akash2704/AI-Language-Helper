# AI Language Helper

AI Language Helper is a full-stack, AI-powered language learning platform. It provides interactive chat-based learning, real-time corrections, and personalized feedback to help users improve their language skills.

## Features
- **AI-Powered Chat**: Practice conversations with an AI that provides instant corrections and suggestions.
- **User Authentication**: Secure login, registration, and session management.
- **Personalized Feedback**: Receive feedback on mistakes and track your progress.
- **Multiple Languages & Levels**: Choose your target language and proficiency level.
- **Modern UI**: Built with Next.js, React, and Tailwind CSS for a fast, responsive experience.

## Project Structure
```
AI-language-helper/
├── Backend/                  # Python FastAPI backend
│   ├── app.py                # Main API server
│   ├── chatbot.py            # AI chat logic
│   ├── Dockerfile            # Backend containerization
│   ├── pyproject.toml        # Python dependencies
│   └── ...                   # Other backend files
├── language-learning-frontend/ # Next.js frontend
│   ├── src/                  # React/Next.js source code
│   ├── package.json          # JS dependencies
│   ├── tailwind.config.js    # Tailwind CSS config
│   └── ...                   # Other frontend files
└── README.md                 # Project overview (this file)
```

## Getting Started

### Backend (FastAPI)
1. Go to the `Backend` directory:
   ```bash
   cd Backend
   ```
2. (Recommended) Create a virtual environment and activate it.
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   # or if using poetry
   poetry install --no-root
   ```
4. Run the backend server:
   ```bash
   uvicorn app:app --reload
   ```

### Frontend (Next.js)
1. Go to the `language-learning-frontend` directory:
   ```bash
   cd language-learning-frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   # or
   yarn install
   ```
3. Start the development server:
   ```bash
   npm run dev
   # or
   yarn dev
   ```
4. Open [http://localhost:3000](http://localhost:3000) in your browser.

## Deployment
- The backend can be containerized using the provided `Dockerfile`.
- The frontend is ready for deployment on Vercel, Netlify, or any static hosting supporting Next.js.

## Requirements
- Python 3.8+
- Node.js 18+

## License
This project is for educational purposes. See individual files for license details.

---

*Built with ❤️ by Akash Ajay Kallai.*
