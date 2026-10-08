
import joblib
import pandas as pd
import streamlit as st
import plotly.express as px

from pathlib import Path
from sqlalchemy import text
from database_connection import get_engine


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Student Success Platform",
    page_icon="🎓",
    layout="wide"
)

st.title("🎓 Student Success Early-Signal Platform")
st.caption(
    "ML-based risk identification with teacher-led intervention "
    "and outcome tracking."
)


# --------------------------------------------------
# LOAD DATABASE AND ML MODEL
# --------------------------------------------------

@st.cache_resource
def load_model_files():
    model_dir = Path(__file__).parent / "models"

    model = joblib.load(model_dir / "risk_model.pkl")
    label_encoder = joblib.load(model_dir / "label_encoder.pkl")
    features = joblib.load(model_dir / "features.pkl")

    return model, label_encoder, features


try:
    engine = get_engine()
    model, label_encoder, features = load_model_files()

    # Test the database connection
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))

except Exception as e:
    st.error("Could not initialize the database or ML model.")
    st.code(str(e))
    st.stop()


# --------------------------------------------------
# HELPER FUNCTIONS
# --------------------------------------------------

def read_sql(query, params=None):
    return pd.read_sql(
        text(query),
        engine,
        params=params or {}
    )


def get_students():
    return read_sql("""
        SELECT student_id, name, course, semester
        FROM students
        ORDER BY student_id
    """)


def get_student_performance(student_id):
    query = """
        SELECT
            s.student_id,
            s.name,
            s.course,
            s.semester,
            sp.attendance,
            sp.internal_marks,
            sp.assignment_completion,
            sp.previous_gpa,
            sp.failed_subjects,
            sp.study_hours,
            sp.previous_semester_marks,
            sp.practical_marks,
            sp.class_participation
        FROM students s
        JOIN student_performance sp
          ON s.student_id = sp.student_id
        WHERE s.student_id = :student_id
    """

    return read_sql(query, {"student_id": student_id})


def latest_predictions():
    return read_sql("""
        SELECT DISTINCT ON (rp.student_id)
            rp.student_id,
            s.name,
            rp.risk_level,
            rp.risk_probability,
            rp.prediction_date
        FROM risk_predictions rp
        JOIN students s
          ON s.student_id = rp.student_id
        ORDER BY rp.student_id, rp.prediction_date DESC,
                 rp.prediction_id DESC
    """)


def save_prediction(student_id, risk_level, probability):
    query = text("""
        INSERT INTO risk_predictions
            (student_id, risk_level, risk_probability)
        VALUES
            (:student_id, :risk_level, :risk_probability)
    """)

    with engine.begin() as connection:
        connection.execute(
            query,
            {
                "student_id": student_id,
                "risk_level": risk_level,
                "risk_probability": probability,
            }
        )


# --------------------------------------------------
# SIDEBAR NAVIGATION
# --------------------------------------------------

page = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard",
        "Risk Prediction",
        "Teacher Intervention",
        "Outcome Tracking",
    ]
)


# --------------------------------------------------
# PAGE 1: DASHBOARD
# --------------------------------------------------

if page == "Dashboard":
    st.header("📊 Dashboard")

    students = get_students()
    predictions = latest_predictions()

    total_students = len(students)
    total_predictions = len(predictions)

    if total_predictions:
        high_risk = int(
            predictions["risk_level"]
            .astype(str)
            .str.lower()
            .eq("high")
            .sum()
        )
    else:
        high_risk = 0

    col1, col2, col3 = st.columns(3)

    col1.metric("Total Students", total_students)
    col2.metric("Students with Predictions", total_predictions)
    col3.metric("Currently High Risk", high_risk)

    st.subheader("Latest Risk Predictions")

    if predictions.empty:
        st.info(
            "No predictions have been saved yet. "
            "Open Risk Prediction to generate the first prediction."
        )
    else:
        chart_data = (
            predictions["risk_level"]
            .astype(str)
            .value_counts()
            .rename_axis("Risk Level")
            .reset_index(name="Students")
        )

        fig = px.bar(
            chart_data,
            x="Risk Level",
            y="Students",
            title="Latest Risk Level Distribution"
        )

        st.plotly_chart(fig, use_container_width=True)

        st.dataframe(
            predictions.sort_values(
                "prediction_date",
                ascending=False
            ),
            use_container_width=True,
            hide_index=True
        )


# --------------------------------------------------
# PAGE 2: RISK PREDICTION
# --------------------------------------------------

elif page == "Risk Prediction":
    st.header("🤖 Student Risk Prediction")

    students = get_students()

    if students.empty:
        st.warning("No students were found in the students table.")
        st.stop()

    student_options = {
        f"{row['student_id']} - {row['name']}": row["student_id"]
        for _, row in students.iterrows()
    }

    selected_label = st.selectbox(
        "Select a student",
        list(student_options.keys())
    )

    student_id = student_options[selected_label]

    student_data = get_student_performance(student_id)

    if student_data.empty:
        st.error(
            "No performance record exists for this student. "
            "Check the student_performance table."
        )
        st.stop()

    row = student_data.iloc[0]

    st.subheader("Student Information")

    col1, col2, col3 = st.columns(3)
    col1.write(f"**Name:** {row['name']}")
    col2.write(f"**Course:** {row['course']}")
    col3.write(f"**Semester:** {row['semester']}")

    with st.expander("View input performance data"):
        st.dataframe(
            student_data[features],
            use_container_width=True,
            hide_index=True
        )

    if st.button("Predict Student Risk", type="primary"):
        try:
            X_student = student_data[features]

            if X_student.isnull().any().any():
                st.error(
                    "This student's performance data contains missing "
                    "values. Clean or impute the data before prediction."
                )
                st.stop()

            prediction_encoded = model.predict(X_student)
            risk_level = str(
                label_encoder.inverse_transform(
                    prediction_encoded
                )[0]
            )

            probabilities = model.predict_proba(X_student)[0]
            predicted_index = list(prediction_encoded).index(
                prediction_encoded[0]
            )
            probability = float(probabilities[predicted_index])

            # Find the probability corresponding to the predicted class.
            class_position = list(model.classes_).index(
                prediction_encoded[0]
            )
            probability = float(probabilities[class_position])

            save_prediction(
                student_id,
                risk_level,
                probability
            )

            st.success("Prediction generated and saved to PostgreSQL.")

            st.subheader("Prediction Result")
            st.metric("Predicted Risk Level", risk_level)
            st.metric(
                "Model Probability for Predicted Class",
                f"{probability:.1%}"
            )

            st.caption(
                "This probability is the model's estimated probability "
                "for its predicted class, not a guarantee of student outcome. "
                "A teacher should review the result before deciding on support."
            )

        except Exception as e:
            st.error("Prediction failed.")
            st.code(str(e))


# --------------------------------------------------
# PAGE 3: TEACHER INTERVENTION
# --------------------------------------------------

elif page == "Teacher Intervention":
    st.header("🧑‍🏫 Teacher Intervention")

    students = get_students()

    if students.empty:
        st.warning("No students were found.")
        st.stop()

    student_options = {
        f"{row['student_id']} - {row['name']}": row["student_id"]
        for _, row in students.iterrows()
    }

    with st.form("intervention_form"):
        selected_label = st.selectbox(
            "Select student",
            list(student_options.keys())
        )

        intervention_type = st.selectbox(
            "Intervention type",
            [
                "Academic Counselling",
                "Extra Classes",
                "Attendance Follow-up",
                "Assignment Support",
                "Parent Meeting",
                "Peer Mentoring",
                "Other",
            ]
        )

        teacher_comment = st.text_area(
            "Teacher comments and planned actions"
        )

        status = st.selectbox(
            "Intervention status",
            ["Planned", "In Progress", "Completed"]
        )

        submitted = st.form_submit_button(
            "Save Intervention",
            type="primary"
        )

    if submitted:
        query = text("""
            INSERT INTO interventions
                (student_id, intervention_type, teacher_comment, status)
            VALUES
                (:student_id, :intervention_type,
                 :teacher_comment, :status)
        """)

        try:
            with engine.begin() as connection:
                connection.execute(
                    query,
                    {
                        "student_id": student_options[selected_label],
                        "intervention_type": intervention_type,
                        "teacher_comment": teacher_comment,
                        "status": status,
                    }
                )

            st.success("Intervention saved successfully.")

        except Exception as e:
            st.error("Could not save intervention.")
            st.code(str(e))

    st.subheader("Previous Interventions")

    interventions = read_sql("""
        SELECT
            i.intervention_id,
            i.student_id,
            s.name,
            i.intervention_type,
            i.teacher_comment,
            i.status,
            i.intervention_date
        FROM interventions i
        JOIN students s ON s.student_id = i.student_id
        ORDER BY i.intervention_date DESC
    """)

    st.dataframe(
        interventions,
        use_container_width=True,
        hide_index=True
    )


# --------------------------------------------------
# PAGE 4: OUTCOME TRACKING
# --------------------------------------------------

elif page == "Outcome Tracking":
    st.header("📈 Student Outcome Tracking")

    students = get_students()

    if students.empty:
        st.warning("No students were found.")
        st.stop()

    student_options = {
        f"{row['student_id']} - {row['name']}": row["student_id"]
        for _, row in students.iterrows()
    }

    with st.form("outcome_form"):
        selected_label = st.selectbox(
            "Select student",
            list(student_options.keys())
        )

        attendance_after = st.number_input(
            "Attendance after intervention (%)",
            min_value=0.0,
            max_value=100.0,
            value=75.0
        )

        marks_after = st.number_input(
            "Marks after intervention",
            min_value=0.0,
            max_value=100.0,
            value=50.0
        )

        risk_level_after = st.selectbox(
            "Current assessed risk level",
            ["Low", "Medium", "High"]
        )

        outcome_status = st.selectbox(
            "Outcome",
            [
                "Improved",
                "No Significant Change",
                "Needs Further Support",
            ]
        )

        notes = st.text_area(
            "Outcome notes"
        )

        submitted = st.form_submit_button(
            "Save Outcome",
            type="primary"
        )

    if submitted:
        query = text("""
            INSERT INTO outcomes
                (
                    student_id,
                    attendance_after,
                    marks_after,
                    risk_level_after,
                    outcome_status,
                    notes
                )
            VALUES
                (
                    :student_id,
                    :attendance_after,
                    :marks_after,
                    :risk_level_after,
                    :outcome_status,
                    :notes
                )
        """)

        try:
            with engine.begin() as connection:
                connection.execute(
                    query,
                    {
                        "student_id": student_options[selected_label],
                        "attendance_after": attendance_after,
                        "marks_after": marks_after,
                        "risk_level_after": risk_level_after,
                        "outcome_status": outcome_status,
                        "notes": notes,
                    }
                )

            st.success("Student outcome saved successfully.")

        except Exception as e:
            st.error("Could not save outcome.")
            st.code(str(e))

    st.subheader("Recorded Outcomes")

    outcomes = read_sql("""
        SELECT
            o.outcome_id,
            o.student_id,
            s.name,
            o.outcome_date,
            o.attendance_after,
            o.marks_after,
            o.risk_level_after,
            o.outcome_status,
            o.notes
        FROM outcomes o
        JOIN students s ON s.student_id = o.student_id
        ORDER BY o.outcome_date DESC
    """)

    st.dataframe(
        outcomes,
        use_container_width=True,
        hide_index=True
    )