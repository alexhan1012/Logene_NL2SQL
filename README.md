# PathQC NL2SQL

A Natural Language to SQL application for the PathQC 2.0 pathology information system.

## Setup

### Backend

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your API keys
uvicorn main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Environment Variables

Copy `backend/.env.example` to `backend/.env` and fill in:

- `ARK_API_KEY`: Your Volcano Engine API key
- `ARK_MODEL`: Model name (default: doubao-pro-32k-241215)
- `ARK_BASE_URL`: API base URL (default: https://ark.cn-beijing.volces.com/api/v3)

## Features

- Natural language to SQL conversion using Volcano Engine LLM
- Skill-based table selection (2-step LLM process)
- Conversation history stored in SQLite
- Interactive table relationship diagram
- Full table schema browser
- React + TypeScript frontend with Ant Design
