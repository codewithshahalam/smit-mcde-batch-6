# Task 11 - Multi-File Student Gradebook
import csv
import os


def grade_for(average):
    for cutoff, letter in ((85, "A"), (70, "B"), (55, "C"), (40, "D")):
        if average >= cutoff:
            return letter
    return "F"


def _sort_key(student_id):
    return (0, int(student_id), student_id) if student_id.isdigit() else (1, 0, student_id)


def build_gradebook(students_path, scores_path, report_path):

    students = {}
    with open(students_path, newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames or {"student_id", "name"} - set(reader.fieldnames):
            raise ValueError("students.csv must have columns: student_id,name")
        for row in reader:
            sid = (row["student_id"] or "").strip()
            if sid and sid not in students:
                students[sid] = row["name"].strip()

    marks = {sid: {} for sid in students}
    rejected = []
    with open(scores_path, newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames or {"student_id", "subject", "marks"} - set(reader.fieldnames):
            raise ValueError("scores.csv must have columns: student_id,subject,marks")
        for row in reader:
            sid = (row["student_id"] or "").strip()
            subject = (row["subject"] or "").strip()
            reason = None
            value = None
            if sid not in students:
                reason = "unknown student ID"
            elif not subject:
                reason = "missing subject"
            else:
                try:
                    value = float(row["marks"])
                    if not 0 <= value <= 100 or value != value:
                        reason = "marks must be between 0 and 100"
                except (TypeError, ValueError):
                    reason = "marks is not a number"
                if reason is None and subject.lower() in {s.lower() for s in marks[sid]}:
                    reason = "duplicate student-subject entry"
            if reason:
                rejected.append({"line": reader.line_num, "student_id": sid,
                                 "subject": subject, "marks": row["marks"],
                                 "reason": reason})
            else:
                marks[sid][subject] = value

    scored, unscored = [], []
    for sid in students:
        if marks[sid]:
            avg = sum(marks[sid].values()) / len(marks[sid])
            scored.append((sid, avg))
        else:
            unscored.append(sid)
    scored.sort(key=lambda item: (-item[1], _sort_key(item[0])))
    unscored.sort(key=_sort_key)

    report = []
    for rank, (sid, avg) in enumerate(scored, start=1):
        report.append({"student_id": sid, "name": students[sid],
                       "subjects": len(marks[sid]), "average": round(avg, 2),
                       "grade": grade_for(avg), "rank": rank})
    for sid in unscored:
        report.append({"student_id": sid, "name": students[sid], "subjects": 0,
                       "average": "", "grade": "N/A", "rank": ""})

    with open(report_path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=[
            "student_id", "name", "subjects", "average", "grade", "rank"])
        writer.writeheader()
        writer.writerows(report)
    return report, rejected


def create_sample_files(folder):
    os.makedirs(folder, exist_ok=True)
    with open(os.path.join(folder, "students.csv"), "w") as h:
        h.write("student_id,name\n101,Ali\n102,Sara\n103,Bilal\n104,Hina\n")
    with open(os.path.join(folder, "scores.csv"), "w") as h:
        h.write("student_id,subject,marks\n101,Math,90\n101,Physics,80\n101,English,85\n"
                "102,Math,60\n102,Physics,72\n103,Math,35\n"
                "103,Math,50\n999,Math,70\n102,Art,101\n102,Art,abc\n")


if __name__ == "__main__":
    create_sample_files("sample_data")
    rows, bad = build_gradebook("sample_data/students.csv", "sample_data/scores.csv", "report.csv")
    for r in rows:
        print(r)
    print("Rejected:")
    for r in bad:
        print(r)