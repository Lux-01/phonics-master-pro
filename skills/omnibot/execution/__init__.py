"""
Execution Module - Phase 3 Core Component
End-to-end job completion with 8-step workflow and human checkpoints.

ACA Implementation:
- Requirements Analysis ✓
- Architecture Design ✓
- Data Flow Planning ✓
- Edge Case Handling ✓
- Checkpoint Integration ✓
- Error Recovery ✓
- Testing Strategy ✓
"""

from .job_workflow import (
    JobExecutionOrchestrator,
    ExecutionPhase,
    Checkpoint,
    CheckpointStatus,
    TaskItem
)
from .requirements_parser import (
    RequirementsParser,
    ParsedRequirement,
    ParsedProject,
    AmbiguityDetector,
    TechnologyExtractor,
    ScopeEstimator
)

__all__ = [
    # Job execution
    'JobExecutionOrchestrator',
    'ExecutionPhase',
    'Checkpoint',
    'CheckpointStatus',
    'TaskItem',
    # Requirements parsing
    'RequirementsParser',
    'ParsedRequirement',
    'ParsedProject',
    'AmbiguityDetector',
    'TechnologyExtractor',
    'ScopeEstimator'
]


class JobExecutor:
    """
    Unified job execution interface combining all workflow capabilities.
    
    Usage:
        executor = JobExecutor()
        job = executor.start_job("project_123", requirements, "Client Name")
        
        # Execute through checkpoints
        for phase in ExecutionPhase:
            result = executor.execute_step(job['job_id'], phase)
            if result.get('checkpoint'):
                # Wait for human approval
                pass
    """
    
    def __init__(self, omnibot=None):
        self.orchestrator = JobExecutionOrchestrator(omnibot)
        self.parser = RequirementsParser()
    
    def start_job(self, job_id: str, requirements: str, client: str) -> dict:
        """Start a new job execution workflow."""
        return self.orchestrator.start_job(job_id, requirements, client)
    
    def execute_step(self, job_id: str, phase: ExecutionPhase, approval: bool = False):
        """
        Execute a specific workflow step with checkpoint handling.
        
        Args:
            job_id: Job identifier
            phase: Phase to execute
            approval: Whether human approval has been given (for checkpoint phases)
            
        Returns:
            Execution result with checkpoint status if needed
        """
        # Check for existing checkpoints
        job = self.orchestrator.active_jobs.get(job_id)
        if not job:
            return {'error': 'Job not found'}
        
        # Phases requiring checkpoints
        checkpoint_phases = [
            ExecutionPhase.REQUIREMENTS,
            ExecutionPhase.DESIGN,
            ExecutionPhase.DELIVERY
        ]
        
        if phase in checkpoint_phases and not approval:
            # Request checkpoint
            checkpoint = self.orchestrator.checkpoint_request_approval(
                job_id, phase, job.get('artifacts', [])
            )
            return {
                'checkpoint': True,
                'phase': phase.value,
                'message': f'[CHECKPOINT] Approval required for {phase.value}',
                'description': checkpoint.description,
                'artifacts': checkpoint.artifacts
            }
        
        # Execute the phase
        return self.orchestrator.execute_phase(job_id, phase)
    
    def handle_client_feedback(self, job_id: str, feedback: str):
        """Process client feedback and update job tasks."""
        return self.orchestrator.handle_client_feedback(job_id, feedback)
    
    def complete_job(self, job_id: str, final_approval: bool = False):
        """
        Complete a job with final checkpoint.
        
        Args:
            job_id: Job identifier
            final_approval: Whether final human approval given
            
        Returns:
            Completion status
        """
        if not final_approval:
            return {
                'checkpoint': True,
                'phase': 'final_delivery',
                'message': '[CHECKPOINT] Final approval required before delivery',
                'action_required': 'Approve final delivery?'
            }
        
        return self.orchestrator.mark_job_complete(job_id)
    
    def get_job_status(self, job_id: str):
        """Get current job execution status."""
        return self.orchestrator.get_job_status(job_id)
    
    def list_jobs(self):
        """List all active jobs."""
        return self.orchestrator.list_jobs()
