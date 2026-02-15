# 🌍 Environment Configuration Guide

## Overview

The unified platform now supports **three separate environments** with isolated configurations:

- **Development** - Local development with debug enabled
- **QA/Staging** - Testing environment with production-like settings
- **Production** - Live production environment with strict security

Each environment has its own:
- Configuration file (`.env.dev`, `.env.qa`, `.env.prod`)
- Database settings
- API credentials
- Security settings
- Feature flags

---

## 📁 File Structure

```
unified_platform/
├── .env.example          # Template file (committed to git)
├── .env                  # Active environment (symlink, git-ignored)
├── .env.dev             # Development config (git-ignored)
├── .env.qa              # QA/staging config (git-ignored)
├── .env.prod            # Production config (git-ignored)
├── switch-env.sh        # Environment switcher script
├── common/
│   └── config/
│       ├── env_loader.py    # Environment loader module
│       ├── settings.py      # Settings with environment support
│       └── bot_config.py    # Bot configuration
└── ohgrt_api/
    └── config.py        # API configuration
```

---

## 🚀 Quick Start

### 1. Initial Setup

Create environment files from template:

```bash
# Navigate to project root
cd unified_platform

# Create all environment files
cp .env.example .env.dev
cp .env.example .env.qa
cp .env.example .env.prod
```

Or use the automatic setup:

```bash
./switch-env.sh create
```

### 2. Configure Each Environment

Edit each file with environment-specific credentials:

**Development (`.env.dev`):**
```bash
nano .env.dev
# Set development credentials
# Use local database, test API keys, etc.
```

**QA (`.env.qa`):**
```bash
nano .env.qa
# Set QA/staging credentials
# Use staging database, QA API keys, etc.
```

**Production (`.env.prod`):**
```bash
nano .env.prod
# Set production credentials
# Use production database, live API keys, etc.
# ⚠️  ENSURE ALL KEYS ARE SECURE!
```

### 3. Switch Environment

Use the switcher script:

```bash
# Switch to development
./switch-env.sh dev

# Switch to QA
./switch-env.sh qa

# Switch to production
./switch-env.sh prod

# Check current environment
./switch-env.sh status
```

### 4. Verify Configuration

```bash
# Check which environment is active
cat .env | grep ENVIRONMENT

# Or use the status command
./switch-env.sh status
```

### 5. Start Application

```bash
# The application will automatically load the correct environment
python main.py

# Or for specific components
python run_bot.py
python run_api.py
```

---

## 🔧 Environment Switcher Script

### Usage

```bash
./switch-env.sh [command]
```

### Commands

| Command | Description |
|---------|-------------|
| `dev` | Switch to development environment |
| `qa` | Switch to QA/staging environment |
| `prod` | Switch to production environment |
| `status` | Show current environment status |
| `create` | Create missing environment files from template |
| `help` | Show help message |

### Examples

```bash
# Switch environments
./switch-env.sh dev        # → .env links to .env.dev
./switch-env.sh qa         # → .env links to .env.qa
./switch-env.sh prod       # → .env links to .env.prod

# Check status
./switch-env.sh status

# Output:
# ==========================================
#    Environment Switcher
# ==========================================
#
# Current Environment Status:
# ─────────────────────────────────────────
# Environment: development
# Type: Symlink
# Target: .env.dev
# ─────────────────────────────────────────
```

---

## 🎯 Environment-Specific Settings

### Development Environment (`.env.dev`)

**Purpose:** Local development and debugging

**Key Settings:**
```bash
ENVIRONMENT=development
LOG_LEVEL=DEBUG
CORS_ORIGINS=*
RATE_LIMIT_ENABLED=false
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=1440  # 24 hours
POSTGRES_HOST=localhost
POSTGRES_DB=unified_platform_dev
```

**Characteristics:**
- ✅ Verbose logging (DEBUG)
- ✅ CORS open to all origins
- ✅ Rate limiting disabled
- ✅ Long-lived tokens for convenience
- ✅ Local database
- ✅ Test API keys

### QA/Staging Environment (`.env.qa`)

**Purpose:** Testing and quality assurance

**Key Settings:**
```bash
ENVIRONMENT=qa
LOG_LEVEL=INFO
CORS_ORIGINS=https://qa.yourdomain.com,https://qa-admin.yourdomain.com
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS_PER_MINUTE=300
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60  # 1 hour
POSTGRES_HOST=qa-db-server.example.com
POSTGRES_DB=unified_platform_qa
```

**Characteristics:**
- ✅ Moderate logging (INFO)
- ✅ CORS restricted to QA domains
- ✅ Rate limiting enabled (moderate)
- ✅ Standard token expiration
- ✅ Staging database
- ✅ QA API keys

### Production Environment (`.env.prod`)

**Purpose:** Live production deployment

**Key Settings:**
```bash
ENVIRONMENT=production
LOG_LEVEL=WARNING
CORS_ORIGINS=https://yourdomain.com,https://admin.yourdomain.com
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS_PER_MINUTE=60
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=15  # 15 minutes
POSTGRES_HOST=prod-db-server.example.com
POSTGRES_DB=unified_platform_prod
```

**Characteristics:**
- ✅ Minimal logging (WARNING)
- ✅ CORS restricted to production domains
- ✅ Strict rate limiting
- ✅ Short-lived tokens for security
- ✅ Production database
- ✅ Live API keys
- ✅ Strong encryption keys
- ✅ Secure passwords

---

## 🔐 Security Best Practices

### Critical Production Settings

**⚠️  MUST CHANGE in Production:**

1. **JWT Secret Key**
   ```bash
   # Generate secure key:
   openssl rand -hex 32

   # Add to .env.prod:
   JWT_SECRET_KEY=<your-generated-key>
   ```

2. **Encryption Key**
   ```bash
   # Generate Fernet key:
   python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

   # Add to .env.prod:
   ENCRYPTION_KEY=<your-generated-key>
   ```

3. **Database Password**
   ```bash
   # Use strong password (min 32 chars)
   POSTGRES_PASSWORD=<strong-random-password>
   ```

4. **CORS Origins**
   ```bash
   # NEVER use "*" in production
   CORS_ORIGINS=https://yourdomain.com,https://api.yourdomain.com
   ```

### Never Commit

**Files to NEVER commit to git:**
- `.env`
- `.env.dev`
- `.env.qa`
- `.env.prod`
- `firebase-credentials*.json`
- Any file with actual credentials

**These are protected by `.gitignore`**

### Environment File Checklist

Before deploying to production, verify:

- [ ] All API keys are production keys
- [ ] Database credentials are secure
- [ ] JWT_SECRET_KEY is unique and secure (32+ chars)
- [ ] ENCRYPTION_KEY is unique and secure (32 chars)
- [ ] CORS_ORIGINS lists only your domains
- [ ] LOG_LEVEL is WARNING or ERROR
- [ ] Rate limiting is enabled and strict
- [ ] Token expiration is short (15 minutes)
- [ ] Firebase credentials path is correct
- [ ] No default passwords remain

---

## 🔄 Programmatic Usage

### In Python Code

The environment is automatically detected and loaded:

```python
from common.config.settings import settings, get_environment, is_production, is_development, is_qa

# Get current environment
current_env = get_environment()  # Returns: "development", "qa", or "production"

# Check environment
if is_production():
    print("Running in PRODUCTION mode")
elif is_qa():
    print("Running in QA mode")
elif is_development():
    print("Running in DEVELOPMENT mode")

# Access settings (automatically loaded from correct .env file)
print(f"Database: {settings.POSTGRES_DB}")
print(f"Log Level: {settings.LOG_LEVEL}")
```

### Manual Environment Loading

```python
from common.config.env_loader import load_environment

# Load specific environment
load_environment("production")

# Load and suppress output
load_environment("qa", verbose=False)

# Check current environment
from common.config.env_loader import get_current_environment
env = get_current_environment()
print(f"Running in: {env}")
```

### Environment Detection Priority

The system detects environment in this order:

1. **ENVIRONMENT environment variable**
   ```bash
   export ENVIRONMENT=production
   python main.py
   ```

2. **ENVIRONMENT in .env file**
   ```bash
   # .env file contains:
   ENVIRONMENT=development
   ```

3. **Default to development**

---

## 🛠️ Troubleshooting

### Problem: "Environment file not found"

**Solution:**
```bash
# Create missing files
./switch-env.sh create

# Or manually
cp .env.example .env.dev
cp .env.example .env.qa
cp .env.example .env.prod
```

### Problem: "Invalid environment"

**Error:**
```
ValueError: Invalid environment 'test'. Must be one of: development, qa, production
```

**Solution:**
Use only valid environment names: `development`, `qa`, `production`, or their aliases (`dev`, `staging`, `prod`)

### Problem: Application using wrong environment

**Diagnosis:**
```bash
# Check current environment
./switch-env.sh status

# Check .env content
cat .env | head -20
```

**Solution:**
```bash
# Switch to correct environment
./switch-env.sh [dev|qa|prod]

# Restart application
```

### Problem: Settings not updating

**Solution:**
```bash
# Restart application after switching environments
# Settings are cached, restart is required

# For development with auto-reload
uvicorn main:app --reload
```

### Problem: Permission denied on switch-env.sh

**Solution:**
```bash
chmod +x switch-env.sh
```

---

## 📊 Environment Comparison Table

| Feature | Development | QA | Production |
|---------|------------|-----|-----------|
| Log Level | DEBUG | INFO | WARNING |
| CORS | * (all) | Specific domains | Specific domains |
| Rate Limiting | Disabled | Moderate (300/min) | Strict (60/min) |
| Token Expiry | 24 hours | 1 hour | 15 minutes |
| Database | Local | Staging server | Production server |
| API Keys | Test keys | QA keys | Production keys |
| Debug Mode | Enabled | Disabled | Disabled |
| Error Details | Full stack traces | Limited | Minimal |
| Security Checks | Relaxed | Moderate | Strict |

---

## 🔍 Verification Commands

### Check Current Environment

```bash
# Using script
./switch-env.sh status

# Using environment variable
echo $ENVIRONMENT

# From .env file
grep ENVIRONMENT .env

# In Python
python -c "from common.config.settings import get_environment; print(get_environment())"
```

### Verify Configuration

```bash
# Check database connection string
python -c "from common.config.settings import settings; print(settings.database_url)"

# Check log level
python -c "from common.config.settings import settings; print(settings.LOG_LEVEL)"

# Check if production mode
python -c "from common.config.settings import is_production; print('Production:', is_production())"
```

---

## 🚦 Deployment Workflow

### Development → QA

```bash
# 1. Test locally
./switch-env.sh dev
python main.py
# Run tests

# 2. Switch to QA
./switch-env.sh qa

# 3. Deploy to QA server
git push qa-server main

# 4. Verify on QA
curl https://qa.yourdomain.com/health
```

### QA → Production

```bash
# 1. Final QA verification
./switch-env.sh qa
python -m pytest

# 2. Switch to production
./switch-env.sh prod

# 3. Security checklist
# ✅ Check all credentials
# ✅ Verify JWT secret
# ✅ Check CORS settings
# ✅ Verify rate limits

# 4. Deploy to production
git push production main

# 5. Verify deployment
curl https://yourdomain.com/health

# 6. Monitor logs
tail -f /var/log/app/production.log
```

---

## 📚 Additional Resources

### Related Files

- `common/config/env_loader.py` - Environment loading logic
- `common/config/settings.py` - Settings with environment support
- `ohgrt_api/config.py` - API-specific configuration
- `.env.example` - Template file with all variables
- `.gitignore` - Protected files list

### Configuration Documentation

- `AUTHENTICATION_FINAL_SETUP.md` - Authentication & JWT setup
- `COMPLETE_ADMIN_DASHBOARD_SUMMARY.md` - Admin dashboard features
- `ADMIN_DASHBOARD_FEATURES.md` - Dashboard capabilities

### Security Guidelines

1. **Never commit** `.env*` files (except `.env.example`)
2. **Rotate secrets** regularly (JWT keys, encryption keys)
3. **Use strong passwords** (32+ characters)
4. **Restrict CORS** in production
5. **Enable rate limiting** in production
6. **Use short token expiry** in production
7. **Monitor logs** for suspicious activity

---

## ✅ Summary

You now have a complete **multi-environment configuration system**:

✅ **Three environments**: Development, QA, Production
✅ **Environment switcher**: Easy switching with `./switch-env.sh`
✅ **Auto-loading**: Automatic environment detection
✅ **Security**: Protected files, environment-specific settings
✅ **Programmatic access**: Check environment in code
✅ **Git-safe**: Credentials never committed
✅ **Production-ready**: Strict security for production

### Next Steps

1. ✅ Create environment files: `./switch-env.sh create`
2. ✅ Fill in credentials for each environment
3. ✅ Test switching: `./switch-env.sh dev`
4. ✅ Verify settings load correctly
5. ✅ Deploy to QA and production

**Your project is now ready for professional multi-environment deployment!** 🚀
