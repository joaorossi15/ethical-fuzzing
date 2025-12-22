# Overview

This repository implements a fuzzing-based framework for evaluating **inference-time privacy risks** in deployed Large Language Models (LLMs) under **black-box conditions**.

The framework operationalizes privacy risks as executable artifacts composed of:
- structured base seeds,
- risk-specific fuzzing strategies, and
- explicit privacy oracles.

The current prototype instantiates the **misuse and malicious use of personal data** risk using canary injection and multi-message conversational trajectories. It supports evaluation across multiple commercial LLM providers (OpenAI, Google Gemini, and DeepSeek) and records all executions for reproducible manual oracle evaluation.

This repository accompanies the paper *“Fuzzing Inference-Time Privacy Risks in Deployed Large Language Models”* and provides all artifacts needed to reproduce the experiments.

## Usage
- Create a `.env` file with the respective API keys;
- Choose on `main.py` the providers and models to test;
- Run `main.py` and the output will be at `outputs/{file_name}.csv`
