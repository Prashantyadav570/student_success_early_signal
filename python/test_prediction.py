import joblib

model = joblib.load("models/risk_model.pkl")
label_encoder = joblib.load("models/label_encoder.pkl")
features = joblib.load("models/features.pkl")

print("Model loaded successfully!")
print("Features:", features)

import pandas as pd
from sqlalchemy import create_engine

username = "postgres"
password = "root"
host = "localhost"
port = "5432"
database = "student_success_db"

engine = create_engine(
    f"postgresql+psycopg2://{username}:{password}@{host}:{port}/{database}"
)


query = """
SELECT
    s.student_id,
    s.name,
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
WHERE s.student_id = 'STU0001';
"""

student = pd.read_sql(query, engine)

print(student)

X_student = student[features]

prediction_encoded = model.predict(X_student)

prediction = label_encoder.inverse_transform(
    prediction_encoded
)

print("Predicted Risk:", prediction[0])

probabilities = model.predict_proba(X_student)

confidence = probabilities.max()

print("Probability:", confidence)



from datetime import datetime

student_id = str(student.iloc[0]["student_id"])
risk_level = prediction[0]
risk_probability = float(confidence)


from sqlalchemy import text

insert_query = text("""
    INSERT INTO risk_predictions
    (student_id, risk_level, risk_probability)
    VALUES
    (:student_id, :risk_level, :risk_probability)
""")

with engine.begin() as connection:
    connection.execute(
        insert_query,
        {
            "student_id": student_id,
            "risk_level": str(prediction[0]),
            "risk_probability": float(confidence)
        }
    )

print("Prediction saved successfully!")