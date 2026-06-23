# Overview

This repository implements a fuzzing-based framework for evaluating inference-time privacy risks in deployed Large Language Models (LLMs) under black-box conditions.

The framework operationalizes privacy risks as executable artifacts composed of:

* structured seed datasets,
* risk-specific fuzzing strategies,
* prompt generation mechanisms, and
* explicit privacy oracles.

The current implementation evaluates two privacy risks:

1. **Misuse and Disclosure of Personal Data**, using canary-based disclosures embedded within multi-turn conversational trajectories.
2. **Re-identification of De-identified Information**, using domain-specific identity inference scenarios constructed from partially anonymized profiles.

The framework supports evaluation across multiple commercial LLM providers (OpenAI, Google Gemini, and DeepSeek) and records all executions for reproducible oracle evaluation and analysis.

This repository accompanies the paper *"Fuzzing Inference-Time Privacy Risks in Deployed Large Language Models"* and provides all artifacts required to reproduce the experiments.

## Usage

1. Create a `.env` file containing the required API keys.
2. Select the providers and models to evaluate in `main.py`.
3. Run:

```bash
python main.py
```

Results will be written to:

```text
outputs/{file_name}.csv
```

Execution logs are stored separately to support experiment traceability and reproduction.
