# Design: Reusable Document Tooling Promotion

## Current State

The tender workspace contains working document and vector helpers, but their defaults encode `D:/project` paths and project-specific authority assumptions.

## Target State

The target repository owns a reusable tool surface with three layers: PDF tools, document pipeline core, and vector/retrieval framework helpers.

## Boundary Decisions

- Consumer projects own real configs, output roots, guard rules, source authority, and data.
- Portable Poppler is local ignored cache because existing evidence-intake requirements keep third-party binaries out of tracked source.
- Scripts default to caller/current working directory local output when no consumer config is supplied.
