//+------------------------------------------------------------------+
//|                                          MQL5 Push Sender       |
//|                                   For Mikrobot FastVersion      |
//|                      Sends push notification via your MT5 EA    |
//+------------------------------------------------------------------+
#property copyright "Mikrobot FastVersion"
#property version   "1.00"
#property script_show_inputs

//--- Input parameters
input string CustomMessage = "Pekka ja Aulikki menivät saunaan ja Pekka avasi kaljapullon johon Auni sanoi; ota nyt mielummin Paulaner:ia";
input bool   EnablePushNotification = true;
input bool   EnableEmailAlert = false;
input bool   EnableSoundAlert = true;

//+------------------------------------------------------------------+
//| Script program start function                                    |
//+------------------------------------------------------------------+
void OnStart()
{
   //--- Get current time
   datetime current_time = TimeCurrent();
   string time_str = TimeToString(current_time, TIME_DATE|TIME_MINUTES);
   
   //--- Prepare notification message
   string notification_title = "Mikrobot FastVersion Test";
   string full_message = StringFormat("%s\n\nTime: %s\nAccount: %d\nMetaQuotes ID: 03A06890", 
                                     CustomMessage, time_str, AccountInfoInteger(ACCOUNT_LOGIN));
   
   //--- Print to Journal (Experts tab)
   Print("========================================");
   Print("MIKROBOT PUSH NOTIFICATION SENDER");
   Print("========================================");
   Print("Message: ", CustomMessage);
   Print("Time: ", time_str);
   Print("Account: ", AccountInfoInteger(ACCOUNT_LOGIN));
   Print("MetaQuotes ID: 03A06890");
   Print("========================================");
   
   //--- Send push notification to mobile
   if(EnablePushNotification)
   {
      bool push_result = SendNotification(full_message);
      if(push_result)
      {
         Print("✅ Push notification sent successfully to mobile!");
         Print("Check your MT5 mobile app (MetaQuotes ID: 03A06890)");
      }
      else
      {
         Print("❌ Push notification failed. Check your mobile settings.");
         Print("Ensure push notifications are enabled in Tools -> Options -> Notifications");
      }
   }
   
   //--- Send email alert (if enabled)
   if(EnableEmailAlert)
   {
      bool email_result = SendMail(notification_title, full_message);
      if(email_result)
         Print("📧 Email alert sent successfully!");
      else
         Print("❌ Email alert failed. Check email settings in Tools -> Options -> Email");
   }
   
   //--- Play sound alert (if enabled)
   if(EnableSoundAlert)
   {
      PlaySound("alert.wav");
      Print("🔊 Sound alert played");
   }
   
   //--- Create file for Mikrobot to confirm message was sent
   string filename = "mikrobot_push_confirmation.txt";
   int file_handle = FileOpen(filename, FILE_WRITE|FILE_TXT);
   
   if(file_handle != INVALID_HANDLE)
   {
      FileWrite(file_handle, "MIKROBOT PUSH NOTIFICATION CONFIRMATION");
      FileWrite(file_handle, "==========================================");
      FileWrite(file_handle, "Message: " + CustomMessage);
      FileWrite(file_handle, "Sent at: " + time_str);
      FileWrite(file_handle, "Account: " + IntegerToString(AccountInfoInteger(ACCOUNT_LOGIN)));
      FileWrite(file_handle, "Push Result: " + (EnablePushNotification ? "Attempted" : "Disabled"));
      FileWrite(file_handle, "Email Result: " + (EnableEmailAlert ? "Attempted" : "Disabled"));
      FileWrite(file_handle, "Sound Result: " + (EnableSoundAlert ? "Played" : "Disabled"));
      FileWrite(file_handle, "MetaQuotes ID: 03A06890");
      FileWrite(file_handle, "==========================================");
      
      FileClose(file_handle);
      Print("📄 Confirmation file created: ", filename);
   }
   else
   {
      Print("❌ Could not create confirmation file");
   }
   
   //--- Show alert dialog
   Alert("Mikrobot Push Notification Sent!\n", CustomMessage);
   
   Print("🎉 Mikrobot notification process completed!");
   Print("Check your mobile MT5 app for the push notification.");
}

//+------------------------------------------------------------------+
//| Check if push notifications are properly configured             |
//+------------------------------------------------------------------+
bool CheckPushConfiguration()
{
   //--- This function could check if push notifications are enabled
   //--- But MQL5 doesn't provide direct access to these settings
   //--- So we'll just return true and let SendNotification() handle it
   return true;
}
//+------------------------------------------------------------------+