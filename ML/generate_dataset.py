"""Generate a synthetic resume-quality dataset for the KNN model.

Features
--------
skills_count          : number of distinct skills listed        (0-25)
years_experience      : total professional experience in years  (0-20)
education_level       : 0=None/School, 1=Diploma, 2=Bachelor, 3=Master/PhD
certifications_count  : number of certifications                (0-10)
project_relevance     : relevance of projects to target role    (0-10)
resume_completeness   : % of resume sections filled in          (0-100)

Label: 0 = Needs Improvement, 1 = Moderate Resume, 2 = Strong Resume
"""

import csv
import os
import random

random.seed(42)

FEATURES = [
    "skills_count",
    "years_experience",
    "education_level",
    "certifications_count",
    "project_relevance",
    "resume_completeness",
]

LABELS = {0: "Needs Improvement", 1: "Moderate Resume", 2: "Strong Resume"}


def score(row):
    """Weighted rubric used to derive the ground-truth label."""
    return (
        min(row["skills_count"], 20) / 20 * 25
        + min(row["years_experience"], 10) / 10 * 20
        + row["education_level"] / 3 * 15
        + min(row["certifications_count"], 5) / 5 * 10
        + row["project_relevance"] / 10 * 15
        + row["resume_completeness"] / 100 * 15
    )


def make_row():
    row = {
        "skills_count": random.randint(0, 25),
        "years_experience": round(random.uniform(0, 20), 1),
        "education_level": random.choice([0, 1, 2, 2, 3]),
        "certifications_count": random.randint(0, 10),
        "project_relevance": random.randint(0, 10),
        "resume_completeness": random.randint(10, 100),
    }
    s = score(row) + random.gauss(0, 3)  # label noise
    row["label"] = 2 if s >= 70 else 1 if s >= 45 else 0
    return row


def main(n=900, out=None):
    out = out or os.path.join(os.path.dirname(__file__), "resume_dataset.csv")
    rows = [make_row() for _ in range(n)]
    with open(out, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FEATURES + ["label"])
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} rows to {out}")
    for k, v in LABELS.items():
        print(f"  {v}: {sum(1 for r in rows if r['label'] == k)}")


if __name__ == "__main__":
    main()
