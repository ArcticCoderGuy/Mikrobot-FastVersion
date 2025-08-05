# MIKROBOT FASTVERSION - Navigation Guide

**MIKROBOT Trading Platform Complete Navigation Reference**

## 🏠 Main URLs

### Primary Access Points
- **Landing Page**: `http://127.0.0.1:8000/`
- **Admin Panel**: `http://127.0.0.1:8000/admin/`
- **Trading Dashboard**: `http://127.0.0.1:8000/dashboard/`

### Login Credentials
- **Email**: admin@mikrobot.com
- **Password**: admin123

---

## ⚙️ Configuration Management

### Configuration Center
- **URL**: `http://127.0.0.1:8000/admin/mikrobot/config/`
- **Purpose**: Central configuration management with MIKROBOT_FASTVERSION.md integration
- **Features**: Position sizing, subscription tiers, quality control, asset classes

### Configuration Actions
- **Validate Compliance**: `http://127.0.0.1:8000/admin/mikrobot/config/validate/`
- **Export Configuration**: `http://127.0.0.1:8000/admin/mikrobot/config/export/`

---

## 👥 User Management

### User Administration
- **All Users**: `http://127.0.0.1:8000/admin/accounts/user/`
- **Add New User**: `http://127.0.0.1:8000/admin/accounts/user/add/`
- **Trading Accounts**: `http://127.0.0.1:8000/admin/accounts/tradingaccount/`
- **Add Trading Account**: `http://127.0.0.1:8000/admin/accounts/tradingaccount/add/`

---

## 🖥️ Command Line Interface

### Management Commands
```bash
# Navigate to platform directory
cd "C:\Users\HP\Dev\Mikrobot Fastversion\mikrobot_platform"

# Show all configuration
python manage.py config_manager show

# Validate Above Robust compliance
python manage.py config_manager validate

# Export configuration to JSON
python manage.py config_manager export

# Sync with MIKROBOT_FASTVERSION.md
python manage.py config_manager sync

# Show specific configuration value
python manage.py config_manager show --key="POSITION_SIZING.DEFAULT_RISK_PERCENT"
```

### Server Management
```bash
# Start development server
python manage.py runserver 8000

# Start without auto-reload (stable)
python manage.py runserver 8000 --noreload

# Create superuser
python manage.py createsuperuser

# Run database migrations
python manage.py migrate
```

---

## 📊 Dashboard Features

### Real-time Status Monitoring
- **System Compliance**: Above Robust standards validation
- **Risk Management**: 0.55% per trade standard
- **Quality Control**: Cp/Cpk ≥ 3.0 Six Sigma standards
- **Asset Classes**: 9 supported asset types

### Revenue Model Overview
- **Basic Tier**: $99/month (10 trades/day)
- **Professional Tier**: $199/month (50 trades/day)
- **Enterprise Tier**: $499/month (unlimited trades)

---

## 🎯 Quick Actions

### Administrative Tasks
1. **Login to Admin**: Navigate to `/admin/` with credentials
2. **Configure System**: Use `/admin/mikrobot/config/`
3. **Add Users**: Use `/admin/accounts/user/add/`
4. **Monitor Compliance**: Use `/admin/mikrobot/config/validate/`
5. **Export Settings**: Use `/admin/mikrobot/config/export/`

### Configuration Updates
1. **Web Interface**: Use configuration center for GUI updates
2. **Command Line**: Use `config_manager` commands for CLI updates
3. **File Sync**: Auto-sync with MIKROBOT_FASTVERSION.md
4. **Validation**: Real-time compliance checking

---

## 🔧 Technical Details

### Platform Architecture
- **Django 4.2.7**: Web framework
- **SQLite Database**: Development database
- **Above Robust Standards**: ASCII-only, submarine-grade precision
- **Position Sizing**: ATR-based dynamic calculation
- **Asset Support**: FOREX, CFD_INDICES, CFD_CRYPTO, CFD_METALS, CFD_ENERGIES, CFD_STOCKS

### Integration Points
- **MIKROBOT_FASTVERSION.md**: Master configuration file
- **MT5 Trading Accounts**: Encrypted credential storage
- **Subscription Management**: Tiered access control
- **Quality Control**: Six Sigma monitoring

---

## 🚨 Troubleshooting

### Common Issues
1. **Server won't start**: Check if port 8000 is available
2. **Login fails**: Verify credentials (admin@mikrobot.com / admin123)
3. **Configuration not saving**: Check file permissions
4. **Navigation broken**: Clear browser cache

### Support Commands
```bash
# Check system status
python manage.py config_manager validate

# Reset admin password
python manage.py changepassword admin@mikrobot.com

# Check database status
python manage.py dbshell

# Collect static files
python manage.py collectstatic
```

---

**MIKROBOT FASTVERSION - Above Robust Navigation Complete**
*All systems operational with submarine-grade precision*