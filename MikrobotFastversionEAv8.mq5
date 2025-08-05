//+------------------------------------------------------------------+
//|                                     MikrobotFastversionEAv8.mq5 |
//|                              STUPID EA - PATTERN DETECTION ONLY |
//|                  v8.0 - Simple M5 Watcher for All Asset Classes |
//+------------------------------------------------------------------+
#property copyright "Mikrobot FastVersion - STUPID EA v8.0"
#property version   "8.00"
#property description "BUILD: 20250103-008 - STUPID EA: M5 PATTERN DETECTION ONLY"
#property description "✓ Watches M5 BOS on ALL asset classes | ✓ Sends simple signals to Python"
#property description "✓ NO intelligence | ✓ NO calculations | ✓ NO ATR | ✓ NO ML"
#property description "✓ Python MCP/ML does ALL thinking | ✓ EA just executes Python results"

//--- Input parameters
input group "=== STUPID EA v8 SETTINGS ==="
input double YlipipTrigger = 0.6;              // Ylipip trigger threshold
input int    SignalCheckInterval = 1000;       // Check patterns every 1 second
input int    MagicNumber = 999888;             // Magic number for trades
input bool   DebugMode = true;                 // Enable debug logging

//--- Global variables
datetime lastSignalCheck;
string signalFilePath;
string executionFilePath;
string currentBuild = "20250103-008";

//--- ALL ASSET CLASSES TO MONITOR
string AllSymbols[] = {
    // FOREX (7)
    "EURUSD", "GBPUSD", "USDJPY", "USDCHF", "AUDUSD", "USDCAD", "NZDUSD",
    // CFD_INDICES (8) 
    "SPX500", "NAS100", "UK100", "GER40", "FRA40", "AUS200", "JPN225", "HK50",
    // CFD_CRYPTO (7)
    "BTCUSD", "ETHUSD", "XRPUSD", "LTCUSD", "BCHUSD", "ADAUSD", "DOTUSD",
    // CFD_METALS (4)
    "XAUUSD", "XAGUSD", "XPTUSD", "XPDUSD",
    // CFD_ENERGIES (3)
    "UKOUSD", "USOUSD", "NGAS"
};

//+------------------------------------------------------------------+
//| Expert initialization function                                   |
//+------------------------------------------------------------------+
int OnInit()
{
    Print("======================================================================");
    Print("BUILD: 20250103-008 - STUPID EA: M5 PATTERN DETECTION ONLY");
    Print("MIKROBOT FASTVERSION v8.0 - STUPID EA INITIALIZATION");
    Print("======================================================================");
    
    // Initialize file paths
    signalFilePath = TerminalInfoString(TERMINAL_COMMONDATA_PATH) + "\\Files\\m5_pattern_signal.json";
    executionFilePath = TerminalInfoString(TERMINAL_COMMONDATA_PATH) + "\\Files\\python_execution_command.json";
    
    Print("STUPID EA v8.0 Configuration:");
    Print("✓ Ylipip Trigger: ", YlipipTrigger);
    Print("✓ Monitoring ", ArraySize(AllSymbols), " symbols across ALL asset classes");
    Print("✓ NO intelligence in EA - Python MCP/ML does ALL thinking");
    Print("✓ EA only detects M5 patterns and executes Python commands");
    
    // List monitored symbols
    Print("Monitored symbols:");
    for(int i = 0; i < ArraySize(AllSymbols); i++)
    {
        if(i % 5 == 0) Print("  ", AllSymbols[i], " ", AllSymbols[i+1], " ", AllSymbols[i+2], " ", AllSymbols[i+3], " ", AllSymbols[i+4]);
    }
    
    lastSignalCheck = TimeCurrent();
    
    Print("✓ STUPID EA v8.0 INITIALIZATION COMPLETE");
    Print("✓ WATCHING M5 PATTERNS ON ALL ASSET CLASSES");
    
    return(INIT_SUCCEEDED);
}

//+------------------------------------------------------------------+
//| Expert tick function                                             |
//+------------------------------------------------------------------+
void OnTick()
{
    // Check for patterns every second
    if(TimeCurrent() - lastSignalCheck >= SignalCheckInterval/1000.0)
    {
        CheckM5PatternsOnAllSymbols();
        CheckForPythonExecutionCommands();
        lastSignalCheck = TimeCurrent();
    }
}

//+------------------------------------------------------------------+
//| Check M5 patterns on all monitored symbols                      |
//+------------------------------------------------------------------+
void CheckM5PatternsOnAllSymbols()
{
    for(int i = 0; i < ArraySize(AllSymbols); i++)
    {
        string symbol = AllSymbols[i];
        
        // Skip if symbol not available
        if(!SymbolSelect(symbol, true))
            continue;
            
        // STUPID CHECK: Simple M5 pattern detection
        bool m5Pattern = DetectSimpleM5Pattern(symbol);
        
        if(m5Pattern)
        {
            // Send STUPID signal to Python
            SendStupidSignalToPython(symbol);
        }
    }
}

//+------------------------------------------------------------------+
//| Detect simple M5 pattern (STUPID VERSION)                       |
//+------------------------------------------------------------------+
bool DetectSimpleM5Pattern(string symbol)
{
    // Get M5 data
    MqlRates rates[];
    if(CopyRates(symbol, TIMEFRAME_M5, 0, 10, rates) < 10)
        return false;
    
    // STUPID M5 BOS detection: Current candle broke previous high/low
    double currentHigh = rates[9].high;
    double currentLow = rates[9].low;
    double previousHigh = rates[8].high;
    double previousLow = rates[8].low;
    
    // Simple break detection
    bool bullishBreak = (currentHigh > previousHigh);
    bool bearishBreak = (currentLow < previousLow);
    
    // STUPID ylipip check (simplified)
    double priceMove = MathAbs(rates[9].close - rates[8].close);
    double point = SymbolInfoDouble(symbol, SYMBOL_POINT);
    double pipMove = priceMove / (point * 10); // Rough pip calculation
    
    bool ylipipTriggered = (pipMove >= YlipipTrigger);
    
    if(DebugMode && (bullishBreak || bearishBreak))
    {
        Print("STUPID PATTERN DETECTED on ", symbol, ": Break=", (bullishBreak ? "BULL" : "BEAR"), 
              ", PipMove=", pipMove, ", YlipipOK=", ylipipTriggered);
    }
    
    return (bullishBreak || bearishBreak) && ylipipTriggered;
}

//+------------------------------------------------------------------+
//| Send stupid signal to Python MCP/ML system                      |
//+------------------------------------------------------------------+
void SendStupidSignalToPython(string symbol)
{
    Print("============================================================");
    Print("STUPID SIGNAL DETECTED: ", symbol);
    Print("============================================================");
    
    // Get current price data
    MqlTick tick;
    if(!SymbolInfoTick(symbol, tick))
        return;
        
    // Create STUPID signal (no intelligence, just raw data)
    string stupidSignal = StringFormat(
        "{"
        "\"timestamp\":\"%s\","
        "\"symbol\":\"%s\","
        "\"pattern\":\"M5_BOS_DETECTED\","
        "\"current_price\":%.5f,"
        "\"ylipip_trigger\":%.2f,"
        "\"source\":\"STUPID_EA_v8\","
        "\"intelligence_needed\":\"PYTHON_MCP_ML\","
        "\"build_version\":\"%s\""
        "}",
        TimeToString(TimeCurrent()),
        symbol,
        tick.bid,
        YlipipTrigger,
        currentBuild
    );
    
    // Write signal file for Python
    int file = FileOpen("m5_pattern_signal.json", FILE_WRITE | FILE_TXT | FILE_COMMON);
    if(file != INVALID_HANDLE)
    {
        FileWriteString(file, stupidSignal);
        FileClose(file);
        
        Print("STUPID SIGNAL SENT TO PYTHON:");
        Print("  Symbol: ", symbol);
        Print("  Pattern: M5_BOS_DETECTED");
        Print("  Price: ", tick.bid);
        Print("  Message: Python MCP/ML system - please do ALL the thinking!");
    }
    else
    {
        Print("ERROR: Failed to send stupid signal to Python");
    }
}

//+------------------------------------------------------------------+
//| Check for execution commands from Python                        |
//+------------------------------------------------------------------+
void CheckForPythonExecutionCommands()
{
    // Check if Python sent us a trade to execute
    if(!FileIsExist(executionFilePath))
        return;
        
    // Read execution command from Python
    int file = FileOpen("python_execution_command.json", FILE_READ | FILE_TXT | FILE_COMMON);
    if(file == INVALID_HANDLE)
        return;
        
    string commandContent = FileReadString(file, (int)FileSize(file));
    FileClose(file);
    
    if(StringLen(commandContent) == 0)
        return;
        
    // Execute Python's command (STUPID execution)
    ExecutePythonCommand(commandContent);
    
    // Delete processed command file
    FileDelete("python_execution_command.json", FILE_COMMON);
}

//+------------------------------------------------------------------+
//| Execute command from Python (STUPID execution)                  |
//+------------------------------------------------------------------+
void ExecutePythonCommand(string commandData)
{
    Print("============================================================");
    Print("EXECUTING PYTHON COMMAND - STUPID EA v8");
    Print("============================================================");
    
    // Parse Python's command (simplified JSON parsing)
    string symbol = ExtractValue(commandData, "symbol");
    string direction = ExtractValue(commandData, "direction");
    double lotSize = StringToDouble(ExtractValue(commandData, "lot_size"));
    double slPrice = StringToDouble(ExtractValue(commandData, "sl_price"));
    double tpPrice = StringToDouble(ExtractValue(commandData, "tp_price"));
    
    Print("PYTHON CALCULATED VALUES:");
    Print("  Symbol: ", symbol);
    Print("  Direction: ", direction);
    Print("  Lot Size: ", lotSize, " (Python calculated)");
    Print("  SL Price: ", slPrice, " (Python calculated)");
    Print("  TP Price: ", tpPrice, " (Python calculated)");
    Print("  STUPID EA: Just executing Python's intelligence...");
    
    // STUPID execution - just do what Python calculated
    MqlTradeRequest request;
    MqlTradeResult result;
    
    ZeroMemory(request);
    request.action = TRADE_ACTION_DEAL;
    request.symbol = symbol;
    request.volume = lotSize;
    request.type = (direction == "BUY") ? ORDER_TYPE_BUY : ORDER_TYPE_SELL;
    request.price = (direction == "BUY") ? SymbolInfoDouble(symbol, SYMBOL_ASK) : SymbolInfoDouble(symbol, SYMBOL_BID);
    request.sl = slPrice;
    request.tp = tpPrice;
    request.magic = MagicNumber;
    request.comment = "StupidEA_v8_PythonExecution";
    request.type_filling = ORDER_FILLING_FOK;
    
    bool orderResult = OrderSend(request, result);
    
    if(orderResult && result.retcode == TRADE_RETCODE_DONE)
    {
        Print("SUCCESS: STUPID EA executed Python's trade");
        Print("  Trade: ", direction, " ", lotSize, " ", symbol);
        Print("  Order: #", result.order);
        Print("  SL: ", slPrice, " | TP: ", tpPrice);
        Print("  PYTHON DID ALL THE THINKING - EA JUST EXECUTED!");
    }
    else
    {
        Print("ERROR: STUPID EA failed to execute Python's trade");
        Print("  Error: ", result.comment);
    }
}

//+------------------------------------------------------------------+
//| Extract value from JSON-like string                            |
//+------------------------------------------------------------------+
string ExtractValue(string data, string key)
{
    string searchPattern = "\"" + key + "\":";
    int startPos = StringFind(data, searchPattern);
    if(startPos == -1) return "";
    
    startPos += StringLen(searchPattern);
    
    // Skip whitespace and quotes
    while(startPos < StringLen(data) && (StringGetCharacter(data, startPos) == ' ' || StringGetCharacter(data, startPos) == '"'))
        startPos++;
        
    int endPos = startPos;
    while(endPos < StringLen(data) && StringGetCharacter(data, endPos) != ',' && StringGetCharacter(data, endPos) != '}' && StringGetCharacter(data, endPos) != '"')
        endPos++;
        
    return StringSubstr(data, startPos, endPos - startPos);
}

//+------------------------------------------------------------------+