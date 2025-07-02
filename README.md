# Secure File Sharing System

![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![MongoDB](https://img.shields.io/badge/MongoDB-4EA94B?style=for-the-badge&logo=mongodb&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)

A secure REST API for file sharing between operation users (upload) and client users (download), featuring JWT authentication and encrypted download URLs.

## Features

- **Role-based access control**
  - 👨‍💼 Operation Users: Upload files (PPTX, DOCX, XLSX only)
  - 👥 Client Users: Download files, list available files
- **Secure authentication** with JWT tokens
- **Email verification** for client users
- **Encrypted download URLs** with expiration
- **File type validation** using magic numbers

## Quick Start

### 1. Prerequisites
- Python 3.10+
- MongoDB instance (local or cloud)
- (Optional) SMTP server for email verification

### 2. Installation
```bash
# Clone repository
git clone https://github.com/yourusername/secure-file-share.git
cd secure-file-share

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# OR
venv\Scripts\activate    # Windows

# Install dependencies
pip install -r requirements.txt

cp .env.example .env

MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=secure_file_share
SECRET_KEY=your-very-secure-key-generate-with-openssl-rand-hex-32

# Email settings (optional)
SMTP_SERVER=
SMTP_PORT=
SMTP_USERNAME=
SMTP_PASSWORD=
FROM_EMAIL=

uvicorn app.main:app --reload

Access the API docs at:
🔗 http://localhost:8000/docs

API Endpoints
Method	Endpoint	Description	Access
POST	/auth/signup	Client user registration	Public
GET	/auth/verify-email	Email verification	Public
POST	/auth/login	User login	Public
POST	/files/upload	Upload files	Ops User
GET	/files/download/{file_id}	Generate download link	Client User
GET	/files/download	Download file	Valid Token
GET	/files/list	List available files	Client User

pytest

gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app

ACCESS_TOKEN_EXPIRE_MINUTES=30
ALGORITHM=HS256
# Add HTTPS configuration

secure_file_share/
├── app/
│   ├── models/        # MongoDB models
│   ├── routes/        # API endpoints
│   ├── schemas/       # Pydantic models
│   ├── utils/         # Helper functions
│   ├── config.py      # App configuration
│   └── main.py       # FastAPI app
├── tests/             # Test cases
├── .env.example       # Env template
├── requirements.txt   # Dependencies
└── README.md          # This file 
```
License
Amritansh Raizada


