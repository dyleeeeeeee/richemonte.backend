# Backend Cleanup Plan

## 🗑️ Files to Delete (Redundant)

### **Old Monolithic Files**
- ❌ `app.py` (22KB) - Original monolithic version, replaced by modular structure
- ❌ `app_modular.py` (16KB) - Intermediate version, superseded by app_new.py
- ❌ `seed.py` (7KB) - Original version, replaced by seed_new.py

### **Standalone Module Files (Duplicates)**
- ❌ `auth.py` (2KB) - Duplicate of `auth/` directory
- ❌ `config.py` (808 bytes) - Duplicate of `core/config.py`
- ❌ `services.py` (2.4KB) - Duplicate of `services/` directory
- ❌ `utils.py` (1.5KB) - Duplicate of `utils/` directory
- ❌ `email_templates.py` (4.3KB) - Duplicate of `templates/email_templates.py`

**Total files to delete: 8**

---

## ✅ Files to Keep (Production)

### **Main Application**
- ✅ `app_new.py` → Rename to `app.py` (production main file)
- ✅ `seed_new.py` → Rename to `seed.py` (production seeding)

### **Directory Modules**
- ✅ `core/` - Configuration and database
- ✅ `auth/` - Authentication logic
- ✅ `utils/` - Utility functions
- ✅ `services/` - Business logic
- ✅ `templates/` - Email templates

### **Configuration Files**
- ✅ `.env.example` - Environment template
- ✅ `.gitignore` - Git ignore rules
- ✅ `requirements.txt` - Dependencies
- ✅ `schema.sql` - Database schema
- ✅ `railway.toml` - Railway deployment
- ✅ `Procfile` - Heroku/Render deployment
- ✅ `runtime.txt` - Python version

---

## 🔧 Actions Required

1. **Backup old files** (move to `_archive/` directory)
2. **Delete standalone duplicates**
3. **Rename production files**
4. **Verify imports still work**
5. **Update deployment configs if needed**

---

## 📊 Final Structure

```
backend/
├── core/
│   ├── __init__.py
│   ├── config.py
│   └── database.py
├── auth/
│   ├── __init__.py
│   ├── jwt_handler.py
│   └── middleware.py
├── utils/
│   ├── __init__.py
│   ├── validators.py
│   └── generators.py
├── services/
│   ├── __init__.py
│   ├── email_service.py
│   ├── notification_service.py
│   └── user_service.py
├── templates/
│   ├── __init__.py
│   └── email_templates.py
├── app.py              # ← Renamed from app_new.py
├── seed.py             # ← Renamed from seed_new.py
├── schema.sql
├── requirements.txt
├── .env.example
├── .gitignore
├── railway.toml
├── Procfile
└── runtime.txt
```

**Clean, production-ready structure with no duplicates.**
