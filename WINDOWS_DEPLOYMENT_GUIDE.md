# 🖥️ WINDOWS MT5 DEPLOYMENT GUIDE

## 🎯 **TAVOITE:**
Käynnistää Windows-koneella (192.168.0.100) MT5 Bridge server, joka vastaanottaa Mac:ilta (192.168.0.114) kaupankäyntisignaaleja ja suorittaa OIKEAT kaupat MT5:ssä tilillä 95244786.

---

## 📋 **VAIHEET:**

### **1. MT5 SETUP**
```
1. Avaa MetaTrader 5 Windows-koneessa
2. Kirjaudu tilille:
   - Account: 95244786
   - Password: Ua@tOnLp
   - Server: MetaQuotesDemo
3. Varmista että tili on aktiivinen ja kaupankäynti sallittu
```

### **2. PYTHON DEPENDENCIES**
```bash
# Command Prompt (Administrator)
pip install MetaTrader5 flask requests

# Tai jos pip ei toimi:
python -m pip install MetaTrader5 flask requests
```

### **3. COPY FILES TO WINDOWS**
Kopioi nämä tiedostot Mac:ilta Windows-koneelle:

```
Windows Desktop/Mikrobot/
├── windows_mt5_executor.py
├── test_webhook_from_windows.py
└── README_WINDOWS.txt
```

### **4. NETWORK CONFIGURATION**
Varmista että:
- Windows IP: 192.168.0.100
- Mac IP: 192.168.0.114
- Firewall sallii portin 8001 (MT5 Bridge)

**Windows Firewall:**
```cmd
# Command Prompt (Administrator)
netsh advfirewall firewall add rule name="Mikrobot MT5 Bridge" dir=in action=allow protocol=TCP localport=8001
```

### **5. START MT5 BRIDGE**
```cmd
# Command Prompt
cd Desktop\Mikrobot
python windows_mt5_executor.py
```

**Odotettu output:**
```
INFO:__main__:✅ Connected to MT5: 95244786, Balance: 10000.0
INFO:__main__:🚀 MT5 Bridge started on port 8001
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:8001
 * Running on http://192.168.0.100:8001
```

### **6. TEST CONNECTION**
**From Windows:**
```cmd
python test_webhook_from_windows.py
```

**From Mac (to verify):**
```bash
curl http://192.168.0.100:8001/status
```

---

## 🔥 **TROUBLESHOOTING:**

### **MT5 Connection Error:**
```
❌ MT5 initialization failed
❌ MT5 login failed
```
**Fix:** Varmista että MT5 on auki ja tili kirjautunut manuaalisesti ensin

### **Port Error:**
```
[Errno 10048] Only one usage of each socket address
```
**Fix:** Portti 8001 jo käytössä. Sammuta bridge ja käynnistä uudelleen

### **Firewall Blocking:**
```
Connection refused from Mac
```
**Fix:** Lisää Windows Firewall rule (katso kohta 4)

### **MetaTrader5 Module Error:**
```
ModuleNotFoundError: No module named 'MetaTrader5'
```
**Fix:** `pip install MetaTrader5`

---

## 📊 **EXPECTED RESULTS:**

### **Successful Connection:**
```
✅ Connected to MT5: 95244786, Balance: 10000.0
✅ Mac webhook is reachable!
✅ Bridge ready for trading signals!
```

### **Trade Execution:**
```
📨 Received signal: {'symbol': 'EURUSD', 'action': 'BUY', ...}
✅ Order executed: 123456789
✅ Confirmation sent to Mac
```

---

## 🎯 **FINAL VERIFICATION:**

1. **MT5 Bridge Status:** `http://192.168.0.100:8001/status`
2. **Mac Connectivity:** Mac → Windows ping < 20ms
3. **Windows Connectivity:** Windows → Mac webhook works
4. **Account Ready:** MT5 shows account 95244786 logged in

---

## 🚀 **GO LIVE:**

Kun kaikki testit onnistuvat:

1. **Windows:** Keep `windows_mt5_executor.py` running
2. **Mac:** Start Django webhook server
3. **Mac:** Start real Mikrobot trading

**Windows pitää olla päällä ja MT5 Bridge ajossa 24/7!**

---

# ⚡ CRITICAL SUCCESS FACTORS:

✅ **MT5 manually logged in first**  
✅ **Windows Firewall configured**  
✅ **Both machines on 192.168.0.x network**  
✅ **Python dependencies installed**  
✅ **Bridge server running on port 8001**

**Kun nämä kaikki OK → REAL TRADES START! 🔥**