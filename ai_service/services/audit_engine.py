"""
Audit Engine - Creates and saves immutable audit records of all workflow
executions for compliance, debugging, and review.

Audit records are saved in JSON format under the tenant's subdirectory.
"""

import os
import json
import uuid
import time
from datetime import datetime, timedelta


class AuditEngine:
    """
    Manages immutable audit logging for the AI CFO Business Workflow Planner
    and Workflow Orchestrator.
    """

    def __init__(self, base_log_dir: str = "audit_logs"):
        self.base_log_dir = base_log_dir

    def create_record(
        self,
        tenant_id: str,
        original_prompt: str,
        detected_intent: str,
        planner_output: dict,
        validator_corrections: list,
        ai_model_used: str = "gemini-3.6-flash",
        ai_provider: str = "gemini"
    ) -> dict:
        """
        Initialize a new audit record for a workflow execution.
        """
        audit_id = str(uuid.uuid4())
        record = {
            "audit_id": audit_id,
            "tenant_id": tenant_id,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "original_prompt": original_prompt,
            "detected_intent": detected_intent,
            "planner_output": planner_output,
            "validator_corrections": validator_corrections,
            "step_results": [],
            "ai_model_used": ai_model_used,
            "ai_provider": ai_provider,
            "overall_confidence": 0.0,
            "workflow_state": "Draft",
            "prompt_version": "v1.0",
            "policy_version": "v1.0",
            "execution_duration_ms": 0,
            "llm_time_ms": 0,
            "user_approval": "pending",
            "rollback_status": "none",
            "rollback_details": None
        }
        self._write_record(tenant_id, audit_id, record)
        return record

    def update_step_results(
        self,
        tenant_id: str,
        audit_id: str,
        step_results: list,
        overall_confidence: float,
        workflow_state: str = None,
        execution_duration_ms: int = 0,
        llm_time_ms: int = 0
    ) -> dict:
        """
        Update the step results and overall confidence once execution is complete.
        """
        record = self.read_record(tenant_id, audit_id)
        if record:
            record["step_results"] = step_results
            record["overall_confidence"] = overall_confidence
            if workflow_state:
                record["workflow_state"] = workflow_state
            record["execution_duration_ms"] = execution_duration_ms
            record["llm_time_ms"] = llm_time_ms
            self._write_record(tenant_id, audit_id, record)
        return record

    def update_rollback(
        self,
        tenant_id: str,
        audit_id: str,
        status: str,
        details: dict
    ) -> dict:
        """
        Log rollback operations on failures.
        """
        record = self.read_record(tenant_id, audit_id)
        if record:
            record["rollback_status"] = status
            record["rollback_details"] = details
            self._write_record(tenant_id, audit_id, record)
        return record

    def read_record(self, tenant_id: str, audit_id: str) -> dict:
        """
        Retrieve an audit record.
        """
        file_path = self._get_file_path(tenant_id, audit_id)
        if os.path.exists(file_path):
            try:
                with open(file_path, "r") as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error reading audit file {file_path}: {e}")
        return {}

    def _get_file_path(self, tenant_id: str, audit_id: str) -> str:
        """Get path to the JSON file for a given tenant and audit ID."""
        tenant_dir = os.path.join(self.base_log_dir, tenant_id)
        if not os.path.exists(tenant_dir):
            os.makedirs(tenant_dir, exist_ok=True)
        return os.path.join(tenant_dir, f"{audit_id}.json")

    def _write_record(self, tenant_id: str, audit_id: str, record: dict):
        """Write record to file system."""
        file_path = self._get_file_path(tenant_id, audit_id)
        try:
            with open(file_path, "w") as f:
                json.dump(record, f, indent=2)
        except Exception as e:
            print(f"Error writing audit file {file_path}: {e}")

    def check_recent_duplicate(self, tenant_id: str, amount: float, entity_name: str, time_window_seconds: int = 300) -> bool:
        """Check if a similar transaction occurred within the recent time window."""
        tenant_dir = os.path.join(self.base_log_dir, tenant_id)
        if not os.path.exists(tenant_dir):
            return False

        now_time = datetime.utcnow()
        cutoff_time = now_time - timedelta(seconds=time_window_seconds)

        for filename in os.listdir(tenant_dir):
            if not filename.endswith(".json"):
                continue
                
            try:
                with open(os.path.join(tenant_dir, filename), "r") as f:
                    record = json.load(f)
                    
                record_time = datetime.fromisoformat(record.get("timestamp", "").replace("Z", "+00:00"))
                # Remove timezone info for naive comparison
                record_time = record_time.replace(tzinfo=None)
                
                if record_time < cutoff_time:
                    continue
                    
                # Check step results for extraction matching amount and entity
                for step_result in record.get("step_results", []):
                    if step_result.get("status") in ("completed", "waiting_approval", "completed_with_warning"):
                        data = step_result.get("data", {})
                        extraction = data.get("extraction")
                        if extraction:
                            ext_amount = extraction.get("total_amount")
                            ext_entity = extraction.get("entity", {})
                            if ext_entity and ext_amount is not None:
                                ext_entity_name = ext_entity.get("name", "").lower()
                                if abs(ext_amount - amount) < 0.01 and ext_entity_name == entity_name.lower():
                                    return True
            except Exception:
                continue
                
        return False
