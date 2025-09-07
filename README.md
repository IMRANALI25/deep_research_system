---
title: "**[Deep Search Agentic System]{.underline}**"
---

**🔑 Hierarchy Explanation**


- **Core Orchestration**

  1.  drs.py : Starts the system, coordinates requirement agent.

  2.  Requirement_agent.py : It gathers all requirements for the given
      topic

  3.  planning_agent.py : Requirement agent handoffs to Planning agent
      and it breaks down requirements and create summary query. It
      handoffs to the

  4.  lead_research_agent.py : Supervises web research, synthesis,
      report generation.

  5.  web_research_agent.py : Runs web searches (Tavily, etc.).

  6.  synthesis_agent.py : cross validation & consistency check,
      advanced summarization & abstraction, relevance filtering
      and processes research results.

  7.  report_generation_agent.py : Generates final professional reports.

- **Support Modules (Utilities)**

  1.  api_keys.py: Get API keys from environment.

  2.  config_constants.py: Constants variables for application

  3.  helper_classes.py: Helper Pydantic and dataclasses for program

  4.  helper_functions.py: Utility Functions for program

  5.  llm_parameters.py: Initialize LLM parameters.

  6.  tavily_response_data.py: Methods used for use of tavily web search
      service.

  7.  topics.py: Test topics data for Agent

  8.  user_profile.py: User Class

- **Output Files**

> Few generated out files, .md and .html formats, for test topics.

- **Config / Metadata**

  1.  .env : Environment variables (API keys, etc.).

  2.  .gitignore : Ignore rules for git.

  3.  .python-version : Ensures correct Python version.

  4.  pyproject.toml, uv.lock : Dependency + build system.

- **Docs & Tests**

  1.  README.md : Documentation.

  2.  testQ.txt : Test inputs/questions.

**Queries**

1.  Analyze the economic impact of remote work policies on small
    businesses vs large corporations, including productivity data and
    employee satisfaction trends

2.  How has artificial intelligence changed healthcare from 2020 to
    2024, including both benefits and concerns from medical
    professionals?

3.  Compare the environmental impact of electric vs hybrid vs gas cars

4.  What are the benefits of electric car vs gasoline car

5.  What is renewable energy?

6.  Pros and cons of Agentic AI at work in 2025

7.  Climate change impact on agriculture
