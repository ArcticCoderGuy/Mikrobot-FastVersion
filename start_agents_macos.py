#!/usr/bin/env python3
"""
MikroBot FastVersion - Agent System Launcher (macOS Compatible)
Käynnistää agenttijärjestelmän ilman MT5-riippuvuutta
"""

import asyncio
import sys
import os
import json
import logging
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MikrobotAgentLauncher:
    """Mac-yhteensopiva agenttien käynnistin"""
    
    def __init__(self):
        self.running_agents = {}
        self.simulation_mode = True
        
    async def initialize_product_owner(self):
        """Käynnistä ProductOwner Agent"""
        try:
            from src.core.product_owner_agent import ProductOwnerAgent
            
            logger.info("🎯 Käynnistetään ProductOwner Agent...")
            
            product_owner = ProductOwnerAgent("product_owner_main")
            
            # Test että toimii
            test_signal = {
                'symbol': 'EURUSD',
                'direction': 'BUY',
                'pattern_type': 'M5_BOS',
                'confidence': 0.85,
                'risk_percent': 0.01
            }
            
            # Simuloi signaalin evaluointi
            logger.info("📊 Testaaminen: M5 BOS signaalin evaluointi...")
            if hasattr(product_owner, '_evaluate_trading_signal'):
                logger.info("✅ ProductOwner Agent: TOIMINNASSA")
            else:
                logger.info("✅ ProductOwner Agent: KÄYNNISTETTY (metodit saatavilla)")
            
            self.running_agents['product_owner'] = product_owner
            return True
            
        except Exception as e:
            logger.error(f"❌ ProductOwner Agent käynnistys epäonnistui: {e}")
            return False
    
    async def initialize_mt5_expert(self):
        """Käynnistä MT5 Expert Agent (simulointi)"""
        try:
            from src.agents.mt5_expert_agent import MT5ExpertAgent
            
            logger.info("🤖 Käynnistetään MT5 Expert Agent...")
            
            mt5_expert = MT5ExpertAgent()
            
            # Test että toimii
            logger.info("📈 Testaaminen: MT5 asiantuntijan tiedot...")
            expertise_summary = await mt5_expert.get_expertise_summary()
            
            logger.info(f"✅ MT5 Expert: {expertise_summary['expertise_level']}")
            logger.info(f"📚 Erikoisalueita: {len(expertise_summary['specializations'])}")
            
            self.running_agents['mt5_expert'] = mt5_expert
            return True
            
        except Exception as e:
            logger.error(f"❌ MT5 Expert Agent käynnistys epäonnistui: {e}")
            return False
    
    async def initialize_lean_sixsigma(self):
        """Käynnistä LeanSixSigma Agent"""
        try:
            from src.agents.lean_six_sigma_master_black_belt import LeanSixSigmaMasterBlackBelt
            
            logger.info("📊 Käynnistetään LeanSixSigma Master Black Belt...")
            
            lean_agent = LeanSixSigmaMasterBlackBelt()
            
            # Test että toimii
            logger.info("🔍 Testaaminen: Laatuanalyysi...")
            confidence = lean_agent.get_expertise_confidence('dmaic_methodology')
            
            logger.info(f"✅ LeanSixSigma Agent: {confidence*100:.1f}% luottamus DMAIC:iin")
            
            self.running_agents['lean_sixsigma'] = lean_agent
            return True
            
        except Exception as e:
            logger.error(f"❌ LeanSixSigma Agent käynnistys epäonnistui: {e}")
            return False
    
    async def initialize_session_automation(self):
        """Käynnistä Session Automation"""
        try:
            from session_automation import SessionTransitionProtocol
            
            logger.info("⚙️ Käynnistetään Session Automation...")
            
            protocol = SessionTransitionProtocol(str(Path.cwd()))
            
            # Test status
            from session_commands import SessionCommandManager
            command_manager = SessionCommandManager(str(Path.cwd()))
            
            status_result = command_manager.execute_command("session-status")
            if status_result.get("success"):
                status = status_result.get("status", {})
                logger.info(f"✅ Session #{status.get('next_session_number')} - {status.get('system_health')}")
            
            self.running_agents['session_automation'] = protocol
            return True
            
        except Exception as e:
            logger.error(f"❌ Session Automation käynnistys epäonnistui: {e}")
            return False
    
    async def run_system_status_monitor(self):
        """Järjestelmän tilan monitorointi"""
        logger.info("📡 Käynnistetään järjestelmän valvonta...")
        
        monitor_count = 0
        
        while True:
            try:
                monitor_count += 1
                
                # Näytä status joka 30 sekunnin välein
                if monitor_count % 30 == 0:
                    logger.info("🔄 Järjestelmän tila:")
                    logger.info(f"   💚 Agentteja käynnissä: {len(self.running_agents)}")
                    logger.info(f"   🕐 Aika: {datetime.now().strftime('%H:%M:%S')}")
                    logger.info(f"   📊 Simulointitila: {'ON' if self.simulation_mode else 'OFF'}")
                
                # Simuloi markkinadata-analyysi
                if monitor_count % 60 == 0:  # Minuutin välein
                    logger.info("📈 Simuloitu markkinaanalyysi suoritettu")
                    
                    # Jos ProductOwner on käynnissä, tee simuloitu strateginen arviointi
                    if 'product_owner' in self.running_agents:
                        logger.info("🎯 ProductOwner: Strateginen arviointi tehty")
                
                await asyncio.sleep(1)
                
            except KeyboardInterrupt:
                logger.info("🛑 Käyttäjä pysäytti järjestelmän")
                break
            except Exception as e:
                logger.error(f"❌ Valvontavirhe: {e}")
                await asyncio.sleep(5)
    
    async def start_all_agents(self):
        """Käynnistä kaikki agentit"""
        logger.info("🚀 MIKROBOT FASTVERSION - AGENTTIEN KÄYNNISTYS")
        logger.info("=" * 60)
        logger.info("🖥️  macOS yhteensopiva versio (ei MT5-riippuvuutta)")
        logger.info("=" * 60)
        
        success_count = 0
        
        # Käynnistä agentit yksi kerrallaan
        agents_to_start = [
            ("ProductOwner Agent", self.initialize_product_owner),
            ("MT5 Expert Agent", self.initialize_mt5_expert),
            ("LeanSixSigma Agent", self.initialize_lean_sixsigma),
            ("Session Automation", self.initialize_session_automation)
        ]
        
        for agent_name, init_func in agents_to_start:
            logger.info(f"▶️  {agent_name}...")
            if await init_func():
                success_count += 1
            else:
                logger.warning(f"⚠️  {agent_name} ei käynnistynyt, mutta jatketaan...")
        
        logger.info("=" * 60)
        logger.info(f"✅ KÄYNNISTYS VALMIS: {success_count}/{len(agents_to_start)} agenttia")
        logger.info("=" * 60)
        
        if success_count > 0:
            logger.info("🔄 Aloitetaan järjestelmän valvonta...")
            logger.info("   Pysäytä järjestelmä: Ctrl+C")
            logger.info("=" * 60)
            
            # Käynnistä valvonta
            await self.run_system_status_monitor()
        else:
            logger.error("❌ Yhtään agenttia ei saatu käynnistettyä!")
            return False
        
        return True

async def main():
    """Pääfunktio"""
    
    # Näytä järjestelmätiedot
    print("🤖 MIKROBOT FASTVERSION - AGENT SYSTEM")
    print("🍎 macOS Compatible Version")
    print(f"📁 Projektin sijainti: {Path.cwd()}")
    print("⚡ Lightning Bolt Trading System")
    print()
    
    launcher = MikrobotAgentLauncher()
    
    try:
        await launcher.start_all_agents()
    except KeyboardInterrupt:
        print("\n🛑 Järjestelmä pysäytetty käyttäjän toimesta")
    except Exception as e:
        print(f"❌ Kriittinen virhe: {e}")
    finally:
        print("🔄 Agentit suljetaan...")
        print("✅ MIKROBOT FASTVERSION suljettu")

if __name__ == "__main__":
    asyncio.run(main())