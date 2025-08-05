//+------------------------------------------------------------------+
//|                                                   MikrobotEA.mq5 |
//|                            Signal-Based Trading Expert Advisor |
//|                      Resolves Python-MT5 connection conflicts   |
//+------------------------------------------------------------------+
#property copyright "Mikrobot FastVersion"
#property version   "2.00"
#property description "Signal-based EA for conflict-free Python integration"

//--- Input parameters
input int    MagicNumber = 999888;         // Magic number for trades
input double DefaultLotSize = 0.01;        // Default lot size
input int    SignalCheckInterval = 100;    // Check signals every 100ms
input int    MaxSignalAge = 300;           // Max signal age in seconds
input bool   EnablePushNotifications = true;
input bool   DebugMode = true;             // Enable debug logging

//--- Global variables
string SignalFileName = "MikrobotEA_signal.json";
string ResponseFileName = "MikrobotEA_response.json";
string StatusFileName = "MikrobotEA_status.json";

datetime LastSignalCheck = 0;
datetime LastHeartbeat = 0;
int TotalSignalsProcessed = 0;
int SuccessfulTrades = 0;
int FailedTrades = 0;

//+------------------------------------------------------------------+
//| Expert initialization function                                   |
//+------------------------------------------------------------------+
int OnInit()
{
   Print("========================================");
   Print("MIKROBOT EA v2.0 - Signal-Based Trading");
   Print("========================================");
   Print("Account: ", AccountInfoInteger(ACCOUNT_LOGIN));
   Print("Server: ", AccountInfoString(ACCOUNT_SERVER));
   Print("Magic Number: ", MagicNumber);
   Print("Signal File: ", SignalFileName);
   Print("Response File: ", ResponseFileName);
   Print("========================================");
   
   // Clean up any existing signal files
   if(FileIsExist(SignalFileName))
      FileDelete(SignalFileName);
   if(FileIsExist(ResponseFileName))
      FileDelete(ResponseFileName);
   
   // Create status file
   UpdateStatusFile("INITIALIZED");
   
   LastHeartbeat = TimeCurrent();
   
   // Send initialization notification
   if(EnablePushNotifications)
   {
      string init_msg = StringFormat("Mikrobot EA Initialized\nAccount: %d\nTime: %s", 
                                    AccountInfoInteger(ACCOUNT_LOGIN), 
                                    TimeToString(TimeCurrent(), TIME_DATE|TIME_MINUTES));
      SendNotification(init_msg);
   }
   
   Print("✅ Mikrobot EA initialized successfully");
   return(INIT_SUCCEEDED);
}

//+------------------------------------------------------------------+
//| Expert deinitialization function                               |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
{
   Print("Mikrobot EA shutting down. Reason: ", reason);
   
   // Clean up files
   if(FileIsExist(SignalFileName))
      FileDelete(SignalFileName);
   if(FileIsExist(ResponseFileName))
      FileDelete(ResponseFileName);
   if(FileIsExist(StatusFileName))
      FileDelete(StatusFileName);
      
   UpdateStatusFile("STOPPED");
   
   Print("🛑 Mikrobot EA deinitialized");
}

//+------------------------------------------------------------------+
//| Expert tick function                                            |
//+------------------------------------------------------------------+
void OnTick()
{
   // Update heartbeat
   LastHeartbeat = TimeCurrent();
   
   // Check for new signals every interval
   if(TimeCurrent() - LastSignalCheck >= SignalCheckInterval/1000.0)
   {
      CheckForSignals();
      LastSignalCheck = TimeCurrent();
   }
   
   // Update status file periodically (every 30 seconds)
   static datetime last_status_update = 0;
   if(TimeCurrent() - last_status_update >= 30)
   {
      UpdateStatusFile("RUNNING");
      last_status_update = TimeCurrent();
   }
}

//+------------------------------------------------------------------+
//| Check for new trading signals                                   |
//+------------------------------------------------------------------+
void CheckForSignals()
{
   if(!FileIsExist(SignalFileName))
      return;
      
   // Read signal file
   int file_handle = FileOpen(SignalFileName, FILE_READ|FILE_TXT);
   if(file_handle == INVALID_HANDLE)
   {
      if(DebugMode)
         Print("⚠️ Cannot open signal file: ", GetLastError());
      return;
   }
   
   string signal_content = "";
   while(!FileIsEnd(file_handle))
   {
      signal_content += FileReadString(file_handle) + "\n";
   }
   FileClose(file_handle);
   
   if(StringLen(signal_content) == 0)
      return;
   
   if(DebugMode)
      Print("📥 Processing signal: ", StringSubstr(signal_content, 0, 100), "...");
   
   // Parse and process signal
   ProcessSignal(signal_content);
   
   // Remove processed signal file
   FileDelete(SignalFileName);
   
   TotalSignalsProcessed++;
}

//+------------------------------------------------------------------+
//| Process trading signal                                          |
//+------------------------------------------------------------------+
void ProcessSignal(string signal_json)
{
   // Simple JSON parsing for signal data
   string signal_id = ExtractJsonValue(signal_json, "signal_id");
   string signal_type = ExtractJsonValue(signal_json, "signal_type");
   string symbol = ExtractJsonValue(signal_json, "symbol");
   string action = ExtractJsonValue(signal_json, "action");
   string volume_str = ExtractJsonValue(signal_json, "volume");
   string price_str = ExtractJsonValue(signal_json, "price");
   string sl_str = ExtractJsonValue(signal_json, "sl");
   string tp_str = ExtractJsonValue(signal_json, "tp");
   string comment = ExtractJsonValue(signal_json, "comment");
   string timestamp_str = ExtractJsonValue(signal_json, "timestamp");
   
   if(DebugMode)
   {
      Print("📊 Signal Details:");
      Print("  ID: ", signal_id);
      Print("  Type: ", signal_type);
      Print("  Symbol: ", symbol);
      Print("  Action: ", action);
      Print("  Volume: ", volume_str);
   }
   
   // Validate signal age
   if(!ValidateSignalAge(timestamp_str))
   {
      SendResponse(signal_id, false, 0, 10001, "Signal expired");
      return;
   }
   
   // Process different signal types
   if(signal_type == "CONNECTION_TEST")
   {
      ProcessConnectionTest(signal_id);
   }
   else if(signal_type == "OPEN")
   {
      ProcessOpenOrder(signal_id, symbol, action, StringToDouble(volume_str), 
                      StringToDouble(price_str), StringToDouble(sl_str), 
                      StringToDouble(tp_str), comment);
   }
   else if(signal_type == "CLOSE")
   {
      string ticket_str = ExtractJsonValue(signal_json, "ticket");
      ProcessCloseOrder(signal_id, StringToInteger(ticket_str));
   }
   else if(signal_type == "STATUS_REQUEST")
   {
      ProcessStatusRequest(signal_id, action);
   }
   else if(signal_type == "DISCONNECT")
   {
      ProcessDisconnect(signal_id);
   }
   else
   {
      Print("❌ Unknown signal type: ", signal_type);
      SendResponse(signal_id, false, 0, 10002, "Unknown signal type");
   }
}

//+------------------------------------------------------------------+
//| Process connection test                                         |
//+------------------------------------------------------------------+
void ProcessConnectionTest(string signal_id)
{
   Print("🔗 Connection test received");
   
   // Get account info for response
   string account_info = StringFormat(
      "\"account\":{\"login\":%d,\"balance\":%.2f,\"equity\":%.2f,\"margin\":%.2f}",
      AccountInfoInteger(ACCOUNT_LOGIN),
      AccountInfoDouble(ACCOUNT_BALANCE),
      AccountInfoDouble(ACCOUNT_EQUITY),
      AccountInfoDouble(ACCOUNT_MARGIN)
   );
   
   SendResponse(signal_id, true, 0, 0, "Connection successful", 0.0, account_info);
   
   if(EnablePushNotifications)
      SendNotification("Mikrobot EA: Python connection established ✅");
}

//+------------------------------------------------------------------+
//| Process open order signal                                      |
//+------------------------------------------------------------------+
void ProcessOpenOrder(string signal_id, string symbol, string action, 
                     double volume, double price, double sl, double tp, string comment)
{
   Print("📈 Processing ", action, " order for ", symbol);
   
   // Validate symbol
   if(!SymbolSelect(symbol, true))
   {
      SendResponse(signal_id, false, 0, 10003, "Symbol not available: " + symbol);
      return;
   }
   
   // Determine order type
   ENUM_ORDER_TYPE order_type;
   if(action == "BUY")
      order_type = ORDER_TYPE_BUY;
   else if(action == "SELL")
      order_type = ORDER_TYPE_SELL;
   else
   {
      SendResponse(signal_id, false, 0, 10004, "Invalid action: " + action);
      return;
   }
   
   // Get current price if not specified
   if(price <= 0)
   {
      if(action == "BUY")
         price = SymbolInfoDouble(symbol, SYMBOL_ASK);
      else
         price = SymbolInfoDouble(symbol, SYMBOL_BID);
   }
   
   // Use default volume if not specified
   if(volume <= 0)
      volume = DefaultLotSize;
   
   // Normalize volume
   double min_volume = SymbolInfoDouble(symbol, SYMBOL_VOLUME_MIN);
   double max_volume = SymbolInfoDouble(symbol, SYMBOL_VOLUME_MAX);
   double volume_step = SymbolInfoDouble(symbol, SYMBOL_VOLUME_STEP);
   
   volume = MathMax(volume, min_volume);
   volume = MathMin(volume, max_volume);
   volume = NormalizeDouble(volume / volume_step, 0) * volume_step;
   
   // Prepare trade request
   MqlTradeRequest request = {0};
   MqlTradeResult result = {0};
   
   request.action = TRADE_ACTION_DEAL;
   request.symbol = symbol;
   request.volume = volume;
   request.type = order_type;
   request.price = price;
   request.sl = sl;
   request.tp = tp;
   request.deviation = 10;
   request.magic = MagicNumber;
   request.comment = comment + " [" + signal_id + "]";
   request.type_time = ORDER_TIME_GTC;
   request.type_filling = ORDER_FILLING_IOC;
   
   // Send order
   bool order_result = OrderSend(request, result);
   
   if(order_result && result.retcode == TRADE_RETCODE_DONE)
   {
      Print("✅ Order executed successfully. Ticket: ", result.order);
      SuccessfulTrades++;
      
      SendResponse(signal_id, true, (int)result.order, 0, "Order executed", result.price);
      
      if(EnablePushNotifications)
      {
         string msg = StringFormat("Mikrobot Trade ✅\n%s %s %.2f lots\nPrice: %.5f\nTicket: %d", 
                                  action, symbol, volume, result.price, result.order);
         SendNotification(msg);
      }
   }
   else
   {
      Print("❌ Order failed. Error: ", result.retcode, " - ", result.comment);
      FailedTrades++;
      
      SendResponse(signal_id, false, 0, (int)result.retcode, result.comment);
      
      if(EnablePushNotifications)
      {
         string msg = StringFormat("Mikrobot Trade Failed ❌\n%s %s\nError: %s", 
                                  action, symbol, result.comment);
         SendNotification(msg);
      }
   }
}

//+------------------------------------------------------------------+
//| Process close order signal                                     |
//+------------------------------------------------------------------+
void ProcessCloseOrder(string signal_id, int ticket)
{
   Print("🔄 Closing position: ", ticket);
   
   // Check if position exists
   if(!PositionSelectByTicket(ticket))
   {
      SendResponse(signal_id, false, 0, 10005, "Position not found: " + IntegerToString(ticket));
      return;
   }
   
   string symbol = PositionGetString(POSITION_SYMBOL);
   double volume = PositionGetDouble(POSITION_VOLUME);
   ENUM_POSITION_TYPE pos_type = (ENUM_POSITION_TYPE)PositionGetInteger(POSITION_TYPE);
   
   // Determine close type
   ENUM_ORDER_TYPE close_type = (pos_type == POSITION_TYPE_BUY) ? ORDER_TYPE_SELL : ORDER_TYPE_BUY;
   
   // Get close price
   double close_price = (close_type == ORDER_TYPE_SELL) ? 
                       SymbolInfoDouble(symbol, SYMBOL_BID) : 
                       SymbolInfoDouble(symbol, SYMBOL_ASK);
   
   // Prepare close request
   MqlTradeRequest request = {0};
   MqlTradeResult result = {0};
   
   request.action = TRADE_ACTION_DEAL;
   request.symbol = symbol;
   request.volume = volume;
   request.type = close_type;
   request.position = ticket;
   request.price = close_price;
   request.deviation = 10;
   request.magic = MagicNumber;
   request.comment = "Close [" + signal_id + "]";
   
   // Send close order
   bool close_result = OrderSend(request, result);
   
   if(close_result && result.retcode == TRADE_RETCODE_DONE)
   {
      Print("✅ Position closed successfully");
      SendResponse(signal_id, true, ticket, 0, "Position closed", result.price);
      
      if(EnablePushNotifications)
      {
         string msg = StringFormat("Mikrobot Close ✅\nTicket: %d\nClose Price: %.5f", 
                                  ticket, result.price);
         SendNotification(msg);
      }
   }
   else
   {
      Print("❌ Close failed. Error: ", result.retcode, " - ", result.comment);
      SendResponse(signal_id, false, 0, (int)result.retcode, result.comment);
   }
}

//+------------------------------------------------------------------+
//| Process status request                                          |
//+------------------------------------------------------------------+
void ProcessStatusRequest(string signal_id, string request_type)
{
   if(request_type == "GET_ACCOUNT")
   {
      string account_data = StringFormat(
         "\"account\":{\"login\":%d,\"balance\":%.2f,\"equity\":%.2f,\"margin\":%.2f,\"free_margin\":%.2f,\"margin_level\":%.2f}",
         AccountInfoInteger(ACCOUNT_LOGIN),
         AccountInfoDouble(ACCOUNT_BALANCE),
         AccountInfoDouble(ACCOUNT_EQUITY),
         AccountInfoDouble(ACCOUNT_MARGIN),
         AccountInfoDouble(ACCOUNT_FREEMARGIN),
         AccountInfoDouble(ACCOUNT_MARGIN_LEVEL)
      );
      
      SendResponse(signal_id, true, 0, 0, "Account info", 0.0, account_data);
   }
   else if(request_type == "GET_POSITIONS")
   {
      string positions_data = GetPositionsJson();
      SendResponse(signal_id, true, 0, 0, "Positions info", 0.0, positions_data);
   }
   else
   {
      SendResponse(signal_id, false, 0, 10006, "Unknown status request: " + request_type);
   }
}

//+------------------------------------------------------------------+
//| Process disconnect signal                                       |
//+------------------------------------------------------------------+
void ProcessDisconnect(string signal_id)
{
   Print("👋 Disconnect signal received");
   SendResponse(signal_id, true, 0, 0, "Disconnected");
   
   if(EnablePushNotifications)
      SendNotification("Mikrobot EA: Python disconnected 👋");
}

//+------------------------------------------------------------------+
//| Send response to Python                                        |
//+------------------------------------------------------------------+
void SendResponse(string signal_id, bool success, int ticket, int error_code, 
                 string error_message, double execution_price = 0.0, string account_info = "")
{
   string response_json = StringFormat(
      "{\n"
      "  \"signal_id\": \"%s\",\n"
      "  \"success\": %s,\n"
      "  \"ticket\": %d,\n"
      "  \"error_code\": %d,\n"
      "  \"error_message\": \"%s\",\n"
      "  \"execution_price\": %.5f,\n"
      "  \"execution_time\": \"%s\"",
      signal_id,
      success ? "true" : "false",
      ticket,
      error_code,
      error_message,
      execution_price,
      TimeToString(TimeCurrent(), TIME_DATE|TIME_MINUTES|TIME_SECONDS)
   );
   
   if(StringLen(account_info) > 0)
   {
      response_json += ",\n  \"account_info\": {" + account_info + "}";
   }
   
   response_json += "\n}";
   
   // Write response file
   int file_handle = FileOpen(ResponseFileName, FILE_WRITE|FILE_TXT);
   if(file_handle != INVALID_HANDLE)
   {
      FileWrite(file_handle, response_json);
      FileClose(file_handle);
      
      if(DebugMode)
         Print("📤 Response sent: ", success ? "SUCCESS" : "FAILED");
   }
   else
   {
      Print("❌ Cannot write response file: ", GetLastError());
   }
}

//+------------------------------------------------------------------+
//| Update status file                                             |
//+------------------------------------------------------------------+
void UpdateStatusFile(string status)
{
   string status_json = StringFormat(
      "{\n"
      "  \"status\": \"%s\",\n"
      "  \"last_heartbeat\": \"%s\",\n"
      "  \"signals_processed\": %d,\n"
      "  \"successful_trades\": %d,\n"
      "  \"failed_trades\": %d,\n"
      "  \"account\": %d\n"
      "}",
      status,
      TimeToString(TimeCurrent(), TIME_DATE|TIME_MINUTES|TIME_SECONDS),
      TotalSignalsProcessed,
      SuccessfulTrades,
      FailedTrades,
      AccountInfoInteger(ACCOUNT_LOGIN)
   );
   
   int file_handle = FileOpen(StatusFileName, FILE_WRITE|FILE_TXT);
   if(file_handle != INVALID_HANDLE)
   {
      FileWrite(file_handle, status_json);
      FileClose(file_handle);
   }
}

//+------------------------------------------------------------------+
//| Get positions as JSON string                                   |
//+------------------------------------------------------------------+
string GetPositionsJson()
{
   string positions_json = "\"positions\":[";
   bool first = true;
   
   for(int i = 0; i < PositionsTotal(); i++)
   {
      if(PositionGetSymbol(i) != "")
      {
         ulong ticket = PositionGetInteger(POSITION_TICKET);
         string symbol = PositionGetString(POSITION_SYMBOL);
         double volume = PositionGetDouble(POSITION_VOLUME);
         double price_open = PositionGetDouble(POSITION_PRICE_OPEN);
         double price_current = PositionGetDouble(POSITION_PRICE_CURRENT);
         double profit = PositionGetDouble(POSITION_PROFIT);
         double sl = PositionGetDouble(POSITION_SL);
         double tp = PositionGetDouble(POSITION_TP);
         string comment = PositionGetString(POSITION_COMMENT);
         ENUM_POSITION_TYPE pos_type = (ENUM_POSITION_TYPE)PositionGetInteger(POSITION_TYPE);
         string type_str = (pos_type == POSITION_TYPE_BUY) ? "BUY" : "SELL";
         
         if(!first) positions_json += ",";
         first = false;
         
         positions_json += StringFormat(
            "{\"ticket\":%d,\"symbol\":\"%s\",\"type\":\"%s\",\"volume\":%.2f,"
            "\"price_open\":%.5f,\"price_current\":%.5f,\"profit\":%.2f,"
            "\"sl\":%.5f,\"tp\":%.5f,\"comment\":\"%s\"}",
            ticket, symbol, type_str, volume, price_open, price_current, 
            profit, sl, tp, comment
         );
      }
   }
   
   positions_json += "]";
   return positions_json;
}

//+------------------------------------------------------------------+
//| Validate signal age                                            |
//+------------------------------------------------------------------+
bool ValidateSignalAge(string timestamp_str)
{
   if(StringLen(timestamp_str) == 0)
      return true; // No timestamp = accept
   
   // Simple timestamp validation (ISO format expected)
   // This is a basic implementation - in production, use proper datetime parsing
   datetime current_time = TimeCurrent();
   
   // For now, accept all signals with timestamps
   // TODO: Implement proper ISO datetime parsing
   return true;
}

//+------------------------------------------------------------------+
//| Extract JSON value (simple implementation)                     |
//+------------------------------------------------------------------+
string ExtractJsonValue(string json, string key)
{
   string search_pattern = "\"" + key + "\"";
   int key_pos = StringFind(json, search_pattern);
   
   if(key_pos == -1)
      return "";
   
   int colon_pos = StringFind(json, ":", key_pos);
   if(colon_pos == -1)
      return "";
   
   int value_start = colon_pos + 1;
   
   // Skip whitespace
   while(value_start < StringLen(json) && 
         (StringGetCharacter(json, value_start) == ' ' || 
          StringGetCharacter(json, value_start) == '\t'))
      value_start++;
   
   if(value_start >= StringLen(json))
      return "";
   
   int value_end;
   char first_char = (char)StringGetCharacter(json, value_start);
   
   if(first_char == '"')
   {
      // String value
      value_start++; // Skip opening quote
      value_end = StringFind(json, "\"", value_start);
      if(value_end == -1)
         return "";
   }
   else
   {
      // Number or boolean value
      value_end = StringFind(json, ",", value_start);
      if(value_end == -1)
         value_end = StringFind(json, "}", value_start);
      if(value_end == -1)
         value_end = StringLen(json);
      
      // Trim whitespace
      while(value_end > value_start && 
            (StringGetCharacter(json, value_end-1) == ' ' || 
             StringGetCharacter(json, value_end-1) == '\t' ||
             StringGetCharacter(json, value_end-1) == '\n' ||
             StringGetCharacter(json, value_end-1) == '\r'))
         value_end--;
   }
   
   return StringSubstr(json, value_start, value_end - value_start);
}

//+------------------------------------------------------------------+