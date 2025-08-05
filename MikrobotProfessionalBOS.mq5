//+------------------------------------------------------------------+
//|                                    MikrobotProfessionalBOS.mq5  |
//|           25,000 EUR MARKET STRUCTURE EDUCATION IMPLEMENTATION   |
//|              PROFESSIONAL MARKET READING - HH/HL/LH/LL LOGIC     |
//+------------------------------------------------------------------+
#property copyright "MIKROBOT PROFESSIONAL - 25K EUR Market Structure"
#property version   "1.00"
#property description "Professional Market Structure Reading - HH/HL/LH/LL + Contextual BOS"
#property strict

//--- Input parameters
input double YlipipTrigger = 0.6;              
input int    MagicNumber = 999888;             
input bool   DebugMode = true;                 

//--- Market Structure Analysis
enum MarketStructure
{
    UPTREND,        // HH + HL pattern
    DOWNTREND,      // LH + LL pattern  
    TRANSITION,     // Mixed signals
    UNKNOWN         // Insufficient data
};

enum SwingType
{
    HIGHER_HIGH,    // HH
    HIGHER_LOW,     // HL  
    LOWER_HIGH,     // LH
    LOWER_LOW       // LL
};

//--- Global structure tracking
MarketStructure currentTrend = UNKNOWN;
double lastSwingHigh = 0;
double lastSwingLow = 0;
datetime lastSwingHighTime = 0;
datetime lastSwingLowTime = 0;

//--- Professional BOS detection
bool professionalBOS = false;
string bosType = "";
double bosLevel = 0;

//+------------------------------------------------------------------+
//| Professional Market Structure Analysis                          |
//+------------------------------------------------------------------+
MarketStructure AnalyzeMarketStructure(string symbol)
{
    MqlRates rates[];
    if(CopyRates(symbol, PERIOD_M5, 0, 50, rates) < 50)
        return UNKNOWN;
    
    // Find significant swing points over 50 candles
    double swingHighs[10];
    double swingLows[10];  
    datetime swingHighTimes[10];
    datetime swingLowTimes[10];
    int highCount = 0, lowCount = 0;
    
    // Professional swing detection - look for significant peaks/valleys
    for(int i = 5; i < 45; i++)  // Avoid edges
    {
        bool isSwingHigh = true;
        bool isSwingLow = true;
        
        // Check if this is a swing high (higher than 5 candles on each side)
        for(int j = i-5; j <= i+5; j++)
        {
            if(j != i && rates[j].high >= rates[i].high)
                isSwingHigh = false;
            if(j != i && rates[j].low <= rates[i].low)
                isSwingLow = false;
        }
        
        if(isSwingHigh && highCount < 10)
        {
            swingHighs[highCount] = rates[i].high;
            swingHighTimes[highCount] = rates[i].time;
            highCount++;
        }
        
        if(isSwingLow && lowCount < 10) 
        {
            swingLows[lowCount] = rates[i].low;
            swingLowTimes[lowCount] = rates[i].time;
            lowCount++;
        }
    }
    
    if(highCount < 3 || lowCount < 3)
        return UNKNOWN;
    
    // Analyze structure pattern - PROFESSIONAL LOGIC
    int higherHighs = 0, lowerHighs = 0;
    int higherLows = 0, lowerLows = 0;
    
    // Count HH/LH pattern in highs
    for(int i = 1; i < highCount; i++)
    {
        if(swingHighs[i] > swingHighs[i-1])
            higherHighs++;
        else
            lowerHighs++;
    }
    
    // Count HL/LL pattern in lows  
    for(int i = 1; i < lowCount; i++)
    {
        if(swingLows[i] > swingLows[i-1]) 
            higherLows++;
        else
            lowerLows++;
    }
    
    // Professional structure classification
    if(DebugMode)
    {
        Print("MARKET STRUCTURE ANALYSIS:");
        Print("  Higher Highs: ", higherHighs, " vs Lower Highs: ", lowerHighs);
        Print("  Higher Lows: ", higherLows, " vs Lower Lows: ", lowerLows);
    }
    
    // Determine trend based on PROFESSIONAL LOGIC
    if(higherHighs > lowerHighs && higherLows > lowerLows)
        return UPTREND;    // HH + HL = Uptrend
    else if(lowerHighs > higherHighs && lowerLows > higherLows)  
        return DOWNTREND;  // LH + LL = Downtrend
    else
        return TRANSITION; // Mixed signals
}

//+------------------------------------------------------------------+
//| PROFESSIONAL BOS Detection - 25K EUR Logic                     |
//+------------------------------------------------------------------+
bool DetectProfessionalBOS(string symbol)
{
    // First analyze current market structure
    MarketStructure structure = AnalyzeMarketStructure(symbol);
    currentTrend = structure;
    
    if(structure == UNKNOWN)
        return false;
    
    MqlRates rates[];
    if(CopyRates(symbol, PERIOD_M5, 0, 20, rates) < 20)
        return false;
    
    double currentHigh = rates[19].high;
    double currentLow = rates[19].low;
    
    // Find the most recent significant structural levels
    double keyResistance = 0, keySupport = 0;
    
    // Look for last significant swing high/low
    for(int i = 18; i >= 5; i--)
    {
        // Check for swing high
        if(rates[i].high > rates[i-1].high && rates[i].high > rates[i+1].high &&
           rates[i].high > rates[i-2].high && rates[i].high > rates[i+2].high)
        {
            if(keyResistance == 0 || rates[i].high > keyResistance)
                keyResistance = rates[i].high;
        }
        
        // Check for swing low
        if(rates[i].low < rates[i-1].low && rates[i].low < rates[i+1].low &&
           rates[i].low < rates[i-2].low && rates[i].low < rates[i+2].low)
        {
            if(keySupport == 0 || rates[i].low < keySupport)
                keySupport = rates[i].low;
        }
    }
    
    bool bosDetected = false;
    
    // PROFESSIONAL CONTEXTUAL BOS LOGIC - 25K EUR WORTH!
    if(structure == UPTREND)
    {
        // In uptrend, BOS = break below key support (HL level)
        // This signals UPTREND DEATH - like wireframe model
        if(keySupport > 0 && currentLow < keySupport)
        {
            bosDetected = true;
            bosType = "BEARISH_BOS_UPTREND_DEATH";
            bosLevel = keySupport;
            
            if(DebugMode)
            {
                Print("*** PROFESSIONAL BOS DETECTED ***");
                Print("UPTREND DEATH - Bearish BOS");
                Print("Broke below key support: ", keySupport);
                Print("Current low: ", currentLow);
                Print("Market transitioning from UPTREND to DOWNTREND");
            }
        }
    }
    else if(structure == DOWNTREND)
    {
        // In downtrend, BOS = break above key resistance (LH level)  
        // This signals DOWNTREND DEATH - like wireframe model
        if(keyResistance > 0 && currentHigh > keyResistance)
        {
            bosDetected = true;
            bosType = "BULLISH_BOS_DOWNTREND_DEATH";
            bosLevel = keyResistance;
            
            if(DebugMode)
            {
                Print("*** PROFESSIONAL BOS DETECTED ***");
                Print("DOWNTREND DEATH - Bullish BOS");
                Print("Broke above key resistance: ", keyResistance);
                Print("Current high: ", currentHigh);
                Print("Market transitioning from DOWNTREND to UPTREND");
            }
        }
    }
    
    if(bosDetected)
    {
        professionalBOS = true;
        
        if(DebugMode)
        {
            Print("=== 25K EUR MARKET STRUCTURE EDUCATION IN ACTION ===");
            Print("BOS Type: ", bosType);
            Print("BOS Level: ", bosLevel);
            Print("Previous Trend: ", EnumToString(structure));
            Print("Signal: DROP TO M1 FOR BREAK-AND-RETEST + 0.6 YLIPIP!");
            Print("=== PROFESSIONAL MARKET READING ACTIVATED ===");
        }
    }
    
    return bosDetected;
}

//+------------------------------------------------------------------+
//| Expert initialization function                                   |
//+------------------------------------------------------------------+
int OnInit()
{
    Print("======================================================================");
    Print("MIKROBOT PROFESSIONAL BOS - 25,000 EUR MARKET STRUCTURE EDUCATION");
    Print("PROFESSIONAL MARKET READING - HH/HL/LH/LL LOGIC DEPLOYED");
    Print("======================================================================");
    
    Print("PROFESSIONAL FEATURES ACTIVATED:");
    Print("✓ Market Structure Analysis (HH/HL/LH/LL patterns)");
    Print("✓ Contextual BOS Detection (Uptrend/Downtrend Death)");
    Print("✓ Professional Market Reading (25K EUR Education)");
    Print("✓ Winning Trader Logic Implementation");
    
    currentTrend = UNKNOWN;
    professionalBOS = false;
    
    return(INIT_SUCCEEDED);
}

//+------------------------------------------------------------------+
//| THE LB LIGHTNING BOLT DETECTION - COMPLETE BIDIRECTIONAL SYSTEM|
//+------------------------------------------------------------------+
bool DetectLightningBolt(string symbol, double bosLevel, string bosDirection)
{
    MqlRates rates[];
    if(CopyRates(symbol, PERIOD_M1, 0, 20, rates) < 20)
        return false;
    
    // COMPLETE BIDIRECTIONAL LIGHTNING BOLT SYSTEM
    bool breakDetected = false;
    bool retestDetected = false;
    int breakCandleIndex = -1;
    int retestCandleIndex = -1;
    
    if(bosDirection == "BULLISH_BOS_DOWNTREND_DEATH")
    {
        // BULLISH Lightning Bolt: Break ABOVE resistance → Retest DOWN → Entry ABOVE
        
        // Phase 1: Find BREAK ABOVE resistance (BOS level)
        for(int i = 15; i < 19; i++)
        {
            if(rates[i].high > bosLevel && rates[i-1].high <= bosLevel)
            {
                breakDetected = true;
                breakCandleIndex = i;
                
                if(DebugMode)
                {
                    Print("⚡ BULLISH LIGHTNING BOLT PHASE 1: BREAK ABOVE RESISTANCE");
                    Print("  Break Candle: ", i);
                    Print("  Break High: ", rates[i].high);
                    Print("  Resistance Level: ", bosLevel);
                }
                break;
            }
        }
        
        if(!breakDetected) return false;
        
        // Phase 2: Find RETEST back DOWN to resistance
        for(int i = breakCandleIndex + 1; i < 19; i++)
        {
            double tolerance = 3 * SymbolInfoDouble(symbol, SYMBOL_POINT);
            
            if(rates[i].low <= bosLevel + tolerance && rates[i].low >= bosLevel - tolerance)
            {
                retestDetected = true;
                retestCandleIndex = i;
                
                if(DebugMode)
                {
                    Print("⚡ BULLISH LIGHTNING BOLT PHASE 2: RETEST DOWN TO SUPPORT");
                    Print("  Retest Candle: ", i);
                    Print("  Retest Low: ", rates[i].low);
                    Print("  Support Level (ex-resistance): ", bosLevel);
                }
                break;
            }
        }
    }
    else if(bosDirection == "BEARISH_BOS_UPTREND_DEATH")
    {
        // BEARISH Lightning Bolt: Break BELOW support → Retest UP → Entry BELOW
        
        // Phase 1: Find BREAK BELOW support (BOS level)
        for(int i = 15; i < 19; i++)
        {
            if(rates[i].low < bosLevel && rates[i-1].low >= bosLevel)
            {
                breakDetected = true;
                breakCandleIndex = i;
                
                if(DebugMode)
                {
                    Print("⚡ BEARISH LIGHTNING BOLT PHASE 1: BREAK BELOW SUPPORT");
                    Print("  Break Candle: ", i);
                    Print("  Break Low: ", rates[i].low);
                    Print("  Support Level: ", bosLevel);
                }
                break;
            }
        }
        
        if(!breakDetected) return false;
        
        // Phase 2: Find RETEST back UP to support
        for(int i = breakCandleIndex + 1; i < 19; i++)
        {
            double tolerance = 3 * SymbolInfoDouble(symbol, SYMBOL_POINT);
            
            if(rates[i].high >= bosLevel - tolerance && rates[i].high <= bosLevel + tolerance)
            {
                retestDetected = true;
                retestCandleIndex = i;
                
                if(DebugMode)
                {
                    Print("⚡ BEARISH LIGHTNING BOLT PHASE 2: RETEST UP TO RESISTANCE");
                    Print("  Retest Candle: ", i);
                    Print("  Retest High: ", rates[i].high);
                    Print("  Resistance Level (ex-support): ", bosLevel);
                }
                break;
            }
        }
    }
    
    if(!retestDetected) return false;
    
    // Phase 3: Validate 3+ CANDLE LB formation
    int candleCount = retestCandleIndex - breakCandleIndex + 1;
    
    if(candleCount >= 3)
    {
        double currentPrice = rates[19].close;
        bool lightningBoltConfirmed = false;
        
        if(bosDirection == "BULLISH_BOS_DOWNTREND_DEATH")
        {
            // Confirm bullish continuation after retest
            double retestLow = rates[retestCandleIndex].low;
            lightningBoltConfirmed = (currentPrice > retestLow + (2 * SymbolInfoDouble(symbol, SYMBOL_POINT)));
        }
        else if(bosDirection == "BEARISH_BOS_UPTREND_DEATH")
        {
            // Confirm bearish continuation after retest
            double retestHigh = rates[retestCandleIndex].high;
            lightningBoltConfirmed = (currentPrice < retestHigh - (2 * SymbolInfoDouble(symbol, SYMBOL_POINT)));
        }
        
        if(lightningBoltConfirmed)
        {
            if(DebugMode)
            {
                Print("⚡⚡⚡ LIGHTNING BOLT CONFIRMED! ⚡⚡⚡");
                Print("  Direction: ", bosDirection == "BULLISH_BOS_DOWNTREND_DEATH" ? "BULLISH" : "BEARISH");
                Print("  Pattern: 3+ CANDLE LB");
                Print("  Candle Count: ", candleCount);
                Print("  Current Price: ", currentPrice);
                Print("  READY FOR 0.6 YLIPIP ENTRY!");
                Print("⚡ BIDIRECTIONAL LIGHTNING BOLT COMPLETE ⚡");
            }
            
            return true;
        }
    }
    
    return false;
}

//+------------------------------------------------------------------+
//| 0.6 YLIPIP Entry Calculation - BIDIRECTIONAL SYSTEM           |
//+------------------------------------------------------------------+
double CalculateYlipipEntry(string symbol, double retestLevel, string direction)
{
    double pipValue = 0.01; // For JPY pairs
    if(StringFind(symbol, "JPY") < 0)
        pipValue = 0.0001; // For major pairs
    
    double ylipipEntry;
    
    if(direction == "BULLISH_BOS_DOWNTREND_DEATH")
    {
        // BULLISH: Entry ABOVE retest level + 0.6 pips
        ylipipEntry = retestLevel + (0.6 * pipValue);
    }
    else if(direction == "BEARISH_BOS_UPTREND_DEATH")
    {
        // BEARISH: Entry BELOW retest level - 0.6 pips  
        ylipipEntry = retestLevel - (0.6 * pipValue);
    }
    
    if(DebugMode)
    {
        Print("💰 BIDIRECTIONAL YLIPIP ENTRY CALCULATION:");
        Print("  Direction: ", direction == "BULLISH_BOS_DOWNTREND_DEATH" ? "BUY" : "SELL");
        Print("  Retest Level: ", retestLevel);
        Print("  Pip Value: ", pipValue);
        Print("  YLIPIP Entry: ", ylipipEntry);
        Print("  Entry Type: ", direction == "BULLISH_BOS_DOWNTREND_DEATH" ? "ABOVE retest + 0.6" : "BELOW retest - 0.6");
        Print("  Ready for BIDIRECTIONAL LIGHTNING BOLT EXECUTION!");
    }
    
    return ylipipEntry;
}

//+------------------------------------------------------------------+
//| Expert tick function - COMPLETE 25K EUR SYSTEM                 |
//+------------------------------------------------------------------+
void OnTick()
{
    static datetime lastCheck = 0;
    static bool bosActive = false;
    
    if(TimeCurrent() - lastCheck >= 5)  // Check every 5 seconds
    {
        // Phase 1: Professional M5 BOS Detection
        if(!bosActive && DetectProfessionalBOS(Symbol()))
        {
            bosActive = true;
            // bosLevel is now set globally by DetectProfessionalBOS function
            
            Print("🎯 M5 BOS DETECTED - SWITCHING TO M1 LIGHTNING BOLT MODE");
            Print("  BOS Level: ", bosLevel);
            Print("  Monitoring M1 for Lightning Bolt pattern...");
        }
        
        // Phase 2: Bidirectional Lightning Bolt Detection on M1
        if(bosActive && bosLevel > 0)
        {
            if(DetectLightningBolt(Symbol(), bosLevel, bosType))
            {
                // Phase 3: Calculate perfect bidirectional entry
                double ylipipEntry = CalculateYlipipEntry(Symbol(), bosLevel, bosType);
                
                string tradeDirection = (bosType == "BULLISH_BOS_DOWNTREND_DEATH") ? "BUY" : "SELL";
                
                Print("🚀 COMPLETE BIDIRECTIONAL 25K EUR SYSTEM ACTIVATION:");
                Print("  ✓ M5 BOS: Professional market structure reading");
                Print("  ✓ M1 Lightning Bolt: 3+ candle LB pattern confirmed");
                Print("  ✓ Direction: ", tradeDirection, " trade setup");
                Print("  ✓ 0.6 YLIPIP Entry: ", ylipipEntry);
                Print("  🎯 READY FOR BIDIRECTIONAL PROFESSIONAL EXECUTION!");
                Print("=== BIDIRECTIONAL LIGHTNING BOLT TRADE SIGNAL ACTIVE ===");
                
                // Reset for next opportunity
                bosActive = false;
                bosLevel = 0;
            }
        }
        
        lastCheck = TimeCurrent();
    }
}

//+------------------------------------------------------------------+