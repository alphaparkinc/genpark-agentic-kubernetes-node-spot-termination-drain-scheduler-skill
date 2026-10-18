from client import AgenticK8sSpotTerminationDrainScheduler

def main():
    scheduler = AgenticK8sSpotTerminationDrainScheduler()
    pods = [
        {"pod_name": "etl-sync", "priority_class": "BATCH", "graceful_period_sec": 10},
        {"pod_name": "auth-gateway", "priority_class": "SYSTEM_CRITICAL", "graceful_period_sec": 20},
        {"pod_name": "catalog-service", "priority_class": "PRODUCTION", "graceful_period_sec": 25}
    ]
    res = scheduler.schedule_spot_node_drain("node-spot-us-east-1a-99", pods, seconds_remaining=110)
    print("--- K8s Spot Drain Coordinator ---")
    print(f"Node: {res['node_id']} | Countdown: {res['preemption_countdown_sec']}s")
    print(f"Cordon: {res['node_cordon_command']}")
    for ev in res['eviction_sequence']:
        print(f"[{ev['sequence']}] {ev['pod_name']} ({ev['priority_class']}) -> {ev['scheduled_eviction_command']}")

if __name__ == "__main__":
    main()
