# FinanceFlareAI

AI-powered personal budget tracker with automatic expense categorization and spending insights.

## Features

- 🔐 JWT authentication
- 💰 Transaction management (income/expenses)
- 🤖 AI-powered categorization using OpenAI
- 📊 Interactive dashboard with charts
- 🌙 Dark/light mode
- 📱 Responsive design

## Tech Stack

- **Frontend**: React 19, TypeScript, Vite, Tailwind CSS, Recharts
- **Backend**: FastAPI, SQLAlchemy, PostgreSQL, JWT
- **AI**: OpenAI GPT for transaction categorization

## Quick Start

1. **Clone and setup**
   ```bash
   git clone <repository-url>
   cd FinanceFlareAI
   cp env.example .env
   # Add your OpenAI API key to .env
   ```

2. **Start with Docker**
   ```bash
   docker-compose up --build -d
   ```

3. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

## Environment Variables

Create `.env` file with:
```env
OPENAI_API_KEY=your_openai_api_key_here
SECRET_KEY=your_secret_key_here
DATABASE_URL=postgresql://financeflareai_user:financeflareai_password@postgres:5432/financeflareai
```

## Development

```bash
# Frontend
cd frontend
npm install
npm run dev

# Backend
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```
