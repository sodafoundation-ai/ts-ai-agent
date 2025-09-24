import argparse

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from workflows.run_queries import run_workflow
import yaml

# Load available copilot modes dynamically
def get_available_modes():
    with open("config/agent_modes.yaml") as f:
        modes = yaml.safe_load(f)['modes']
    return {mode['name']: mode['module'] for mode in modes}

def main():
    parser = argparse.ArgumentParser(description="tsdb_ai_agent CLI Workflows")

    parser.add_argument(
        "--query-set",
        type=str,
        required=True,
        help="Path to the query set YAML file (e.g., test/query_sets/set1.yaml)"
    )

    parser.add_argument(
        "--copilot",
        type=str,
        required=True,
        help="Copilot logic to use (e.g., MCP, PROM_DIRECT)"
    )

    parser.add_argument(
        "--output",
        type=str,
        default="output/",
        help="Path to save the output responses (default: output/)"
    )

    parser.add_argument(
        "--prometheus-config",
        type=str,
        default="config/prometheus_config.yaml",
        help="Path to Prometheus config YAML file (default: config/prometheus_config.yaml)"
    )

    args = parser.parse_args()

    copilot_modes = get_available_modes()
    if args.copilot not in copilot_modes:
        print(f"[ERROR] Unknown copilot mode '{args.copilot}'. Available modes: {', '.join(copilot_modes)}")
        exit(1)

    # Ensure output directory exists
    os.makedirs(os.path.dirname(args.output), exist_ok=True)

    print(f"[INFO] Running with query set: {args.query_set}")
    print(f"[INFO] Using copilot: {args.copilot}")
    print(f"[INFO] Saving to: {args.output}")

    run_workflow(
        query_set_path=args.query_set,
        prom_config_path=args.prometheus_config,
        copilot_mode_module=copilot_modes[args.copilot],
        output_dir=args.output
    )

if __name__ == "__main__":
    main()
