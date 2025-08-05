from encoding_utils import ASCIIFileManager, ascii_print, write_ascii_json, read_mt5_signal, write_mt5_signal
#!/usr/bin/env python3
"""
Session Documentation Quality Validator
Comprehensive quality assurance system for session documentation
"""

import re
import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass
from enum import Enum


class ValidationLevel(Enum):
    """Validation strictness levels"""
    MINIMAL = "minimal"
    STANDARD = "standard"
    COMPREHENSIVE = "comprehensive"
    ENTERPRISE = "enterprise"


class ValidationSeverity(Enum):
    """Issue severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class ValidationIssue:
    """Individual validation issue"""
    category: str
    severity: ValidationSeverity
    message: str
    location: Optional[str] = None
    suggestion: Optional[str] = None


@dataclass
class ValidationResult:
    """Complete validation result"""
    overall_score: float
    category_scores: Dict[str, float]
    issues: List[ValidationIssue]
    passed: bool
    execution_time_ms: float
    recommendations: List[str]


class SessionQualityValidator:
    """Comprehensive session documentation quality validator"""
    
    def __init__(self, project_root: str = None):
        self.project_root = Path(project_root) if project_root else Path.cwd()
        
        # Quality thresholds by validation level
        self.thresholds = {
            ValidationLevel.MINIMAL: {
                "overall_minimum": 60.0,
                "template_completeness": 70.0,
                "cross_reference_integrity": 80.0,
                "metric_accuracy": 60.0,
                "content_quality": 50.0
            },
            ValidationLevel.STANDARD: {
                "overall_minimum": 80.0,
                "template_completeness": 85.0,
                "cross_reference_integrity": 90.0,
                "metric_accuracy": 80.0,
                "content_quality": 75.0
            },
            ValidationLevel.COMPREHENSIVE: {
                "overall_minimum": 90.0,
                "template_completeness": 95.0,
                "cross_reference_integrity": 98.0,
                "metric_accuracy": 90.0,
                "content_quality": 85.0
            },
            ValidationLevel.ENTERPRISE: {
                "overall_minimum": 95.0,
                "template_completeness": 98.0,
                "cross_reference_integrity": 99.0,
                "metric_accuracy": 95.0,
                "content_quality": 90.0
            }
        }
        
        # Required template sections
        self.required_sections = {
            "claude_md": [
                "Executive Summary",
                "Key Accomplishments", 
                "Performance Metrics",
                "Session Correlation",
                "File Inventory",
                "Decision Rationale",
                "Preparation"
            ],
            "session_summary": [
                "Executive Summary",
                "Session Objectives",
                "Major Implementation Achievements",
                "Performance Benchmarks Achieved",
                "File Changes Summary",
                "Decision Rationale",
                "Session Preparation",
                "Quality Assurance Checklist"
            ],
            "quick_reference": [
                "Executive Summary",
                "Session Commands",
                "Documentation Management",
                "Quality Assurance"
            ]
        }
        
        # Cross-reference patterns
        self.reference_patterns = {
            "session_links": r'\[Session #(\d+)\]',
            "correlation_tags": r'\[S(\d+)-([A-Z]+)-([a-zA-Z-]+)\]',
            "file_references": r'`([^`]+\.md)`',
            "code_references": r'`([^`]+\.py)`',
            "section_links": r'#([a-zA-Z0-9-]+)'
        }
    
    def validate_session_documentation(self, 
                                     documentation: Dict[str, str],
                                     level: ValidationLevel = ValidationLevel.STANDARD) -> ValidationResult:
        """Validate complete session documentation"""
        
        start_time = time.time()
        issues = []
        category_scores = {}
        
        # 1. Template completeness validation
        template_score, template_issues = self._validate_template_completeness(documentation)
        category_scores["template_completeness"] = template_score
        issues.extend(template_issues)
        
        # 2. Cross-reference integrity validation
        ref_score, ref_issues = self._validate_cross_reference_integrity(documentation)
        category_scores["cross_reference_integrity"] = ref_score
        issues.extend(ref_issues)
        
        # 3. Content quality validation
        content_score, content_issues = self._validate_content_quality(documentation)
        category_scores["content_quality"] = content_score
        issues.extend(content_issues)
        
        # 4. Metric accuracy validation
        metric_score, metric_issues = self._validate_metric_accuracy(documentation)
        category_scores["metric_accuracy"] = metric_score
        issues.extend(metric_issues)
        
        # 5. Consistency validation
        consistency_score, consistency_issues = self._validate_consistency(documentation)
        category_scores["consistency"] = consistency_score
        issues.extend(consistency_issues)
        
        # Calculate overall score
        overall_score = sum(category_scores.values()) / len(category_scores)
        
        # Check against thresholds
        thresholds = self.thresholds[level]
        passed = overall_score >= thresholds["overall_minimum"]
        
        # Generate recommendations
        recommendations = self._generate_recommendations(category_scores, issues, level)
        
        execution_time = (time.time() - start_time) * 1000
        
        return ValidationResult(
            overall_score=overall_score,
            category_scores=category_scores,
            issues=issues,
            passed=passed,
            execution_time_ms=execution_time,
            recommendations=recommendations
        )
    
    def _validate_template_completeness(self, documentation: Dict[str, str]) -> Tuple[float, List[ValidationIssue]]:
        """Validate template section completeness"""
        issues = []
        scores = []
        
        # Check CLAUDE.md section
        claude_content = documentation.get("claude_md_section", "")
        if claude_content:
            required = self.required_sections["claude_md"]
            present = sum(1 for section in required if section in claude_content)
            score = (present / len(required)) * 100
            scores.append(score)
            
            if score < 85:
                missing = [s for s in required if s not in claude_content]
                issues.append(ValidationIssue(
                    category="template_completeness",
                    severity=ValidationSeverity.ERROR,
                    message=f"CLAUDE.md section missing required sections: {missing}",
                    suggestion="Add all required template sections"
                ))
        else:
            issues.append(ValidationIssue(
                category="template_completeness",
                severity=ValidationSeverity.CRITICAL,
                message="CLAUDE.md section content is missing",
                suggestion="Generate CLAUDE.md section content"
            ))
            scores.append(0)
        
        # Check session summary
        summary_content = documentation.get("session_summary", "")
        if summary_content:
            required = self.required_sections["session_summary"]
            present = sum(1 for section in required if section in summary_content)
            score = (present / len(required)) * 100
            scores.append(score)
            
            if score < 85:
                missing = [s for s in required if s not in summary_content]
                issues.append(ValidationIssue(
                    category="template_completeness",
                    severity=ValidationSeverity.ERROR,
                    message=f"Session summary missing required sections: {missing}",
                    suggestion="Add all required session summary sections"
                ))
        else:
            issues.append(ValidationIssue(
                category="template_completeness",
                severity=ValidationSeverity.CRITICAL,
                message="Session summary content is missing",
                suggestion="Generate session summary content"
            ))
            scores.append(0)
        
        return sum(scores) / len(scores) if scores else 0, issues
    
    def _validate_cross_reference_integrity(self, documentation: Dict[str, str]) -> Tuple[float, List[ValidationIssue]]:
        """Validate cross-reference integrity"""
        issues = []
        total_references = 0
        valid_references = 0
        
        for doc_type, content in documentation.items():
            if not content:
                continue
                
            # Check session links
            session_links = re.findall(self.reference_patterns["session_links"], content)
            for session_num in session_links:
                total_references += 1
                # Validate session exists (simplified check)
                if int(session_num) <= 10:  # Assume sessions 1-10 are valid range
                    valid_references += 1
                else:
                    issues.append(ValidationIssue(
                        category="cross_reference_integrity",
                        severity=ValidationSeverity.WARNING,
                        message=f"Invalid session reference: Session #{session_num}",
                        location=doc_type,
                        suggestion="Verify session number exists"
                    ))
            
            # Check correlation tags
            correlation_tags = re.findall(self.reference_patterns["correlation_tags"], content)
            for session_num, category, component in correlation_tags:
                total_references += 1
                # Validate tag structure
                if category in ["ARCH", "PERF", "SEC", "TEST", "AUTO", "QUAL"]:
                    valid_references += 1
                else:
                    issues.append(ValidationIssue(
                        category="cross_reference_integrity",
                        severity=ValidationSeverity.WARNING,
                        message=f"Invalid correlation tag category: {category}",
                        location=doc_type,
                        suggestion="Use standard correlation tag categories"
                    ))
            
            # Check file references
            file_refs = re.findall(self.reference_patterns["file_references"], content)
            for file_ref in file_refs:
                total_references += 1
                file_path = self.project_root / file_ref
                if file_path.exists() or file_ref in ["CLAUDE.md", "CLAUDE_QUICK_REFER.md", "SESSION_TRANSITION_PROTOCOL.md"]:
                    valid_references += 1
                else:
                    issues.append(ValidationIssue(
                        category="cross_reference_integrity",
                        severity=ValidationSeverity.ERROR,
                        message=f"Broken file reference: {file_ref}",
                        location=doc_type,
                        suggestion="Verify file exists or update reference"
                    ))
        
        # Calculate integrity score
        integrity_score = (valid_references / total_references * 100) if total_references > 0 else 100
        
        return integrity_score, issues
    
    def _validate_content_quality(self, documentation: Dict[str, str]) -> Tuple[float, List[ValidationIssue]]:
        """Validate content quality and depth"""
        issues = []
        scores = []
        
        for doc_type, content in documentation.items():
            if not content:
                continue
                
            # Check content length (minimum substance)
            if len(content) < 1000:
                issues.append(ValidationIssue(
                    category="content_quality",
                    severity=ValidationSeverity.WARNING,
                    message=f"{doc_type} content appears too brief ({len(content)} chars)",
                    suggestion="Add more detailed content"
                ))
                scores.append(60)
            else:
                scores.append(90)
            
            # Check for placeholder text
            placeholders = ["TODO", "[PLACEHOLDER]", "TBD", "[TO BE DETERMINED]"]
            placeholder_count = sum(1 for p in placeholders if p in content.upper())
            if placeholder_count > 0:
                issues.append(ValidationIssue(
                    category="content_quality",
                    severity=ValidationSeverity.WARNING,
                    message=f"{doc_type} contains {placeholder_count} placeholder(s)",
                    suggestion="Replace placeholders with actual content"
                ))
                scores.append(max(70, 90 - placeholder_count * 10))
            
            # Check for metrics and specific data
            has_metrics = bool(re.search(r'\d+(?:\.\d+)?%|\d+(?:\.\d+)?\s*ms|\d+(?:\.\d+)?\s*seconds', content))
            if not has_metrics:
                issues.append(ValidationIssue(
                    category="content_quality",
                    severity=ValidationSeverity.INFO,
                    message=f"{doc_type} lacks specific performance metrics",
                    suggestion="Add quantifiable metrics and measurements"
                ))
                scores.append(80)
            else:
                scores.append(95)
        
        return sum(scores) / len(scores) if scores else 0, issues
    
    def _validate_metric_accuracy(self, documentation: Dict[str, str]) -> Tuple[float, List[ValidationIssue]]:
        """Validate accuracy and consistency of metrics"""
        issues = []
        scores = []
        
        # Extract all metrics from documentation
        metrics = {}
        for doc_type, content in documentation.items():
            if not content:
                continue
                
            # Find percentage metrics
            percentages = re.findall(r'(\w+[^:]*?):\s*(\d+(?:\.\d+)?%)', content)
            for metric_name, value in percentages:
                metric_key = metric_name.strip().lower()
                if metric_key in metrics and metrics[metric_key] != value:
                    issues.append(ValidationIssue(
                        category="metric_accuracy",
                        severity=ValidationSeverity.ERROR,
                        message=f"Inconsistent metric values for '{metric_name}': {metrics[metric_key]} vs {value}",
                        location=doc_type,
                        suggestion="Ensure consistent metric values across all documentation"
                    ))
                    scores.append(60)
                else:
                    metrics[metric_key] = value
            
            # Find timing metrics
            timings = re.findall(r'(\w+[^:]*?):\s*<?\s*(\d+(?:\.\d+)?)\s*(ms|seconds?)', content)
            for metric_name, value, unit in timings:
                # Validate realistic timing values
                value_ms = float(value) if unit == 'ms' else float(value) * 1000
                if value_ms > 10000:  # > 10 seconds seems unrealistic for most operations
                    issues.append(ValidationIssue(
                        category="metric_accuracy",
                        severity=ValidationSeverity.WARNING,
                        message=f"Unusually high timing metric: {metric_name} = {value} {unit}",
                        location=doc_type,
                        suggestion="Verify timing measurement accuracy"
                    ))
                    scores.append(70)
                else:
                    scores.append(95)
        
        # Check for presence of key performance indicators
        required_metrics = ["processing time", "success rate", "coverage", "accuracy"]
        found_metrics = 0
        for doc_type, content in documentation.items():
            for metric in required_metrics:
                if metric.lower() in content.lower():
                    found_metrics += 1
                    break
        
        metric_coverage = (found_metrics / len(required_metrics)) * 100
        scores.append(metric_coverage)
        
        if metric_coverage < 50:
            issues.append(ValidationIssue(
                category="metric_accuracy",
                severity=ValidationSeverity.WARNING,
                message="Low coverage of key performance metrics",
                suggestion="Include more quantifiable performance measurements"
            ))
        
        return sum(scores) / len(scores) if scores else 100, issues
    
    def _validate_consistency(self, documentation: Dict[str, str]) -> Tuple[float, List[ValidationIssue]]:
        """Validate consistency across documentation"""
        issues = []
        scores = []
        
        # Check session number consistency
        session_numbers = set()
        for content in documentation.values():
            if content:
                numbers = re.findall(r'SESSION #(\d+)', content)
                session_numbers.update(numbers)
        
        if len(session_numbers) > 1:
            issues.append(ValidationIssue(
                category="consistency",
                severity=ValidationSeverity.ERROR,
                message=f"Inconsistent session numbers found: {session_numbers}",
                suggestion="Ensure consistent session numbering throughout documentation"
            ))
            scores.append(50)
        else:
            scores.append(100)
        
        # Check date consistency
        dates = set()
        for content in documentation.values():
            if content:
                found_dates = re.findall(r'(\d{4}-\d{2}-\d{2})', content)
                dates.update(found_dates)
        
        if len(dates) > 1:
            issues.append(ValidationIssue(
                category="consistency",
                severity=ValidationSeverity.WARNING,
                message=f"Multiple dates found in documentation: {dates}",
                suggestion="Verify date consistency or document date changes"
            ))
            scores.append(80)
        else:
            scores.append(100)
        
        # Check terminology consistency
        terminology_variations = {
            "microbot": ["mikrobot", "microbot", "micro-bot"],
            "session": ["session", "context window", "development session"],
            "validation": ["validation", "verification", "checking"]
        }
        
        for standard_term, variations in terminology_variations.items():
            found_variations = set()
            for content in documentation.values():
                if content:
                    for variation in variations:
                        if variation.lower() in content.lower():
                            found_variations.add(variation)
            
            if len(found_variations) > 2:  # Allow some variation
                issues.append(ValidationIssue(
                    category="consistency",
                    severity=ValidationSeverity.INFO,
                    message=f"Multiple terminology variations for '{standard_term}': {found_variations}",
                    suggestion=f"Consider standardizing on one term for '{standard_term}'"
                ))
                scores.append(85)
            else:
                scores.append(100)
        
        return sum(scores) / len(scores) if scores else 100, issues
    
    def _generate_recommendations(self, 
                                category_scores: Dict[str, float], 
                                issues: List[ValidationIssue],
                                level: ValidationLevel) -> List[str]:
        """Generate improvement recommendations"""
        recommendations = []
        thresholds = self.thresholds[level]
        
        # Category-specific recommendations
        for category, score in category_scores.items():
            threshold = thresholds.get(category, 80.0)
            if score < threshold:
                if category == "template_completeness":
                    recommendations.append("Add missing template sections to improve completeness")
                elif category == "cross_reference_integrity":
                    recommendations.append("Fix broken links and verify all cross-references")
                elif category == "content_quality":
                    recommendations.append("Enhance content depth and add more specific details")
                elif category == "metric_accuracy":
                    recommendations.append("Include more quantifiable metrics and verify accuracy")
                elif category == "consistency":
                    recommendations.append("Standardize terminology and formatting across documents")
        
        # Issue-based recommendations
        critical_issues = [i for i in issues if i.severity == ValidationSeverity.CRITICAL]
        error_issues = [i for i in issues if i.severity == ValidationSeverity.ERROR]
        
        if critical_issues:
            recommendations.append("Address critical issues immediately before proceeding")
        if error_issues:
            recommendations.append("Fix error-level issues to improve documentation quality")
        
        # High-level recommendations
        if category_scores.get("overall", 0) < thresholds["overall_minimum"]:
            recommendations.append("Overall quality below target - focus on completeness and accuracy")
        
        return recommendations
    
    def validate_existing_files(self, level: ValidationLevel = ValidationLevel.STANDARD) -> ValidationResult:
        """Validate existing project documentation files"""
        
        documentation = {}
        
        # Load existing files
        claude_md_path = self.project_root / "CLAUDE.md"
        if claude_md_path.exists():
            documentation["claude_md"] = claude_md_path.read_text(encoding='utf-8')
        
        quick_ref_path = self.project_root / "CLAUDE_QUICK_REFER.md"
        if quick_ref_path.exists():
            documentation["quick_reference"] = quick_ref_path.read_text(encoding='utf-8')
        
        session_summaries = list(self.project_root.glob("SESSION_*_SUMMARY.md"))
        for session_file in session_summaries:
            key = f"session_summary_{session_file.stem}"
            documentation[key] = session_file.read_text(encoding='utf-8')
        
        return self.validate_session_documentation(documentation, level)
    
    def generate_quality_report(self, result: ValidationResult) -> str:
        """Generate human-readable quality report"""
        
        report = f"""# CHART Session Documentation Quality Report

## TARGET Overall Assessment
**Quality Score**: {result.overall_score:.1f}% | **Status**: {'OK PASSED' if result.passed else 'ERROR FAILED'}
**Validation Time**: {result.execution_time_ms:.1f}ms

## GRAPH_UP Category Breakdown
"""
        
        for category, score in result.category_scores.items():
            status = "OK" if score >= 80 else "WARNING" if score >= 60 else "ERROR"
            report += f"- **{category.replace('_', ' ').title()}**: {score:.1f}% {status}\n"
        
        if result.issues:
            report += f"\n##  Issues Found ({len(result.issues)})\n"
            
            # Group issues by severity
            by_severity = {}
            for issue in result.issues:
                if issue.severity not in by_severity:
                    by_severity[issue.severity] = []
                by_severity[issue.severity].append(issue)
            
            for severity in [ValidationSeverity.CRITICAL, ValidationSeverity.ERROR, ValidationSeverity.WARNING, ValidationSeverity.INFO]:
                if severity in by_severity:
                    icon = {"CRITICAL": "", "ERROR": "ERROR", "WARNING": "WARNING", "INFO": ""}[severity.name]
                    report += f"\n### {icon} {severity.name.title()} ({len(by_severity[severity])})\n"
                    for issue in by_severity[severity]:
                        report += f"- **{issue.category}**: {issue.message}\n"
                        if issue.suggestion:
                            report += f"   *{issue.suggestion}*\n"
        
        if result.recommendations:
            report += f"\n##  Recommendations\n"
            for i, rec in enumerate(result.recommendations, 1):
                report += f"{i}. {rec}\n"
        
        report += f"\n## OK Quality Assurance Summary\n"
        report += f"- Template completeness: {result.category_scores.get('template_completeness', 0):.1f}%\n"
        report += f"- Cross-reference integrity: {result.category_scores.get('cross_reference_integrity', 0):.1f}%\n"
        report += f"- Content quality: {result.category_scores.get('content_quality', 0):.1f}%\n"
        report += f"- Metric accuracy: {result.category_scores.get('metric_accuracy', 0):.1f}%\n"
        report += f"- Consistency: {result.category_scores.get('consistency', 0):.1f}%\n"
        
        return report


def main():
    """Command-line interface for quality validation"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Session Documentation Quality Validator")
    parser.add_argument("--level", type=str, default="standard", 
                       choices=["minimal", "standard", "comprehensive", "enterprise"],
                       help="Validation level")
    parser.add_argument("--report", action="store_true", help="Generate detailed quality report")
    parser.add_argument("--output", type=str, help="Output file for report")
    
    args = parser.parse_args()
    
    validator = SessionQualityValidator()
    level = ValidationLevel(args.level)
    
    print(f" Running {level.value} quality validation...")
    result = validator.validate_existing_files(level)
    
    print(f"\nCHART Validation Results:")
    print(f"Overall Score: {result.overall_score:.1f}%")
    print(f"Status: {'OK PASSED' if result.passed else 'ERROR FAILED'}")
    print(f"Issues Found: {len(result.issues)}")
    print(f"Execution Time: {result.execution_time_ms:.1f}ms")
    
    if args.report:
        report = validator.generate_quality_report(result)
        if args.output:
            Path(args.output).write_text(report, encoding='utf-8')
            print(f" Quality report saved to: {args.output}")
        else:
            print("\n" + report)


if __name__ == "__main__":
    # Initialize ASCII-only output
    sys.stdout.reconfigure(encoding='utf-8', errors='ignore')
    sys.stderr.reconfigure(encoding='utf-8', errors='ignore')

    main()