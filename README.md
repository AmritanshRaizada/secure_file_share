# Secure File Sharing System

A REST API for secure file sharing between operation users and client users, built with FastAPI and MongoDB.

## Features

- **User Types**:
  - Operation Users (upload files)
  - Client Users (download files)
- **Authentication**: JWT token-based security
- **File Restrictions**: 
  - Only `.pptx`, `.docx`, and `.xlsx` files allowed for upload
- **Secure Downloads**:
  - Time-limited, encrypted download URLs
  - Role-based access control

## Tech Stack

- **Backend**: Python 3.10+, FastAPI
- **Database**: MongoDB
- **Authentication**: JWT
- **File Validation**: python-magic

## Setup

### Prerequisites

- Python 3.10+
- MongoDB (local or Atlas)
- SMTP server (for email verification - optional)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/secure-file-share.git
   cd secure-file-share

   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # OR
   venv\Scripts\activate    # Windows

   pip install -r requirements.txt

   cp .env.example .env
   # Edit .env with your configuration

   uvicorn app.main:app --reload

API Documentation
Access interactive docs at:

Swagger UI: http://localhost:8000/docs

Redoc: http://localhost:8000/redoc

Environment Variables
Variable	Required	Description
MONGODB_URL	Yes	MongoDB connection string
DATABASE_NAME	Yes	Database name
SECRET_KEY	Yes	JWT secret key
ALGORITHM	No	JWT algorithm (default: HS256)
ACCESS_TOKEN_EXPIRE_MINUTES	No	Token expiry (default: 30)
Email-related variables	No	Required for email verification
Testing
Run tests with:

bash
pytest
Deployment
Production Recommendations:
Use Gunicorn with Uvicorn workers:

bash
gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app
Configure HTTPS

Set proper CORS policies

Implement rate limiting

Project Structure
text
secure_file_share/
├── app/               # Application code
│   ├── models/        # Database models
│   ├── schemas/       # Pydantic models
│   ├── utils/         # Helper functions
│   ├── routes/        # API endpoints
│   └── config.py      # Configuration
├── tests/             # Test cases
├── requirements.txt   # Dependencies
└── .env               # Environment variables

### Key Sections Included:
1. **Project Overview** - Brief description
2. **Features** - Core functionality
3. **Setup Instructions** - Step-by-step installation
4. **API Documentation** - How to access docs
5. **Configuration** - Environment variables
6. **Testing** - How to run tests
7. **Deployment** - Production recommendations
8. **Project Structure** - Directory layout

### Customization Tips:
1. Replace `yourusername` with your actual GitHub username
2. Add your license file if not using MIT
3. Include any additional deployment instructions specific to your setup
4. Add contributor guidelines if it's an open-source project

Would you like me to add any specific additional sections like:
- API endpoint examples?
- Screenshots of the documentation interface?
- Detailed contributor guidelines?