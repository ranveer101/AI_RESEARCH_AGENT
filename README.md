# AI Research Assistant

A full-stack AI research assistant that searches the web, reads sources, writes a structured research report, and produces a critic review.

## Tech Stack

- Python
- FastAPI
- LangGraph
- LangChain
- Mistral AI
- Tavily Search
- Chroma / Hugging Face embeddings
- HTML, CSS, JavaScript

## Setup

1. Open PowerShell in this folder.

2. Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\activate
```

3. Install dependencies:

```powershell
pip install -r requirements.txt
```

4. Create a `.env` file from `.env.example` and add your API keys:

```powershell
copy .env.example .env
```

5. Start the app:

```powershell
python -m uvicorn api:app --host 127.0.0.1 --port 8000
```

6. Open the browser:

```text
http://127.0.0.1:8000/
```

## Notes

- Do not commit or share your real `.env` file.
- The first run may download the embedding model, so it can take longer.
- If port `8000` is busy, use another port, for example:

```powershell
python -m uvicorn api:app --host 127.0.0.1 --port 8001
```

## Deployment

This project is optimized for deployment on **Render**, but it also works on Heroku, Railway, or any platform supporting Python/FastAPI.

### Deploying to Render (Recommended)

1.  **Push to GitHub**: Push your project to a GitHub repository.
2.  **Create Web Service**: In the Render dashboard, create a new "Web Service" and connect your repository.
3.  **Automatic Setup**: Render will automatically detect the `render.yaml` file in the root directory and configure the build and start commands.
4.  **Environment Variables**: You will be prompted to enter your API keys:
    *   `MISTRAL_API_KEY`
    *   `TAVILY_API_KEY`
5.  **Health Check**: The service uses `/health` for monitoring.

### Alternative Deployment (Manual)

If you are not using `render.yaml`, use the following settings:
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn api:app --host 0.0.0.0 --port $PORT`
- **Environment Variables**: Add `MISTRAL_API_KEY` and `TAVILY_API_KEY`.
