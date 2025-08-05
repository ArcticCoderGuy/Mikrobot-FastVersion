//+------------------------------------------------------------------+
//|                                          SimpleMikrobotEA.mq5    |
//|                                   Simple Signal Processor EA     |
//+------------------------------------------------------------------+
#property copyright "Mikrobot"
#property version   "1.00"

// Global variables
datetime lastCheckTime = 0;

//+------------------------------------------------------------------+
//| Expert initialization function                                   |
//+------------------------------------------------------------------+
int OnInit()
{
   Print("=== Simple Mikrobot EA Started ===");
   Print("Looking for signals in Common/Files folder");
   EventSetTimer(1); // Check every second
   return(INIT_SUCCEEDED);
}

//+------------------------------------------------------------------+
//| Expert deinitialization function                                 |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
{
   EventKillTimer();
   Print("=== Simple Mikrobot EA Stopped ===");
}

//+------------------------------------------------------------------+
//| Timer function                                                   |
//+------------------------------------------------------------------+
void OnTimer()
{
   // Check for signal.json
   if(FileIsExist("signal.json", FILE_COMMON))
   {
      Print("Found signal.json!");
      
      // Read the file
      int handle = FileOpen("signal.json", FILE_READ|FILE_TXT|FILE_ANSI|FILE_COMMON);
      if(handle != INVALID_HANDLE)
      {
         string content = "";
         while(!FileIsEnding(handle))
         {
            content += FileReadString(handle);
         }
         FileClose(handle);
         
         Print("Signal content: ", content);
         
         // Delete signal file
         FileDelete("signal.json", FILE_COMMON);
         
         // Create simple response
         string response = "{\"signal_id\": 1, \"status\": \"success\", ";
         response += "\"account\": " + IntegerToString(AccountInfoInteger(ACCOUNT_LOGIN)) + ", ";
         response += "\"balance\": " + DoubleToString(AccountInfoDouble(ACCOUNT_BALANCE), 2) + ", ";
         response += "\"equity\": " + DoubleToString(AccountInfoDouble(ACCOUNT_EQUITY), 2) + "}";
         
         // Write response
         int responseHandle = FileOpen("response.json", FILE_WRITE|FILE_TXT|FILE_ANSI|FILE_COMMON);
         if(responseHandle != INVALID_HANDLE)
         {
            FileWriteString(responseHandle, response);
            FileClose(responseHandle);
            Print("Response written!");
         }
      }
   }
}
//+------------------------------------------------------------------+