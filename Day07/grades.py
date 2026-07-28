# grades.py

def calculate_average(scores):
    return sum(scores) / len(scores)


def get_letter_grade(average):
    if average >= 90:
        return "A"
    elif average >= 80:
        return "B"
    elif average >= 70:
        return "C"
    elif average >= 60:
        return "D"
    else:
        return "F"


def create_report(name, scores):
    average = calculate_average(scores)
    grade = get_letter_grade(average)

    report = f"""
Student: {name}
Scores : {scores}
Average: {average:.2f}
Grade  : {grade}
"""

    return report


if __name__ == "__main__":
    print(create_report("İrem", [85, 90, 78]))