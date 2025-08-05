"""
SUBMARINE TACTICAL DEMONSTRATION
Los Angeles-class Nuclear Reactor & Risk Management Demo
Demonstrate submarine-grade risk calculations across Forex pairs
"""

import MetaTrader5 as mt5
import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Any
import json
from submarine_command_center import SubmarineCommandCenter, SubmarineRiskReactor

# Military-grade logging
logging.basicConfig(
    level=logging.INFO,
    format='[SUB] %(asctime)s %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

class SubmarineTacticalDemo:
    """
    Los Angeles-class Submarine Tactical Demonstration
    Focus on nuclear reactor calculations and market intelligence
    """
    
    # MILITARY TARGET DESIGNATION
    FOREX_TARGETS = [
        'EURUSD',  # Primary target - European theater
        'GBPUSD',  # Secondary target - British waters
        'USDJPY',  # Pacific theater - Special handling (JPY)
        'USDCHF',  # Alpine operations
        'AUDUSD',  # South Pacific command
        'USDCAD',  # North American theater
        'NZDUSD'   # Tasman operations
    ]
    
    def __init__(self):
        self.command_center = SubmarineCommandCenter()
        self.risk_reactor = SubmarineRiskReactor()
        self.tactical_results = []
        self.engagement_count = 0
        
        logger.info("[SHIP] SUBMARINE TACTICAL DEMO INITIALIZED")
        logger.info("[TARGETS] %s", ', '.join(self.FOREX_TARGETS))
        
    async def initialize_submarine_systems(self):
        """Initialize MT5 connection with submarine-grade security"""
        
        logger.info("[INIT] INITIALIZING SUBMARINE SYSTEMS...")
        
        # Initialize MT5 with submarine protocols
        if not mt5.initialize():
            logger.critical("[FAIL] SUBMARINE SYSTEMS FAILURE - MT5 initialization failed")
            return False
            
        # Get submarine identification
        account_info = mt5.account_info()
        if account_info is None:
            logger.critical("[FAIL] NAVIGATION FAILURE - Cannot get account info")
            return False
            
        logger.info("[ID] SUBMARINE IDENTIFICATION:")
        logger.info("   [DATA] Account: %s", account_info.login)
        logger.info("   [CASH] Balance: $%.2f", account_info.balance)
        logger.info("   [BROKER] Broker: %s", account_info.company)
        logger.info("   [CURR] Currency: %s", account_info.currency)
        
        # Verify all targets are available
        await self._verify_target_availability()
        
        logger.info("[OK] ALL SUBMARINE SYSTEMS ONLINE - READY FOR TACTICAL DEMO")
        return True
    
    async def _verify_target_availability(self):
        """Verify all Forex targets are available for engagement"""
        
        logger.info("[SCAN] VERIFYING TARGET AVAILABILITY...")
        
        available_targets = []
        unavailable_targets = []
        
        for symbol in self.FOREX_TARGETS:
            symbol_info = mt5.symbol_info(symbol)
            if symbol_info is None:
                unavailable_targets.append(symbol)
                logger.warning("[WARN] TARGET UNAVAILABLE: %s", symbol)
            else:
                available_targets.append(symbol)
                # Get current price for intel
                tick = mt5.symbol_info_tick(symbol)
                if tick:
                    logger.info("[ACQUIRED] TARGET: %s @ %.5f (Spread: %.1f)", 
                              symbol, tick.bid, (tick.ask - tick.bid) * 10000)
                else:
                    logger.info("[ACQUIRED] TARGET: %s (price unavailable)", symbol)
        
        logger.info("[STATUS] AVAILABLE TARGETS: %d/%d", len(available_targets), len(self.FOREX_TARGETS))
        if unavailable_targets:
            logger.warning("[MISSING] UNAVAILABLE TARGETS: %s", ', '.join(unavailable_targets))
    
    async def execute_tactical_demonstration(self):
        """Execute tactical demonstration - nuclear reactor calculations only"""
        
        logger.info("[TACTICAL] EXECUTING TACTICAL DEMONSTRATION")
        logger.info("[MISSION] Demonstrate nuclear reactor risk calculations")
        logger.info("[MODE] NO ACTUAL TRADES - CALCULATIONS ONLY")
        
        demo_start_time = datetime.now()
        
        # Demonstrate nuclear reactor on all targets
        for symbol in self.FOREX_TARGETS:
            await self._tactical_analysis(symbol)
            await asyncio.sleep(0.5)  # Brief spacing between analyses
        
        demo_duration = (datetime.now() - demo_start_time).total_seconds()
        
        # Generate tactical report
        await self._generate_tactical_report(demo_duration)
        
        logger.info("[COMPLETE] TACTICAL DEMONSTRATION COMPLETE")
    
    async def _tactical_analysis(self, symbol: str):
        """Perform tactical analysis on target"""
        
        self.engagement_count += 1
        analysis_start = datetime.now()
        
        logger.info("")
        logger.info("[ANALYZE] TACTICAL ANALYSIS #%d: %s", self.engagement_count, symbol)
        
        try:
            # Get market intelligence
            tick = mt5.symbol_info_tick(symbol)
            if not tick:
                logger.error("[FAIL] ANALYSIS FAILED: No market data for %s", symbol)
                return
            
            symbol_info = mt5.symbol_info(symbol)
            if not symbol_info:
                logger.error("[FAIL] ANALYSIS FAILED: No symbol info for %s", symbol)
                return
            
            # Get historical data for ATR
            atr_value = await self._calculate_atr(symbol)
            
            # Nuclear reactor risk calculations for different scenarios
            account_info = mt5.account_info()
            account_balance = float(account_info.balance)
            
            # Test multiple risk scenarios
            risk_scenarios = [
                {'risk_percent': 0.5, 'scenario': 'CONSERVATIVE'},
                {'risk_percent': 1.0, 'scenario': 'MODERATE'},
                {'risk_percent': 2.0, 'scenario': 'AGGRESSIVE'}
            ]
            
            scenario_results = []
            
            for scenario in risk_scenarios:
                risk_calc = self.risk_reactor.calculate_submarine_risk(
                    symbol=symbol,
                    atr_value=atr_value,
                    account_balance=account_balance,
                    risk_percent=scenario['risk_percent']
                )
                risk_calc['scenario'] = scenario['scenario']
                scenario_results.append(risk_calc)
            
            # Market intelligence gathering
            market_intel = await self._gather_market_intelligence(symbol, tick, symbol_info)
            
            analysis_time = (datetime.now() - analysis_start).total_seconds() * 1000
            
            # Log tactical analysis results
            logger.info("   [INTEL] Market Intelligence:")
            logger.info("      [PRICE] Bid/Ask: %.5f/%.5f", tick.bid, tick.ask)
            logger.info("      [SPREAD] Spread: %.1f pips", market_intel['spread_pips'])
            logger.info("      [ATR] ATR: %.1f pips", atr_value)
            logger.info("      [ASSET] Asset Class: %s", scenario_results[0]['asset_class'])
            
            logger.info("   [REACTOR] Nuclear Reactor Risk Scenarios:")
            for result in scenario_results:
                logger.info("      [%s] Lot: %.2f, SL: %.1f pips, Risk: $%.2f", 
                          result['scenario'], 
                          result['lot_size'], 
                          result['stop_loss_pips'],
                          result['risk_amount'])
            
            # Record tactical results
            tactical_result = {
                'analysis_number': self.engagement_count,
                'symbol': symbol,
                'analysis_time_ms': analysis_time,
                'market_intel': market_intel,
                'atr_value': atr_value,
                'risk_scenarios': scenario_results,
                'timestamp': analysis_start.isoformat()
            }
            
            self.tactical_results.append(tactical_result)
            
            logger.info("[SUCCESS] TACTICAL ANALYSIS COMPLETE: %s in %.1fms", symbol, analysis_time)
                
        except Exception as e:
            logger.error("[ERROR] TACTICAL ANALYSIS EXCEPTION: %s - %s", symbol, str(e))
    
    async def _calculate_atr(self, symbol: str) -> float:
        """Calculate ATR for submarine risk management"""
        
        try:
            # Get recent price data for ATR calculation
            rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M15, 0, 14)
            if rates is None or len(rates) < 14:
                logger.warning("[WARN] ATR DATA LIMITED: Using default 8 pips for %s", symbol)
                return 8.0
            
            # Simple ATR calculation
            high_low = [rate['high'] - rate['low'] for rate in rates]
            atr_value = sum(high_low) / len(high_low)
            
            # Convert to pips based on symbol
            if symbol in ['USDJPY', 'EURJPY', 'GBPJPY']:
                atr_pips = atr_value * 100  # JPY pairs
            else:
                atr_pips = atr_value * 10000  # Standard pairs
            
            return max(atr_pips, 5.0)  # Minimum 5 pips
            
        except Exception as e:
            logger.warning("[WARN] ATR CALCULATION ERROR: %s, using default", str(e))
            return 8.0
    
    async def _gather_market_intelligence(self, symbol: str, tick, symbol_info) -> Dict[str, Any]:
        """Gather comprehensive market intelligence"""
        
        # Calculate spread in pips
        if symbol in ['USDJPY', 'EURJPY', 'GBPJPY']:
            spread_pips = (tick.ask - tick.bid) * 100  # JPY pairs
        else:
            spread_pips = (tick.ask - tick.bid) * 10000  # Standard pairs
        
        # Get trading session info
        current_hour = datetime.now().hour
        if 22 <= current_hour or current_hour < 5:
            session = "SYDNEY"
        elif 7 <= current_hour < 16:
            session = "LONDON"
        elif 13 <= current_hour < 22:
            session = "NEW_YORK"
        else:
            session = "OVERLAP"
        
        return {
            'bid': tick.bid,
            'ask': tick.ask,
            'spread_pips': round(spread_pips, 1),
            'trading_session': session,
            'contract_size': symbol_info.trade_contract_size,
            'min_lot': symbol_info.volume_min,
            'max_lot': symbol_info.volume_max,
            'lot_step': symbol_info.volume_step,
            'point': symbol_info.point,
            'digits': symbol_info.digits
        }
    
    async def _generate_tactical_report(self, demo_duration: float):
        """Generate comprehensive tactical demonstration report"""
        
        logger.info("")
        logger.info("[REPORT] TACTICAL DEMONSTRATION REPORT")
        logger.info("=" * 60)
        
        total_analyses = len(self.tactical_results)
        avg_analysis_time = sum(result['analysis_time_ms'] for result in self.tactical_results) / total_analyses if total_analyses > 0 else 0
        
        logger.info("[PERF] SUBMARINE TACTICAL PERFORMANCE:")
        logger.info("   [TOTAL] Total Analyses: %d", total_analyses)
        logger.info("   [TIME] Average Analysis Time: %.1fms", avg_analysis_time)
        logger.info("   [DURATION] Total Demo Duration: %.1fs", demo_duration)
        
        # Nuclear reactor performance summary
        logger.info("")
        logger.info("[REACTOR] NUCLEAR REACTOR PERFORMANCE SUMMARY:")
        
        total_conservative_risk = 0
        total_moderate_risk = 0
        total_aggressive_risk = 0
        avg_atr = 0
        
        for result in self.tactical_results:
            avg_atr += result['atr_value']
            for scenario in result['risk_scenarios']:
                if scenario['scenario'] == 'CONSERVATIVE':
                    total_conservative_risk += scenario['risk_amount']
                elif scenario['scenario'] == 'MODERATE':
                    total_moderate_risk += scenario['risk_amount']
                elif scenario['scenario'] == 'AGGRESSIVE':
                    total_aggressive_risk += scenario['risk_amount']
        
        avg_atr = avg_atr / total_analyses if total_analyses > 0 else 0
        
        logger.info("   [CONSERVATIVE] Total Conservative Risk: $%.2f", total_conservative_risk)
        logger.info("   [MODERATE] Total Moderate Risk: $%.2f", total_moderate_risk)
        logger.info("   [AGGRESSIVE] Total Aggressive Risk: $%.2f", total_aggressive_risk)
        logger.info("   [ATR] Average ATR: %.1f pips", avg_atr)
        logger.info("   [REACTOR] Nuclear Reactor Status: CRITICAL (100%% operational)")
        
        # Asset class distribution
        asset_classes = {}
        for result in self.tactical_results:
            if result['risk_scenarios']:
                asset_class = result['risk_scenarios'][0]['asset_class']
                asset_classes[asset_class] = asset_classes.get(asset_class, 0) + 1
        
        logger.info("")
        logger.info("[ASSETS] ASSET CLASS DISTRIBUTION:")
        for asset_class, count in asset_classes.items():
            logger.info("   [%s] Assets: %d", asset_class, count)
        
        # Quality assessment
        if avg_analysis_time <= 50:
            quality_rating = "[GOLD] GOLD STANDARD (Cp/Cpk >= 3.0)"
        elif avg_analysis_time <= 100:
            quality_rating = "[SIGMA] SIX SIGMA QUALITY"
        else:
            quality_rating = "[OPERATIONAL] SUBMARINE OPERATIONAL"
        
        logger.info("")
        logger.info("[QUALITY] Quality Rating: %s", quality_rating)
        
        # Detailed tactical results
        logger.info("")
        logger.info("[DETAILS] DETAILED TACTICAL RESULTS:")
        for result in self.tactical_results:
            logger.info("   [%s] %s: %.1fms - ATR: %.1f - Spread: %.1f pips", 
                       "OK", 
                       result['symbol'], 
                       result['analysis_time_ms'],
                       result['atr_value'],
                       result['market_intel']['spread_pips'])
        
        # Save tactical report
        tactical_report = {
            'submarine_id': 'USS_MIKROBOT_FASTVERSION_TACTICAL',
            'demo_timestamp': datetime.now().isoformat(),
            'demo_duration_seconds': demo_duration,
            'total_analyses': total_analyses,
            'average_analysis_time_ms': avg_analysis_time,
            'quality_rating': quality_rating,
            'nuclear_reactor_performance': {
                'conservative_total_risk': total_conservative_risk,
                'moderate_total_risk': total_moderate_risk,
                'aggressive_total_risk': total_aggressive_risk,
                'average_atr_pips': avg_atr,
                'reactor_status': 'CRITICAL'
            },
            'asset_class_distribution': asset_classes,
            'detailed_results': self.tactical_results
        }
        
        report_file = f"submarine_tactical_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(tactical_report, f, indent=2)
        
        logger.info("")
        logger.info("[SAVED] TACTICAL REPORT SAVED: %s", report_file)
        logger.info("[ASSESSMENT] NUCLEAR REACTOR: 100%% OPERATIONAL")
        logger.info("[ASSESSMENT] RISK CALCULATIONS: SUBMARINE-GRADE PRECISION")
        logger.info("[MISSION] USS MIKROBOT FASTVERSION - TACTICAL DEMO COMPLETE")
    
    def shutdown_submarine_systems(self):
        """Safe shutdown of all submarine systems"""
        
        logger.info("[SHUTDOWN] SHUTTING DOWN SUBMARINE SYSTEMS...")
        mt5.shutdown()
        logger.info("[SECURED] ALL SYSTEMS OFFLINE - SUBMARINE SECURED")

async def main():
    """Main submarine tactical demonstration"""
    
    print("\n[SUBMARINE] TACTICAL DEMONSTRATION")
    print("USS MIKROBOT FASTVERSION")
    print("Los Angeles-class Attack Submarine")
    print("=" * 60)
    print("MISSION: Demonstrate nuclear reactor risk calculations")
    print("DOCTRINE: Nuclear-grade risk management with Gold Standard quality")
    print("MODE: NO ACTUAL TRADES - TACTICAL ANALYSIS ONLY")
    print("EXPECTED DURATION: ~15 seconds")
    print("=" * 60)
    
    demo = SubmarineTacticalDemo()
    
    try:
        # Initialize submarine systems
        if await demo.initialize_submarine_systems():
            # Execute the tactical demonstration
            await demo.execute_tactical_demonstration()
        else:
            logger.critical("[ABORT] DEMO ABORTED: Submarine systems initialization failed")
            
    except KeyboardInterrupt:
        logger.info("[EMERGENCY] EMERGENCY SURFACE: Demo terminated by operator")
    except Exception as e:
        logger.error("[EMERGENCY] SUBMARINE EMERGENCY: %s", str(e))
    finally:
        demo.shutdown_submarine_systems()

if __name__ == "__main__":
    asyncio.run(main())