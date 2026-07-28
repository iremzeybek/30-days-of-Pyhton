# main.py

from grades import create_report

student_name = input("İrem: ")

scores = []
for i in range(3):
    score = int(input(f"Enter score {i+1}: "))
    scores.append(score)

result = create_report(student_name, scores)

print(result)