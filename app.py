import os
import json
import pickle
import hashlib
import secrets
import re
from datetime import datetime
from functools import wraps

from dotenv import load_dotenv
from openai import OpenAI

import numpy as np
import mysql.connector

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    jsonify
)


load_dotenv()


BASE = os.path.dirname(os.path.abspath(__file__))


def env_int(name, default):
    try:
        return int(os.getenv(name, default))
    except (TypeError, ValueError):
        return default


app = Flask(__name__)

app.secret_key = os.getenv(
    "SECRET_KEY",
    "resumeiq-development-secret"
)


# =========================================================
# DATABASE
# =========================================================

DB_CONFIG = {
    "host": os.getenv("MYSQL_HOST", "localhost"),
    "port": env_int("MYSQL_PORT", 3306),
    "user": os.getenv("MYSQL_USER", "root"),
    "password": os.getenv("MYSQL_PASSWORD", ""),
    "database": os.getenv(
        "MYSQL_DATABASE",
        "ai_resume_builder"
    ),
    "connection_timeout": env_int("MYSQL_CONNECT_TIMEOUT", 10)
}

MYSQL_SSL_CA = os.getenv("MYSQL_SSL_CA", "").strip()

if MYSQL_SSL_CA:
    DB_CONFIG["ssl_ca"] = MYSQL_SSL_CA


def db():
    return mysql.connector.connect(**DB_CONFIG)


# =========================================================
# OPENROUTER / OPENAI COMPATIBLE AI
# =========================================================

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()

OPENAI_BASE_URL = os.getenv(
    "OPENAI_BASE_URL",
    "https://openrouter.ai/api/v1"
).strip()

OPENAI_MODEL = os.getenv(
    "OPENAI_MODEL",
    "openai/gpt-4o-mini"
).strip()


client = None

if OPENAI_API_KEY:
    client = OpenAI(
        api_key=OPENAI_API_KEY,
        base_url=OPENAI_BASE_URL
    )


# =========================================================
# KNN MODEL
# =========================================================

MODEL_PATH = os.path.join(
    BASE,
    "models",
    "resume_knn_model.pkl"
)


with open(MODEL_PATH, "rb") as f:
    MODEL = pickle.load(f)


FEATURES = MODEL["features"]
LABELS = MODEL["labels"]


try:
    with open(
        os.path.join(
            BASE,
            "ML",
            "knn_model.json"
        ),
        encoding="utf-8"
    ) as f:
        MODEL_META = json.load(f)

except Exception:
    MODEL_META = {
        "accuracy": 0.0
    }


# =========================================================
# PASSWORD
# =========================================================

def hash_password(password, salt=None):

    salt = salt or secrets.token_hex(16)

    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode(),
        salt.encode(),
        120000
    ).hex()

    return f"{salt}${digest}"


def verify_password(password, stored):

    try:

        salt, digest = stored.split(
            "$",
            1
        )

        calculated = hash_password(
            password,
            salt
        ).split(
            "$",
            1
        )[1]

        return secrets.compare_digest(
            calculated,
            digest
        )

    except ValueError:
        return False


# =========================================================
# LOGIN REQUIRED
# =========================================================

def login_required(fn):

    @wraps(fn)
    def wrapper(*args, **kwargs):

        if "user_id" not in session:
            return redirect(
                url_for("auth")
            )

        return fn(*args, **kwargs)

    return wrapper


# =========================================================
# HELPERS
# =========================================================

def clean(value):
    return (value or "").strip()


def rows(cur):

    cols = [
        d[0]
        for d in cur.description
    ]

    return [
        dict(zip(cols, row))
        for row in cur.fetchall()
    ]


def resume_or_404(cur, resume_id):

    cur.execute(
        """
        SELECT *
        FROM resumes
        WHERE id=%s
        AND user_id=%s
        """,
        (
            resume_id,
            session["user_id"]
        )
    )

    return cur.fetchone()


# =========================================================
# GET RESUME DATA
# =========================================================

def get_resume_data(resume_id):

    conn = db()

    cur = conn.cursor(
        dictionary=True
    )

    try:

        cur.execute(
            """
            SELECT *
            FROM resumes
            WHERE id=%s
            AND user_id=%s
            """,
            (
                resume_id,
                session["user_id"]
            )
        )

        resume = cur.fetchone()

        if not resume:
            return None

        data = dict(resume)

        for table in (
            "education",
            "experience",
            "skills",
            "projects",
            "certifications"
        ):

            cur.execute(
                f"""
                SELECT *
                FROM {table}
                WHERE resume_id=%s
                ORDER BY id
                """,
                (resume_id,)
            )

            data[table] = cur.fetchall()

        return data

    finally:

        cur.close()
        conn.close()


# =========================================================
# EDUCATION LEVEL
# =========================================================

def education_level(data):

    levels = [
        e.get("level", "")
        for e in data.get(
            "education",
            []
        )
    ]

    if any(
        x in (
            "Master's",
            "Master",
            "PhD",
            "Doctorate"
        )
        for x in levels
    ):
        return 3

    if any(
        x in (
            "Bachelor's",
            "Bachelor",
            "B.Tech",
            "B.E."
        )
        for x in levels
    ):
        return 2

    if any(
        x in (
            "Diploma",
            "Intermediate",
            "12th"
        )
        for x in levels
    ):
        return 1

    return 0


# =========================================================
# EXPERIENCE YEARS
# =========================================================

def years_experience(data):

    total = 0.0

    for experience in data.get(
        "experience",
        []
    ):

        try:

            start = int(
                experience.get(
                    "start_year"
                ) or 0
            )

            end = experience.get(
                "end_year"
            ) or ""

            if str(end).lower() in (
                "present",
                "current"
            ):

                end_year = datetime.now().year

            else:

                end_year = int(end)

            if (
                start > 0
                and end_year >= start
            ):

                total += (
                    end_year - start
                )

        except (
            ValueError,
            TypeError
        ):
            pass

    return round(
        max(0, total),
        1
    )


# =========================================================
# FEATURE VECTOR
# =========================================================

def feature_vector(data):

    skills_count = len([
        skill
        for skill in data.get(
            "skills",
            []
        )
        if clean(
            skill.get("skill")
        )
    ])

    exp_years = years_experience(
        data
    )

    cert_count = len([
        cert
        for cert in data.get(
            "certifications",
            []
        )
        if clean(
            cert.get("certification")
        )
    ])

    projects = [
        project
        for project in data.get(
            "projects",
            []
        )
        if clean(
            project.get("project_name")
        )
    ]

    if projects:

        project_relevance = round(
            sum(
                max(
                    0,
                    min(
                        10,
                        int(
                            project.get(
                                "relevance"
                            ) or 0
                        )
                    )
                )
                for project in projects
            )
            / len(projects),
            1
        )

    else:

        project_relevance = 0

    checks = [

        clean(
            data.get("full_name")
        ),

        clean(
            data.get("email")
        ),

        clean(
            data.get("phone")
        ),

        clean(
            data.get("location")
        ),

        clean(
            data.get("target_role")
        ),

        clean(
            data.get("summary")
        ),

        clean(
            data.get("objective")
        ),

        len(
            data.get(
                "education",
                []
            )
        ) > 0,

        len(
            data.get(
                "experience",
                []
            )
        ) > 0,

        len(
            data.get(
                "skills",
                []
            )
        ) > 0,

        len(
            data.get(
                "projects",
                []
            )
        ) > 0,

        len(
            data.get(
                "certifications",
                []
            )
        ) > 0

    ]

    filled = sum(
        bool(x)
        for x in checks
    )

    completeness = round(
        filled / len(checks) * 100
    )

    return [
        skills_count,
        exp_years,
        education_level(data),
        cert_count,
        project_relevance,
        completeness
    ]


# =========================================================
# KNN PREDICTION
# =========================================================

def predict(features):

    x = np.array(
        [features],
        dtype=float
    )

    scaled = MODEL[
        "scaler"
    ].transform(x)

    pred = int(
        MODEL[
            "knn"
        ].predict(scaled)[0]
    )

    probabilities = MODEL[
        "knn"
    ].predict_proba(scaled)[0]

    confidence = float(
        max(probabilities) * 100
    )

    category = LABELS[pred]

    rubric = round(

        min(
            features[0],
            20
        ) / 20 * 25

        +

        min(
            features[1],
            10
        ) / 10 * 20

        +

        features[2] / 3 * 15

        +

        min(
            features[3],
            5
        ) / 5 * 10

        +

        features[4] / 10 * 15

        +

        features[5] / 100 * 15
    )

    return (
        category,
        confidence,
        rubric,
        pred
    )


# =========================================================
# RECOMMENDATIONS
# =========================================================

def recommendations(features):

    skills, years, education, certs, project, completeness = features

    output = []

    if skills < 8:

        output.append(
            "List at least 8 concrete skills — tools, languages, frameworks."
        )

    if project < 6:

        output.append(
            "Raise project relevance: highlight projects closest to your target role."
        )

    if years < 2:

        output.append(
            "With limited experience, add more projects to demonstrate ability."
        )

    if completeness < 80:

        output.append(
            "Complete more resume sections to improve completeness."
        )

    if certs < 2:

        output.append(
            "Add relevant certifications when available."
        )

    if not output:

        output.append(
            "Strong feature coverage. Keep achievements measurable and role-specific."
        )

    return output


# =========================================================
# GENERATIVE AI
# =========================================================

def llm_generate(kind, payload):

    if client is None:

        return (
            None,
            "Generative AI is not configured. "
            "Set OPENAI_API_KEY in your .env file."
        )

    role = clean(
        payload.get(
            "target_role"
        )
    )

    if not role:
        role = "the target role"


    # -----------------------------------------------------
    # SUMMARY
    # -----------------------------------------------------

    if kind == "summary":

        instruction = (
            "You are a professional resume writer. "
            "Write a concise, ATS-friendly professional "
            f"resume summary for a candidate targeting {role}. "
            "Use ONLY the supplied facts. "
            "Do not invent employers, degrees, dates, "
            "metrics, technologies, achievements or experience. "
            "Return only the final summary text."
        )


    # -----------------------------------------------------
    # OBJECTIVE
    # -----------------------------------------------------

    elif kind == "objective":

        instruction = (
            "You are a professional resume writer. "
            f"Write a concise career objective for a candidate "
            f"targeting {role}. "
            "Use ONLY the supplied facts. "
            "Avoid generic filler and do not invent experience. "
            "Return only the final objective text."
        )


    # -----------------------------------------------------
    # SKILL
    # -----------------------------------------------------

    elif kind == "skill":

        skill = clean(
            payload.get(
                "skill"
            )
        )

        instruction = (
            "You are a professional resume writer. "
            f'Write one concise ATS-friendly description for '
            f'the skill "{skill}" for a resume targeting {role}. '
            "Do not invent experience, certifications or achievements. "
            "Return only the description."
        )


    # -----------------------------------------------------
    # PROJECT
    # -----------------------------------------------------

    else:

        instruction = (
            "You are a professional resume writer. "
            f"Write a concise ATS-friendly project description "
            f"for a resume targeting {role}. "
            "Mention only the supplied technologies and project facts. "
            "Do not invent results, users, numbers or achievements. "
            "Return only the final project description."
        )


    try:

        response = client.chat.completions.create(

            model=OPENAI_MODEL,

            messages=[

                {
                    "role": "system",
                    "content": instruction
                },

                {
                    "role": "user",
                    "content": json.dumps(
                        payload,
                        ensure_ascii=False
                    )
                }

            ],

            temperature=0.3,

            max_tokens=180

        )


        if not response.choices:

            return (
                None,
                "The AI API returned no choices."
            )


        text = (
            response
            .choices[0]
            .message
            .content
        )


        if not text:

            return (
                None,
                "The AI API returned empty content."
            )


        return (
            text.strip(),
            None
        )


    except Exception as exc:

        print(
            "OPENROUTER ERROR:",
            repr(exc)
        )

        return (
            None,
            f"Generative AI request failed: {exc}"
        )


# =========================================================
# GLOBALS
# =========================================================

@app.context_processor
def inject_globals():

    return {
        "user_email": session.get(
            "email",
            ""
        )
    }


# =========================================================
# HOME
# =========================================================

@app.route("/")
def index():

    if "user_id" in session:

        return redirect(
            url_for("dashboard")
        )

    return render_template(
        "index.html"
    )


# =========================================================
# AUTH
# =========================================================

@app.route("/auth")
def auth():

    return render_template(
        "auth.html"
    )


# =========================================================
# REGISTER
# =========================================================

@app.post("/api/register")
def register():

    data = request.json or {}

    name = clean(
        data.get("name")
    )

    email = clean(
        data.get("email")
    ).lower()

    password = data.get(
        "password",
        ""
    )

    confirm_password = data.get(
        "confirm_password",
        ""
    )


    if not name:

        return jsonify(
            error="Full name is required."
        ), 400


    if not re.fullmatch(
        r"[A-Za-z][A-Za-z .'-]{1,99}",
        name
    ):

        return jsonify(
            error="Enter a valid full name."
        ), 400


    if not re.fullmatch(
        r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$",
        email
    ):

        return jsonify(
            error="Enter a valid email address."
        ), 400


    if len(password) < 8:

        return jsonify(
            error="Password must contain at least 8 characters."
        ), 400


    if not re.search(
        r"[A-Z]",
        password
    ):

        return jsonify(
            error="Password must contain at least one uppercase letter."
        ), 400


    if not re.search(
        r"[a-z]",
        password
    ):

        return jsonify(
            error="Password must contain at least one lowercase letter."
        ), 400


    if not re.search(
        r"\d",
        password
    ):

        return jsonify(
            error="Password must contain at least one number."
        ), 400


    if not re.search(
        r"[^A-Za-z0-9]",
        password
    ):

        return jsonify(
            error="Password must contain at least one special character."
        ), 400


    if password != confirm_password:

        return jsonify(
            error="Passwords do not match."
        ), 400


    conn = db()

    cur = conn.cursor()

    try:

        cur.execute(
            """
            SELECT id
            FROM users
            WHERE email=%s
            """,
            (email,)
        )

        if cur.fetchone():

            return jsonify(
                error="An account with this email already exists."
            ), 409


        cur.execute(
            """
            INSERT INTO users(
                name,
                email,
                password_hash
            )
            VALUES(%s,%s,%s)
            """,
            (
                name,
                email,
                hash_password(
                    password
                )
            )
        )

        conn.commit()

        uid = cur.lastrowid

        session["user_id"] = uid

        session["email"] = email

        session["name"] = name

        return jsonify(
            ok=True
        )


    except mysql.connector.Error as exc:

        conn.rollback()

        print(
            "REGISTER DATABASE ERROR:",
            repr(exc)
        )

        return jsonify(
            error=str(exc)
        ), 500


    finally:

        cur.close()
        conn.close()


# =========================================================
# LOGIN
# =========================================================

@app.post("/api/login")
def login():

    data = request.json or {}

    email = clean(
        data.get("email")
    ).lower()

    password = data.get(
        "password",
        ""
    )


    conn = db()

    cur = conn.cursor(
        dictionary=True
    )

    try:

        cur.execute(
            """
            SELECT *
            FROM users
            WHERE email=%s
            """,
            (email,)
        )

        user = cur.fetchone()


        if not user:

            return jsonify(
                error="Invalid email or password."
            ), 401


        if not verify_password(
            password,
            user["password_hash"]
        ):

            return jsonify(
                error="Invalid email or password."
            ), 401


        session["user_id"] = user["id"]

        session["email"] = user["email"]

        session["name"] = user.get(
            "name",
            ""
        )


        return jsonify(
            ok=True
        )


    finally:

        cur.close()
        conn.close()


# =========================================================
# LOGOUT
# =========================================================

@app.get("/logout")
def logout():

    session.clear()

    return redirect(
        url_for("index")
    )


# =========================================================
# DASHBOARD
# =========================================================

@app.route("/dashboard")
@login_required
def dashboard():

    conn = db()

    cur = conn.cursor(
        dictionary=True
    )

    try:

        cur.execute(
            """
            SELECT
                id,
                title,
                template,
                score,
                category,
                updated_at
            FROM resumes
            WHERE user_id=%s
            ORDER BY updated_at DESC
            """,
            (
                session["user_id"],
            )
        )

        resumes = cur.fetchall()

    finally:

        cur.close()
        conn.close()


    return render_template(
        "dashboard.html",
        resumes=resumes
    )


# =========================================================
# CREATE RESUME
# =========================================================

@app.post("/api/resumes")
@login_required
def create_resume():

    conn = db()

    cur = conn.cursor()

    try:

        cur.execute(
            """
            INSERT INTO resumes(
                user_id,
                title,
                template
            )
            VALUES(%s,%s,%s)
            """,
            (
                session["user_id"],
                "Untitled Resume",
                "modern"
            )
        )

        conn.commit()

        resume_id = cur.lastrowid

        return jsonify(
            id=resume_id,
            redirect=url_for(
                "editor",
                resume_id=resume_id
            )
        )

    finally:

        cur.close()
        conn.close()


# =========================================================
# DELETE RESUME
# =========================================================

@app.post(
    "/api/resumes/<int:resume_id>/delete"
)
@login_required
def delete_resume(resume_id):

    conn = db()

    cur = conn.cursor()

    try:

        cur.execute(
            """
            DELETE FROM resumes
            WHERE id=%s
            AND user_id=%s
            """,
            (
                resume_id,
                session["user_id"]
            )
        )

        conn.commit()

        return jsonify(
            ok=True
        )

    finally:

        cur.close()
        conn.close()


# =========================================================
# EDITOR
# =========================================================

@app.route(
    "/resume/<int:resume_id>"
)
@login_required
def editor(resume_id):

    data = get_resume_data(
        resume_id
    )

    if not data:

        return redirect(
            url_for("dashboard")
        )


    features = feature_vector(
        data
    )


    if data.get("category"):

        category = data["category"]

        confidence = float(
            data.get(
                "confidence"
            ) or 0
        )

        rubric = int(
            data.get(
                "score"
            ) or 0
        )

    else:

        category, confidence, rubric, _ = predict(
            features
        )

        if not data.get(
            "evaluated_at"
        ):

            category = "Not evaluated"


    return render_template(

        "editor.html",

        data=data,

        features=features,

        category=category,

        confidence=confidence,

        rubric=rubric,

        accuracy=float(
            MODEL_META.get(
                "accuracy",
                0
            )
        ) * 100
    )


# =========================================================
# GET RESUME API
# =========================================================

@app.get(
    "/api/resumes/<int:resume_id>"
)
@login_required
def api_get_resume(resume_id):

    data = get_resume_data(
        resume_id
    )

    if data:

        return jsonify(
            data
        ), 200


    return jsonify(
        error="Not found"
    ), 404


# =========================================================
# UPDATE RESUME
# =========================================================

@app.put(
    "/api/resumes/<int:resume_id>"
)
@login_required
def api_update_resume(resume_id):

    body = request.json or {}

    conn = db()

    cur = conn.cursor()

    try:

        cur.execute(
            """
            SELECT id
            FROM resumes
            WHERE id=%s
            AND user_id=%s
            """,
            (
                resume_id,
                session["user_id"]
            )
        )

        if not cur.fetchone():

            return jsonify(
                error="Not found"
            ), 404


        fields = [

            "title",
            "template",
            "target_role",
            "full_name",
            "email",
            "phone",
            "location",
            "website",
            "github",
            "linkedin",
            "summary",
            "objective"

        ]


        values = [

            body.get(
                field,
                ""
            )

            for field in fields

        ]


        query = (
            "UPDATE resumes SET "
            +
            ",".join(
                f"{field}=%s"
                for field in fields
            )
            +
            """
            WHERE id=%s
            AND user_id=%s
            """
        )


        cur.execute(
            query,
            values + [
                resume_id,
                session["user_id"]
            ]
        )


        tables = [

            "education",
            "experience",
            "skills",
            "projects",
            "certifications"

        ]


        for table in tables:

            cur.execute(
                f"""
                DELETE FROM {table}
                WHERE resume_id=%s
                """,
                (resume_id,)
            )


            items = body.get(
                table,
                []
            ) or []


            for item in items:


                # -----------------------------------------
                # EDUCATION
                # -----------------------------------------

                if table == "education":

                    cur.execute(
                        """
                        INSERT INTO education(
                            resume_id,
                            institution,
                            degree,
                            field_of_study,
                            level,
                            start_year,
                            end_year,
                            grade
                        )
                        VALUES(
                            %s,%s,%s,%s,
                            %s,%s,%s,%s
                        )
                        """,
                        (
                            resume_id,

                            item.get(
                                "institution",
                                ""
                            ),

                            item.get(
                                "degree",
                                ""
                            ),

                            item.get(
                                "field_of_study",
                                ""
                            ),

                            item.get(
                                "level",
                                "Bachelor's"
                            ),

                            item.get(
                                "start_year",
                                ""
                            ),

                            item.get(
                                "end_year",
                                ""
                            ),

                            item.get(
                                "grade",
                                ""
                            )
                        )
                    )


                # -----------------------------------------
                # EXPERIENCE
                # -----------------------------------------

                elif table == "experience":

                    cur.execute(
                        """
                        INSERT INTO experience(
                            resume_id,
                            company,
                            role,
                            start_year,
                            end_year,
                            responsibilities
                        )
                        VALUES(
                            %s,%s,%s,
                            %s,%s,%s
                        )
                        """,
                        (
                            resume_id,

                            item.get(
                                "company",
                                ""
                            ),

                            item.get(
                                "role",
                                ""
                            ),

                            item.get(
                                "start_year",
                                ""
                            ),

                            item.get(
                                "end_year",
                                ""
                            ),

                            item.get(
                                "responsibilities",
                                ""
                            )
                        )
                    )


                # -----------------------------------------
                # SKILLS
                # -----------------------------------------

                elif table == "skills":

                    cur.execute(
                        """
                        INSERT INTO skills(
                            resume_id,
                            skill,
                            description
                        )
                        VALUES(
                            %s,%s,%s
                        )
                        """,
                        (
                            resume_id,

                            item.get(
                                "skill",
                                ""
                            ),

                            item.get(
                                "description",
                                ""
                            )
                        )
                    )


                # -----------------------------------------
                # PROJECTS
                # -----------------------------------------

                elif table == "projects":

                    try:

                        relevance = int(
                            item.get(
                                "relevance"
                            ) or 0
                        )

                    except (
                        ValueError,
                        TypeError
                    ):

                        relevance = 0


                    relevance = max(
                        0,
                        min(
                            10,
                            relevance
                        )
                    )


                    cur.execute(
                        """
                        INSERT INTO projects(
                            resume_id,
                            project_name,
                            tech_stack,
                            relevance,
                            description
                        )
                        VALUES(
                            %s,%s,%s,%s,%s
                        )
                        """,
                        (
                            resume_id,

                            item.get(
                                "project_name",
                                ""
                            ),

                            item.get(
                                "tech_stack",
                                ""
                            ),

                            relevance,

                            item.get(
                                "description",
                                ""
                            )
                        )
                    )


                # -----------------------------------------
                # CERTIFICATIONS
                # -----------------------------------------

                elif table == "certifications":

                    cur.execute(
                        """
                        INSERT INTO certifications(
                            resume_id,
                            certification,
                            issuer,
                            year
                        )
                        VALUES(
                            %s,%s,%s,%s
                        )
                        """,
                        (
                            resume_id,

                            item.get(
                                "certification",
                                ""
                            ),

                            item.get(
                                "issuer",
                                ""
                            ),

                            item.get(
                                "year",
                                ""
                            )
                        )
                    )


        conn.commit()

        return jsonify(
            ok=True
        )


    except mysql.connector.Error as exc:

        conn.rollback()

        print(
            "RESUME UPDATE DATABASE ERROR:",
            repr(exc)
        )

        return jsonify(
            error=str(exc)
        ), 500


    finally:

        cur.close()
        conn.close()


# =========================================================
# KNN EVALUATION
# =========================================================

@app.post(
    "/api/resumes/<int:resume_id>/evaluate"
)
@login_required
def evaluate(resume_id):

    data = get_resume_data(
        resume_id
    )

    if not data:

        return jsonify(
            error="Not found"
        ), 404


    features = feature_vector(
        data
    )


    category, confidence, rubric, _ = predict(
        features
    )


    conn = db()

    cur = conn.cursor()

    try:

        cur.execute(
            """
            UPDATE resumes
            SET
                score=%s,
                category=%s,
                confidence=%s,
                evaluated_at=NOW()
            WHERE id=%s
            AND user_id=%s
            """,
            (
                rubric,
                category,
                confidence,
                resume_id,
                session["user_id"]
            )
        )

        conn.commit()

    finally:

        cur.close()
        conn.close()


    return jsonify(

        category=category,

        confidence=round(
            confidence,
            1
        ),

        rubric=rubric,

        accuracy=round(
            float(
                MODEL_META.get(
                    "accuracy",
                    0
                )
            ) * 100,
            1
        ),

        features=features,

        recommendations=recommendations(
            features
        )
    )


# =========================================================
# GENERATIVE AI API
# =========================================================

@app.post("/api/generate")
@login_required
def generate():

    body = request.json or {}

    kind = body.get(
        "kind",
        "summary"
    )

    payload = body.get(
        "payload",
        {}
    )


    if not isinstance(
        payload,
        dict
    ):

        return jsonify(
            error="Invalid payload."
        ), 400


    text, error = llm_generate(
        kind,
        payload
    )


    if text:

        return jsonify(
            text=text
        ), 200


    return jsonify(
        error=error or "AI generation failed."
    ), 503


# =========================================================
# PRINT / PDF
# =========================================================

@app.get(
    "/resume/<int:resume_id>/print"
)
@login_required
def print_resume(resume_id):

    data = get_resume_data(
        resume_id
    )

    if not data:

        return redirect(
            url_for("dashboard")
        )


    return render_template(
        "resume_print.html",
        data=data
    )


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":

    app.run(
        host=os.getenv("HOST", "0.0.0.0"),
        port=env_int("PORT", 5000),
        debug=os.getenv("FLASK_DEBUG", "0") == "1"
    )
