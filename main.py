import time
from dataclasses import dataclass, field
from typing import Callable, Dict, Any, List

@dataclass
class Step:
    name: str
    func: Callable[[Dict[str, Any]], Any]
    needs: List[str] = field(default_factory=list)
    retries: int = 1

def mock_llm(prompt, context):
    return {'text': f'LLM processed: {prompt[:40]}...', 'context': context}

def run_workflow(steps, initial=None):
    steps = {s.name: s for s in steps}
    results = dict(initial or {})
    done = set()
    while len(done) < len(steps):
        ready = [s for n, s in steps.items() if n not in done and all(d in done for d in s.needs)]
        if not ready:
            raise RuntimeError('Cycle or missing dependency')
        for step in ready:
            inputs = {k: results[k] for k in step.needs}
            for attempt in range(step.retries + 1):
                try:
                    results[step.name] = step.func(inputs)
                    done.add(step.name)
                    print(f'[OK] {step.name}')
                    break
                except Exception as e:
                    print(f'[RETRY {attempt + 1}] {step.name}: {e}')
                    if attempt == step.retries:
                        raise
    return results

def main():
    workflow = [
        Step('parse', lambda x: {'query': 'Summarize recent AI agent trends'}),
        Step('retrieve', lambda x: {'docs': ['AI agents are growing', 'Workflow automation helps']}, needs=['parse']),
        Step('llm', lambda x: mock_llm(x['parse']['query'], x['retrieve']['docs']), needs=['parse', 'retrieve'], retries=2),
        Step('format', lambda x: {'answer': x['llm']['text'] + ' | docs=' + str(len(x['retrieve']['docs']))}, needs=['llm']),
    ]
    result = run_workflow(workflow)
    print(result['format'])

if __name__ == '__main__':
    main()