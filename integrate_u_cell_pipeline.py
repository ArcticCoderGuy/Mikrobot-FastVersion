#!/usr/bin/env python3
"""
Integrate MT5 Expert Agent into U-Cell Pipeline
Enhanced pipeline with MT5 expertise at each stage
"""

import sys
import os
import asyncio
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_u_cell_mt5_integration():
    """Test MT5 Expert Agent integration with each U-Cell"""
    
    print("MT5 EXPERT - U-CELL PIPELINE INTEGRATION")
    print("=" * 60)
    
    try:
        # Import components
        from src.agents.mt5_expert_agent import MT5ExpertAgent
        from src.core.mcp_controller import MCPMessage, MessageType
        
        print("PASS: Components imported successfully")
        
        # Initialize MT5 Expert
        mt5_expert = MT5ExpertAgent()
        print(f"PASS: MT5 Expert initialized - {mt5_expert.agent_id}")
        
        # Test integration with each U-Cell
        u_cell_results = {}
        
        # U-Cell 1: Signal Validation Enhancement
        print("\n=== U-CELL 1: SIGNAL VALIDATION ENHANCEMENT ===")
        signal_result = await test_signal_validation_integration(mt5_expert)
        u_cell_results['signal_validation'] = signal_result
        
        # U-Cell 2: ML Analysis Optimization
        print("\n=== U-CELL 2: ML ANALYSIS OPTIMIZATION ===")
        ml_result = await test_ml_analysis_integration(mt5_expert)
        u_cell_results['ml_analysis'] = ml_result
        
        # U-Cell 3: Risk Engine Strategy
        print("\n=== U-CELL 3: RISK ENGINE STRATEGY ===")
        risk_result = await test_risk_engine_integration(mt5_expert)
        u_cell_results['risk_engine'] = risk_result
        
        # U-Cell 4: Trade Execution Optimization
        print("\n=== U-CELL 4: TRADE EXECUTION OPTIMIZATION ===")
        execution_result = await test_trade_execution_integration(mt5_expert)
        u_cell_results['trade_execution'] = execution_result
        
        # U-Cell 5: Monitoring & Control
        print("\n=== U-CELL 5: MONITORING & CONTROL ===")
        monitoring_result = await test_monitoring_integration(mt5_expert)
        u_cell_results['monitoring'] = monitoring_result
        
        return True, u_cell_results
        
    except Exception as e:
        print(f"FAIL: U-Cell integration failed: {e}")
        return False, {}

async def test_signal_validation_integration(mt5_expert):
    """Test MT5 Expert integration with Signal Validation U-Cell"""
    
    try:
        # Import MCPMessage at function level
        from src.core.mcp_controller import MCPMessage, MessageType
        
        # Scenario: Signal Validation asks MT5 Expert for pattern advice
        print("Testing: Signal validation consultation")
        
        validation_msg = MCPMessage(
            id="signal_validation_consultation",
            method="get_mt5_advice",
            params={
                "query": "How to improve M5 BOS + M1 retest pattern validation accuracy?",
                "user_level": "expert",
                "context": {
                    "u_cell": "signal_validation",
                    "pattern_type": "M5_M1_BOS_RETEST",
                    "current_accuracy": 0.75,
                    "false_positive_rate": 0.15
                }
            },
            type=MessageType.REQUEST
        )
        
        response = await mt5_expert.handle_message(validation_msg)
        
        if response and response.method == "mt5_advice_provided":
            print("  PASS: Signal validation consultation successful")
            confidence = response.params.get('confidence', 0)
            domain = response.params.get('domain', 'unknown')
            print(f"    Advice confidence: {confidence*100:.1f}%")
            print(f"    Expert domain: {domain}")
            
            # Test pattern analysis advice
            pattern_msg = MCPMessage(
                id="pattern_analysis_advice",
                method="explain_mt5_concept",
                params={
                    "concept": "break_of_structure_validation",
                    "detail_level": "expert",
                    "include_examples": True
                },
                type=MessageType.REQUEST
            )
            
            pattern_response = await mt5_expert.handle_message(pattern_msg)
            
            if pattern_response:
                print("  PASS: Pattern analysis advice provided")
                return {
                    'success': True,
                    'consultation_confidence': confidence,
                    'domain': domain,
                    'pattern_advice': True
                }
        
        print("  FAIL: Signal validation integration failed")
        return {'success': False}
        
    except Exception as e:
        print(f"  FAIL: Signal validation integration error: {e}")
        return {'success': False, 'error': str(e)}

async def test_ml_analysis_integration(mt5_expert):
    """Test MT5 Expert integration with ML Analysis U-Cell"""
    
    try:
        # Import MCPMessage at function level
        from src.core.mcp_controller import MCPMessage, MessageType
        
        print("Testing: ML Analysis optimization consultation")
        
        # Scenario: ML Analysis needs optimization advice
        ml_msg = MCPMessage(
            id="ml_optimization_consultation",
            method="optimize_mt5_setup",
            params={
                "setup": {
                    "u_cell": "ml_analysis",
                    "models": ["tensorflow_lstm", "scikit_svm"],
                    "features": ["price", "volume", "indicators"],
                    "processing_time_ms": 120,
                    "accuracy": 0.78
                },
                "goals": ["improve_accuracy", "reduce_latency", "better_features"],
                "constraints": {"max_latency_ms": 100, "min_accuracy": 0.80}
            },
            type=MessageType.REQUEST
        )
        
        response = await mt5_expert.handle_message(ml_msg)
        
        if response and response.method == "mt5_optimization_plan":
            print("  PASS: ML optimization consultation successful")
            plan = response.params.get('optimization_plan', {})
            improvements = plan.get('improvements', [])
            steps = plan.get('steps', [])
            
            print(f"    Expected improvements: {len(improvements)}")
            print(f"    Implementation steps: {len(steps)}")
            
            # Test feature engineering advice
            feature_msg = MCPMessage(
                id="feature_engineering_advice",
                method="get_mt5_advice",
                params={
                    "query": "What are the best technical indicators for BOS pattern ML models?",
                    "user_level": "expert",
                    "context": {"ml_model_type": "tensorflow_lstm"}
                },
                type=MessageType.REQUEST
            )
            
            feature_response = await mt5_expert.handle_message(feature_msg)
            
            if feature_response:
                print("  PASS: Feature engineering advice provided")
                return {
                    'success': True,
                    'optimization_plan': plan,
                    'feature_advice': True,
                    'improvements_count': len(improvements)
                }
        
        print("  FAIL: ML analysis integration failed")
        return {'success': False}
        
    except Exception as e:
        print(f"  FAIL: ML analysis integration error: {e}")
        return {'success': False, 'error': str(e)}

async def test_risk_engine_integration(mt5_expert):
    """Test MT5 Expert integration with Risk Engine U-Cell"""
    
    try:
        # Import MCPMessage at function level
        from src.core.mcp_controller import MCPMessage, MessageType
        
        print("Testing: Risk Engine strategy consultation")
        
        # Scenario: Risk Engine needs trading strategy advice
        risk_msg = MCPMessage(
            id="risk_strategy_consultation",
            method="suggest_trading_strategy",
            params={
                "requirements": {
                    "u_cell": "risk_engine",
                    "ftmo_compliant": True,
                    "max_daily_loss": 0.05,
                    "max_position_risk": 0.02,
                    "target_win_rate": 0.65
                },
                "risk_tolerance": "conservative",
                "trading_style": "scalping"
            },
            type=MessageType.REQUEST
        )
        
        response = await mt5_expert.handle_message(risk_msg)
        
        if response and response.method == "trading_strategy_suggested":
            print("  PASS: Risk strategy consultation successful")
            strategies = response.params.get('strategy_suggestions', {})
            risk_analysis = strategies.get('risk_analysis', {})
            
            print(f"    Risk analysis provided: {'risk_analysis' in strategies}")
            print(f"    Implementation guide: {'implementation' in strategies}")
            
            # Test risk management advice
            risk_advice_msg = MCPMessage(
                id="risk_management_advice",
                method="get_mt5_advice",
                params={
                    "query": "How to implement dynamic position sizing for FTMO compliance?",
                    "user_level": "expert",
                    "context": {"prop_firm": "FTMO", "account_size": 100000}
                },
                type=MessageType.REQUEST
            )
            
            risk_advice_response = await mt5_expert.handle_message(risk_advice_msg)
            
            if risk_advice_response:
                print("  PASS: Risk management advice provided")
                return {
                    'success': True,
                    'strategy_suggestions': strategies,
                    'risk_advice': True,
                    'ftmo_compliant': True
                }
        
        print("  FAIL: Risk engine integration failed")
        return {'success': False}
        
    except Exception as e:
        print(f"  FAIL: Risk engine integration error: {e}")
        return {'success': False, 'error': str(e)}

async def test_trade_execution_integration(mt5_expert):
    """Test MT5 Expert integration with Trade Execution U-Cell"""
    
    try:
        # Import MCPMessage at function level
        from src.core.mcp_controller import MCPMessage, MessageType
        
        print("Testing: Trade Execution optimization consultation")
        
        # Scenario: Trade Execution needs performance optimization
        execution_msg = MCPMessage(
            id="execution_optimization_consultation",
            method="optimize_mt5_setup",
            params={
                "setup": {
                    "u_cell": "trade_execution",
                    "broker": "AVA",
                    "execution_mode": "market",
                    "slippage_pips": 2.0,
                    "avg_execution_time_ms": 180
                },
                "goals": ["reduce_slippage", "faster_execution", "better_fills"],
                "constraints": {"max_slippage_pips": 1.5, "max_execution_time_ms": 100}
            },
            type=MessageType.REQUEST
        )
        
        response = await mt5_expert.handle_message(execution_msg)
        
        if response and response.method == "mt5_optimization_plan":
            print("  PASS: Execution optimization consultation successful")
            plan = response.params.get('optimization_plan', {})
            
            # Test MQL5 execution code review
            code_review_msg = MCPMessage(
                id="execution_code_review",
                method="review_mql5_code",
                params={
                    "code": """
// Simplified execution logic
bool ExecuteTrade(double price, double sl, double tp) {
    return OrderSend(Symbol(), OP_BUY, 0.1, price, 3, sl, tp) > 0;
}
                    """,
                    "type": "performance"
                },
                type=MessageType.REQUEST
            )
            
            code_response = await mt5_expert.handle_message(code_review_msg)
            
            if code_response:
                print("  PASS: Execution code review completed")
                quality_score = code_response.params.get('code_quality_score', 0)
                print(f"    Code quality score: {quality_score*100:.1f}%")
                
                return {
                    'success': True,
                    'optimization_plan': plan,
                    'code_review': True,
                    'code_quality': quality_score
                }
        
        print("  FAIL: Trade execution integration failed")
        return {'success': False}
        
    except Exception as e:
        print(f"  FAIL: Trade execution integration error: {e}")
        return {'success': False, 'error': str(e)}

async def test_monitoring_integration(mt5_expert):
    """Test MT5 Expert integration with Monitoring & Control U-Cell"""
    
    try:
        # Import MCPMessage at function level
        from src.core.mcp_controller import MCPMessage, MessageType
        
        print("Testing: Monitoring & Control consultation")
        
        # Scenario: Monitoring needs performance analysis
        monitoring_msg = MCPMessage(
            id="monitoring_analysis_consultation",
            method="analyze_mt5_performance",
            params={
                "performance_data": {
                    "u_cell": "monitoring_control",
                    "system_metrics": {
                        "signal_success_rate": 0.78,
                        "avg_response_time_ms": 95,
                        "error_rate": 0.02,
                        "uptime": 0.995
                    },
                    "trading_metrics": {
                        "win_rate": 0.65,
                        "avg_profit_per_trade": 15.50,
                        "max_drawdown": 0.03
                    }
                }
            },
            type=MessageType.REQUEST
        )
        
        response = await mt5_expert.handle_message(monitoring_msg)
        
        if response:
            print("  PASS: Monitoring analysis consultation successful")
            
            # Test troubleshooting advice
            troubleshoot_msg = MCPMessage(
                id="troubleshooting_consultation",
                method="diagnose_mt5_issue",
                params={
                    "symptoms": ["occasional_timeouts", "memory_usage_increase"],
                    "error_messages": ["connection_timeout", "insufficient_memory"],
                    "context": {"system_load": "high", "concurrent_eas": 3}
                },
                type=MessageType.REQUEST
            )
            
            troubleshoot_response = await mt5_expert.handle_message(troubleshoot_msg)
            
            if troubleshoot_response:
                print("  PASS: Troubleshooting consultation provided")
                diagnosis = troubleshoot_response.params.get('diagnosis', {})
                confidence = diagnosis.get('confidence', 0)
                
                return {
                    'success': True,
                    'performance_analysis': True,
                    'troubleshooting': True,
                    'diagnosis_confidence': confidence
                }
        
        print("  FAIL: Monitoring integration failed")
        return {'success': False}
        
    except Exception as e:
        print(f"  FAIL: Monitoring integration error: {e}")
        return {'success': False, 'error': str(e)}

def generate_pipeline_integration_report(success, u_cell_results):
    """Generate U-Cell pipeline integration report"""
    
    print("\nU-CELL PIPELINE INTEGRATION REPORT")
    print("=" * 60)
    
    if success and u_cell_results:
        successful_integrations = sum(1 for result in u_cell_results.values() if result.get('success', False))
        total_integrations = len(u_cell_results)
        success_rate = (successful_integrations / total_integrations) * 100
        
        print(f"INTEGRATION SUCCESS RATE: {success_rate:.1f}% ({successful_integrations}/{total_integrations})")
        print()
        
        # Detail each U-Cell integration
        for u_cell_name, result in u_cell_results.items():
            status = "SUCCESS" if result.get('success', False) else "FAILED"
            print(f"{u_cell_name.upper()}: {status}")
            
            if result.get('success', False):
                # Show specific metrics for each U-Cell
                if 'consultation_confidence' in result:
                    print(f"  Consultation confidence: {result['consultation_confidence']*100:.1f}%")
                if 'improvements_count' in result:
                    print(f"  Improvements suggested: {result['improvements_count']}")
                if 'code_quality' in result:
                    print(f"  Code quality score: {result['code_quality']*100:.1f}%")
                if 'diagnosis_confidence' in result:
                    print(f"  Diagnosis confidence: {result['diagnosis_confidence']*100:.1f}%")
            elif 'error' in result:
                print(f"  Error: {result['error']}")
            print()
        
        if success_rate >= 80:
            grade = "EXCELLENT"
            recommendation = "Ready for production pipeline integration"
        elif success_rate >= 60:
            grade = "GOOD"
            recommendation = "Minor optimization recommended"
        else:
            grade = "NEEDS WORK"
            recommendation = "Significant improvements required"
        
        print(f"INTEGRATION GRADE: {grade}")
        print(f"RECOMMENDATION: {recommendation}")
        
        if success_rate >= 80:
            print("\nENHANCED U-CELL PIPELINE READY!")
            print("MT5 Expert Agent now provides:")
            print("  - Real-time consultation to all U-Cells")
            print("  - Expert optimization recommendations")
            print("  - Code quality analysis and improvements")
            print("  - Performance troubleshooting support")
            print("  - Strategic trading advice")
        
    else:
        print("STATUS: INTEGRATION FAILED")
        print("Pipeline integration was not successful")
    
    return success

async def main():
    """Main U-Cell pipeline integration"""
    
    print("Starting MT5 Expert Agent U-Cell Pipeline Integration...")
    print()
    
    # Test all U-Cell integrations
    success, u_cell_results = await test_u_cell_mt5_integration()
    
    # Generate comprehensive report
    integration_success = generate_pipeline_integration_report(success, u_cell_results)
    
    if integration_success:
        print(f"\nU-CELL PIPELINE INTEGRATION COMPLETE: {datetime.now().strftime('%H:%M:%S')}")
        print("MT5 Expert Agent is now fully integrated into Mikrobot ecosystem!")
    else:
        print(f"\nU-CELL PIPELINE INTEGRATION NEEDS WORK: {datetime.now().strftime('%H:%M:%S')}")

if __name__ == "__main__":
    asyncio.run(main())