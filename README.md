# 🤖 CodeForge AI

**CodeForge AI is an autonomous, multi-agent platform for intelligent codebase modernization. It acts as a team of expert AI software engineers that analyzes, refactors, documents, and tests your legacy code, automatically bringing it up to modern standards.**

Unlike simple linters or script-based refactoring tools, CodeForge AI uses a sophisticated **Lead Architect** model to create a strategic plan and deploys a team of **Specialist Agents** to execute it. This allows it to handle complex projects across multiple languages with minimal human intervention.



---

## 🚀 Key Features

* **True Autonomy**: Set your high-level goals (e.g., "Upgrade to Python 3.12 and add full test coverage"), and CodeForge AI handles the entire process.
* **Multi-Agent Architecture**: A `Lead Architect` LLM plans the work, and specialist SLMs for syntax, dependencies, documentation, testing, and security execute it in parallel.
* **Comprehensive Modernization**: Goes beyond syntax changes to manage dependencies, write Google-style docstrings, generate `pytest` unit tests, and review for common security vulnerabilities.
* **Multi-Language Support**: Extensible architecture supporting Python, JavaScript, TypeScript, and more.
* **Enterprise-Ready**: Deployed via Docker and designed for scalability with a REST API, job queue, and persistent database.
* **Interactive Tools**: Manage modernization jobs through a powerful CLI with rich progress tracking or a real-time web dashboard.

---

## 🏗️ System Architecture

CodeForge AI is built on a robust, scalable architecture designed for production workloads.

1.  **Interfaces (CLI / Web UI)**: Users submit modernization jobs through a developer-friendly CLI or an interactive web dashboard.
2.  **API Server (FastAPI)**: A high-performance async API server accepts jobs, places them in a queue, and provides status updates.
3.  **Job Management (Postgres & Redis)**: Job details and status are persisted in a PostgreSQL database, while Redis can be used for caching and message brokering.
4.  **Core AI System (CodeForgeAI)**:
    * **Lead Architect (Controller LLM)**: Analyzes the codebase against the user's goals and generates a detailed, multi-step execution plan.
    * **Specialist Agents (SLMs)**: A team of agents execute tasks in parallel, each focused on a specific domain (refactoring, testing, etc.).
5.  **Tools (GitPython / File System)**: Agents use tools to interact with the codebase, cloning the repository, reading/writing files, and committing changes to a new branch.



---

## 🎯 Go-to-Market & Business Model

CodeForge AI is positioned to solve the multi-billion dollar problem of technical debt for businesses of all sizes.

* **Target Market**: Companies with codebases older than 5 years, those facing challenges with developer velocity, and organizations with strict compliance or security requirements.
* **SaaS Tiers**:
    * **Developer ($49/mo)**: For individuals and small teams.
    * **Team ($199/mo)**: For growing businesses needing advanced features and collaboration.
    * **Enterprise (Custom)**: For large organizations requiring on-premise deployment, custom-trained agents, and dedicated support.

---

## 🔧 Quick Start with Docker

The fastest way to get CodeForge AI running is with Docker.

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/your-username/codeforge-ai.git](https://github.com/your-username/codeforge-ai.git)
    cd codeforge-ai
    ```

2.  **Set up environment variables:**
    ```bash
    cp .env.example .env
    ```
    Now, edit the `.env` file and add your `OPENAI_API_KEY`.

3.  **Build and run the containers:**
    ```bash
    docker-compose up --build -d
    ```

4.  **Access the services:**
    * **Web Dashboard**: [http://localhost:8080](http://localhost:8080)
    * **API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 💻 CLI Usage

The CLI is a powerful tool for developers to interact with CodeForge AI directly from the terminal.

* **Analyze a project (dry run):**
    ```bash
    python cli.py modernize [https://github.com/user/repo](https://github.com/user/repo) \
      -g "Upgrade to Python 3.11" \
      -g "Add comprehensive documentation" \
      --dry-run
    ```

* **Execute a full modernization:**
    ```bash
    python cli.py modernize [https://github.com/user/repo](https://github.com/user/repo) \
      -g "Upgrade to Python 3.11" \
      -g "Generate unit tests with pytest" \
      --branch "feat/auto-upgrade-py311"
    ```

* **Generate a local analysis report:**
    ```bash
    python cli.py analyze /path/to/your/local/project
    ```