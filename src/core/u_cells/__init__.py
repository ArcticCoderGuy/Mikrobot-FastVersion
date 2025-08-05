"""
U-Cell Architecture for Mikrobot FastVersion
FoxBox Framework™ Standard Implementation

The 5 deterministic U-Cells:
1. Signal Validation
2. ML Analysis
3. Risk Engine
4. Trade Execution
5. Monitoring & Control
"""

from typing import Dict, Any, Optional
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class CellInput:
    """Standard input format for U-Cell processing"""
    timestamp: datetime
    data: Dict[str, Any]
    metadata: Dict[str, Any]
    previous_cell: Optional[str] = None
    trace_id: Optional[str] = None


@dataclass
class CellOutput:
    """Standard output format for U-Cell processing"""
    timestamp: datetime
    status: str  # 'success', 'failed', 'rejected'
    data: Dict[str, Any]
    next_cell: Optional[str] = None
    trace_id: Optional[str] = None
    errors: Optional[list] = None


class UCell(ABC):
    """Base U-Cell interface following FoxBox deterministic principles"""
    
    def __init__(self, cell_id: str, name: str):
        self.cell_id = cell_id
        self.name = name
        self.is_active = True
        self.metrics = {
            'processed': 0,
            'success': 0,
            'failed': 0,
            'rejected': 0
        }
    
    @abstractmethod
    def validate_input(self, cell_input: CellInput) -> bool:
        """Validate input before processing"""
        pass
    
    @abstractmethod
    def process(self, cell_input: CellInput) -> CellOutput:
        """Process input and return output"""
        pass
    
    def execute(self, cell_input: CellInput) -> CellOutput:
        """Execute cell with validation and metrics"""
        self.metrics['processed'] += 1
        
        try:
            # Validate input
            if not self.validate_input(cell_input):
                self.metrics['rejected'] += 1
                return CellOutput(
                    timestamp=datetime.utcnow(),
                    status='rejected',
                    data={'reason': 'Invalid input'},
                    trace_id=cell_input.trace_id,
                    errors=['Input validation failed']
                )
            
            # Process
            output = self.process(cell_input)
            
            # Update metrics
            if output.status == 'success':
                self.metrics['success'] += 1
            else:
                self.metrics['failed'] += 1
            
            return output
            
        except Exception as e:
            logger.error(f"Cell {self.name} error: {str(e)}")
            self.metrics['failed'] += 1
            return CellOutput(
                timestamp=datetime.utcnow(),
                status='failed',
                data={},
                trace_id=cell_input.trace_id,
                errors=[str(e)]
            )
    
    def get_metrics(self) -> Dict[str, Any]:
        """Return cell performance metrics"""
        total = self.metrics['processed']
        if total == 0:
            return self.metrics
        
        return {
            **self.metrics,
            'success_rate': self.metrics['success'] / total,
            'failure_rate': self.metrics['failed'] / total,
            'rejection_rate': self.metrics['rejected'] / total
        }