#!/usr/bin/env python3
"""
Job Execution Orchestrator - End-to-end job completion.

Workflow:
1. Parses requirements → Creates tasks → Estimates time
2. Researches domain → Gathers best practices
3. Designs solution → Creates mockups/specs
4. Implements → Uses ACA methodology
5. Self-tests → Fixes bugs
6. Documents → Creates README/USAGE
7. Package → Zips deliverables
8. Queues for human review
9. Delivers → Handles client communication
10. Invoice → Tracks payment

HUMAN CHECKPOINTS at:
- After requirements parsing (confirm understanding)
- After design phase (approve approach)
- After implementation (code review)
- Before delivery (final approval)
"""

import json
import logging
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import shutil


class ExecutionPhase(Enum):
    """Phases of job execution."""
    REQUIREMENTS = "requirements"
    RESEARCH = "research"
    DESIGN = "design"
    IMPLEMENTATION = "implementation"
    TESTING = "testing"
    DOCUMENTATION = "documentation"
    PACKAGING = "packaging"
    REVIEW = "review"
    DELIVERY = "delivery"
    INVOICING = "invoicing"


class CheckpointStatus(Enum):
    """Status of checkpoint."""
    PENDING = "pending"
    WAITING_APPROVAL = "waiting_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    MODIFIED = "modified"


@dataclass
class Checkpoint:
    """Human approval checkpoint."""
    phase: ExecutionPhase
    status: CheckpointStatus
    description: str
    artifacts: List[str] = field(default_factory=list)
    notes: str = ""
    requested_at: Optional[str] = None
    resolved_at: Optional[str] = None


@dataclass
class TaskItem:
    """A task in the workflow."""
    task_id: str
    description: str
    phase: ExecutionPhase
    estimated_hours: float
    completed: bool = False
    actual_hours: float = 0.0


class JobExecutionOrchestrator:
    """
    Orchestrates complete job execution from start to delivery.
    """
    
    def __init__(self, omnibot=None, data_dir: Optional[str] = None):
        self.logger = logging.getLogger("Omnibot.JobExecutionOrchestrator")
        self.omnibot = omnibot
        
        # Storage
        self.data_dir = Path(data_dir) if data_dir else Path(__file__).parent / "execution_data"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Active jobs
        self.active_jobs: Dict[str, Dict] = {}
        self.jobs_file = self.data_dir / "active_jobs.json"
        self._load_jobs()
        
        # Outputs
        self.output_dir = self.data_dir / "outputs"
        self.output_dir.mkdir(exist_ok=True)
        
        self.logger.info("JobExecutionOrchestrator initialized")
    
    def _load_jobs(self):
        """Load active jobs."""
        if self.jobs_file.exists():
            try:
                self.active_jobs = json.loads(self.jobs_file.read_text())
            except Exception as e:
                self.logger.error(f"Failed to load jobs: {e}")
    
    def _save_jobs(self):
        """Save active jobs."""
        try:
            self.jobs_file.write_text(json.dumps(self.active_jobs, indent=2, default=str))
        except Exception as e:
            self.logger.error(f"Failed to save jobs: {e}")
    
    def start_job(self, job_id: str, requirements: str, client: str) -> Dict:
        """
        Start a new job execution.
        
        Args:
            job_id: Job identifier
            requirements: Client requirements
            client: Client name
            
        Returns:
            Job context
        """
        self.logger.info(f"Starting job {job_id} for {client}")
        
        job = {
            "job_id": job_id,
            "client": client,
            "requirements_text": requirements,
            "status": ExecutionPhase.REQUIREMENTS.value,
            "started_at": datetime.now().isoformat(),
            "tasks": [],
            "checkpoints": [],
            "artifacts": [],
            "output_dir": str(self.output_dir / job_id)
        }
        
        # Create output directory
        Path(job["output_dir"]).mkdir(parents=True, exist_ok=True)
        
        self.active_jobs[job_id] = job
        self._save_jobs()
        
        # Step 1: Parse requirements
        self._parse_requirements(job_id)
        
        return job
    
    def _parse_requirements(self, job_id: str) -> Dict:
        """Parse job requirements into tasks."""
        job = self.active_jobs.get(job_id)
        if not job:
            return {"error": "Job not found"}
        
        self.logger.info(f"Parsing requirements for {job_id}")
        
        # Parse requirements (use ACA or simple extraction)
        requirements = job["requirements_text"]
        
        # Create initial checkpoint
        checkpoint = Checkpoint(
            phase=ExecutionPhase.REQUIREMENTS,
            status=CheckpointStatus.WAITING_APPROVAL,
            description="Parse requirements and create task breakdown",
            artifacts=[],
            requested_at=datetime.now().isoformat()
        )
        
        job["checkpoints"].append({
            "phase": checkpoint.phase.value,
            "status": checkpoint.status.value,
            "description": checkpoint.description,
            "requested_at": checkpoint.requested_at
        })
        
        # Create tasks based on requirements
        tasks = self._generate_tasks_from_requirements(requirements)
        job["tasks"] = [t.__dict__ for t in tasks]
        
        self._save_jobs()
        
        return {
            "job_id": job_id,
            "tasks_created": len(tasks),
            "checkpoint": f"Waiting approval: {checkpoint.description}"
        }
    
    def _generate_tasks_from_requirements(self, requirements: str) -> List[TaskItem]:
        """Generate task items from requirements."""
        tasks = []
        
        # Simple parsing - in real implementation would use NLP
        if "web" in requirements.lower() or "website" in requirements.lower():
            tasks.append(TaskItem(
                task_id="design_ux",
                description="Design UX/UI mockups",
                phase=ExecutionPhase.DESIGN,
                estimated_hours=8
            ))
            tasks.append(TaskItem(
                task_id="frontend_dev",
                description="Develop frontend interface",
                phase=ExecutionPhase.IMPLEMENTATION,
                estimated_hours=16
            ))
        
        if "backend" in requirements.lower() or "api" in requirements.lower():
            tasks.append(TaskItem(
                task_id="api_design",
                description="Design API endpoints",
                phase=ExecutionPhase.DESIGN,
                estimated_hours=4
            ))
            tasks.append(TaskItem(
                task_id="backend_dev",
                description="Develop backend API",
                phase=ExecutionPhase.IMPLEMENTATION,
                estimated_hours=20
            ))
        
        # Always add documentation and testing
        tasks.append(TaskItem(
            task_id="testing",
            description="Write and run tests",
            phase=ExecutionPhase.TESTING,
            estimated_hours=4
        ))
        tasks.append(TaskItem(
            task_id="documentation",
            description="Create documentation",
            phase=ExecutionPhase.DOCUMENTATION,
            estimated_hours=2
        ))
        
        return tasks
    
    def execute_phase(self, job_id: str, phase: ExecutionPhase) -> Dict:
        """
        Execute a specific phase.
        
        Args:
            job_id: Job identifier
            phase: Phase to execute
            
        Returns:
            Execution result
        """
        self.logger.info(f"Executing phase {phase.value} for {job_id}")
        
        job = self.active_jobs.get(job_id)
        if not job:
            return {"error": "Job not found"}
        
        result = {"phase": phase.value}
        
        if phase == ExecutionPhase.RESEARCH:
            result["research"] = self._do_research(job)
        elif phase == ExecutionPhase.DESIGN:
            result["design"] = self._do_design(job)
        elif phase == ExecutionPhase.IMPLEMENTATION:
            result["implementation"] = self._do_implementation(job)
        elif phase == ExecutionPhase.TESTING:
            result["testing"] = self._do_testing(job)
        elif phase == ExecutionPhase.DOCUMENTATION:
            result["docs"] = self._do_documentation(job)
        elif phase == ExecutionPhase.PACKAGING:
            result["package"] = self._do_packaging(job)
        
        job["status"] = phase.value
        self._save_jobs()
        
        return result
    
    def _do_research(self, job: Dict) -> Dict:
        """Research phase - gather best practices."""
        self.logger.info("Researching best practices...")
        
        # Would use omnibot research capabilities
        research_results = {
            "patterns_found": 3,
            "examples_collected": 5,
            "technology_stack_recommended": ["Python", "FastAPI", "React"]
        }
        
        # Save research
        research_file = Path(job["output_dir"]) / "research.json"
        research_file.write_text(json.dumps(research_results, indent=2))
        
        return research_results
    
    def _do_design(self, job: Dict) -> Dict:
        """Design phase - create specifications."""
        self.logger.info("Creating design specifications...")
        
        design = {
            "architecture": "recommended_architecture.md",
            "data_model": "data_model.md",
            "api_spec": "api_specification.md"
        }
        
        # Create design documents
        for doc_name in design.values():
            doc_path = Path(job["output_dir"]) / doc_name
            doc_path.write_text(f"# {doc_name.replace('_', ' ').title()}\n\n(TBD - Design phase)\n")
        
        return {"design documents created": len(design)}
    
    def _do_implementation(self, job: Dict) -> Dict:
        """Implementation phase - write code."""
        self.logger.info("Implementing solution...")
        
        # Mark tasks as ready for implementation
        impl_dir = Path(job["output_dir"]) / "src"
        impl_dir.mkdir(exist_ok=True)
        
        # Would use ACA methodology here
        # For now, create placeholder structure
        (impl_dir / "main.py").touch()
        (impl_dir / "requirements.txt").touch()
        
        return {"files_created": 2, "implementation_dir": str(impl_dir)}
    
    def _do_testing(self, job: Dict) -> Dict:
        """Testing phase - validate implementation."""
        self.logger.info("Running tests...")
        
        tests_dir = Path(job["output_dir"]) / "tests"
        tests_dir.mkdir(exist_ok=True)
        
        test_file = tests_dir / "test_main.py"
        test_file.write_text("# Test suite\n")
        
        return {"tests_written": 1}
    
    def _do_documentation(self, job: Dict) -> Dict:
        """Documentation phase - create docs."""
        self.logger.info("Creating documentation...")
        
        docs_dir = Path(job["output_dir"]) / "docs"
        docs_dir.mkdir(exist_ok=True)
        
        # README
        readme = docs_dir / "README.md"
        readme.write_text(f"""# {job['job_id']}

## Overview
(Client project)

## Installation
```bash
pip install -r requirements.txt
```

## Usage
See USAGE.md

## License
(Client specific)
""")
        
        # USAGE
        usage = docs_dir / "USAGE.md"
        usage.write_text("# Usage Guide\n\n(Detailed usage instructions)\n")
        
        return {"docs_created": 2, "docs_dir": str(docs_dir)}
    
    def _do_packaging(self, job: Dict) -> Dict:
        """Packaging phase - prepare deliverables."""
        self.logger.info("Packaging deliverables...")
        
        output_dir = Path(job["output_dir"])
        zip_path = self.data_dir / f"{job['job_id']}_deliverable.zip"
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            for file in output_dir.rglob("*"):
                if file.is_file():
                    zf.write(file, arcname=file.relative_to(output_dir))
        
        job["artifacts"].append(str(zip_path))
        self._save_jobs()
        
        return {"package": str(zip_path), "files_included": len(list(output_dir.rglob("*")))}
    
    def checkpoint_request_approval(self, job_id: str, phase: ExecutionPhase,
                                  artifacts: List[str]) -> Checkpoint:
        """
        Request human approval at a checkpoint.
        
        Args:
            job_id: Job identifier
            phase: Current phase
            artifacts: List of artifact files
            
        Returns:
            Checkpoint
        """
        checkpoint = Checkpoint(
            phase=phase,
            status=CheckpointStatus.WAITING_APPROVAL,
            description=f"Approval needed for {phase.value} phase",
            artifacts=artifacts,
            requested_at=datetime.now().isoformat()
        )
        
        job = self.active_jobs.get(job_id)
        if job:
            job["checkpoints"].append({
                "phase": phase.value,
                "status": checkpoint.status.value,
                "description": checkpoint.description,
                "artifacts": artifacts,
                "requested_at": checkpoint.requested_at
            })
            self._save_jobs()
        
        self.logger.info(f"Checkpoint created for {job_id}: {phase.value}")
        return checkpoint
    
    def resolve_checkpoint(self, job_id: str, phase: ExecutionPhase,
                          approval: str, notes: str = "") -> bool:
        """
        Resolve a checkpoint with approval decision.
        
        Args:
            job_id: Job identifier
            phase: Phase to resolve
            approval: "approved", "rejected", or "modified"
            notes: Additional notes
            
        Returns:
            True if resolved
        """
        job = self.active_jobs.get(job_id)
        if not job:
            return False
        
        for cp in job["checkpoints"]:
            if cp["phase"] == phase.value:
                cp["status"] = approval
                cp["notes"] = notes
                cp["resolved_at"] = datetime.now().isoformat()
                break
        
        self._save_jobs()
        self.logger.info(f"Checkpoint {phase.value} {approval} for {job_id}")
        return True
    
    def get_job_status(self, job_id: str) -> Dict:
        """Get current job status."""
        job = self.active_jobs.get(job_id)
        if not job:
            return {"error": "Job not found"}
        
        completed = sum(1 for t in job.get("tasks", []) if t.get("completed"))
        total = len(job.get("tasks", []))
        
        return {
            "job_id": job_id,
            "client": job.get("client"),
            "status": job.get("status"),
            "started_at": job.get("started_at"),
            "progress": f"{completed}/{total} tasks",
            "progress_percent": (completed / total * 100) if total > 0 else 0,
            "pending_checkpoints": len([c for c in job.get("checkpoints", []) 
                                      if c.get("status") == "waiting_approval"])
        }
    
    def list_jobs(self) -> List[Dict]:
        """List all active jobs."""
        return [
            {
                "job_id": jid,
                "client": job.get("client"),
                "status": job.get("status"),
                "started_at": job.get("started_at")
            }
            for jid, job in self.active_jobs.items()
        ]
    
    def mark_job_complete(self, job_id: str) -> Dict:
        """Mark a job as complete."""
        job = self.active_jobs.get(job_id)
        if job:
            job["status"] = "completed"
            job["completed_at"] = datetime.now().isoformat()
            self._save_jobs()
            
            return {
                "job_id": job_id,
                "status": "completed",
                "artifacts": job.get("artifacts", [])
            }
        
        return {"error": "Job not found"}
    
    def handle_client_feedback(self, job_id: str, feedback: str) -> Dict:
        """
        Process client feedback and adjust job accordingly.
        
        Args:
            job_id: Job identifier
            feedback: Client feedback text
            
        Returns:
            Feedback processing result
        """
        self.logger.info(f"Processing feedback for job {job_id}")
        
        job = self.active_jobs.get(job_id)
        if not job:
            return {"error": "Job not found"}
        
        # Analyze feedback for action items
        feedback_lower = feedback.lower()
        
        # Detect feedback type
        if any(word in feedback_lower for word in ['revision', 'change', 'update', 'modify', 'fix']):
            action_type = "revision"
        elif any(word in feedback_lower for word in ['approve', 'good', 'great', 'perfect', 'love']):
            action_type = "approval"
        else:
            action_type = "clarification"
        
        # Create feedback record
        feedback_record = {
            "received_at": datetime.now().isoformat(),
            "feedback": feedback[:500],
            "action_type": action_type,
            "processed": False
        }
        
        if "feedback" not in job:
            job["feedback"] = []
        job["feedback"].append(feedback_record)
        
        # Generate tasks based on feedback
        new_tasks = []
        if action_type == "revision":
            # Create revision tasks
            new_tasks.append({
                "task_id": f"revision_{len(job['feedback'])}",
                "description": f"Address client feedback: {feedback[:100]}...",
                "phase": ExecutionPhase.IMPLEMENTATION.value,
                "estimated_hours": 4,
                "completed": False,
                "from_feedback": True
            })
            job["status"] = ExecutionPhase.IMPLEMENTATION.value
        elif action_type == "approval":
            feedback_record["processed"] = True
            feedback_record["resolution"] = "Client approved - no action needed"
            job["status"] = ExecutionPhase.REVIEW.value
        else:
            # Clarification needed - move back to requirements
            new_tasks.append({
                "task_id": f"clarify_{len(job['feedback'])}",
                "description": "Clarify requirements with client",
                "phase": ExecutionPhase.REQUIREMENTS.value,
                "estimated_hours": 1,
                "completed": False,
                "from_feedback": True
            })
        
        job["tasks"].extend(new_tasks)
        self._save_jobs()
        
        return {
            "job_id": job_id,
            "action_type": action_type,
            "tasks_created": len(new_tasks),
            "new_status": job["status"],
            "message": f"Processed {action_type} feedback" if feedback else "No feedback provided"
        }