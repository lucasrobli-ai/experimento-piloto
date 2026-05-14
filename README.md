# Avaliando códigos gerados por LLMs

## Visão Geral

Este repositório contém experimentos para avaliar a qualidade e a segurança de códigos-fonte gerados por *Large Language Models* (LLMs), por meio do GitHub Copilot.

O objetivo principal é avaliar fragilidades, vulnerabilidades presentes em códigos gerados automaticamente, utilizando ferramentas de mercado e de código aberto como Semgrep e SonarQube.

## Objetivos do Projeto

- Avaliar a segurança de código gerado por diferentes LLMs
- Identificar vulnerabilidades mapeadas em CWEs
- Comparar resultados entre ferramentas SAST
- Analisar padrões recorrentes de falhas em código gerado automaticamente

## Estrutura dos Experimentos

Cada experimento segue, de forma geral, o seguinte fluxo:

- Geração de código por um LLM, por meio do GitHub Copilot
- Execução de ferramentas SAST sobre o código gerado
- Extração e normalização dos resultados (JSON/CSV)

### Classificação por

- Linha do erro
- Tipo de vulnerabilidade
- CWE associada
- Severidade (BAIXA, MÉDIA, ALTA, CRÍTICA)

## Modelos avaliados

- Claude Haiku 4.5
- GPT-4.0
- GPT-4.1
- GPT-5.1 Mini

## Ferramentas Utilizadas

### Semgrep
- Análise estática baseada em padrões
- Detecção rápida de vulnerabilidades e más práticas
- Suporte a múltiplas linguagens

### SonarQube

- Análise de qualidade e segurança
- Identificação de Bugs, Vulnerabilidades e Security Hotspots
- Classificação por severidade
