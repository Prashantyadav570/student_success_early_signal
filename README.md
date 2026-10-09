# Student Success Early-Signal Platform with Human-in-the-Loop Intervention

An academic capstone project that helps identify students who may need additional academic support by combining student-performance indicators, risk prediction, and teacher-led interventions. The platform is built with Python and Streamlit and uses PostgreSQL hosted on Supabase for persistent data storage.

> **Live application:** [Open the Streamlit app] https://prashantyadav570-student-success-early-signal-pythonapp-vvpg2h.streamlit.app/ 
> **GitHub repository:** https://github.com/Prashantyadav570/student_success_early_signal



---

## Table of Contents

- [Project Overview](#project-overview)
- [Objectives](#objectives)
- [Key Features](#key-features)
- [Technology Stack](#technology-stack)
- [System Workflow](#system-workflow)
- [Database Design](#database-design)
- [Dataset](#dataset)
- [Project Structure](#project-structure)
- [Run Locally](#run-locally)
- [Configure Supabase](#configure-supabase)
- [Deploy on Streamlit Community Cloud](#deploy-on-streamlit-community-cloud)
- [Security and Privacy](#security-and-privacy)
- [Limitations and Responsible Use](#limitations-and-responsible-use)
- [Future Enhancements](#future-enhancements)
- [Author](#author)

## Project Overview

Students can experience academic difficulties for many reasons, and warning signs may appear across attendance, marks, assignment completion, study habits, and previous academic performance. This project provides a dashboard to review these indicators, estimate student risk using a trained machine-learning model, and record follow-up actions.

The platform follows a **human-in-the-loop** approach: predictions are intended to support teachers, not replace their professional judgment. Teachers can review a student's circumstances and decide whether an intervention is appropriate.

## Objectives

- Consolidate student and academic-performance information in one application.
- Use available performance indicators to estimate academic risk.
- Present results through an accessible Streamlit interface.
- Record predictions, teacher interventions, and follow-up outcomes in PostgreSQL.
- Support review of whether a student's situation changes after an intervention.
- Demonstrate an end-to-end workflow spanning data, machine learning, web application, and cloud database.

## Key Features

- **Student dashboard:** View student and performance information available in the database.
- **Risk prediction:** Generate a risk estimate for a selected student using the project's trained model.
- **Intervention tracking:** Record teacher follow-up actions and comments.
- **Outcome tracking:** Record follow-up indicators, risk status, and notes after an intervention.
- **Persistent storage:** Store application records in PostgreSQL hosted by Supabase.
- **Cloud access:** Open the deployed Streamlit application in a modern web browser without installing the development environment.

*Available screens and actions depend on the current deployed version of the application.*

## Technology Stack

- **Language:** Python
- **Web application:** Streamlit
- **Data processing:** pandas and the Python data-science libraries used by the project
- **Machine learning:** Trained model and associated preprocessing/label-encoding files stored in the project
- **Database:** PostgreSQL on Supabase
- **Database access:** SQLAlchemy and psycopg2
- **Version control:** Git and GitHub
- **Deployment:** Streamlit Community Cloud

## System Workflow

1. Student records and performance indicators are loaded from the database.
2. The application prepares the selected student's input features.
3. The trained model estimates the student's academic-risk category.
4. The result can be saved to the `risk_predictions` table.
5. A teacher can record a follow-up action in `interventions`.
6. Follow-up information can be recorded in `outcomes`.
7. The saved records can be reviewed later from the application or database.

## Database Design

The application is designed around these PostgreSQL tables:

| Table | Purpose |
|---|---|
| `students` | Student profile details, such as student ID, name, course, and semester |
| `student_performance` | Academic indicators such as attendance, marks, assignment completion, GPA, study hours, and participation |
| `risk_predictions` | Risk-prediction records, including risk level, probability, and prediction date |
| `interventions` | Teacher intervention type, comments, status, and date |
| `outcomes` | Follow-up information, such as later attendance, marks, risk level, outcome status, and notes |

The application connects to the database using the settings configured in Streamlit secrets. The VS Code environment and the deployed Streamlit application must be configured to use the same Supabase project if they are expected to share records.

## Dataset

The project dataset is stored in `Data/student_success_cleaned.csv`. The inspected dataset contains 2,000 records and includes fields such as:

- Student identifier and profile information
- Attendance and internal marks
- Assignment completion
- Previous GPA and previous-semester marks
- Failed subjects
- Study hours
- Practical marks and class participation
- Risk-level label

## Project Structure

The repository includes the main Streamlit application, database connection helper, dataset, and model assets. The layout may evolve as the project is developed.

```text
Capstone_project/
├── Data/
│   └── student_success_cleaned.csv
└── python/
    ├── app.py
    ├── database_connection.py
    ├── models/
    └── .streamlit/
        └── secrets.toml   # Local only; do not commit
```

Other development scripts may be present for testing the database connection, inspecting data, or migrating CSV records to Supabase.

## Run Locally

### 1. Clone the repository

```bash
git clone https://github.com/Prashantyadav570/student_success_early_signal.git
cd student_success_early_signal
```

### 2. Create and activate a virtual environment (recommended)

On Windows:

```bat
py -m venv .venv
.venv\Scripts\activate
```

### 3. Install dependencies

If the repository contains a `requirements.txt`, run:

```bash
pip install -r requirements.txt
```

If it does not, install the packages required by the imports in the project, at minimum the packages used for Streamlit, pandas, SQLAlchemy, and PostgreSQL connectivity. Add a tested `requirements.txt` to the repository so setup is reproducible.

### 4. Configure database secrets

Create this local file if it does not exist:

`python/.streamlit/secrets.toml`

Use the following format, replacing the placeholders with the values shown for your Supabase project:

```toml
[database]
username = "YOUR_SUPABASE_POOLER_USERNAME"
password = "YOUR_SUPABASE_DATABASE_PASSWORD"
host = "YOUR_SUPABASE_POOLER_HOST"
port = "5432"
database = "postgres"
```

For Supabase, copy the correct connection details from the project's **Connect** panel. Do not guess the hostname. Use the Session Pooler details if that is how the application is configured.

### 5. Start the application

From the repository root, run:

```bash
streamlit run python/app.py
```

If you prefer to run from the `python` directory:

```bash
cd python
streamlit run app.py
```

Streamlit will print a local URL in the terminal, usually `http://localhost:8501`.

## Configure Supabase

1. Create or open your Supabase project.
2. Open the SQL Editor and create the database tables expected by the application, if they do not already exist.
3. Copy the correct connection details from **Connect** in the Supabase dashboard.
4. Configure the same values in local `secrets.toml` and in Streamlit Community Cloud's app secrets if both environments should use the same database.
5. Verify that the app can connect and that newly saved predictions, interventions, and outcomes appear in the expected tables.

Do not run migration scripts repeatedly without checking whether they insert duplicate rows. Back up important data before making schema changes.

## Deploy on Streamlit Community Cloud

1. Push the project to GitHub.
2. In Streamlit Community Cloud, create or open the app connected to the repository.
3. Set the application entry point to `python/app.py`.
4. Add the database configuration under **Manage app → Settings → Secrets** using TOML format.
5. Deploy or reboot the app and review the logs if an error appears.
6. Test a prediction and an outcome from the deployed URL, then verify that the corresponding rows appear in the intended Supabase project.

The live URL should be added near the top of this README after deployment.

## Security and Privacy

- **Never commit secrets.** Do not push `secrets.toml`, database passwords, private connection strings, or API keys to GitHub.
- Confirm `.streamlit/secrets.toml` is ignored by Git. If a credential was committed, rotate it; deleting it from the latest commit alone may not remove it from Git history.
- Use a database account with only the permissions the application requires.
- Avoid publishing personally identifiable student information. Follow institutional rules and applicable privacy requirements.
- Keep dependencies updated and review access permissions for the deployed application and database.

## Limitations and Responsible Use

- A model's output is an estimate, not a certainty or a final judgment about a student.
- Model quality depends on dataset quality, representativeness, feature validity, and ongoing evaluation.
- A risk category should prompt review and supportive follow-up, not punishment or automatic decisions.
- Teachers or authorized staff should consider context, check data accuracy, and make intervention decisions.
- This capstone should not be treated as a validated production system for high-stakes decisions without additional evaluation, governance, and privacy review.

## Future Enhancements

- Add model evaluation metrics and explainability for individual predictions.
- Add role-based access for teachers and administrators.
- Improve audit logging and validation of intervention/outcome entries.
- Add automated reminders for students who need follow-up.
- Track intervention effectiveness over time using clearly defined outcome measures.
- Add automated tests and a reproducible dependency file.
- Improve data anonymization and data-retention controls.

## Author

**Prashant Yadav**  
BCA Capstone Project

- **GitHub:** https://github.com/Prashantyadav570/student_success_early_signal
- **Live application:** (https://prashantyadav570-student-success-early-signal-pythonapp-vvpg2h.streamlit.app/)

---

If you use or extend this project, review the dataset permissions, environment configuration, and responsible-use considerations before deployment.
