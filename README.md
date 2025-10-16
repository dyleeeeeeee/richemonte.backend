# Concierge Bank Backend

Luxury banking platform backend built with Python Quart, Supabase, and Resend.

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env with your credentials

# Run development server
python app.py

# Visit: http://localhost:5000/health
```

## 📁 Project Structure

```
backend/
├── app.py                    # Main application
├── run.py                    # Production entry point
├── schema.sql                # Database schema
├── seed.py                   # Data seeding script
├── routes/                   # API endpoints (9 modules)
├── core/                     # Config & database
├── auth/                     # Authentication logic
├── services/                 # Business logic (email, notifications)
├── utils/                    # Utilities (generators, validators, DB helpers)
└── templates/                # Email templates
```

## 🔌 API Endpoints

**Authentication** (4 endpoints)
- POST /api/auth/register, /api/auth/login, /api/auth/logout
- GET /api/auth/me

**Core Banking** (13 endpoints)
- Accounts, Cards, Transfers, Bills, Checks, Beneficiaries

**User Services** (5 endpoints)  
- Settings, Notifications, Statements

## 🌐 Deployment

**Procfile** included for Railway/Render deployment.

## 📚 Recent Updates

- `AUTH_SETTINGS_SYNC_COMPLETE.md` - Auth overhaul & settings implementation
- `UX_CONSISTENCY_COMPLETE.md` - Dashboard UX standardization
- `schema.sql` - Database schema reference

## ✅ Status

- **Auth**: Pure JWT with Bearer tokens ✅
- **Settings**: Profile, Security, Notifications - All persistent ✅
- **UX**: Light glassmorphic mode across all pages ✅
- **Production Ready**: Yes ✅
