"""
KORJAA LOT SIZE JA STOP LEVELS
Päivitä EA:n risk management parametrit
"""

def create_fixed_ea():
    """Luo korjattu EA versio"""
    
    print("KORJATAAN LOT SIZE JA STOP LEVELS...")
    print("=" * 50)
    
    # Korjaukset:
    # 1. Lot size laskennan korjaus
    # 2. ATR distance kerrotaan suuremmaksi
    # 3. Minimum stop distance tarkistus
    
    fixed_code = '''// Korjattu CalculateLotSize funktio
double CalculateLotSize()
{
   double balance = AccountInfoDouble(ACCOUNT_BALANCE);
   double risk_amount = balance * RiskPercent / 100.0;
   double atr_distance = CalculateATRDistance();
   
   // Muunna ATR pips -> points oikein
   double stop_points = atr_distance;
   if(_Digits == 5 || _Digits == 3) 
      stop_points *= 10;
   
   double tick_value = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_VALUE);
   if(tick_value == 0) tick_value = 1.0;
   
   // Laske lot size
   double lot_size = risk_amount / (stop_points * tick_value);
   
   // Tiukemmat rajat
   double min_lot = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN);
   double max_lot = MathMin(2.0, SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MAX)); // Max 2.0 lots
   double step = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_STEP);
   
   if(min_lot == 0) min_lot = 0.01;
   if(step == 0) step = 0.01;
   
   // Varmista järkevä koko
   lot_size = MathMax(min_lot, MathMin(max_lot, lot_size));
   lot_size = MathRound(lot_size / step) * step;
   
   // Debug print
   Print("Lot calculation: Balance=", balance, " Risk=", risk_amount, 
         " ATR=", atr_distance, " Result=", lot_size);
   
   return NormalizeDouble(lot_size, 2);
}

// Korjattu ExecuteBuyOrder
void ExecuteBuyOrder()
{
   double price = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
   double atr_pips = CalculateATRDistance();
   
   // Minimum stop distance
   double min_stop = SymbolInfoInteger(_Symbol, SYMBOL_TRADE_STOPS_LEVEL) * _Point;
   if(min_stop == 0) min_stop = 20 * _Point; // Default 20 points
   
   // Laske SL ja TP (suuremmat etäisyydet)
   double sl_distance = MathMax(atr_pips * 10 * _Point, min_stop * 2);
   double tp_distance = sl_distance * 2.5; // 1:2.5 RR
   
   double sl = price - sl_distance;
   double tp = price + tp_distance;
   double lot_size = CalculateLotSize();
   
   // Normalize prices
   sl = NormalizeDouble(sl, _Digits);
   tp = NormalizeDouble(tp, _Digits);
   
   Print("BUY Setup: Price=", price, " SL=", sl, " (", (price-sl)/_Point, " points)",
         " TP=", tp, " (", (tp-price)/_Point, " points)", " Lots=", lot_size);
   
   if(trade.Buy(lot_size, _Symbol, price, sl, tp, "MIKROBOT_BUY_V4"))
   {
      Print("BUY order executed: ", trade.ResultOrder(), " at ", price);
   }
   else
   {
      Print("BUY order failed: ", trade.ResultRetcode(), " - ", trade.ResultRetcodeDescription());
   }
}
'''
    
    print("KORJAUKSET:")
    print("1. Lot size maksimi: 2.0")
    print("2. Minimum stop distance: 20 points")
    print("3. SL distance: ATR * 10 points (min 40 points)")
    print("4. TP distance: SL * 2.5")
    print("5. Debug print lot laskennasta")
    
    print("\nKORJAA EA MANUAALISESTI:")
    print("1. Avaa MetaEditor")
    print("2. Etsi CalculateLotSize() funktio")
    print("3. Korvaa se yllä olevalla koodilla")
    print("4. Etsi ExecuteBuyOrder() ja ExecuteSellOrder()")
    print("5. Päivitä stop distance laskenta")
    print("6. Käännä uudelleen (F7)")
    
    return True

if __name__ == "__main__":
    create_fixed_ea()
    
    print("\n\nTAI VAIHTOEHTOISESTI:")
    print("Voin luoda kokonaan uuden EA version v5")
    print("jossa nämä ongelmat on korjattu valmiiksi.")