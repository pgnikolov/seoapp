# SEO Keyword Extractor

A full-stack web application for crawling websites and extracting keywords/phrases, similar to SEMrush.

## Features
- **Async Crawler**: Efficiently crawls relevant pages while respecting `robots.txt` and rate limits.
- **Content Extraction**: Extracts text from titles, meta tags, headings, and body.
- **Intelligent Scoring**: Ranks keywords using TF-IDF and weighted importance of HTML zones (Title > H1 > Body).
- **Intent Detection**: Categorizes keywords as Commercial, Informational, or Navigational.
- **Language Support**: Auto-detects and supports English and Bulgarian.
- **Modern Dashboard**: Responsive UI with filters, sorting, and keyword insights.

## Tech Stack
- **Backend**: Python (FastAPI), httpx, BeautifulSoup4, scikit-learn, SQLite.
- **Frontend**: React, Tailwind CSS, Lucide Icons.
- **Infrastructure**: Docker, docker-compose.

## How to Run

### Option 1: Using Docker (Recommended)
1. Make sure you have **Docker** installed.
2. Clone the repository.
3. Check if you have the Docker Compose plugin (v2) or the standalone `docker-compose` (v1):
   - For **Docker Compose v2** (recommended):
     ```bash
     docker compose up --build
     ```
   - For **Docker Compose v1**:
     ```bash
     docker-compose up --build
     ```

### Option 2: Running Locally (No Docker)

#### Prerequisites
- **Python 3.10+**
- **Node.js 18+**

#### 1. Backend Setup
```bash
cd backend
# Create a virtual environment
python -m venv venv
# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate
# Install dependencies
pip install -r requirements.txt
# (Optional) Download NLTK data if it doesn't happen automatically
# python -c "import nltk; nltk.download('stopwords')"
# Run the server
uvicorn app.main:app --reload --port 8000
```

#### 2. Frontend Setup
```bash
cd frontend
# Install dependencies
npm install
# Start the application
npm start
```
The frontend will be available at `http://localhost:3000`.

### Troubleshooting
If you see `Command 'docker-compose' not found` when using Option 1, you may need to install it. 

If you encounter `EACCES: permission denied` when running `npm install` (Option 2), it's likely because `node_modules` was created by Docker with root permissions. Fix it by running:
```bash
sudo rm -rf frontend/node_modules
```
Then try `npm install` again.

On **Ubuntu/Debian**, you can install the Docker Compose plugin (v2) with:
```bash
sudo apt update
sudo apt install docker-compose-v2
```
Alternatively, for the standalone version:
```bash
sudo apt install docker-compose
```

4. Open your browser at:
   - Frontend: [http://localhost:3000](http://localhost:3000)
   - Backend API Docs: [http://localhost:8000/docs](http://localhost:8000/docs)

## Project Structure
- `backend/`: FastAPI application code, crawler, and keyword analyzer.
- `frontend/`: React application and dashboard.
- `docker-compose.yml`: Orchestrates the services.

## Development & Testing
To run backend tests:
```bash
cd backend
pip install -r requirements.txt
pytest
```
