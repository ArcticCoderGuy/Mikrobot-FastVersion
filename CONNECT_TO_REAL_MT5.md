# MT5 Live Connection Status

## Nykyinen Tilanne

### ✅ Sinulla on:
- MT5 Terminal auki
- Manuaalinen kauppa (tiketti 398xxx)
- Demo-tili 95244786 aktiivinen

### ❌ Puuttuu:
- Salasana järjestelmälle
- Live-yhteys botista MT5:een

## Yhdistä Botti Live MT5:een

### Vaihtoehto 1: Anna salasana
```bash
python run_crypto_demo.py
# Syötä salasana kun pyydetään
```

### Vaihtoehto 2: Kova-koodaa salasana (VAIN DEMO!)
```python
# Lisää run_crypto_demo.py tiedostoon:
DEMO_PASSWORD = "sinun_demo_salasanasi"

# Muuta rivi 543:
password = DEMO_PASSWORD  # Oli: input("Enter demo account password: ")
```

### Vaihtoehto 3: Ympäristömuuttuja
```bash
set MT5_DEMO_PASSWORD=sinun_salasanasi
python run_crypto_demo.py
```

## Todellinen MT5 Trading

Kun salasana on annettu, järjestelmä:
1. ✅ Yhdistää MT5:een (näet Experts-välilehdellä)
2. ✅ Alkaa käydä kauppaa kryptoilla
3. ✅ Näyttää kaupat samassa terminaalissa 398-kauppasi kanssa
4. ✅ Tallentaa kaikki lokiin

## Tarkista Yhteys

```python
# test_mt5_live.py
import MetaTrader5 as mt5

mt5.initialize()
authorized = mt5.login(95244786, "SALASANA_TÄHÄN", "MetaQuotes-Demo")
if authorized:
    print("✅ Yhdistetty!")
    account = mt5.account_info()
    print(f"Saldo: {account.balance}")
    print(f"Equity: {account.equity}")
    positions = mt5.positions_get()
    print(f"Positioita: {len(positions) if positions else 0}")
else:
    print("❌ Kirjautuminen epäonnistui")
mt5.shutdown()
```

## Live Crypto Trading Demo

Kun salasana on kunnossa:
```bash
python run_crypto_demo.py
```

Näet MT5:ssä:
- Journal: Connection messages
- Experts: Bot activity
- Trade: Bot positions (BTCUSD, ETHUSD, etc.)
- History: Completed trades

**HUOM**: 398-kauppasi ja botin kaupat näkyvät samassa listassa!