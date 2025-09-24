import yaml, importlib
from pathlib import Path
from datetime import datetime

def load_yaml(path): return yaml.safe_load(open(path))

def run_workflow(query_set_path, prom_config_path, copilot_mode_module, output_dir="test/output/"):
    queries = load_yaml(query_set_path)['queries']
    prom_config = load_yaml(prom_config_path)
    copilot = importlib.import_module(copilot_mode_module)

    result = {}
    for q in queries:
        if isinstance(q, dict):
            query_text = q.get('text', '')
            repeat_times = q.get('repeat', 1)
        else:
            query_text = q
            repeat_times = 1

        for i in range(repeat_times):
            run_label = f"{query_text} (run {i+1})" if repeat_times > 1 else query_text
            try:
                answer = copilot.run(query_text, prom_config)
                if isinstance(answer, dict):
                    answer = dict(answer)  # shallow copy
                    if "ollama_response" in answer:
                        ollama_response = answer.pop("ollama_response")
                        answer = {"ollama_response": ollama_response, **answer}
                    if "final_answer" in answer:
                        final_answer = answer.pop("final_answer")
                        answer = {"final": final_answer, **answer}
                result[run_label] = answer
            except Exception as e:
                result[run_label] = {"error": str(e)}

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    name = Path(query_set_path).stem
    output_file = Path(output_dir) / f"{name}_{timestamp}.yaml"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(yaml.dump(result))
    print(f"[INFO] Results saved to {output_file}")
