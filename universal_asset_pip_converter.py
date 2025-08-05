from encoding_utils import ASCIIFileManager, ascii_print, write_ascii_json, read_mt5_signal, write_mt5_signal
#!/usr/bin/env python3
"""
UNIVERSAL ASSET PIP CONVERTER - MIKROBOT FASTVERSION
==================================================

Comprehensive pip value conversion system for ALL 9 MT5 asset classes
Implements MIKROBOT_FASTVERSION.md Universal 0.6 Ylipip Trigger specification

ASSET CLASSES SUPPORTED:
1. FOREX (Currency pairs)
2. CFD-INDICES (Stock indices)
3. CFD-CRYPTO (Cryptocurrencies)
4. CFD-METALS (Precious metals)
5. CFD-ENERGIES (Oil, gas)
6. CFD-AGRICULTURAL (Commodities)
7. CFD-BONDS (Government bonds)
8. CFD-SHARES (Individual stocks)
9. CFD-ETFS (Exchange traded funds)

COMPLIANCE: MIKROBOT_FASTVERSION.md ABSOLUTE
"""

import MetaTrader5 as mt5
import json
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

# Asset classification system
ASSET_CLASSIFICATIONS = {
    # 1. FOREX - Currency pairs
    'FOREX': {
        'symbols': [
            'EURUSD', 'GBPUSD', 'USDJPY', 'USDCHF', 'AUDUSD', 'USDCAD', 'NZDUSD',
            'EURGBP', 'EURJPY', 'GBPJPY', 'AUDJPY', 'EURAUD', 'GBPAUD', 'EURCHF',
            'GBPCHF', 'AUDCHF', 'CADCHF', 'NZDCHF', 'EURCZK', 'EURHUF', 'EURPLN',
            'EURSEK', 'EURNOK', 'EURDKK', 'USDSEK', 'USDNOK', 'USDDKK', 'USDPLN',
            'USDCZK', 'USDHUF', 'USDSGD', 'USDHKD', 'USDMXN', 'USDZAR', 'USDTRY'
        ],
        'pip_calculation': 'forex_standard',
        'decimal_adjustment': 'auto',
        'jpy_special': True
    },
    
    # 2. CFD-INDICES - Stock market indices
    'CFD_INDICES': {
        'symbols': [
            'US30', 'US500', 'USTEC', 'US2000', 'DJI30', 'SPX500', 'NAS100',
            'GER40', 'GER30', 'DAX40', 'UK100', 'FTSE100', 'FRA40', 'CAC40',
            'ESP35', 'IBEX35', 'ITA40', 'MIB40', 'NED25', 'AEX25', 'SUI20',
            'SMI20', 'AUS200', 'ASX200', 'JPN225', 'N225', 'HKG33', 'HSI33'
        ],
        'pip_calculation': 'index_points',
        'decimal_adjustment': 'minimal',
        'point_value': 1.0
    },
    
    # 3. CFD-CRYPTO - Cryptocurrencies
    'CFD_CRYPTO': {
        'symbols': [
            'BTCUSD', 'ETHUSD', 'XRPUSD', 'ADAUSD', 'DOTUSD', 'LTCUSD', 'LINKUSD',
            'BCHUSD', 'XLMUSD', 'EOSUSD', 'TRXUSD', 'BNBUSD', 'SOLUSD', 'AVAXUSD',
            'MATICUSD', 'DOGEUSD', 'ATOMUSD', 'FILUSD', 'APTUSD', 'NEARUSD',
            'BTCEUR', 'ETHEUR', 'XRPEUR', 'ADAEUR', 'DOTEUR', 'LTCEUR'
        ],
        'pip_calculation': 'crypto_dynamic',
        'decimal_adjustment': 'price_based',
        'btc_special': True
    },
    
    # 4. CFD-METALS - Precious metals
    'CFD_METALS': {
        'symbols': [
            'XAUUSD', 'XAGUSD', 'XPTUSD', 'XPDUSD', 'XAUEUR', 'XAGEUR',
            'GOLD', 'SILVER', 'PLATINUM', 'PALLADIUM'
        ],
        'pip_calculation': 'metals_standard',
        'decimal_adjustment': 'metals_specific',
        'gold_special': True
    },
    
    # 5. CFD-ENERGIES - Oil and gas
    'CFD_ENERGIES': {
        'symbols': [
            'USOIL', 'UKOIL', 'NGAS', 'CRUDE', 'BRENT', 'WTI', 'NATGAS',
            'HEATING', 'GASOLINE', 'OILGAS'
        ],
        'pip_calculation': 'energy_standard',
        'decimal_adjustment': 'commodity_based',
        'oil_special': True
    },
    
    # 6. CFD-AGRICULTURAL - Agricultural commodities
    'CFD_AGRICULTURAL': {
        'symbols': [
            'WHEAT', 'CORN', 'SOYBEANS', 'RICE', 'COFFEE', 'COCOA', 'SUGAR',
            'COTTON', 'LUMBER', 'CATTLE', 'HOGS', 'FEEDER'
        ],
        'pip_calculation': 'agricultural_standard',
        'decimal_adjustment': 'commodity_based',
        'contract_specific': True
    },
    
    # 7. CFD-BONDS - Government bonds
    'CFD_BONDS': {
        'symbols': [
            'US10Y', 'US30Y', 'US2Y', 'US5Y', 'DE10Y', 'DE30Y', 'UK10Y', 'UK30Y',
            'FR10Y', 'IT10Y', 'ES10Y', 'JP10Y', 'AU10Y', 'CA10Y'
        ],
        'pip_calculation': 'bonds_basis_points',
        'decimal_adjustment': 'basis_points',
        'yield_based': True
    },
    
    # 8. CFD-SHARES - Individual stocks
    'CFD_SHARES': {
        'symbols': [
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'NFLX',
            'AMD', 'INTC', 'ORCL', 'CRM', 'ADBE', 'PYPL', 'DIS', 'BA', 'JPM',
            'V', 'MA', 'WMT', 'HD', 'PG', 'JNJ', 'UNH', 'KO', 'PEP'
        ],
        'pip_calculation': 'shares_cents',
        'decimal_adjustment': 'currency_based',
        'cent_based': True
    },
    
    # 9. CFD-ETFS - Exchange traded funds
    'CFD_ETFS': {
        'symbols': [
            'SPY', 'QQQ', 'IWM', 'VTI', 'VOO', 'VEA', 'VWO', 'BND', 'VNQ',
            'GLD', 'SLV', 'USO', 'TLT', 'HYG', 'LQD', 'EFA', 'EEM', 'XLF'
        ],
        'pip_calculation': 'etf_cents',
        'decimal_adjustment': 'currency_based',
        'cent_based': True
    }
}

@dataclass
class AssetPipInfo:
    """Complete asset pip information"""
    symbol: str
    asset_class: str
    point: float
    digits: int
    pip_value: float
    pip_size: float
    ylipip_06_value: float  # 0.6 ylipip in price units
    currency_profit: str
    contract_size: float
    min_volume: float
    max_volume: float
    volume_step: float
    calculation_method: str

class UniversalAssetPipConverter:
    """
    Universal pip converter for all 9 MT5 asset classes
    Implements MIKROBOT_FASTVERSION.md 0.6 ylipip universal trigger
    """
    
    def __init__(self):
        self.setup_logging()
        self.asset_cache: Dict[str, AssetPipInfo] = {}
        self.classification_cache: Dict[str, str] = {}
        
        logger.info("=== UNIVERSAL ASSET PIP CONVERTER INITIALIZED ===")
        logger.info("Supporting 9 MT5 asset classes")
        logger.info("Universal 0.6 ylipip trigger standard")
    
    def setup_logging(self):
        """Setup logging system"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('universal_pip_converter.log'),
                logging.StreamHandler()
            ]
        )
        global logger
        logger = logging.getLogger(__name__)
    
    def classify_asset(self, symbol: str) -> str:
        """
        Classify symbol into one of 9 MT5 asset classes
        Uses comprehensive pattern matching and symbol databases
        """
        if symbol in self.classification_cache:
            return self.classification_cache[symbol]
        
        # Direct lookup in classification database
        for asset_class, config in ASSET_CLASSIFICATIONS.items():
            if symbol in config['symbols']:
                self.classification_cache[symbol] = asset_class
                logger.info(f"Asset classified: {symbol} -> {asset_class}")
                return asset_class
        
        # Pattern-based classification fallback
        asset_class = self._pattern_based_classification(symbol)
        self.classification_cache[symbol] = asset_class
        logger.info(f"Pattern-based classification: {symbol} -> {asset_class}")
        
        return asset_class
    
    def _pattern_based_classification(self, symbol: str) -> str:
        """Pattern-based asset classification"""
        symbol_upper = symbol.upper()
        
        # FOREX patterns
        forex_currencies = ['USD', 'EUR', 'GBP', 'JPY', 'CHF', 'AUD', 'CAD', 'NZD', 'SEK', 'NOK', 'DKK']
        if len(symbol_upper) == 6 and any(curr in symbol_upper for curr in forex_currencies):
            return 'FOREX'
        
        # CRYPTO patterns
        crypto_patterns = ['BTC', 'ETH', 'XRP', 'ADA', 'DOT', 'LTC', 'LINK', 'BCH', 'XLM', 'EOS', 'TRX', 'BNB', 'SOL', 'AVAX', 'MATIC', 'DOGE', 'ATOM']
        if any(crypto in symbol_upper for crypto in crypto_patterns):
            return 'CFD_CRYPTO'
        
        # METALS patterns
        metals_patterns = ['XAU', 'XAG', 'XPT', 'XPD', 'GOLD', 'SILVER', 'PLATINUM', 'PALLADIUM']
        if any(metal in symbol_upper for metal in metals_patterns):
            return 'CFD_METALS'
        
        # INDICES patterns
        indices_patterns = ['US30', 'US500', 'USTEC', 'GER40', 'UK100', 'FRA40', 'DAX', 'FTSE', 'CAC', 'IBEX', 'MIB', 'AEX', 'SMI', 'ASX', 'N225', 'HSI']
        if any(index in symbol_upper for index in indices_patterns):
            return 'CFD_INDICES'
        
        # ENERGIES patterns
        energy_patterns = ['OIL', 'NGAS', 'CRUDE', 'BRENT', 'WTI', 'NATGAS', 'HEATING', 'GASOLINE']
        if any(energy in symbol_upper for energy in energy_patterns):
            return 'CFD_ENERGIES'
        
        # AGRICULTURAL patterns
        agri_patterns = ['WHEAT', 'CORN', 'SOYBEANS', 'RICE', 'COFFEE', 'COCOA', 'SUGAR', 'COTTON', 'LUMBER', 'CATTLE', 'HOGS']
        if any(agri in symbol_upper for agri in agri_patterns):
            return 'CFD_AGRICULTURAL'
        
        # BONDS patterns
        bond_patterns = ['10Y', '30Y', '2Y', '5Y']
        if any(bond in symbol_upper for bond in bond_patterns):
            return 'CFD_BONDS'
        
        # ETF patterns
        etf_patterns = ['SPY', 'QQQ', 'IWM', 'VTI', 'VOO', 'VEA', 'VWO', 'BND', 'VNQ', 'GLD', 'SLV', 'USO', 'TLT', 'HYG', 'LQD', 'EFA', 'EEM', 'XLF']
        if symbol_upper in etf_patterns:
            return 'CFD_ETFS'
        
        # Default to shares if stock-like pattern
        if len(symbol_upper) <= 5 and symbol_upper.isalpha():
            return 'CFD_SHARES'
        
        # Ultimate fallback
        return 'CFD_SHARES'
    
    def get_asset_pip_info(self, symbol: str) -> Optional[AssetPipInfo]:
        """
        Get comprehensive pip information for any MT5 asset
        Implements universal 0.6 ylipip calculation
        """
        if symbol in self.asset_cache:
            return self.asset_cache[symbol]
        
        # Get MT5 symbol info
        symbol_info = mt5.symbol_info(symbol)
        if not symbol_info:
            logger.warning(f"Cannot get MT5 symbol info for {symbol}")
            return None
        
        # Classify asset
        asset_class = self.classify_asset(symbol)
        
        # Calculate pip value based on asset class
        pip_info = self._calculate_asset_pip_value(symbol, symbol_info, asset_class)
        
        if pip_info:
            self.asset_cache[symbol] = pip_info
            logger.info(f"Pip info cached for {symbol}:")
            logger.info(f"  Asset class: {asset_class}")
            logger.info(f"  Pip value: {pip_info.pip_value}")
            logger.info(f"  0.6 ylipip: {pip_info.ylipip_06_value}")
        
        return pip_info
    
    def _calculate_asset_pip_value(self, symbol: str, symbol_info, asset_class: str) -> Optional[AssetPipInfo]:
        """Calculate asset-specific pip value using specialized methods"""
        
        try:
            point = symbol_info.point
            digits = symbol_info.digits
            currency_profit = symbol_info.currency_profit if hasattr(symbol_info, 'currency_profit') else ""
            contract_size = symbol_info.trade_contract_size if hasattr(symbol_info, 'trade_contract_size') else 100000
            
            # Asset-class specific pip calculations
            if asset_class == 'FOREX':
                pip_value, pip_size = self._calculate_forex_pip(symbol, point, digits, currency_profit)
                calculation_method = "forex_standard"
            
            elif asset_class == 'CFD_CRYPTO':
                pip_value, pip_size = self._calculate_crypto_pip(symbol, point, digits)
                calculation_method = "crypto_dynamic"
            
            elif asset_class == 'CFD_INDICES':
                pip_value, pip_size = self._calculate_index_pip(symbol, point, digits)
                calculation_method = "index_points"
            
            elif asset_class == 'CFD_METALS':
                pip_value, pip_size = self._calculate_metals_pip(symbol, point, digits)
                calculation_method = "metals_standard"
            
            elif asset_class == 'CFD_ENERGIES':
                pip_value, pip_size = self._calculate_energy_pip(symbol, point, digits)
                calculation_method = "energy_standard"
            
            elif asset_class == 'CFD_AGRICULTURAL':
                pip_value, pip_size = self._calculate_agricultural_pip(symbol, point, digits)
                calculation_method = "agricultural_standard"
            
            elif asset_class == 'CFD_BONDS':
                pip_value, pip_size = self._calculate_bonds_pip(symbol, point, digits)
                calculation_method = "bonds_basis_points"
            
            elif asset_class == 'CFD_SHARES':
                pip_value, pip_size = self._calculate_shares_pip(symbol, point, digits)
                calculation_method = "shares_cents"
            
            elif asset_class == 'CFD_ETFS':
                pip_value, pip_size = self._calculate_etfs_pip(symbol, point, digits)
                calculation_method = "etf_cents"
            
            else:
                # Fallback to standard calculation
                pip_value, pip_size = self._calculate_standard_pip(point, digits)
                calculation_method = "standard_fallback"
            
            # Calculate universal 0.6 ylipip value
            ylipip_06_value = 0.6 * pip_value
            
            return AssetPipInfo(
                symbol=symbol,
                asset_class=asset_class,
                point=point,
                digits=digits,
                pip_value=pip_value,
                pip_size=pip_size,
                ylipip_06_value=ylipip_06_value,
                currency_profit=currency_profit,
                contract_size=contract_size,
                min_volume=symbol_info.volume_min,
                max_volume=symbol_info.volume_max,
                volume_step=symbol_info.volume_step,
                calculation_method=calculation_method
            )
            
        except Exception as e:
            logger.error(f"Error calculating pip value for {symbol}: {e}")
            return None
    
    def _calculate_forex_pip(self, symbol: str, point: float, digits: int, currency_profit: str) -> Tuple[float, float]:
        """Calculate FOREX pip value with JPY special handling"""
        if 'JPY' in symbol:
            # JPY pairs: 1 pip = 1 point (0.01)
            pip_value = point
            pip_size = point
        else:
            # Standard pairs: 1 pip = 10 points for 5-digit brokers
            if digits == 5:
                pip_value = point * 10
                pip_size = point * 10
            else:
                pip_value = point
                pip_size = point
        
        return pip_value, pip_size
    
    def _calculate_crypto_pip(self, symbol: str, point: float, digits: int) -> Tuple[float, float]:
        """Calculate CRYPTO pip value with price-based adjustment"""
        if 'BTC' in symbol:
            # Bitcoin: Higher pip value due to high price
            pip_value = point * 100
            pip_size = point * 100
        elif any(crypto in symbol for crypto in ['ETH', 'XRP', 'ADA', 'DOT']):
            # Major altcoins: Standard calculation
            pip_value = point * 10
            pip_size = point * 10
        else:
            # Other cryptos: Point-based
            pip_value = point * 10
            pip_size = point * 10
        
        return pip_value, pip_size
    
    def _calculate_index_pip(self, symbol: str, point: float, digits: int) -> Tuple[float, float]:
        """Calculate INDEX pip value (usually 1 point = 1 pip)"""
        pip_value = point
        pip_size = point
        return pip_value, pip_size
    
    def _calculate_metals_pip(self, symbol: str, point: float, digits: int) -> Tuple[float, float]:
        """Calculate METALS pip value with gold/silver specifics"""
        if 'XAU' in symbol or 'GOLD' in symbol:
            # Gold: 1 pip = 10 points (0.10)
            pip_value = point * 10
            pip_size = point * 10
        elif 'XAG' in symbol or 'SILVER' in symbol:
            # Silver: 1 pip = 100 points (0.001)
            pip_value = point * 100
            pip_size = point * 100
        else:
            # Other metals: Standard
            pip_value = point * 10
            pip_size = point * 10
        
        return pip_value, pip_size
    
    def _calculate_energy_pip(self, symbol: str, point: float, digits: int) -> Tuple[float, float]:
        """Calculate ENERGY pip value for oil and gas"""
        if 'OIL' in symbol or 'CRUDE' in symbol or 'BRENT' in symbol or 'WTI' in symbol:
            # Oil: 1 pip = 10 points (0.01)
            pip_value = point * 10
            pip_size = point * 10
        elif 'NGAS' in symbol or 'NATGAS' in symbol:
            # Natural gas: 1 pip = 100 points (0.001)
            pip_value = point * 100
            pip_size = point * 100
        else:
            # Other energies: Standard
            pip_value = point * 10
            pip_size = point * 10
        
        return pip_value, pip_size
    
    def _calculate_agricultural_pip(self, symbol: str, point: float, digits: int) -> Tuple[float, float]:
        """Calculate AGRICULTURAL pip value for commodities"""
        # Agricultural commodities: Contract-specific calculation
        if digits >= 3:
            pip_value = point * 10
            pip_size = point * 10
        else:
            pip_value = point
            pip_size = point
        
        return pip_value, pip_size
    
    def _calculate_bonds_pip(self, symbol: str, point: float, digits: int) -> Tuple[float, float]:
        """Calculate BONDS pip value in basis points"""
        # Bonds: 1 basis point = 0.01% = 0.0001
        pip_value = point * 10  # Basis point calculation
        pip_size = point * 10
        
        return pip_value, pip_size
    
    def _calculate_shares_pip(self, symbol: str, point: float, digits: int) -> Tuple[float, float]:
        """Calculate SHARES pip value in cents"""
        # Individual stocks: 1 pip = 1 cent
        if digits >= 2:
            pip_value = point * 100  # 1 cent
            pip_size = point * 100
        else:
            pip_value = point
            pip_size = point
        
        return pip_value, pip_size
    
    def _calculate_etfs_pip(self, symbol: str, point: float, digits: int) -> Tuple[float, float]:
        """Calculate ETFs pip value in cents"""
        # ETFs: Similar to shares, 1 pip = 1 cent
        if digits >= 2:
            pip_value = point * 100  # 1 cent
            pip_size = point * 100
        else:
            pip_value = point
            pip_size = point
        
        return pip_value, pip_size
    
    def _calculate_standard_pip(self, point: float, digits: int) -> Tuple[float, float]:
        """Standard fallback pip calculation"""
        if digits >= 3:
            pip_value = point * 10
            pip_size = point * 10
        else:
            pip_value = point
            pip_size = point
        
        return pip_value, pip_size
    
    def get_ylipip_trigger_value(self, symbol: str, ylipip_amount: float = 0.6) -> Optional[float]:
        """
        Get ylipip trigger value for any symbol
        Default: 0.6 ylipip (MIKROBOT_FASTVERSION.md universal standard)
        """
        pip_info = self.get_asset_pip_info(symbol)
        if not pip_info:
            return None
        
        ylipip_value = ylipip_amount * pip_info.pip_value
        
        logger.info(f"Ylipip trigger for {symbol}:")
        logger.info(f"  {ylipip_amount} ylipip = {ylipip_value}")
        logger.info(f"  Asset class: {pip_info.asset_class}")
        
        return ylipip_value
    
    def validate_all_asset_classes(self) -> Dict[str, Dict]:
        """
        Validate pip calculations for all 9 asset classes
        Returns comprehensive validation report
        """
        if not mt5.initialize():
            logger.error("MT5 not available for validation")
            return {}
        
        validation_report = {}
        
        for asset_class, config in ASSET_CLASSIFICATIONS.items():
            validation_report[asset_class] = {
                'symbols_tested': [],
                'symbols_valid': [],
                'symbols_failed': [],
                'sample_calculations': []
            }
            
            # Test a sample of symbols from each class
            test_symbols = config['symbols'][:3]  # Test first 3 symbols
            
            for symbol in test_symbols:
                validation_report[asset_class]['symbols_tested'].append(symbol)
                
                try:
                    # Ensure symbol is available
                    if not mt5.symbol_select(symbol, True):
                        validation_report[asset_class]['symbols_failed'].append(f"{symbol}: Not available")
                        continue
                    
                    pip_info = self.get_asset_pip_info(symbol)
                    if pip_info:
                        validation_report[asset_class]['symbols_valid'].append(symbol)
                        validation_report[asset_class]['sample_calculations'].append({
                            'symbol': symbol,
                            'pip_value': pip_info.pip_value,
                            'ylipip_06': pip_info.ylipip_06_value,
                            'method': pip_info.calculation_method
                        })
                    else:
                        validation_report[asset_class]['symbols_failed'].append(f"{symbol}: Calculation failed")
                        
                except Exception as e:
                    validation_report[asset_class]['symbols_failed'].append(f"{symbol}: {str(e)}")
        
        # Generate summary
        logger.info("=== ASSET CLASS VALIDATION COMPLETE ===")
        for asset_class, results in validation_report.items():
            total_tested = len(results['symbols_tested'])
            total_valid = len(results['symbols_valid'])
            success_rate = (total_valid / total_tested * 100) if total_tested > 0 else 0
            
            logger.info(f"{asset_class}: {total_valid}/{total_tested} valid ({success_rate:.1f}%)")
        
        return validation_report
    
    def export_pip_configuration(self, filename: str = None) -> str:
        """Export complete pip configuration for all cached symbols"""
        if not filename:
            filename = f"universal_pip_config_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        export_data = {
            'timestamp': datetime.now().isoformat(),
            'total_symbols': len(self.asset_cache),
            'asset_classes': {},
            'symbol_configurations': {}
        }
        
        # Group by asset class
        for symbol, pip_info in self.asset_cache.items():
            asset_class = pip_info.asset_class
            
            if asset_class not in export_data['asset_classes']:
                export_data['asset_classes'][asset_class] = {
                    'count': 0,
                    'symbols': []
                }
            
            export_data['asset_classes'][asset_class]['count'] += 1
            export_data['asset_classes'][asset_class]['symbols'].append(symbol)
            
            export_data['symbol_configurations'][symbol] = {
                'asset_class': pip_info.asset_class,
                'pip_value': pip_info.pip_value,
                'ylipip_06_value': pip_info.ylipip_06_value,
                'calculation_method': pip_info.calculation_method,
                'digits': pip_info.digits,
                'point': pip_info.point
            }
        
        # Save to file
        with open(filename, 'w', encoding='ascii', errors='ignore') as f:
            json.dump(export_data, f, indent=2)
        
        logger.info(f"Pip configuration exported to {filename}")
        return filename

def main():
    """Demo and validation of Universal Asset Pip Converter"""
    print("=" * 80)
    print("UNIVERSAL ASSET PIP CONVERTER - MIKROBOT FASTVERSION")
    print("=" * 80)
    print("Supporting ALL 9 MT5 Asset Classes:")
    print("1. FOREX (Currency pairs)")
    print("2. CFD-INDICES (Stock indices)")
    print("3. CFD-CRYPTO (Cryptocurrencies)")
    print("4. CFD-METALS (Precious metals)")
    print("5. CFD-ENERGIES (Oil, gas)")
    print("6. CFD-AGRICULTURAL (Commodities)")
    print("7. CFD-BONDS (Government bonds)")
    print("8. CFD-SHARES (Individual stocks)")
    print("9. CFD-ETFS (Exchange traded funds)")
    print("=" * 80)
    
    # Initialize converter
    converter = UniversalAssetPipConverter()
    
    # Connect to MT5
    if not mt5.initialize():
        print("ERROR MT5 connection failed")
        return
    
    print("OK MT5 connected")
    
    # Test symbols from each asset class
    test_symbols = [
        'EURUSD',    # FOREX
        'US30',      # CFD-INDICES
        'BTCUSD',    # CFD-CRYPTO
        'XAUUSD',    # CFD-METALS
        'USOIL',     # CFD-ENERGIES
        'WHEAT',     # CFD-AGRICULTURAL
        'US10Y',     # CFD-BONDS
        'AAPL',      # CFD-SHARES
        'SPY'        # CFD-ETFS
    ]
    
    print("\nTesting pip calculations:")
    print("-" * 80)
    
    for symbol in test_symbols:
        try:
            if not mt5.symbol_select(symbol, True):
                print(f"ERROR {symbol}: Not available")
                continue
            
            pip_info = converter.get_asset_pip_info(symbol)
            if pip_info:
                print(f"OK {symbol:8} | {pip_info.asset_class:15} | Pip: {pip_info.pip_value:10.6f} | 0.6 ylipip: {pip_info.ylipip_06_value:10.6f}")
            else:
                print(f"ERROR {symbol}: Calculation failed")
                
        except Exception as e:
            print(f"ERROR {symbol}: Error - {e}")
    
    print("\nRunning comprehensive validation...")
    validation_report = converter.validate_all_asset_classes()
    
    print("\nExporting configuration...")
    config_file = converter.export_pip_configuration()
    print(f"OK Configuration exported to: {config_file}")
    
    mt5.shutdown()
    print("\nTARGET Universal Asset Pip Converter validation complete!")

if __name__ == "__main__":
    # Initialize ASCII-only output
    sys.stdout.reconfigure(encoding='utf-8', errors='ignore')
    sys.stderr.reconfigure(encoding='utf-8', errors='ignore')

    main()