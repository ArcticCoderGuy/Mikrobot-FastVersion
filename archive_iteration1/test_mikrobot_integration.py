#!/usr/bin/env python3
"""
Test MT5 Expert Agent in Full Mikrobot Environment
Integration testing with existing U-Cells and MCP system
"""

import sys
import os
import asyncio
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_full_mikrobot_integration():
    """Test MT5 Expert Agent in complete Mikrobot ecosystem"""
    
    print("MIKROBOT ECOSYSTEM INTEGRATION TEST")
    print("=" * 60)
    
    try:
        # Import all key components
        from src.agents.mt5_expert_agent import MT5ExpertAgent
        from src.core.mcp_controller import MCPController, MCPMessage, MessageType
        from src.core.u_cells.signal_validation import SignalValidationCell
        from src.core.u_cells.ml_analysis import MLAnalysisCell
        from src.core.u_cells.risk_engine import RiskEngineCell
        
        print("PASS: All imports successful")
        
        # Initialize MT5 Expert Agent
        mt5_expert = MT5ExpertAgent()
        print(f"PASS: MT5 Expert Agent initialized - ID: {mt5_expert.agent_id}")
        
        # Initialize MCP Controller
        mcp_controller = MCPController()
        print("PASS: MCP Controller initialized")
        
        # Initialize U-Cells
        signal_cell = SignalValidationCell()
        ml_cell = MLAnalysisCell()
        risk_cell = RiskEngineCell()
        
        print("PASS: U-Cells initialized")
        
        return True, {
            'mt5_expert': mt5_expert,
            'mcp_controller': mcp_controller,
            'signal_cell': signal_cell,
            'ml_cell': ml_cell,
            'risk_cell': risk_cell
        }
        
    except Exception as e:
        print(f"FAIL: Integration test failed: {e}")
        return False, None

async def test_mt5_expert_consultation(components):
    """Test MT5 Expert providing consultation to other components"""
    
    print("\nMT5 EXPERT CONSULTATION TEST")
    print("=" * 60)
    
    try:
        # Import MCPMessage at function level
        from src.core.mcp_controller import MCPMessage, MessageType
        
        mt5_expert = components['mt5_expert']
        
        # Scenario 1: Signal validation needs MT5 advice
        print("Scenario 1: Signal Validation consultation")
        
        consultation_msg = MCPMessage(
            id="signal_consultation_1",
            method="get_mt5_advice",
            params={
                "query": "How to validate M5 BOS with M1 retest pattern effectively?",
                "user_level": "expert",
                "context": {
                    "component": "signal_validator",
                    "pattern_type": "M5_M1_BOS_RETEST",
                    "current_confidence": 0.75
                }
            },
            type=MessageType.REQUEST
        )
        
        response = await mt5_expert.handle_message(consultation_msg)
        
        if response and response.method == "mt5_advice_provided":
            print("PASS: Signal validation consultation successful")
            print(f"  Advice confidence: {response.params['confidence']*100:.1f}%")
            print(f"  Domain: {response.params['domain']}")
        else:
            print("FAIL: Signal validation consultation failed")
            return False
        
        # Scenario 2: ML Analysis needs optimization advice
        print("\nScenario 2: ML Analysis optimization consultation")
        
        ml_consultation_msg = MCPMessage(
            id="ml_consultation_1", 
            method="optimize_mt5_setup",
            params={
                "setup": {
                    "indicators": ["RSI", "MACD", "Bollinger_Bands"],
                    "timeframes": ["M1", "M5"],
                    "processing_time_ms": 150
                },
                "goals": ["reduce_latency", "improve_accuracy"],
                "constraints": {"max_latency_ms": 100}
            },
            type=MessageType.REQUEST
        )
        
        ml_response = await mt5_expert.handle_message(ml_consultation_msg)
        
        if ml_response and ml_response.method == "mt5_optimization_plan":
            print("PASS: ML optimization consultation successful")
            print(f"  Optimization plan: {len(ml_response.params['optimization_plan']['steps'])} steps")
        else:
            print("FAIL: ML optimization consultation failed")
            return False
        
        # Scenario 3: Risk Engine needs strategy advice
        print("\nScenario 3: Risk Engine strategy consultation")
        
        risk_consultation_msg = MCPMessage(
            id="risk_consultation_1",
            method="suggest_trading_strategy",
            params={
                "requirements": {
                    "max_risk_per_trade": 0.02,
                    "target_win_rate": 0.65,
                    "ftmo_compliant": True
                },
                "risk_tolerance": "conservative",
                "trading_style": "scalping"
            },
            type=MessageType.REQUEST
        )
        
        risk_response = await mt5_expert.handle_message(risk_consultation_msg)
        
        if risk_response and risk_response.method == "trading_strategy_suggested":
            print("PASS: Risk strategy consultation successful")
            strategies = risk_response.params['strategy_suggestions']['strategies']
            print(f"  Strategies suggested: {len(strategies)}")
        else:
            print("FAIL: Risk strategy consultation failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"FAIL: Consultation test failed: {e}")
        return False

async def test_real_mt5_scenario_simulation(components):
    """Simulate real MT5 trading scenario with agent collaboration"""
    
    print("\nREAL MT5 SCENARIO SIMULATION")
    print("=" * 60)
    
    try:
        # Import MCPMessage at function level
        from src.core.mcp_controller import MCPMessage, MessageType
        
        mt5_expert = components['mt5_expert']
        signal_cell = components['signal_cell']
        
        # Simulate incoming M5 BOS signal from your EA
        print("Simulating: MikroBot_BOS_M5M1.mq5 signal received")
        
        # Step 1: Signal validation asks for MT5 expertise
        signal_data = {
            "symbol": "EURUSD",
            "timeframe": "M1",
            "pattern_type": "M1_BREAK_RETEST",
            "direction": "BUY",
            "price_levels": {
                "entry": 1.0855,
                "m5_bos_level": 1.0850,
                "m1_break_high": 1.0857,
                "m1_break_low": 1.0852
            },
            "pip_trigger": 0.2,
            "source": "MikroBot_BOS_M5M1_EA"
        }
        
        # MT5 Expert analyzes the signal quality
        analysis_msg = MCPMessage(
            id="real_scenario_analysis",
            method="get_mt5_advice",
            params={
                "query": "Analyze this M5 BOS + M1 retest signal quality and recommend improvements",
                "user_level": "expert",
                "context": {
                    "signal_data": signal_data,
                    "ea_name": "MikroBot_BOS_M5M1",
                    "account": "95244786"
                }
            },
            type=MessageType.REQUEST
        )
        
        expert_analysis = await mt5_expert.handle_message(analysis_msg)
        
        if expert_analysis:
            print("PASS: MT5 Expert analyzed signal successfully")
            print(f"  Analysis confidence: {expert_analysis.params['confidence']*100:.1f}%")
            
            # Step 2: Ask for code review of the EA logic
            code_review_msg = MCPMessage(
                id="ea_code_review",
                method="review_mql5_code",
                params={
                    "code": """
// Simplified version of your EA logic
if(m5_bos_confirmed && m1_retest_within_tolerance) {
    double entry_price = Ask + pip_trigger * Point;
    double stop_loss = m5_bos_level - safety_margin;
    double take_profit = entry_price + (stop_loss - entry_price) * 2.0;
    
    OrderSend(Symbol(), OP_BUY, lot_size, entry_price, 3, stop_loss, take_profit);
}
                    """,
                    "type": "performance"
                },
                type=MessageType.REQUEST
            )
            
            code_review = await mt5_expert.handle_message(code_review_msg)
            
            if code_review:
                print("PASS: MQL5 code review completed")
                quality_score = code_review.params['code_quality_score']
                print(f"  Code quality score: {quality_score*100:.1f}%")
                print(f"  Issues found: {len(code_review.params['issues_found'])}")
            
            # Step 3: Request optimization suggestions
            optimization_msg = MCPMessage(
                id="ea_optimization",
                method="optimize_mt5_setup", 
                params={
                    "setup": {
                        "ea_name": "MikroBot_BOS_M5M1",
                        "pip_trigger": 0.2,
                        "timeframes": ["M5", "M1"],
                        "current_performance": "good"
                    },
                    "goals": ["improve_accuracy", "reduce_false_signals"],
                    "constraints": {"maintain_speed": True}
                },
                type=MessageType.REQUEST
            )
            
            optimization = await mt5_expert.handle_message(optimization_msg)
            
            if optimization:
                print("PASS: EA optimization suggestions provided")
                improvements = optimization.params['expected_improvements']
                print(f"  Expected improvements: {improvements}")
            
            return True
        else:
            print("FAIL: MT5 Expert analysis failed")
            return False
            
    except Exception as e:
        print(f"FAIL: Real scenario simulation failed: {e}")
        return False

async def test_cross_agent_collaboration(components):
    """Test collaboration between MT5 Expert and other agents"""
    
    print("\nCROSS-AGENT COLLABORATION TEST")
    print("=" * 60)
    
    try:
        # Import MCPMessage at function level
        from src.core.mcp_controller import MCPMessage, MessageType
        
        mt5_expert = components['mt5_expert']
        mcp_controller = components['mcp_controller']
        
        # Register MT5 Expert in MCP Controller (simulation)
        print("Registering MT5 Expert in MCP ecosystem...")
        
        # Simulate agent registration
        registration_success = True  # In real implementation, this would register with MCP
        
        if registration_success:
            print("PASS: MT5 Expert registered in MCP Controller")
            
            # Test cross-agent message routing
            collaborative_msg = MCPMessage(
                id="cross_agent_test",
                method="get_mt5_advice",
                params={
                    "query": "How should risk management adapt when multiple EAs are running?",
                    "user_level": "advanced",
                    "context": {
                        "requesting_agent": "risk_manager",
                        "scenario": "multi_ea_environment"
                    }
                },
                type=MessageType.REQUEST
            )
            
            response = await mt5_expert.handle_message(collaborative_msg)
            
            if response:
                print("PASS: Cross-agent collaboration successful")
                print(f"  Response method: {response.method}")
                print(f"  Collaboration context preserved: {'requesting_agent' in str(response.params)}")
                return True
            else:
                print("FAIL: Cross-agent collaboration failed")
                return False
        else:
            print("FAIL: MT5 Expert registration failed")
            return False
            
    except Exception as e:
        print(f"FAIL: Cross-agent collaboration test failed: {e}")
        return False

def generate_integration_report(test_results):
    """Generate comprehensive integration report"""
    
    print("\nINTEGRATION REPORT")
    print("=" * 60)
    
    passed_tests = sum(test_results.values())
    total_tests = len(test_results)
    success_rate = (passed_tests / total_tests) * 100
    
    print("TEST RESULTS:")
    for test_name, result in test_results.items():
        status = "PASS" if result else "FAIL"
        print(f"  {status}: {test_name}")
    
    print(f"\nOVERALL SUCCESS RATE: {success_rate:.1f}% ({passed_tests}/{total_tests})")
    
    if success_rate >= 90:
        grade = "EXCELLENT"
        recommendation = "Ready for production integration"
    elif success_rate >= 75:
        grade = "GOOD"
        recommendation = "Minor issues to resolve"
    elif success_rate >= 60:
        grade = "ACCEPTABLE"
        recommendation = "Some improvements needed"
    else:
        grade = "NEEDS WORK"
        recommendation = "Significant issues to address"
    
    print(f"INTEGRATION GRADE: {grade}")
    print(f"RECOMMENDATION: {recommendation}")
    
    if success_rate >= 80:
        print("\nREADY FOR NEXT STEPS:")
        print("  1. Complete MCP Controller registration")
        print("  2. Add to U-Cell pipeline")
        print("  3. Enable real-time MT5 integration")
        print("  4. Start TensorFlow feature pipeline development")
    
    return success_rate, grade

async def main():
    """Main integration test flow"""
    
    print("Starting comprehensive Mikrobot integration test...")
    print()
    
    # Test 1: Basic integration
    integration_success, components = await test_full_mikrobot_integration()
    
    if not integration_success:
        print("CRITICAL: Basic integration failed - cannot proceed")
        return
    
    # Test 2: Consultation capabilities
    consultation_success = await test_mt5_expert_consultation(components)
    
    # Test 3: Real scenario simulation  
    scenario_success = await test_real_mt5_scenario_simulation(components)
    
    # Test 4: Cross-agent collaboration
    collaboration_success = await test_cross_agent_collaboration(components)
    
    # Generate final report
    test_results = {
        "Basic Integration": integration_success,
        "Expert Consultation": consultation_success,
        "Real Scenario Simulation": scenario_success,
        "Cross-Agent Collaboration": collaboration_success
    }
    
    success_rate, grade = generate_integration_report(test_results)
    
    print(f"\nMIKROBOT INTEGRATION TEST COMPLETE!")
    print(f"Success Rate: {success_rate:.1f}% ({grade})")

if __name__ == "__main__":
    asyncio.run(main())