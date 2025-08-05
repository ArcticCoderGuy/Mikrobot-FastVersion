//+------------------------------------------------------------------+
//|                                            MikrobotSignalEA.mq5  |
//|                                          Mikrobot Signal Processor|
//|                              Solves the two-user connection issue|
//+------------------------------------------------------------------+
#property copyright "Mikrobot FastVersion"
#property link      "https://mikrobot.fi"
#property version   "1.00"
#property strict

// Input parameters
input int      SignalCheckInterval = 100;    // Check signals every X milliseconds
input int      MagicNumber = 20250802;       // Magic number for bot trades
input bool     EnableNotifications = true;    // Send mobile notifications
input bool     EnableLogging = true;         // Write detailed logs

// Global variables
string SignalFile = "signal.json";
string ResponseFile = "response.json";
int LastSignalId = 0;

//+------------------------------------------------------------------+
//| Expert initialization function                                   |
//+------------------------------------------------------------------+
int OnInit()
{
   Print("=== Mikrobot Signal EA Started ===");
   Print("Account: ", AccountInfoInteger(ACCOUNT_LOGIN));
   Print("Server: ", AccountInfoString(ACCOUNT_SERVER));
   Print("Signal check interval: ", SignalCheckInterval, " ms");
   
   // Create timer for signal checking
   EventSetMillisecondTimer(SignalCheckInterval);
   
   // Send notification
   if(EnableNotifications)
   {
      SendNotification("Mikrobot EA started on " + Symbol());
   }
   
   return(INIT_SUCCEEDED);
}

//+------------------------------------------------------------------+
//| Expert deinitialization function                                 |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
{
   EventKillTimer();
   Print("=== Mikrobot Signal EA Stopped ===");
}

//+------------------------------------------------------------------+
//| Timer function - Check for new signals                          |
//+------------------------------------------------------------------+
void OnTimer()
{
   // Check if signal file exists
   if(!FileIsExist(SignalFile))
      return;
   
   // Read signal
   int handle = FileOpen(SignalFile, FILE_READ|FILE_TXT|FILE_ANSI|FILE_COMMON);
   if(handle == INVALID_HANDLE)
      return;
   
   string jsonStr = "";
   while(!FileIsEnding(handle))
   {
      jsonStr += FileReadString(handle);
   }
   FileClose(handle);
   
   // Delete signal file after reading
   FileDelete(SignalFile, FILE_COMMON);
   
   // Process signal
   ProcessSignal(jsonStr);
}

//+------------------------------------------------------------------+
//| Process incoming signal                                          |
//+------------------------------------------------------------------+
void ProcessSignal(string jsonStr)
{
   // Parse JSON manually (MQL5 doesn't have built-in JSON)
   int signalId = GetJsonInt(jsonStr, "id");
   string action = GetJsonString(jsonStr, "action");
   
   if(signalId <= LastSignalId)
      return; // Already processed
   
   LastSignalId = signalId;
   
   if(EnableLogging)
      Print("Processing signal #", signalId, " Action: ", action);
   
   // Process based on action type
   if(action == "PLACE_ORDER")
   {
      ProcessPlaceOrder(jsonStr, signalId);
   }
   else if(action == "GET_ACCOUNT_INFO")
   {
      ProcessAccountInfo(signalId);
   }
   else if(action == "GET_POSITIONS")
   {
      ProcessGetPositions(signalId);
   }
   else if(action == "CLOSE_POSITION")
   {
      ProcessClosePosition(jsonStr, signalId);
   }
}

//+------------------------------------------------------------------+
//| Process place order signal                                       |
//+------------------------------------------------------------------+
void ProcessPlaceOrder(string jsonStr, int signalId)
{
   string symbol = GetJsonString(jsonStr, "symbol");
   string orderType = GetJsonString(jsonStr, "order_type");
   double volume = GetJsonDouble(jsonStr, "volume");
   double sl = GetJsonDouble(jsonStr, "sl");
   double tp = GetJsonDouble(jsonStr, "tp");
   string comment = GetJsonString(jsonStr, "comment");
   
   // Validate symbol
   if(!SymbolSelect(symbol, true))
   {
      WriteResponse(signalId, "error", "Symbol not available: " + symbol, 0);
      return;
   }
   
   // Get current price
   double price = 0;
   ENUM_ORDER_TYPE type;
   
   if(orderType == "BUY")
   {
      type = ORDER_TYPE_BUY;
      price = SymbolInfoDouble(symbol, SYMBOL_ASK);
   }
   else if(orderType == "SELL")
   {
      type = ORDER_TYPE_SELL;
      price = SymbolInfoDouble(symbol, SYMBOL_BID);
   }
   else
   {
      WriteResponse(signalId, "error", "Invalid order type: " + orderType, 0);
      return;
   }
   
   // Prepare trade request
   MqlTradeRequest request = {};
   MqlTradeResult result = {};
   
   request.action = TRADE_ACTION_DEAL;
   request.symbol = symbol;
   request.volume = volume;
   request.type = type;
   request.price = price;
   request.sl = sl;
   request.tp = tp;
   request.deviation = 10;
   request.magic = MagicNumber;
   request.comment = comment;
   
   // Send order
   if(OrderSend(request, result))
   {
      if(result.retcode == TRADE_RETCODE_DONE)
      {
         WriteResponse(signalId, "success", "Order placed", (int)result.order);
         
         if(EnableNotifications)
         {
            string msg = StringFormat("%s %s %.2f %s @ %.5f", 
                        orderType, symbol, volume, 
                        AccountInfoString(ACCOUNT_CURRENCY), price);
            SendNotification("Mikrobot: " + msg);
         }
      }
      else
      {
         WriteResponse(signalId, "error", "Order failed: " + IntegerToString(result.retcode), 0);
      }
   }
   else
   {
      WriteResponse(signalId, "error", "OrderSend failed", 0);
   }
}

//+------------------------------------------------------------------+
//| Process account info request                                     |
//+------------------------------------------------------------------+
void ProcessAccountInfo(int signalId)
{
   string response = StringFormat(
      "{\"signal_id\": %d, \"status\": \"success\", " +
      "\"account\": %d, \"balance\": %.2f, \"equity\": %.2f, " +
      "\"margin\": %.2f, \"free_margin\": %.2f, \"currency\": \"%s\"}",
      signalId,
      AccountInfoInteger(ACCOUNT_LOGIN),
      AccountInfoDouble(ACCOUNT_BALANCE),
      AccountInfoDouble(ACCOUNT_EQUITY),
      AccountInfoDouble(ACCOUNT_MARGIN),
      AccountInfoDouble(ACCOUNT_MARGIN_FREE),
      AccountInfoString(ACCOUNT_CURRENCY)
   );
   
   WriteResponseRaw(response);
}

//+------------------------------------------------------------------+
//| Process get positions request                                    |
//+------------------------------------------------------------------+
void ProcessGetPositions(int signalId)
{
   int total = PositionsTotal();
   string positions = "";
   
   for(int i = 0; i < total; i++)
   {
      if(PositionSelectByTicket(PositionGetTicket(i)))
      {
         if(i > 0) positions += ", ";
         
         positions += StringFormat(
            "{\"ticket\": %d, \"symbol\": \"%s\", \"type\": \"%s\", " +
            "\"volume\": %.2f, \"profit\": %.2f}",
            PositionGetInteger(POSITION_TICKET),
            PositionGetString(POSITION_SYMBOL),
            PositionGetInteger(POSITION_TYPE) == POSITION_TYPE_BUY ? "BUY" : "SELL",
            PositionGetDouble(POSITION_VOLUME),
            PositionGetDouble(POSITION_PROFIT)
         );
      }
   }
   
   string response = StringFormat(
      "{\"signal_id\": %d, \"status\": \"success\", \"count\": %d, \"positions\": [%s]}",
      signalId, total, positions
   );
   
   WriteResponseRaw(response);
}

//+------------------------------------------------------------------+
//| Write response to file                                          |
//+------------------------------------------------------------------+
void WriteResponse(int signalId, string status, string message, int ticket)
{
   string response = StringFormat(
      "{\"signal_id\": %d, \"status\": \"%s\", \"message\": \"%s\", \"ticket\": %d, \"timestamp\": \"%s\"}",
      signalId, status, message, ticket, TimeToString(TimeCurrent())
   );
   
   WriteResponseRaw(response);
}

//+------------------------------------------------------------------+
//| Write raw response string to file                                |
//+------------------------------------------------------------------+
void WriteResponseRaw(string response)
{
   int handle = FileOpen(ResponseFile, FILE_WRITE|FILE_TXT|FILE_ANSI|FILE_COMMON);
   if(handle != INVALID_HANDLE)
   {
      FileWriteString(handle, response);
      FileClose(handle);
   }
}

//+------------------------------------------------------------------+
//| Simple JSON parser functions                                     |
//+------------------------------------------------------------------+
string GetJsonString(string json, string key)
{
   int start = StringFind(json, "\"" + key + "\"");
   if(start == -1) return "";
   
   start = StringFind(json, "\"", start + StringLen(key) + 2) + 1;
   int end = StringFind(json, "\"", start);
   
   return StringSubstr(json, start, end - start);
}

int GetJsonInt(string json, string key)
{
   int start = StringFind(json, "\"" + key + "\"");
   if(start == -1) return 0;
   
   start = StringFind(json, ":", start) + 1;
   int end = StringFind(json, ",", start);
   if(end == -1) end = StringFind(json, "}", start);
   
   string value = StringSubstr(json, start, end - start);
   StringTrimLeft(value);
   StringTrimRight(value);
   
   return (int)StringToInteger(value);
}

double GetJsonDouble(string json, string key)
{
   int start = StringFind(json, "\"" + key + "\"");
   if(start == -1) return 0;
   
   start = StringFind(json, ":", start) + 1;
   int end = StringFind(json, ",", start);
   if(end == -1) end = StringFind(json, "}", start);
   
   string value = StringSubstr(json, start, end - start);
   StringTrimLeft(value);
   StringTrimRight(value);
   
   return StringToDouble(value);
}

//+------------------------------------------------------------------+
//| Process close position signal                                    |
//+------------------------------------------------------------------+
void ProcessClosePosition(string jsonStr, int signalId)
{
   int ticket = GetJsonInt(jsonStr, "ticket");
   
   if(PositionSelectByTicket(ticket))
   {
      MqlTradeRequest request = {};
      MqlTradeResult result = {};
      
      request.action = TRADE_ACTION_DEAL;
      request.position = ticket;
      request.symbol = PositionGetString(POSITION_SYMBOL);
      request.volume = PositionGetDouble(POSITION_VOLUME);
      request.type = PositionGetInteger(POSITION_TYPE) == POSITION_TYPE_BUY ? ORDER_TYPE_SELL : ORDER_TYPE_BUY;
      request.price = PositionGetInteger(POSITION_TYPE) == POSITION_TYPE_BUY ? 
                      SymbolInfoDouble(request.symbol, SYMBOL_BID) : 
                      SymbolInfoDouble(request.symbol, SYMBOL_ASK);
      request.deviation = 10;
      request.magic = MagicNumber;
      
      if(OrderSend(request, result))
      {
         WriteResponse(signalId, "success", "Position closed", ticket);
      }
      else
      {
         WriteResponse(signalId, "error", "Close failed: " + IntegerToString(result.retcode), ticket);
      }
   }
   else
   {
      WriteResponse(signalId, "error", "Position not found", ticket);
   }
}

//+------------------------------------------------------------------+