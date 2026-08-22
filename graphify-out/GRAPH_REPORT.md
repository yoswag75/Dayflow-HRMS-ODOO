# Graph Report - .  (2026-08-22)

## Corpus Check
- Corpus is ~12,717 words - fits in a single context window. You may not need a graph.

## Summary
- 121 nodes · 93 edges · 47 communities
- Extraction: 86% EXTRACTED · 14% INFERRED · 0% AMBIGUOUS · INFERRED: 13 edges (avg confidence: 0.92)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- API Contract
- Implementation Plan
- Backend Contract
- Executive Architecture
- Product Features
- Cross-Module Stub Schemas
- Simulation and Product Overview
- Functional Scope
- Executive Summary
- Root Architecture

## God Nodes (most connected - your core abstractions)
1. `Dayflow HRMS OpenAPI Specification` - 10 edges
2. `Dayflow HRMS Executive Summary` - 5 edges
3. `Dayflow Product Vision` - 5 edges
4. `Emergency Leave and SLA Workflow` - 5 edges
5. `Modular Monolith Architecture` - 5 edges
6. `Backend Project Structure` - 5 edges
7. `Shared Change Request Foundation` - 4 edges
8. `Service-Only Module Boundary Rule` - 4 edges
9. `Shared Change Request Technical Pattern` - 4 edges
10. `Dayflow Functional Scope` - 4 edges

## Surprising Connections (you probably didn't know these)
- `Fair Recognition System` --semantically_similar_to--> `Fair Gamification Design`  [INFERRED] [semantically similar]
  Docs/Full_project.md → README.md
- `Local Privacy-Preserving SLM` --semantically_similar_to--> `Two-Layer Trust Architecture`  [INFERRED] [semantically similar]
  Docs/Full_project.md → README.md
- `Service-Only Module Boundary Rule` --semantically_similar_to--> `Module Dependency Rule`  [INFERRED] [semantically similar]
  Docs/Tech_details.md → backend/README.md
- `FastAPI Modular Monolith` --semantically_similar_to--> `Modular Monolith Architecture`  [INFERRED] [semantically similar]
  Docs/Exec_summary.md → Docs/Tech_details.md
- `Backend Integration Contract` --conceptually_related_to--> `Representative API Surface`  [INFERRED]
  Functionality.md → Docs/Tech_details.md

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Shared Change Request Documentation** — docs_exec_summary_change_request, docs_full_project_shared_change_request, docs_implementation_shared_change_request_foundation, docs_tech_details_change_request_pattern, readme_problem_solutions [INFERRED 0.95]
- **Auditable Local AI Pattern** — docs_exec_summary_two_layer_ai_architecture, docs_full_project_workforce_simulator, docs_implementation_simulation_engine, docs_implementation_chatbot_wrapper, docs_tech_details_simulation_engine, docs_tech_details_chatbot_ollama_flow, readme_two_layer_trust_architecture [INFERRED 0.95]
- **API Contract Alignment** — functionality_api_contract, docs_tech_details_api_surface, api_dayflow_hrms_api, backend_readme_dev_b_api_surface [INFERRED 0.85]

## Communities (47 total, 0 thin omitted)

### Community 0 - "API Contract"
Cohesion: 0.16
Nodes (15): Attendance API Endpoints, Authentication API Endpoints, Dayflow HRMS OpenAPI Specification, Employee Change Request Endpoints, Onboarding and Gamification API Endpoints, Leave API Endpoints, Notification API Endpoints, Payroll API Endpoints (+7 more)

### Community 1 - "Implementation Plan"
Cohesion: 0.21
Nodes (13): Attendance Summary Service Contract, Authentication and Authorization Foundation, Ollama Chatbot Wrapper, Employee Edit Verification Implementation, Fair Gamification Rules, Dependency-Ordered Implementation Plan, Emergency Leave and SLA Workflow, Notification Service Interface (+5 more)

### Community 2 - "Backend Contract"
Cohesion: 0.18
Nodes (12): Dayflow Backend Guide, Dev B API Surface, Module Dependency Rule, Backend Project Structure, Backend Runtime Configuration, Layered Backend Test Strategy, Backend Python Dependencies, Security and Integration Libraries (+4 more)

### Community 3 - "Executive Architecture"
Cohesion: 0.22
Nodes (9): Shared Change Request Workflow, Dayflow HRMS Executive Summary, Emergency Leave Fast Track, FastAPI Modular Monolith, Deterministic Simulation with Local NLP, Docker Compose Deployment Design, Future Service Extraction Path, Modular Monolith Architecture (+1 more)

### Community 4 - "Product Features"
Cohesion: 0.25
Nodes (8): Fair Gamification, Dayflow Product Vision, Provisional Emergency Leave, Excalidraw Wireframes and Flow Diagrams, Fair Recognition System, Onboarding and Knowledge Transfer Acceleration, Shared Change Request Pattern, Fair Gamification Design

### Community 5 - "Cross-Module Stub Schemas"
Cohesion: 0.48
Nodes (6): AttendanceOut, AttendanceSummaryOut, EmployeeOut, LeaveBalanceOut, PayslipOut, BaseModel

### Community 6 - "Simulation and Product Overview"
Cohesion: 0.29
Nodes (7): Local Privacy-Preserving SLM, Dayflow Non-Functional Requirements, What-If Workforce Simulator, Dayflow Project Overview, Excalidraw Design Reference, Operational Problem Solutions, Two-Layer Trust Architecture

### Community 7 - "Functional Scope"
Cohesion: 0.33
Nodes (6): Core HRMS Feature Checklist, Suggested MVP Delivery Order, Frontend Quality Standards, Dayflow Functional Scope, MVP Scope Deferrals, Role and Access Matrix

### Community 8 - "Executive Summary"
Cohesion: 0.50
Nodes (4): Architecture and Delivery Status, Dayflow Executive Overview, Fair Gamification Summary, Auditable Local AI Design

### Community 9 - "Root Architecture"
Cohesion: 0.67
Nodes (3): Backend Modular Monolith, Module Ownership and Responsibilities, Dayflow Technology Stack

## Knowledge Gaps
- **24 isolated node(s):** `Shared Change Request Workflow`, `Emergency Leave Fast Track`, `Shared Change Request Pattern`, `Onboarding and Knowledge Transfer Acceleration`, `Dayflow Non-Functional Requirements` (+19 more)
  These have ≤1 connection - possible missing edges or undocumented components.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Modular Monolith Architecture` connect `Executive Architecture` to `API Contract`, `Backend Contract`?**
  _High betweenness centrality (0.185) - this node is a cross-community bridge._
- **Why does `Service-Only Module Boundary Rule` connect `Backend Contract` to `API Contract`, `Executive Architecture`?**
  _High betweenness centrality (0.140) - this node is a cross-community bridge._
- **Why does `Dayflow HRMS Executive Summary` connect `Executive Architecture` to `Product Features`?**
  _High betweenness centrality (0.135) - this node is a cross-community bridge._
- **What connects `Shared Change Request Workflow`, `Emergency Leave Fast Track`, `Deterministic Simulation with Local NLP` to the rest of the system?**
  _32 weakly-connected nodes found - possible documentation gaps or missing edges._