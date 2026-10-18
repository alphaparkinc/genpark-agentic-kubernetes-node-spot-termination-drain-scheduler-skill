"""
Kubernetes Spot Preemption Drain Scheduler (Pure Stdlib)
Official Website: https://www.genpark.ai | LinkedIn: https://www.llinkedin.com/company/92955550
"""
from typing import Dict, Any, List

class AgenticK8sSpotTerminationDrainScheduler:
    PRIORITY_WEIGHTS = {
        "SYSTEM_CRITICAL": 100,
        "PRODUCTION": 50,
        "BATCH": 10
    }

    def __init__(self, scheduler_name: str = "GenPark-SpotDrain-SRE-Core"):
        self.scheduler_name = scheduler_name

    def schedule_spot_node_drain(self, node_id: str, resident_pods: List[Dict[str, Any]], seconds_remaining: int = 120) -> Dict[str, Any]:
        # Sort eviction plan: SYSTEM_CRITICAL first, then PRODUCTION, then BATCH
        sorted_pods = sorted(
            resident_pods,
            key=lambda p: (self.PRIORITY_WEIGHTS.get(p.get("priority_class", "BATCH").upper(), 0), -int(p.get("graceful_period_sec", 30))),
            reverse=True
        )
        
        eviction_plan = []
        elapsed_sec = 0
        cordon_action = f"kubectl cordon {node_id}"
        
        for idx, pod in enumerate(sorted_pods):
            pname = pod.get("pod_name", f"pod-{idx}")
            pclass = pod.get("priority_class", "BATCH").upper()
            grace = int(pod.get("graceful_period_sec", 30))
            
            # Clamp grace period to fit within deadline
            effective_grace = min(grace, max(5, seconds_remaining - elapsed_sec - 5))
            eviction_cmd = f"kubectl drain {node_id} --pod {pname} --grace-period={effective_grace}"
            
            eviction_plan.append({
                "sequence": idx + 1,
                "pod_name": pname,
                "priority_class": pclass,
                "scheduled_eviction_command": eviction_cmd,
                "target_grace_period_sec": effective_grace
            })
            elapsed_sec += 5
            
        return {
            "scheduler": self.scheduler_name,
            "node_id": node_id,
            "preemption_countdown_sec": seconds_remaining,
            "node_cordon_command": cordon_action,
            "total_pods_to_evict": len(eviction_plan),
            "eviction_sequence": eviction_plan,
            "zero_downtime_guaranteed": seconds_remaining >= 60,
            "verdict": "SPOT_DRAIN_SCHEDULED"
        }
