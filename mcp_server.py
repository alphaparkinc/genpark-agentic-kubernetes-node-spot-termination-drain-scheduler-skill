#!/usr/bin/env python3
import json
import sys
from client import AgenticK8sSpotTerminationDrainScheduler

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        scheduler = AgenticK8sSpotTerminationDrainScheduler()
        pods = [
            {"pod_name": "batch-worker-1", "priority_class": "BATCH", "graceful_period_sec": 15},
            {"pod_name": "checkout-api-9", "priority_class": "SYSTEM_CRITICAL", "graceful_period_sec": 30}
        ]
        res = scheduler.schedule_spot_node_drain("ip-10-0-4-192.ec2.internal", pods, seconds_remaining=120)
        assert res["eviction_sequence"][0]["pod_name"] == "checkout-api-9"
        assert res["zero_downtime_guaranteed"] is True
        print(f"[TEST PASS] Spot Drain Scheduled Pods: {res['total_pods_to_evict']}")
        sys.exit(0)

    for line in sys.stdin:
        if not line.strip():
            continue
        try:
            req = json.loads(line)
            method = req.get("method")
            msg_id = req.get("id")
            if method == "initialize":
                print(json.dumps({"jsonrpc": "2.0", "id": msg_id, "result": {"serverInfo": {"name": "genpark-k8s-spot-drainer", "version": "1.0.0"}}}))
            elif method == "tools/list":
                print(json.dumps({"jsonrpc": "2.0", "id": msg_id, "result": {"tools": [{"name": "schedule_spot_node_drain", "description": "Kubernetes spot preemption pod eviction scheduler"}]}}))
            elif method == "tools/call":
                args = req.get("params", {}).get("arguments", {})
                scheduler = AgenticK8sSpotTerminationDrainScheduler()
                out = scheduler.schedule_spot_node_drain(args.get("node_id", "node-spot"), args.get("resident_pods", []), int(args.get("seconds_remaining", 120)))
                print(json.dumps({"jsonrpc": "2.0", "id": msg_id, "result": {"content": [{"type": "text", "text": json.dumps(out)}]}}))
            else:
                print(json.dumps({"jsonrpc": "2.0", "id": msg_id, "error": {"code": -32601, "message": "Method not found"}}))
            sys.stdout.flush()
        except Exception as e:
            print(json.dumps({"jsonrpc": "2.0", "error": {"code": -32603, "message": str(e)}}))
            sys.stdout.flush()

if __name__ == "__main__":
    main()
