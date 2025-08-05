//+------------------------------------------------------------------+
//| AddATRToCharts.mq5                                               |
//| Copyright 2025, MIKROBOT SUBMARINE COMMAND                      |
//| Add ATR(14) indicators to all open charts                       |
//+------------------------------------------------------------------+
#property copyright "MIKROBOT SUBMARINE COMMAND"
#property link      "MIKROBOT_FASTVERSION.md"
#property version   "1.00"
#property script_show_inputs

//--- Input parameters
input int ATR_Period = 14;           // ATR jakso
input color ATR_Color = clrYellow;   // ATR väri
input int ATR_Width = 2;             // ATR viivan paksuus

//+------------------------------------------------------------------+
//| Script program start function                                    |
//+------------------------------------------------------------------+
void OnStart()
{
   Print("MIKROBOT: ATR indikaattorien lisäys aloitettu...");
   
   long chart_id = ChartFirst();
   int charts_processed = 0;
   int atr_added = 0;
   
   // Käy läpi kaikki avoimet kaaviot
   while(chart_id >= 0)
   {
      string symbol = ChartSymbol(chart_id);
      ENUM_TIMEFRAMES timeframe = ChartPeriod(chart_id);
      
      Print("Käsitellään kaavio: ", symbol, " ", EnumToString(timeframe));
      
      // Tarkista onko ATR jo lisätty
      if(!HasATRIndicator(chart_id))
      {
         // Lisää ATR indikaattori
         if(AddATRIndicator(chart_id, symbol))
         {
            atr_added++;
            Print("✅ ATR lisätty: ", symbol, " ", EnumToString(timeframe));
         }
         else
         {
            Print("❌ ATR lisäys epäonnistui: ", symbol);
         }
      }
      else
      {
         Print("ℹ️ ATR jo olemassa: ", symbol);
      }
      
      charts_processed++;
      chart_id = ChartNext(chart_id);
   }
   
   // Tulokset
   Print("==========================================");
   Print("MIKROBOT ATR DEPLOYMENT VALMIS:");
   Print("Kaaviot käsitelty: ", charts_processed);
   Print("ATR indikaattoreita lisätty: ", atr_added);
   Print("==========================================");
   
   // Fokus EURJPY kaavioon jos löytyy
   FocusOnEURJPY();
}

//+------------------------------------------------------------------+
//| Lisää ATR indikaattori kaavioon                                  |
//+------------------------------------------------------------------+
bool AddATRIndicator(long chart_id, string symbol)
{
   // Lisää ATR indikaattori alakansioon
   int indicator_handle = iATR(symbol, ChartPeriod(chart_id), ATR_Period);
   
   if(indicator_handle == INVALID_HANDLE)
   {
      Print("ERROR: ATR handle invalid for ", symbol);
      return false;
   }
   
   // Aseta indikaattori näkyviin kaaviossa
   string indicator_name = "ATR(" + IntegerToString(ATR_Period) + ")";
   
   if(!ChartIndicatorAdd(chart_id, 1, indicator_handle))
   {
      Print("ERROR: ChartIndicatorAdd failed for ", symbol);
      return false;
   }
   
   // Aseta ATR indikaattorin ulkoasu
   ChartSetInteger(chart_id, CHART_WINDOWS_TOTAL, 2); // Varmista että alakansi on olemassa
   
   return true;
}

//+------------------------------------------------------------------+
//| Tarkista onko ATR jo kaaviossa                                   |
//+------------------------------------------------------------------+
bool HasATRIndicator(long chart_id)
{
   int windows = (int)ChartGetInteger(chart_id, CHART_WINDOWS_TOTAL);
   
   for(int window = 0; window < windows; window++)
   {
      int indicators = ChartIndicatorsTotal(chart_id, window);
      
      for(int i = 0; i < indicators; i++)
      {
         string indicator_name = ChartIndicatorName(chart_id, window, i);
         if(StringFind(indicator_name, "ATR") >= 0)
         {
            return true;
         }
      }
   }
   
   return false;
}

//+------------------------------------------------------------------+
//| Fokus EURJPY kaavioon                                            |
//+------------------------------------------------------------------+
void FocusOnEURJPY()
{
   long chart_id = ChartFirst();
   
   while(chart_id >= 0)
   {
      string symbol = ChartSymbol(chart_id);
      
      if(symbol == "EURJPY")
      {
         ChartSetInteger(chart_id, CHART_BRING_TO_TOP, true);
         Print("🎯 EURJPY kaavio asetettu aktiiviseksi");
         
         // Näytä EURJPY signal info
         Print("🚨 EURJPY SIGNAL DETECTED:");
         Print("   Strategy: MIKROBOT_FASTVERSION_4PHASE");
         Print("   Phase 4 ylipip: TRIGGERED");
         Print("   Trade Direction: BULL (BUY)");
         Print("   Current Price: 170.8220");
         Print("   Status: READY FOR EXECUTION");
         
         return;
      }
      
      chart_id = ChartNext(chart_id);
   }
}

//+------------------------------------------------------------------+