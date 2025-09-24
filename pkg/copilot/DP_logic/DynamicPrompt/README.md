# Dynamic Prompt Framework

This framework helps you build dynamic, domain-specific prompts for AI applications. It is general-purpose and can be used with any structured or unstructured data source.

## Features
- Modular prompt template sections
- Configurable fine-tuning instructions
- Vector-based context retrieval from embedded domain knowledge
- Easy onboarding via CLI

## Getting Started
1. Prepare your domain knowledge file (e.g., `metrics.txt`)
2. Run the onboarding CLI:
```bash
python onboarding_cli.py
```
This will embed and save your data to `config/embeddings.npz`

3. Ask a question using your framework:
```python
from dynamic_prompt_framework.prompt_builder import PromptBuilder
from dynamic_prompt_framework.retriever import Retriever

question = "How many login failures in the last 24h?"
context = Retriever().query(question)

prompt = PromptBuilder() \
    .with_context(context) \
    .with_user_question(question) \
    .with_overrides() \
    .with_golden_examples() \
    .build()

print(prompt)
```

## Folder Structure
- `config/template_sections/*.md` → Modular prompt pieces
- `config/overrides.json` → Prompt tuning parameters
- `config/golden_examples.json` → Few-shot learning examples
- `config/embeddings.npz` → Compressed vector store

## 📄 `config/template_sections/` — Prompt Templates

The `template_sections` folder contains modular components of the system prompt. Each file here corresponds to a specific section in the final assembled prompt. You can modify these files to control the base behavior of the LLM for your specific use case.

### ✅ Required Files

| Filename       | Description |
|----------------|-------------|
| `system.md`    | Describes the **role** of the LLM. Defines what kind of assistant it is, what task it must perform, and how it should behave. |
| `domain.md`    | Contains **domain-specific knowledge** and assumptions. This can include details like the data source, query language, known metrics, and user preferences. |
| `postamble.md` | Adds any **final instructions** or stylistic requirements. Useful for enforcing things like output format or response tone. |

### 📝 Example Contents

**`system.md`**
```markdown
You are a domain expert AI assistant specialized in generating structured queries in response to user questions. Be concise, accurate, and assume technical proficiency.
```

**`domain.md`**
```markdown
You are working with a Prometheus time-series database. The user may reference metrics such as `http_requests_total`, `cpu_usage_seconds_total`, or `disk_io_time`. Queries will be written using PromQL.
```

**`postamble.md`**
```markdown
Respond only with the query and no explanation unless explicitly asked. Avoid guessing if information is insufficient.
```
