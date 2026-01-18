# Guardrail Agents

Enterprise-grade multi-agent AI framework with built-in safety controls, running entirely on local infrastructure using Ollama.

## The Problem

Organizations deploying AI agents face critical challenges:

- **Safety & Compliance Risk** - No built-in mechanisms to prevent agents from discussing restricted topics, accessing unauthorized data, or violating policies
- **Vendor Lock-in** - Reliance on cloud APIs increases costs and creates data privacy concerns
- **Uncontrolled Agent Behavior** - Agents lack guardrails to enforce business rules before processing requests
- **Knowledge Fragmentation** - Agents can't leverage proprietary knowledge bases or real-time information effectively
- **Task Complexity** - No framework for orchestrating specialized agents to handle different business functions

## The Solution

Guardrail Agents provides a production-ready framework that:

✅ **Enforces Safety Policies** - Guardrail agents classify and block requests before processing  
✅ **Runs Locally** - Complete data sovereignty using Ollama (no cloud dependencies)  
✅ **Integrates Custom Knowledge** - RAG-powered access to proprietary documents and databases  
✅ **Orchestrates Specialized Agents** - Route tasks to focused agents (e.g., calculations, approvals)  
✅ **Maintains Audit Trail** - Track all decisions and policy enforcement  

## Business Benefits

| Challenge | Solution |
|-----------|----------|
| Compliance violations | Agent-based guardrails enforce policies automatically |
| Data privacy concerns | Run entirely on-premises with Ollama |
| High API costs | Eliminate cloud LLM dependencies |
| Uncontrolled outputs | Safety layer validates all responses |
| Knowledge silos | Unified RAG layer across enterprise data |

## Architecture

User Request ↓ [Guardrail Agent] ├→ Policy Check ├→ Content Filter └→ Compliance Validation ↓ [Main Agent] ├→ Route to Tools ├→ Query Knowledge Base (RAG) ├→ Fetch Real-time Data └→ Delegate to Specialized Agents ├→ Approval Agent ├→ Calculation Agent └→ Report Generation Agent ↓ Compliant Response



## Key Features

- **Agent-Based Guardrails** - Implement business policies as dedicated agents
- **Local LLM Integration** - Ollama support for complete data privacy
- **Vector Store RAG** - Query proprietary knowledge bases
- **Multi-Agent Orchestration** - Seamless delegation between specialized agents
- **Audit & Logging** - Track all decisions and policy enforcement
- **Extensible Framework** - Add custom agents and guardrails easily

## Use Cases

**Financial Services**
- Loan approval workflows with compliance guardrails
- Risk assessment with policy enforcement
- Customer inquiry handling with restricted topic blocking

**Healthcare**
- Patient data access with privacy guardrails
- Medical information retrieval with compliance checks
- Appointment scheduling with authorization layers

**Enterprise Support**
- Help desk automation with knowledge base integration
- Ticket routing with policy enforcement
- Internal knowledge queries with access controls

**Legal & Compliance**
- Document review with restricted content filtering
- Contract analysis with policy guardrails
- Regulatory compliance checking

## Quick Start

### Prerequisites
- Python 3.8+
- Ollama installed and running locally
- Access to local LLM model (e.g., Llama 2, Mistral)

### Installation

Clone the repository and install dependencies using the provided requirements file. Start Ollama locally to enable the framework.

### Configuration

Configure your local LLM model through environment variables. Set the Ollama base URL and select your preferred model. Define guardrail policies in YAML format to enforce business rules and compliance requirements.

## Performance & Scalability

- **Latency** - Sub-second guardrail checks on local infrastructure
- **Throughput** - Handle multiple concurrent agent requests
- **Resource Efficient** - Run on standard enterprise hardware
- **Scalable** - Deploy multiple agent instances behind load balancer

## Security

- ✅ No data leaves your infrastructure
- ✅ Encrypted knowledge base storage
- ✅ Audit logging for compliance
- ✅ Role-based access control
- ✅ Policy enforcement at every layer

## Requirements

- Python 3.8+
- Ollama 0.1+
- 8GB+ RAM (recommended)
- Local LLM model

## Roadmap

- [ ] Multi-model support (Claude, Gemini local variants)
- [ ] Advanced RAG with semantic search
- [ ] Workflow automation engine
- [ ] Real-time policy updates
- [ ] Enterprise dashboard & monitoring

## Support & Documentation

- Setup Guide
- Policy Configuration
- Agent Development
- API Reference