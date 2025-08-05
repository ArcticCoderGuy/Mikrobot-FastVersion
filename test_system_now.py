"""
IMMEDIATE SYSTEM TEST
Test if everything is actually working and execute current signal
"""
import MetaTrader5 as mt5
import json
import sys
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8', errors='ignore')

def ascii_print(text):
    ascii_text = ''.join(char for char in str(text) if ord(char) < 128)
    print(ascii_text)

def test_current_system():
    ascii_print("IMMEDIATE SYSTEM STATUS TEST")
    ascii_print("=" * 50)
    
    # Test 1: MT5 Connection
    if not mt5.initialize():
        ascii_print("CRITICAL: MT5 connection FAILED")
        return False
    
    account = mt5.account_info()
    positions = mt5.positions_get()
    
    ascii_print(f"MT5 Status: CONNECTED")
    ascii_print(f"Account: {account.balance:.2f} USD")
    ascii_print(f"Open Positions: {len(positions) if positions else 0}")
    
    if positions:
        ascii_print("Current Positions:")
        for pos in positions:
            ascii_print(f"  {pos.symbol}: {pos.volume} lots, P&L: ${pos.profit:.2f}")
    
    # Test 2: Current Signal
    try:
        signal_file = 'C:/Users/HP/AppData/Roaming/MetaQuotes/Terminal/Common/Files/mikrobot_4phase_signal.json'
        with open(signal_file, 'rb') as f:
            content = f.read()
        
        content_str = content.decode('utf-16le', errors='ignore').replace('\x00', '')
        import re
        content_str = re.sub(r'[^\x20-\x7E\n\r\t]', '', content_str)
        signal = json.loads(content_str)
        
        ascii_print(f"\nCurrent Signal: {signal.get('symbol')} {signal.get('trade_direction')}")
        ascii_print(f"YLIPIP Triggered: {signal.get('phase_4_ylipip', {}).get('triggered', False)}")
        ascii_print(f"Timestamp: {signal.get('timestamp')}")
        
        # Test 3: Check if signal is complete
        phases = ['phase_1_m5_bos', 'phase_2_m1_break', 'phase_3_m1_retest', 'phase_4_ylipip']
        all_phases = all(phase in signal for phase in phases)
        ylipip_triggered = signal.get('phase_4_ylipip', {}).get('triggered', False)
        
        if all_phases and ylipip_triggered:
            ascii_print("Signal Status: READY FOR EXECUTION")
            return execute_current_signal(signal)
        else:
            ascii_print("Signal Status: INCOMPLETE - waiting")
            return True
            
    except Exception as e:
        ascii_print(f"Signal Error: {e}")
        return False
    
    finally:
        mt5.shutdown()

def execute_current_signal(signal):
    """Execute the current signal immediately"""
    ascii_print(f"\nEXECUTING SIGNAL: {signal['symbol']} {signal['trade_direction']}")
    
    symbol = signal['symbol']
    direction = signal['trade_direction']
    
    if not mt5.initialize():
        return False
    
    # Get symbol info
    symbol_info = mt5.symbol_info(symbol)
    tick = mt5.symbol_info_tick(symbol)
    account = mt5.account_info()
    
    if not (symbol_info and tick and account):
        ascii_print("Failed to get market data")
        mt5.shutdown()
        return False
    
    # Calculate position size (conservative)
    risk_amount = account.balance * 0.005  # 0.5% risk for safety
    atr_pips = 6  # Conservative ATR
    pip_value = 10 if 'JPY' not in symbol else 100
    
    lot_size = max(symbol_info.volume_min, risk_amount / (atr_pips * pip_value))
    lot_size = min(lot_size, 1.0)  # Cap at 1.0 lot
    lot_size = round(lot_size, 2)
    
    # Create trade request
    if direction == 'BULL':
        trade_type = mt5.ORDER_TYPE_BUY
        price = tick.ask
    else:
        trade_type = mt5.ORDER_TYPE_SELL
        price = tick.bid
    
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": lot_size,
        "type": trade_type,
        "price": price,
        "deviation": 50,
        "magic": 777777,
        "comment": f"TEST-{direction}",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_FOK,
    }
    
    ascii_print(f"Executing: {lot_size} lots at {price}")
    
    result = mt5.order_send(request)
    
    if result and result.retcode == mt5.TRADE_RETCODE_DONE:
        ascii_print("SUCCESS! Trade executed!")
        ascii_print(f"  Ticket: {result.order}")
        ascii_print(f"  Price: {result.price}")
        ascii_print(f"  Volume: {result.volume}")
        mt5.shutdown()
        return True
    else:
        ascii_print("FAILED!")
        if result:
            ascii_print(f"  Error: {result.retcode} - {result.comment}")
        mt5.shutdown()
        return False

if __name__ == "__main__":
    success = test_current_system()
    if success:
        ascii_print("\nSYSTEM TEST: PASSED")
        ascii_print("Now starting continuous monitoring...")
        
        # Import and run the orchestrator
        try:
            import mcp_trading_orchestrator
            ascii_print("Starting MCP orchestrator...")
            orchestrator = mcp_trading_orchestrator.MCPTradingOrchestrator()
            orchestrator.run()
        except Exception as e:
            ascii_print(f"Orchestrator error: {e}")
            ascii_print("Starting simple continuous executor...")
            import continuous_4phase_executor
    else:
        ascii_print("\nSYSTEM TEST: FAILED")
        ascii_print("Check MT5 connection and try again")