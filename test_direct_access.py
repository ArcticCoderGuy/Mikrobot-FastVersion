#!/usr/bin/env python3
"""
Test MT5 Terminal Direct Access
"""

from mt5_terminal_direct_access import MT5TerminalDirectAccess

def main():
    print('Testing MT5 Terminal Direct Access...')
    monitor = MT5TerminalDirectAccess()

    if monitor.initialize():
        print('SUCCESS: Direct access initialized')
        
        status = monitor.get_complete_status()
        print(f'Terminal Activities: {len(status["terminal_activity"])}')
        print(f'Expert Activities: {len(status["expert_activity"])}')
        print(f'Positions: {len(status["positions"])}')
        print(f'Signal Files: {len(status["signal_files"])}')
        
        # Show recent expert activity
        if status['expert_activity']:
            print('\nRecent Expert Activity:')
            for activity in status['expert_activity'][-5:]:
                print(f'  [{activity["time"]}] {activity["ea_name"]} ({activity["symbol"]}): {activity["message"][:60]}')
        
        # Show positions
        if status['positions']:
            print('\nOpen Positions:')
            for pos in status['positions']:
                profit_sign = '+' if pos['profit'] >= 0 else ''
                print(f'  #{pos["ticket"]} {pos["symbol"]} {pos["volume"]} lots | P&L: {profit_sign}${pos["profit"]:.2f}')
        
        # Export status
        filename = monitor.export_status()
        print(f'Status exported to: {filename}')
        
        monitor.shutdown()
    else:
        print('FAILED to initialize')

if __name__ == "__main__":
    main()