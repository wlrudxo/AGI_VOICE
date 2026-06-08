# Reference Notes for ICCAS 2026 Draft

This file lists candidate references for the ICCAS paper and explains how each reference should be used. Bibliographic details will be filled in later by the user.

The paper should not cite every item equally. The main narrative should stay focused on simulator-in-the-loop MPC weight tuning, Bayesian optimization, and LLM-assisted optimization.

## Core Motivation References

### Can We Automate Scientific Reasoning in Closed-Loop Experiments Using Large Language Models?

Use as the most direct motivation for this paper.

How it supports our paper:

- Shows that LLM reasoning can be evaluated inside closed-loop experimental optimization.
- Frames LLMs as hypothesis generators, progress interpreters, candidate selectors, or standalone optimizers.
- Supports our decision to compare BO-only, LLM-only, and hybrid LLM/BO variants.
- Supports the need for repeated experiments, because LLM optimization can show stochastic outliers and prompt sensitivity.
- Supports the idea that frequent feedback after each experiment can improve LLM-based search.

How to cite in the text:

- Introduction: to motivate LLM reasoning for closed-loop optimization.
- Framework section: to justify the LLM role as a reasoning layer rather than a direct controller.
- Discussion: to explain why single-run results should not be overinterpreted.

Do not overclaim:

- Do not say this proves LLMs are generally better than BO.
- Do not directly transfer chemistry benchmark results to vehicle control.
- Use it as conceptual motivation for closed-loop reasoning, not as automotive evidence.

### Language-Based Bayesian Optimization Research Assistant (BORA)

Use as the main methodological motivation for hybrid LLM/BO.

How it supports our paper:

- Provides a concrete precedent for combining BO with LLM-generated hypotheses and progress commentary.
- Supports the idea that LLMs should intervene selectively rather than replacing numerical optimization.
- Supports our Hybrid BO framing: BO remains the base optimizer, while LLM assists with hypothesis generation, candidate interpretation, or search-region guidance.
- Supports keeping LLM-only as a comparison, but expecting hybrid LLM/BO to be more stable.

How to cite in the text:

- Introduction: as a recent example of language-assisted BO.
- LLM-assisted BO framework: as the closest conceptual reference.
- Optimization methods: to explain LLM intervention, warm-starting, and candidate selection.

Do not overclaim:

- Do not reproduce the full BORA action-selection mechanism unless we actually implement it.
- Do not claim our method is BORA. Our work is BORA-inspired but applied to MPC tuning in vehicle simulation.

## LLM + Bayesian Optimization Background

### Large Language Models to Enhance Bayesian Optimization

Use as a background reference for earlier or component-level LLM-enhanced BO.

How it supports our paper:

- Shows that LLMs can be inserted into BO workflows beyond simple text explanation.
- Can support discussion of warm-starting, surrogate assistance, or candidate sampling.
- Helps place BORA and our work in a broader LLM-BO line.

How to cite:

- Related/background paragraph in Introduction or Framework.

### LABO: LLM-Accelerated Bayesian Optimization through Broad Exploration and Selective Experimentation

Use as a related LLM-assisted BO variant.

How it supports our paper:

- Shows another way to use LLMs in BO: broad exploration and selective evaluation.
- Useful for explaining that LLM assistance can reduce expensive evaluations or guide candidate filtering.

How to cite:

- Briefly in the Framework or Discussion section when describing related LLM-assisted optimization strategies.

### Unleashing LLMs in Bayesian Optimization: Preference-Guided Framework for Scientific Discovery

Use as optional related work if space allows.

How it supports our paper:

- Connects LLMs, preference information, and BO for scientific discovery.
- Useful if we discuss human/LLM preference or qualitative search guidance.

Priority:

- Lower than BORA, Can We, and LLM-to-enhance-BO references.

## Bayesian Optimization and Sampling Baselines

### Scalable Global Optimization via Local Bayesian Optimization

Use as a BO/trust-region background reference if we mention local BO or high-dimensional BO limitations.

How it supports our paper:

- Provides background for BO in higher-dimensional black-box optimization.
- Useful if discussing why BO may need local/trust-region mechanisms when the search space grows.

Priority:

- Optional for the first 6-page version unless BO background needs one strong technical citation.

### Trust-Region Bayesian Optimization for High-Dimensional Black-Box Problems

Use as optional BO background.

How it supports our paper:

- Supports discussion of trust-region BO and high-dimensional black-box optimization.
- May be useful if future Hybrid BO uses LLM-guided trust-region narrowing.

Priority:

- Optional. Include only if the paper explicitly discusses trust-region narrowing.

### Human-in-the-Loop Controller Tuning Using Preferential Bayesian Optimization

Use as a bridge between controller tuning and human-guided BO.

How it supports our paper:

- Shows controller tuning can be treated as an optimization problem with human preference or guidance.
- Helps connect BO to control/calibration, not only chemistry/scientific discovery.
- Useful to justify that tuning control parameters through iterative evaluation is a valid research problem.

How to cite:

- Problem formulation or Introduction.

## Automotive / Vehicle Simulation References

### Computing the Racing Line Using Bayesian Optimization

Use as an automotive-relevant BO reference.

How it supports our paper:

- Shows BO has been applied to vehicle trajectory or racing-line optimization.
- Helps connect BO to vehicle dynamics and driving-performance optimization.

How to cite:

- Introduction or Experimental Setup when motivating simulation-based vehicle optimization.

Priority:

- Medium. Useful because it is closer to vehicles than chemistry examples.

### A Fully Automated Smooth Calibration Generation Methodology for Optimized Driving Comfort

Use as an auto-calibration reference if relevant.

How it supports our paper:

- Supports the broader motivation that vehicle calibration can be automated and optimized.
- Useful if the paper frames MPC weight tuning as a calibration-like task.

Priority:

- Medium. Include if the final Introduction emphasizes automated calibration.

### Simplified-Road-Condition-Based Global Optimization and Calibration Using Model-Based Calibration

Use as an automated calibration/background reference.

How it supports our paper:

- Connects model-based calibration and vehicle parameter optimization.
- Useful for explaining why simulator-based tuning is relevant in automotive development.

Priority:

- Optional. Include if space remains.

## LLM and Autonomous Driving Context

### LLM4AD: Large Language Models for Autonomous Driving -- Concept, Review and Vision

Use as broad LLM-for-autonomous-driving background.

How it supports our paper:

- Establishes that LLMs are being investigated in autonomous driving.
- Helps distinguish our work from direct LLM driving agents.

How to cite:

- Introduction only, briefly.

Do not overuse:

- Our paper is not about LLM as direct driving policy.

### AgentDrive: An Open Benchmark Dataset for Agentic AI Reasoning with LLMs for Autonomous Driving

Use only if discussing LLM reasoning in autonomous-driving contexts.

How it supports our paper:

- Provides background that LLM reasoning can be benchmarked for driving tasks.

Priority:

- Low for the first version because our task is optimizer assistance, not scene reasoning.

### A Comprehensive LLM-Powered Framework for Driving Intelligence Evaluation

Use only as broad LLM-driving evaluation context.

Priority:

- Low unless the introduction needs more autonomous-driving LLM references.

## References to Avoid as Main Baselines

### Curricullm: Automatic Task Curricula Design for Learning Complex Robot Skills Using Large Language Models

Use only as background for LLM-guided reinforcement learning if needed.

Reason to avoid in main comparison:

- Our experiment is not reinforcement learning or curriculum learning.
- Including it as a main reference may make readers expect an RL baseline.

### LLM-Guided Deep Reinforcement Learning for Driving Decision Making

Use only in a short sentence explaining why RL is outside the current scope.

Reason to avoid in main comparison:

- Our problem is static MPC weight tuning, not state-action policy learning.
- A fair RL baseline would require a different formulation and much larger interaction budget.

## Suggested Citation Placement

### Introduction

Use 4-6 references:

- Can We Automate Scientific Reasoning in Closed-Loop Experiments Using Large Language Models?
- Language-Based Bayesian Optimization Research Assistant (BORA)
- Large Language Models to Enhance Bayesian Optimization
- Human-in-the-Loop Controller Tuning Using Preferential Bayesian Optimization
- Computing the Racing Line Using Bayesian Optimization
- LLM4AD, if one broad LLM-driving reference is needed

### Problem Formulation

Use 1-2 references:

- Human-in-the-Loop Controller Tuning Using Preferential Bayesian Optimization
- Any MPC/controller tuning reference to be added later

### Framework

Use 3-4 references:

- BORA
- Can We Automate Scientific Reasoning
- Large Language Models to Enhance Bayesian Optimization
- LABO

### Experimental Setup and Results

Use few or no new references. This section should mostly describe our simulator, objective, metrics, and comparison protocol.

## Current Priority List

High priority:

1. Can We Automate Scientific Reasoning in Closed-Loop Experiments Using Large Language Models?
2. Language-Based Bayesian Optimization Research Assistant (BORA)
3. Large Language Models to Enhance Bayesian Optimization
4. Human-in-the-Loop Controller Tuning Using Preferential Bayesian Optimization
5. Computing the Racing Line Using Bayesian Optimization

Medium priority:

6. LABO: LLM-Accelerated Bayesian Optimization through Broad Exploration and Selective Experimentation
7. LLM4AD: Large Language Models for Autonomous Driving -- Concept, Review and Vision
8. A Fully Automated Smooth Calibration Generation Methodology for Optimized Driving Comfort

Optional:

9. Scalable Global Optimization via Local Bayesian Optimization
10. Trust-Region Bayesian Optimization for High-Dimensional Black-Box Problems
11. Preference-guided LLM/BO or preference-aware BO references

Avoid as main references:

12. RL/curriculum-learning papers, unless used only to justify future work or scope exclusion.
