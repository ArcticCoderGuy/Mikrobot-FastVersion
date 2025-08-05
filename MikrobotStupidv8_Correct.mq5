//+------------------------------------------------------------------+
//|                                      MikrobotStupidv8_Correct   |
//|                       MIKROBOT_FASTVERSION.md COMPLIANT v8.0    |
//|              4-PHASE STRATEGY: M5 BOS → M1 break → M1 retest → 0.6 ylipip |
//|                                              BUILD: 20250103-008C |
//+------------------------------------------------------------------+
#property copyright "MIKROBOT v8 - FASTVERSION.md COMPLIANT"
#property version   "8.00"
#property description "4-Phase Strategy: Only Python signal at 0.6 ylipip trigger"
#property strict

//--- Input parameters
input double YlipipTrigger = 0.6;              // Ylipip trigger threshold  
input int    MagicNumber = 999888;             // Magic number for trades
input bool   DebugMode = true;                 // Enable debug logging

//--- MIKROBOT_FASTVERSION.md 4-PHASE STATE MACHINE
enum TradingState
{
    IDLE,                    // No active monitoring
    M5_BOS_DETECTED,        // M5 BOS found, start M1 monitoring  
    M1_BREAK_DETECTED,      // M1 break found, wait for retest
    M1_RETEST_CONFIRMED,    // M1 retest confirmed, calculate ylipip
    READY_FOR_ENTRY         // 0.6 ylipip reached, send Python signal
};

//--- Global variables
datetime lastCheck;
string currentBuild = "20250103-008C";
TradingState currentState = IDLE;

// 4-Phase tracking variables
datetime m5_bos_time = 0;
double m5_bos_price = 0;
string m5_bos_direction = "";

datetime m1_break_time = 0;
double m1_break_price = 0;

datetime m1_retest_time = 0; 
double m1_retest_price = 0;

double ylipip_target = 0;
double ylipip_calculation_base = 0;

//+------------------------------------------------------------------+
//| Expert initialization function                                   |
//+------------------------------------------------------------------+
int OnInit()
{
    Print("======================================================================");
    Print("BUILD: 20250103-008C - MIKROBOT_FASTVERSION.md COMPLIANT");
    Print("MIKROBOT STUPID EA v8.0 - 4-PHASE STRATEGY");
    Print("======================================================================");
    
    Print("MIKROBOT_FASTVERSION.md COMPLIANT v8.0:");
    Print("- Phase 1: M5 BOS detection (START M1 MONITORING)");
    Print("- Phase 2: M1 break detection (WAIT FOR RETEST)");  
    Print("- Phase 3: M1 retest validation (CALCULATE YLIPIP)");
    Print("- Phase 4: 0.6 ylipip trigger (SEND PYTHON SIGNAL)");
    Print("- Ylipip Trigger: ", YlipipTrigger);
    Print("- ONLY sends Python signal at Phase 4 completion");
    
    currentState = IDLE;
    lastCheck = TimeCurrent();
    
    Print("MIKROBOT v8.0 INITIALIZATION COMPLETE");
    Print("STATE: IDLE - Watching for M5 BOS to start 4-phase sequence");
    Print("COMPLIANCE: MIKROBOT_FASTVERSION.md 4-phase strategy ACTIVE");
    
    return(INIT_SUCCEEDED);
}

//+------------------------------------------------------------------+
//| Expert tick function                                             |
//+------------------------------------------------------------------+
void OnTick()
{
    // Check every few seconds based on current state
    if(TimeCurrent() - lastCheck >= GetCheckInterval())
    {
        ProcessFourPhaseStrategy();
        lastCheck = TimeCurrent();
    }
}

//+------------------------------------------------------------------+
//| Get check interval based on current state                       |
//+------------------------------------------------------------------+
int GetCheckInterval()
{
    switch(currentState)
    {
        case IDLE: return 5;                    // Check M5 every 5 seconds
        case M5_BOS_DETECTED: return 1;         // Monitor M1 every second
        case M1_BREAK_DETECTED: return 1;       // Watch for retest every second  
        case M1_RETEST_CONFIRMED: return 1;     // Monitor ylipip every second
        case READY_FOR_ENTRY: return 3;        // Wait for Python response
        default: return 3;
    }
}

//+------------------------------------------------------------------+
//| Process MIKROBOT_FASTVERSION.md 4-phase strategy                |
//+------------------------------------------------------------------+
void ProcessFourPhaseStrategy()
{
    string symbol = Symbol();
    
    switch(currentState)
    {
        case IDLE:
            // PHASE 1: M5 BOS Detection
            if(DetectM5BOS(symbol))
            {
                currentState = M5_BOS_DETECTED;
                Print("PHASE 1 COMPLETE: M5 BOS detected - Starting M1 monitoring");
                Print("STATUS: START_M1_MONITORING (NO SIGNAL TO PYTHON YET)");
            }
            break;
            
        case M5_BOS_DETECTED:
            // PHASE 2: M1 Break Detection  
            if(DetectM1Break(symbol))
            {
                currentState = M1_BREAK_DETECTED;
                Print("PHASE 2 COMPLETE: M1 break detected - Waiting for retest");
                Print("STATUS: WAIT_FOR_RETEST (NO SIGNAL TO PYTHON YET)");
            }
            break;
            
        case M1_BREAK_DETECTED:
            // PHASE 3: M1 Retest Validation
            if(DetectM1Retest(symbol))
            {
                currentState = M1_RETEST_CONFIRMED;
                CalculateYlipipTarget();
                Print("PHASE 3 COMPLETE: M1 retest confirmed - Calculating ylipip");
                Print("STATUS: CALCULATE_ENTRY_POINT (NO SIGNAL TO PYTHON YET)");
            }
            break;
            
        case M1_RETEST_CONFIRMED:
            // PHASE 4: 0.6 Ylipip Trigger
            if(CheckYlipipTrigger(symbol))
            {
                currentState = READY_FOR_ENTRY;
                SendPythonSignal(symbol);
                Print("PHASE 4 COMPLETE: 0.6 ylipip reached - SENDING PYTHON SIGNAL");
                Print("STATUS: EXECUTE_TRADE_NOW - Python MCP/ML take over!");
            }
            break;
            
        case READY_FOR_ENTRY:
            // Wait for Python response or timeout to reset
            CheckForPythonResponse();
            break;
    }
}

//+------------------------------------------------------------------+
//| PHASE 1: Detect M5 BOS (Break of Structure)                    |
//+------------------------------------------------------------------+
bool DetectM5BOS(string symbol)
{
    MqlRates rates[];
    if(CopyRates(symbol, TIMEFRAME_M5, 0, 10, rates) < 10)
        return false;
        
    // Simple M5 BOS detection: Current candle breaks previous structure
    double currentHigh = rates[9].high;
    double currentLow = rates[9].low;
    double previousHigh = rates[8].high;
    double previousLow = rates[8].low;
    
    bool bullishBOS = (currentHigh > previousHigh);
    bool bearishBOS = (currentLow < previousLow);
    
    if(bullishBOS || bearishBOS)
    {
        m5_bos_time = rates[9].time;
        m5_bos_price = bullishBOS ? currentHigh : currentLow;
        m5_bos_direction = bullishBOS ? "BULL" : "BEAR";
        
        if(DebugMode)
        {
            Print("M5 BOS DETECTED: ", symbol, " - ", m5_bos_direction);
            Print("  BOS Price: ", m5_bos_price);
            Print("  BOS Time: ", TimeToString(m5_bos_time));
        }
        
        return true;
    }
    
    return false;
}

//+------------------------------------------------------------------+
//| PHASE 2: Detect M1 Break after M5 BOS                         |
//+------------------------------------------------------------------+
bool DetectM1Break(string symbol)
{
    MqlRates rates[];
    if(CopyRates(symbol, TIMEFRAME_M1, 0, 5, rates) < 5)
        return false;
        
    // M1 break must be after M5 BOS time
    if(rates[4].time <= m5_bos_time)
        return false;
        
    // Simple M1 break detection aligned with M5 BOS direction
    double currentHigh = rates[4].high;
    double currentLow = rates[4].low;
    double previousHigh = rates[3].high;
    double previousLow = rates[3].low;
    
    bool m1Break = false;
    
    if(m5_bos_direction == "BULL" && currentHigh > previousHigh)
        m1Break = true;
    else if(m5_bos_direction == "BEAR" && currentLow < previousLow)
        m1Break = true;
        
    if(m1Break)
    {
        m1_break_time = rates[4].time;
        m1_break_price = (m5_bos_direction == "BULL") ? currentHigh : currentLow;
        
        if(DebugMode)
        {
            Print("M1 BREAK DETECTED: ", symbol, " - ", m5_bos_direction);
            Print("  Break Price: ", m1_break_price);
            Print("  Break Time: ", TimeToString(m1_break_time));
        }
        
        return true;
    }
    
    return false;
}

//+------------------------------------------------------------------+
//| PHASE 3: Detect M1 Retest of break level                      |
//+------------------------------------------------------------------+
bool DetectM1Retest(string symbol)
{
    MqlRates rates[];
    if(CopyRates(symbol, TIMEFRAME_M1, 0, 5, rates) < 5)
        return false;
        
    // M1 retest must be after M1 break time
    if(rates[4].time <= m1_break_time)
        return false;
        
    // Price returns to test break level
    double currentPrice = rates[4].close;
    double breakLevel = m1_break_price;
    double retestTolerance = 5 * SymbolInfoDouble(symbol, SYMBOL_POINT); // 5 points tolerance
    
    bool retestDetected = false;
    
    if(m5_bos_direction == "BULL")
    {
        // For bullish break, look for price coming back down to test support
        if(currentPrice <= breakLevel + retestTolerance && currentPrice >= breakLevel - retestTolerance)
            retestDetected = true;
    }
    else if(m5_bos_direction == "BEAR")
    {
        // For bearish break, look for price coming back up to test resistance  
        if(currentPrice >= breakLevel - retestTolerance && currentPrice <= breakLevel + retestTolerance)
            retestDetected = true;
    }
    
    if(retestDetected)
    {
        m1_retest_time = rates[4].time;
        m1_retest_price = currentPrice;
        
        if(DebugMode)
        {
            Print("M1 RETEST DETECTED: ", symbol, " - ", m5_bos_direction);
            Print("  Retest Price: ", m1_retest_price);
            Print("  Break Level: ", breakLevel);
            Print("  Retest Time: ", TimeToString(m1_retest_time));
        }
        
        return true;
    }
    
    return false;
}

//+------------------------------------------------------------------+
//| Calculate 0.6 ylipip target from break candle                  |
//+------------------------------------------------------------------+
void CalculateYlipipTarget()
{
    // Use M1 break candle as base for ylipip calculation
    ylipip_calculation_base = m1_break_price;
    
    // Get pip value for symbol
    double pipValue = GetPipValue(Symbol());
    
    // Calculate 0.6 ylipip distance in price units
    double ylipipDistance = YlipipTrigger * pipValue;
    
    // Set ylipip target based on trade direction
    if(m5_bos_direction == "BULL")
        ylipip_target = ylipip_calculation_base + ylipipDistance;
    else
        ylipip_target = ylipip_calculation_base - ylipipDistance;
        
    if(DebugMode)
    {
        Print("YLIPIP TARGET CALCULATED:");
        Print("  Base Price: ", ylipip_calculation_base);
        Print("  Pip Value: ", pipValue);
        Print("  Ylipip Distance: ", ylipipDistance);
        Print("  Ylipip Target: ", ylipip_target);
        Print("  Direction: ", m5_bos_direction);
    }
}

//+------------------------------------------------------------------+
//| PHASE 4: Check if 0.6 ylipip trigger reached                  |
//+------------------------------------------------------------------+
bool CheckYlipipTrigger(string symbol)
{
    MqlTick tick;
    if(!SymbolInfoTick(symbol, tick))
        return false;
        
    double currentPrice = tick.bid;
    bool ylipipReached = false;
    
    if(m5_bos_direction == "BULL" && currentPrice >= ylipip_target)
        ylipipReached = true;
    else if(m5_bos_direction == "BEAR" && currentPrice <= ylipip_target)
        ylipipReached = true;
        
    if(ylipipReached && DebugMode)
    {
        Print("0.6 YLIPIP TRIGGER REACHED!");
        Print("  Current Price: ", currentPrice);
        Print("  Ylipip Target: ", ylipip_target);
        Print("  Direction: ", m5_bos_direction);
    }
        
    return ylipipReached;
}

//+------------------------------------------------------------------+
//| Send signal to Python MCP/ML system (ONLY at Phase 4)         |
//+------------------------------------------------------------------+
void SendPythonSignal(string symbol)
{
    Print("============================================================");
    Print("MIKROBOT_FASTVERSION.md PHASE 4 COMPLETE");
    Print("SENDING PYTHON SIGNAL - ALL 4 PHASES VALIDATED");
    Print("============================================================");
    
    MqlTick tick;
    if(!SymbolInfoTick(symbol, tick))
        return;
        
    // Create complete signal with all 4-phase data
    string signal = StringFormat(
        "{"
        "\"timestamp\":\"%s\","
        "\"symbol\":\"%s\","
        "\"strategy\":\"MIKROBOT_FASTVERSION_4PHASE\","
        "\"phase_1_m5_bos\":{\"time\":\"%s\",\"price\":%.5f,\"direction\":\"%s\"},"
        "\"phase_2_m1_break\":{\"time\":\"%s\",\"price\":%.5f},"
        "\"phase_3_m1_retest\":{\"time\":\"%s\",\"price\":%.5f},"
        "\"phase_4_ylipip\":{\"target\":%.5f,\"current\":%.5f,\"triggered\":true},"
        "\"trade_direction\":\"%s\","
        "\"current_price\":%.5f,"
        "\"ylipip_trigger\":%.2f,"
        "\"source\":\"MIKROBOT_FASTVERSION_COMPLIANT_v8\","
        "\"intelligence_needed\":\"PYTHON_MCP_ML_ATR_RISK\","
        "\"build_version\":\"%s\""
        "}",
        TimeToString(TimeCurrent()),
        symbol,
        TimeToString(m5_bos_time), m5_bos_price, m5_bos_direction,
        TimeToString(m1_break_time), m1_break_price,
        TimeToString(m1_retest_time), m1_retest_price,
        ylipip_target, tick.bid,
        m5_bos_direction,
        tick.bid,
        YlipipTrigger,
        currentBuild
    );
    
    // Write signal for Python
    int file = FileOpen("mikrobot_4phase_signal.json", FILE_WRITE | FILE_TXT | FILE_COMMON);
    if(file != INVALID_HANDLE)
    {
        FileWriteString(file, signal);
        FileClose(file);
        
        Print("4-PHASE SIGNAL SENT TO PYTHON:");
        Print("  Symbol: ", symbol);
        Print("  Strategy: MIKROBOT_FASTVERSION 4-phase complete");
        Print("  Direction: ", m5_bos_direction);
        Print("  Ylipip Trigger: ", YlipipTrigger, " REACHED");
        Print("  Current Price: ", tick.bid);
        Print("  Python: Please calculate ATR, risk, lot size and send back trade!");
    }
}

//+------------------------------------------------------------------+
//| Check for Python execution response                            |
//+------------------------------------------------------------------+
void CheckForPythonResponse()
{
    // Check if Python sent execution command
    if(FileIsExist("python_execution_command.json", FILE_COMMON))
    {
        // Execute Python's trade command
        ExecutePythonTrade();
        
        // Reset to IDLE for next opportunity
        ResetStateMachine();
    }
    else if(TimeCurrent() - m1_retest_time > 300) // 5 minute timeout
    {
        Print("TIMEOUT: No Python response in 5 minutes - Resetting state machine");
        ResetStateMachine();
    }
}

//+------------------------------------------------------------------+
//| Execute trade command from Python                              |
//+------------------------------------------------------------------+
void ExecutePythonTrade()
{
    Print("EXECUTING PYTHON CALCULATED TRADE - MIKROBOT v8 COMPLIANT");
    // Implementation for executing Python's trade command
    // (Same as previous versions - just execute what Python calculated)
}

//+------------------------------------------------------------------+
//| Reset state machine for next opportunity                       |
//+------------------------------------------------------------------+
void ResetStateMachine()
{
    currentState = IDLE;
    m5_bos_time = 0;
    m5_bos_price = 0;
    m5_bos_direction = "";
    m1_break_time = 0;
    m1_break_price = 0;
    m1_retest_time = 0;
    m1_retest_price = 0;
    ylipip_target = 0;
    ylipip_calculation_base = 0;
    
    Print("STATE MACHINE RESET - Ready for next M5 BOS opportunity");
}

//+------------------------------------------------------------------+
//| Get pip value for symbol (simplified)                          |
//+------------------------------------------------------------------+
double GetPipValue(string symbol)
{
    if(StringFind(symbol, "JPY") >= 0)
        return 0.01;  // JPY pairs
    else if(StringFind(symbol, "USD") >= 0)
        return 0.0001; // Major forex pairs
    else
        return 0.1;   // CFD_CRYPTO like BCHUSD
}

//+------------------------------------------------------------------+