"""
KORJAA EA KAANTAMISVIRHEET
Korjaa MikrobotFastversionEA.mq5 kaantamisongelmat
"""

def fix_ea_compilation_errors():
    """Korjaa EA:n kaantamisvirheet"""
    
    print("KORJATAAN EA KAANTAMISVIRHEET...")
    
    ea_file = "C:/Users/HP/AppData/Roaming/MetaQuotes/Terminal/D0E8209F77C8CF37AD8BF550E51FF075/MQL5/Experts/MikrobotFastversionEA.mq5"
    
    try:
        with open(ea_file, 'r', encoding='utf-8') as f:
            content = f.read()
    except:
        try:
            with open(ea_file, 'r', encoding='cp1252') as f:
                content = f.read()
        except Exception as e:
            print(f"ERROR: Tiedoston lukeminen epaonnistui: {e}")
            return False
    
    print("Korjataan virheet...")
    
    # 1. Korjaa FileIsEnd -> !FileIsEnd
    content = content.replace('while(!FileIsEnd(file_handle))', 'while(!FileIsEnd(file_handle))')
    
    # 2. Korjaa ACCOUNT_FREEMARGIN -> ACCOUNT_MARGIN_FREE
    content = content.replace('ACCOUNT_FREEMARGIN', 'ACCOUNT_MARGIN_FREE')
    
    # 3. Korjaa GetWeekStart funktio - lisaa parametri
    # Etsi funktio ja korjaa sen kutsut
    if 'GetWeekStart()' in content:
        content = content.replace('GetWeekStart()', 'GetWeekStart(TimeCurrent())')
    
    # 4. Lisaa puuttuvat funktiot
    missing_functions = '''
//+------------------------------------------------------------------+
//| Write signal file function                                     |
//+------------------------------------------------------------------+
void WriteSignalFile(string filename, string data)
{
   int file_handle = FileOpen(filename, FILE_WRITE|FILE_TXT);
   if(file_handle != INVALID_HANDLE)
   {
      FileWrite(file_handle, data);
      FileClose(file_handle);
   }
}

'''
    
    # Lisaa puuttuvat funktiot ennen viimeista }
    last_brace_pos = content.rfind('}')
    if last_brace_pos > 0:
        content = content[:last_brace_pos] + missing_functions + content[last_brace_pos:]
    
    # 5. Korjaa enum virhe
    content = content.replace('request.action = 0;', 'request.action = TRADE_ACTION_DEAL;')
    
    # 6. Korjaa FileIsEnd funktio
    if 'FileIsEnd' in content and 'file_handle' in content:
        # Varmista että FileIsEnd funktio on oikein
        content = content.replace('FileIsEnd(file_handle)', '!FileIsEnd(file_handle)')
    
    # Tallenna korjattu versio
    try:
        with open(ea_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print("SUCCESS: EA virheet korjattu")
        return True
    except Exception as e:
        print(f"ERROR: Tiedoston tallennus epaonnistui: {e}")
        return False

if __name__ == "__main__":
    success = fix_ea_compilation_errors()
    
    if success:
        print("SUCCESS: EA korjattu, yrita kaantaa uudelleen MetaEditorissa")
    else:
        print("ERROR: Korjaus epaonnistui")