# HIV/SRH Education Chatbot

### AI-Powered HIV and Sexual & Reproductive Health Education

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688.svg)](https://fastapi.tiangolo.com/)
[![Status](https://img.shields.io/badge/Project-In%20Development-orange.svg)](#project-status)
[![Languages](https://img.shields.io/badge/Languages-English%20%7C%20Kiswahili-blue.svg)](#key-features)

**HIV/SRH Education Chatbot** is an ongoing software development project aimed at improving access to reliable, understandable, and responsible HIV and Sexual & Reproductive Health (SRH) educational information.

The platform is being developed using Python and FastAPI, with bilingual English and Kiswahili support, a structured health knowledge base, clinical content governance, and a responsive web interface.

**Repository:** https://github.com/Justine-Xagmi/HIV-SRH-Education-Chatbot

---

## Table of Contents

- [Project Overview](#project-overview)
- [Problem Statement](#problem-statement)
- [Project Objectives](#project-objectives)
- [Key Features](#key-features)
- [Technology Stack](#technology-stack)
- [System Architecture](#system-architecture)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Environment Configuration](#environment-configuration)
- [Running the Application](#running-the-application)
- [API Endpoints](#api-endpoints)
- [Knowledge Management and Clinical Governance](#knowledge-management-and-clinical-governance)
- [Testing](#testing)
- [Project Status](#project-status)
- [Planned Improvements](#planned-improvements)
- [Safety and Medical Disclaimer](#safety-and-medical-disclaimer)
- [Contributing](#contributing)
- [Author](#author)

---

## Project Overview

Access to accurate HIV and Sexual & Reproductive Health information remains important for individuals, young people, and communities.

This project explores how conversational artificial intelligence can support health education by providing an accessible interface through which users can ask questions and receive educational information.

The chatbot is designed around a controlled knowledge retrieval approach. Rather than treating every generated response as authoritative medical information, the system uses a structured knowledge base and approval requirements to control which health documents can be used.

The project currently supports development of:

- HIV prevention, testing, and treatment education.
- Sexual and reproductive health education.
- Sexually transmitted infections (STIs).
- Contraception and family planning.
- Pregnancy and reproductive health.
- HIV-related stigma and discrimination.
- English and Kiswahili communication.

## Problem Statement

Many people experience challenges accessing understandable and reliable HIV and Sexual & Reproductive Health information.

These challenges include:

- Limited access to accessible health education resources.
- Language barriers affecting understanding of health information.
- Stigma and misconceptions surrounding HIV.
- Difficulty finding trustworthy information about prevention, testing, and treatment.
- Limited access to educational resources outside healthcare facilities.

This project aims to explore a technology-based approach to making reviewed health education more accessible.

## Project Objectives

1. Develop an AI-powered conversational platform for HIV and SRH education.
2. Support communication in English and Kiswahili.
3. Establish a structured and traceable health knowledge base.
4. Implement controlled knowledge retrieval using approved health information.
5. Introduce clinical review and approval workflows for health content.
6. Develop a responsive web interface for user interaction.
7. Establish a foundation for future deployment, evaluation, and expansion.

## Key Features

The following features represent the current implementation and development direction.

| Feature | Description |
|---|---|
| Bilingual support | English and Kiswahili language support |
| REST API | FastAPI-based backend |
| Interactive interface | Browser-based chatbot interface |
| Knowledge management | Structured health knowledge documents |
| Source verification | Health information source tracking |
| Clinical governance | Review and approval workflows |
| Persistent storage | Database-backed knowledge management |
| Controlled retrieval | Retrieval restricted to eligible approved content |
| API documentation | Interactive Swagger documentation |
| Automated testing | Pytest-based test suite |

Some features are still being refined and require further validation before production use.

## Technology Stack

### Backend
- Python 3.11
- FastAPI
- Pydantic
- SQLAlchemy

### Database and Migrations
- PostgreSQL (where configured)
- Alembic

### Frontend
- HTML5
- CSS3
- JavaScript

### Testing and Development
- Pytest
- Uvicorn
- Visual Studio Code
- Git and GitHub

## System Architecture

The application follows a modular architecture that separates API handling, knowledge management, persistence, and frontend interaction.

```text
                  USER
                   |
                   v
          RESPONSIVE WEB INTERFACE
             HTML / CSS / JS
                   |
                   v
              FASTAPI
                   |
          +--------+--------+
          |                 |
          v                 v
      CHAT API        LANGUAGE API
          |
          v
   KNOWLEDGE RETRIEVAL
          |
          v
   APPROVED KNOWLEDGE BASE
          |
          v
   CLINICAL REVIEW AND
   APPROVAL REQUIREMENTS
          |
          v
       DATABASE
```

The retrieval layer is designed to prevent unapproved health documents from being used as authoritative chatbot knowledge.

## Project Structure

```text
HIV_SRH_Chatbot/
│
├── alembic/
│   └── versions/
│
├── app/
│   ├── api/
│   │   └── chat.py
│   │
│   ├── core/
│   │   └── config.py
│   │
│   ├── db/
│   │   ├── models.py
│   │   └── repository.py
│   │
│   ├── knowledge/
│   │   ├── ingestion.py
│   │   ├── models.py
│   │   ├── persistent_ingestion.py
│   │   ├── persistent_retrieval.py
│   │   └── persistent_review_workflow.py
│   │
│   ├── static/
│   │   ├── index.html
│   │   ├── style.css
│   │   └── app.js
│   │
│   └── main.py
│
├── docs/
│   ├── knowledge/
│   └── project documentation
│
├── tests/
│
├── .env.example
├── .gitignore
├── alembic.ini
├── pytest.ini
├── requirements.txt
└── README.md
```

*The structure above highlights the main project components; additional files and documentation are available in the repository.*

## Getting Started

### Prerequisites

Make sure you have the following installed:

- Python 3.11 or later.
- Git.
- Visual Studio Code (recommended).
- PostgreSQL, if using the PostgreSQL database configuration.

### 1. Clone the repository

```bash
git clone https://github.com/Justine-Xagmi/HIV-SRH-Education-Chatbot.git
```

### 2. Navigate into the project

```bash
cd HIV-SRH-Education-Chatbot
```

### 3. Create a virtual environment

**Windows PowerShell:**

```powershell
python -m venv .venv
```

### 4. Activate the virtual environment

```powershell
.venv\Scripts\Activate.ps1
```

### 5. Install dependencies

```powershell
python -m pip install -r requirements.txt
```

### 6. Configure environment variables

Create your local environment file:

```powershell
Copy-Item .env.example .env
```

Edit `.env` with the appropriate settings for your local environment.

Never commit your actual `.env` file or database credentials to GitHub.

## Environment Configuration

The application uses environment variables for configuration.

Example configuration:

```env
APP_NAME=HIV_SRH_Education_Chatbot
APP_ENV=development
APP_DEBUG=false
DEFAULT_LANGUAGE=en
SUPPORTED_LANGUAGES=en,sw
```

Additional database and application settings may be required depending on your local configuration.

Refer to `.env.example` and the application configuration module for the settings supported by your current version.

## Running the Application

Start the development server:

```powershell
uvicorn app.main:app --reload
```

Once the server starts, open:

| Resource | URL |
|---|---|
| Main application | http://127.0.0.1:8000/ |
| Health check | http://127.0.0.1:8000/health |
| API documentation | http://127.0.0.1:8000/docs |
| Alternative API documentation | http://127.0.0.1:8000/redoc |

## API Endpoints

The backend provides API endpoints for chatbot interaction, language support, and application health monitoring.

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/` | Application information |
| GET | `/health` | Application health check |
| GET | `/api/v1/languages` | Supported language information |
| POST | `/api/v1/chat` | Submit a chatbot question |

### Example Chat Request

```json
{
  "message": "What are the ways to prevent HIV?",
  "language": "en"
}
```

### Example language values

```json
{
  "language": "en"
}
```

```json
{
  "language": "sw"
}
```

The chat API validates incoming requests and returns structured responses containing the answer, language, source information, and applicable safety notice.

## Knowledge Management and Clinical Governance

Health information requires additional safeguards because inaccurate medical information can have serious consequences.

The project incorporates a structured knowledge management approach with:

- Health document registration and ingestion.
- Source identification and traceability.
- Document version management.
- Document lifecycle management.
- Clinical review and approval workflows.
- Retrieval eligibility checks.
- Source permission and verification requirements.

Only knowledge documents meeting the configured approval requirements are eligible for retrieval.

The project is designed to support review by qualified healthcare professionals before health content is approved for use.

## Testing

The project uses Pytest for automated testing.

Run the test suite:

```powershell
python -m pytest
```

For detailed test output:

```powershell
python -m pytest -v
```

The tests cover application functionality, API validation, knowledge management, database operations, and clinical review workflows.

## Project Status

<details>
<summary><strong>Development status — Work in Progress</strong></summary>

This project is actively being developed.

Current implementation includes:

- FastAPI backend.
- English and Kiswahili language configuration.
- Chat API and language endpoints.
- Responsive browser-based interface.
- Structured knowledge management.
- Persistent knowledge ingestion and retrieval components.
- Clinical review and approval workflow foundations.
- Database models and migration support.
- Automated tests.

Further work is required before the system can be considered complete or ready for production use.

</details>

## Planned Improvements

The following areas are part of the ongoing development roadmap:

- Complete and validate the clinical knowledge base.
- Obtain qualified healthcare professional review of health content.
- Improve chatbot response generation and retrieval quality.
- Expand English and Kiswahili educational content.
- Improve conversation history and user session management.
- Introduce user-controlled conversation retention and deletion.
- Strengthen privacy and data protection mechanisms.
- Improve chatbot evaluation and safety testing.
- Conduct usability and performance testing.
- Prepare secure production deployment.
- Explore additional language support.

## Safety and Medical Disclaimer

This project is intended for health education and informational purposes.

The chatbot is not a substitute for professional medical advice, diagnosis, treatment, or consultation with a qualified healthcare professional.

Health information must undergo appropriate verification and clinical review before approval and use.

Users should consult qualified healthcare professionals for personal medical concerns, diagnosis, testing, or treatment decisions.

The application must not be considered a fully validated clinical decision-support system.

## Contributing

Contributions, suggestions, and constructive feedback are welcome.

If you would like to contribute:

1. Fork the repository.
2. Create a feature branch.
3. Implement your changes.
4. Run the automated tests.
5. Submit a pull request describing your changes.

For significant changes, open an issue first to discuss the proposed improvement.

## Author

**Justine Silwimba**

- GitHub: [@Justine-Xagmi](https://github.com/Justine-Xagmi)
- Project Repository: [HIV-SRH-Education-Chatbot](https://github.com/Justine-Xagmi/HIV-SRH-Education-Chatbot)

---

### Project Vision

Making reliable HIV and Sexual & Reproductive Health education more accessible through responsible, inclusive, and clinically governed conversational technology.

**Built with a focus on accessibility, responsible AI, and health education.**

*Status: Under Active Development.*
