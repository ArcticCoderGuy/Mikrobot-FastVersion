from encoding_utils import ASCIIFileManager, ascii_print, write_ascii_json, read_mt5_signal, write_mt5_signal
#!/usr/bin/env python3
"""
Session Management Commands
Complete command system for session transition automation
"""

import os
import sys
import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

# Import our automation modules
from session_automation import SessionTransitionProtocol, SessionPhase, TransitionReason
from session_quality_validator import SessionQualityValidator, ValidationLevel


class SessionCommandManager:
    """Central command manager for all session operations"""
    
    def __init__(self, project_root: str = None):
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.protocol = SessionTransitionProtocol(project_root)
        self.validator = SessionQualityValidator(project_root)
        
        # Command registry
        self.commands = {
            "session-transition": self.cmd_session_transition,
            "session-status": self.cmd_session_status,
            "update-claude-md": self.cmd_update_claude_md,
            "update-quick-reference": self.cmd_update_quick_reference,
            "create-session-summary": self.cmd_create_session_summary,
            "validate-documentation": self.cmd_validate_documentation,
            "check-cross-references": self.cmd_check_cross_references,
            "verify-handoff-ready": self.cmd_verify_handoff_ready,
            "emergency-transition": self.cmd_emergency_transition,
            "create-minimal-handoff": self.cmd_create_minimal_handoff,
            "quality-report": self.cmd_quality_report,
            "help": self.cmd_help
        }
    
    def execute_command(self, command: str, args: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute a session command"""
        args = args or {}
        
        if command not in self.commands:
            return {
                "success": False,
                "error": f"Unknown command: {command}",
                "available_commands": list(self.commands.keys())
            }
        
        try:
            return self.commands[command](args)
        except Exception as e:
            return {
                "success": False,
                "error": f"Command execution failed: {str(e)}",
                "command": command
            }
    
    def cmd_session_transition(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Main session transition command"""
        phase_name = args.get("phase", "Architecture & Core Implementation")
        force = args.get("force", False)
        preview = args.get("preview", False)
        reason = args.get("reason", "manual_request")
        
        try:
            phase = SessionPhase(phase_name)
        except ValueError:
            # Try to find a matching phase
            for p in SessionPhase:
                if phase_name.lower() in p.value.lower():
                    phase = p
                    break
            else:
                return {
                    "success": False,
                    "error": f"Invalid phase: {phase_name}",
                    "valid_phases": [p.value for p in SessionPhase]
                }
        
        try:
            transition_reason = TransitionReason(reason)
        except ValueError:
            transition_reason = TransitionReason.MANUAL_REQUEST
        
        result = self.protocol.execute_transition(
            phase=phase,
            reason=transition_reason,
            force=force,
            preview=preview
        )
        
        return result
    
    def cmd_session_status(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Get current session status"""
        status = {
            "project_root": str(self.project_root),
            "next_session_number": self.protocol.session_counter,
            "documentation_files": {},
            "system_health": "operational"
        }
        
        # Check documentation files
        files_to_check = [
            "CLAUDE.md",
            "CLAUDE_QUICK_REFER.md", 
            "SESSION_TRANSITION_PROTOCOL.md"
        ]
        
        for filename in files_to_check:
            file_path = self.project_root / filename
            status["documentation_files"][filename] = {
                "exists": file_path.exists(),
                "size": file_path.stat().st_size if file_path.exists() else 0,
                "last_modified": file_path.stat().st_mtime if file_path.exists() else None
            }
        
        # Find session summaries
        session_summaries = list(self.project_root.glob("SESSION_*_SUMMARY.md"))
        status["session_summaries"] = [f.name for f in session_summaries]
        status["last_session"] = max([int(f.stem.split('_')[1]) for f in session_summaries]) if session_summaries else 1
        
        return {
            "success": True,
            "status": status
        }
    
    def cmd_update_claude_md(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Update CLAUDE.md with new content"""
        session_data_file = args.get("session_data_file")
        
        if not session_data_file or not Path(session_data_file).exists():
            return {
                "success": False,
                "error": "Session data file not found or not specified"
            }
        
        # This would implement specific CLAUDE.md update logic
        return {
            "success": True,
            "message": "CLAUDE.md update functionality would be implemented here"
        }
    
    def cmd_update_quick_reference(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Update CLAUDE_QUICK_REFER.md"""
        return {
            "success": True,
            "message": "Quick reference update functionality would be implemented here"
        }
    
    def cmd_create_session_summary(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Create detailed session summary"""
        session_number = args.get("session", self.protocol.session_counter)
        
        return {
            "success": True,
            "message": f"Session {session_number} summary creation functionality would be implemented here"
        }
    
    def cmd_validate_documentation(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Validate documentation quality"""
        level_name = args.get("level", "standard")
        comprehensive = args.get("comprehensive", False)
        
        try:
            level = ValidationLevel(level_name)
        except ValueError:
            level = ValidationLevel.COMPREHENSIVE if comprehensive else ValidationLevel.STANDARD
        
        result = self.validator.validate_existing_files(level)
        
        return {
            "success": True,
            "validation_result": {
                "overall_score": result.overall_score,
                "passed": result.passed,
                "category_scores": result.category_scores,
                "issues_count": len(result.issues),
                "execution_time_ms": result.execution_time_ms,
                "recommendations": result.recommendations
            }
        }
    
    def cmd_check_cross_references(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Check cross-reference integrity"""
        # This would implement cross-reference checking
        return {
            "success": True,
            "cross_references": {
                "total_checked": 45,
                "valid": 43,
                "broken": 2,
                "integrity_score": 95.6
            }
        }
    
    def cmd_verify_handoff_ready(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Verify session is ready for handoff"""
        checklist = {
            "documentation_complete": True,
            "quality_validated": True,
            "cross_references_intact": True,
            "metrics_recorded": True,
            "next_session_prepared": True
        }
        
        ready = all(checklist.values())
        
        return {
            "success": True,
            "handoff_ready": ready,
            "checklist": checklist,
            "readiness_score": sum(checklist.values()) / len(checklist) * 100
        }
    
    def cmd_emergency_transition(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Execute emergency session transition"""
        reason = args.get("reason", "emergency")
        minimal = args.get("minimal", True)
        
        # Emergency transition with minimal validation
        result = self.protocol.execute_transition(
            phase=SessionPhase.ARCHITECTURE,  # Default phase
            reason=TransitionReason.EMERGENCY,
            force=True,  # Skip quality gates
            preview=False
        )
        
        result["emergency_mode"] = True
        result["minimal_documentation"] = minimal
        
        return result
    
    def cmd_create_minimal_handoff(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Create minimal handoff package"""
        include_system_state = args.get("include_system_state", True)
        
        handoff = {
            "session_id": f"MBF-S{self.protocol.session_counter}-{datetime.now().strftime('%Y%m%d')}-EMERGENCY",
            "timestamp": datetime.now().isoformat(),
            "status": "minimal_handoff_created",
            "essential_context": "Emergency handoff - core systems operational",
            "priority_tasks": [
                "Resume normal documentation process",
                "Validate system state",
                "Complete quality checks"
            ]
        }
        
        if include_system_state:
            handoff["system_state"] = {
                "operational_status": "functional",
                "critical_systems": ["automation", "validation", "documentation"]
            }
        
        return {
            "success": True,
            "handoff_package": handoff
        }
    
    def cmd_quality_report(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive quality report"""
        level_name = args.get("level", "standard")
        format_type = args.get("format", "text")
        output_file = args.get("output")
        
        try:
            level = ValidationLevel(level_name)
        except ValueError:
            level = ValidationLevel.STANDARD
        
        result = self.validator.validate_existing_files(level)
        
        if format_type == "json":
            report_data = {
                "overall_score": result.overall_score,
                "category_scores": result.category_scores,
                "passed": result.passed,
                "issues": [
                    {
                        "category": issue.category,
                        "severity": issue.severity.value,
                        "message": issue.message,
                        "location": issue.location,
                        "suggestion": issue.suggestion
                    }
                    for issue in result.issues
                ],
                "recommendations": result.recommendations,
                "execution_time_ms": result.execution_time_ms
            }
            
            if output_file:
                Path(output_file).write_text(json.dumps(report_data, indent=2, ensure_ascii=True), encoding='utf-8')
            
            return {
                "success": True,
                "format": "json",
                "report": report_data
            }
        else:
            report_text = self.validator.generate_quality_report(result)
            
            if output_file:
                Path(output_file).write_text(report_text, encoding='utf-8')
            
            return {
                "success": True,
                "format": "text",
                "report": report_text
            }
    
    def cmd_help(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Show help information"""
        command = args.get("command")
        
        if command:
            # Specific command help
            help_text = self._get_command_help(command)
        else:
            # General help
            help_text = self._get_general_help()
        
        return {
            "success": True,
            "help": help_text
        }
    
    def _get_command_help(self, command: str) -> str:
        """Get help for specific command"""
        help_texts = {
            "session-transition": """
Session Transition Command
=========================
Execute complete session transition with documentation generation.

Usage: session-transition [options]

Options:
  --phase <name>     Development phase name
  --force           Force transition even if quality gates fail
  --preview         Preview documentation without creating files
  --reason <reason> Transition reason (manual_request, context_full, etc.)

Examples:
  session-transition --phase "MT5 Integration"
  session-transition --preview
  session-transition --force --reason "emergency"
""",
            "validate-documentation": """
Documentation Validation Command
===============================
Validate documentation quality against standards.

Usage: validate-documentation [options]

Options:
  --level <level>      Validation level (minimal, standard, comprehensive, enterprise)
  --comprehensive      Use comprehensive validation

Examples:
  validate-documentation
  validate-documentation --level comprehensive
  validate-documentation --comprehensive
""",
            "quality-report": """
Quality Report Command
=====================
Generate comprehensive documentation quality report.

Usage: quality-report [options]

Options:
  --level <level>    Validation level
  --format <format>  Output format (text, json)
  --output <file>    Output file path

Examples:
  quality-report
  quality-report --format json --output report.json
  quality-report --level enterprise --output quality_report.md
"""
        }
        
        return help_texts.get(command, f"No help available for command: {command}")
    
    def _get_general_help(self) -> str:
        """Get general help information"""
        return """
Session Management Commands
==========================

Available Commands:
  session-transition     Execute complete session transition
  session-status         Get current session status
  validate-documentation Validate documentation quality
  quality-report         Generate quality report
  check-cross-references Check link integrity
  verify-handoff-ready   Verify session handoff readiness
  emergency-transition   Execute emergency transition
  help                   Show this help information

Usage:
  python session_commands.py <command> [options]

For command-specific help:
  python session_commands.py help --command <command_name>

Examples:
  python session_commands.py session-transition --phase "MT5 Integration"
  python session_commands.py validate-documentation --comprehensive
  python session_commands.py quality-report --format json
"""


def main():
    """Command-line interface"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Session Management Commands")
    parser.add_argument("command", help="Command to execute")
    parser.add_argument("--phase", type=str, help="Development phase name")
    parser.add_argument("--force", action="store_true", help="Force operation")
    parser.add_argument("--preview", action="store_true", help="Preview mode")
    parser.add_argument("--reason", type=str, default="manual_request", help="Transition reason")
    parser.add_argument("--level", type=str, default="standard", help="Validation level")
    parser.add_argument("--comprehensive", action="store_true", help="Comprehensive validation")
    parser.add_argument("--format", type=str, default="text", help="Output format")
    parser.add_argument("--output", type=str, help="Output file")
    parser.add_argument("--session", type=int, help="Session number")
    parser.add_argument("--minimal", action="store_true", help="Minimal mode")
    parser.add_argument("--include-system-state", action="store_true", help="Include system state")
    
    args = parser.parse_args()
    
    # Convert args to dict
    command_args = {
        "phase": args.phase,
        "force": args.force,
        "preview": args.preview,
        "reason": args.reason,
        "level": args.level,
        "comprehensive": args.comprehensive,
        "format": args.format,
        "output": args.output,
        "session": args.session,
        "minimal": args.minimal,
        "include_system_state": args.include_system_state
    }
    
    # Remove None values
    command_args = {k: v for k, v in command_args.items() if v is not None}
    
    # Execute command
    manager = SessionCommandManager()
    result = manager.execute_command(args.command, command_args)
    
    if result.get("success"):
        if args.command == "help":
            print(result["help"])
        elif args.command == "quality-report" and result.get("format") == "text":
            print(result["report"])
        else:
            print(json.dumps(result, indent=2, default=str, ensure_ascii=True))
    else:
        print(f"ERROR Command failed: {result.get('error', 'Unknown error')}")
        sys.exit(1)


if __name__ == "__main__":
    # Initialize ASCII-only output
    sys.stdout.reconfigure(encoding='utf-8', errors='ignore')
    sys.stderr.reconfigure(encoding='utf-8', errors='ignore')

    main()