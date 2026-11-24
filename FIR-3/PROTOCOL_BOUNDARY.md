# FIR-3 v1.1 — Frozen Protocol Boundary

This document records the operational boundary used to manage the existing v1.1 minimum three-relation protocol. It is a governance summary, not a replacement for the authoritative frozen protocol. If the original signed / dated protocol differs, the original controls.

## Model definitions

Let A_t=R_12,t, B_t=R_23,t, and C_t=R_13,t.

Target: `C_(t+1) = A_t XOR B_t XOR N_t`, where `N_t ~ Bernoulli(0.10)`.

No-interaction negative control: `C_(t+1) = A_t XOR N_t`.

A_t and B_t are independently randomized and balanced. C_t is independently generated and does not enter the transition equation; this does not establish autonomous memory.

## Confirmatory contrasts

For p_ab = P(C_(t+1)=1 | do(A_t=a), do(B_t=b)):

- Target cells (p00,p01,p10,p11) = (0.1,0.9,0.9,0.1).
- Negative-control cells = (0.1,0.1,0.9,0.9).
- ΔA(b)=p_1b-p_0b; ΔB(a)=p_a1-p_a0.
- Ψ=p11-p10-p01+p00.
- Target Ψ=-1.6; negative-control Ψ=0.
- Under independent uniform A,B and independent Bernoulli(0.1) noise, theoretical mutual information is 1-h2(0.1) ≈ 0.531004 bit for both models.

## Frozen design and decision boundaries

The v1.1 minimum design records 400 effective trials per input cell per model (1,600 per model), with four balanced cells. The target interaction direction uses a two-sided 95% interval whose upper bound is below zero. Negative-control equivalence margins are Ψ ±0.20 and each B simple effect ±0.10, assessed by 90% intervals fully contained within the equivalence bounds.

The simulation package uses 40 blocks per model, 10 repetitions per cell per block, 8 held-out blocks, and 10,000 complete-block bootstrap replicates as execution-preparation details. These do not rewrite the frozen protocol.

## Explicit non-claims

Passing synthetic validation does not establish a real-world causal effect, cross-environment invariance, implementation independence, autonomous memory, or a novel causal formalism beyond standard structural causal models.

New analyses are confirmatory only if they were included in the frozen protocol. Otherwise label them exploratory / supplementary.
