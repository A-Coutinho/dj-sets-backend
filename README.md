# 🎶 Backend - DJ Sets API

This is the **FastAPI backend** for the DJ Sets project.  
It integrates with Dropbox to serve MP3s, cover images, and tracklists securely.

---

## ⚡ Features

-   List all available DJ sets with metadata (name, cover, tracklist, link).
-   Stream MP3 files directly from Dropbox via API.
-   Return cover images and text tracklists without exposing Dropbox cookies.
-   Proper CORS configuration for the React frontend.

---

## 🛠️ Tech Stack

-   **FastAPI**
-   **Dropbox API v2**
-   **Uvicorn**
-   **Python 3.11+**

---

## 📂 Project Structure

```plaintext
backend/
├── main.py             # FastAPI entrypoint
├── dropbox.py          # Dropbox API integration
├── requirements.txt    # Python dependencies
├── .env.example        # Example environment variables
└── README.md
```

## 🛠️ Setup & Development

### 1. Clone repo

```bash
git clone https://github.com/yourusername/djsets-backend.git
cd djsets-backend
```

### 2. Create virtual environment

```bash
python -m venv venv
source venv/bin/activate # Linux / macOS
venv\Scripts\activate # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run development server

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8080
```

### 5. Environment Variables

```bash
DROPBOX_CLIENT_ID=your_client_id
DROPBOX_CLIENT_SECRET=your_client_secret
DROPBOX_REFRESH_TOKEN=your_refresh_token
```

### 6. API Endpoints

```bash
GET /files
```

Returns the list of available DJ sets with metadata.

```bash
GET /file?path=/example.mp3
```

Streams a file (MP3, JPG, or TXT) from Dropbox with correct Content-Type.

📸 Demo
[Backend is deployed here](multiple-fast-api.fly.dev)
