# String Formatting & F-strings

print("Hello İrem, this is cool!")

name = "İrem"
print(f"hello {name}, this is cool!")

names = ["İrem", "Jakub", "Tomi", "Georgie"]
for name in names:
    print(f"Hello {name}")

message = "Hi! " +  "These are my friends. "  +  "Nice to meet you."
print(message)

message = ""
for i in names:
    message += f"name: {i}"
print(message)

template = """Hello there, 
{name} These are my friends. 
Nice to meet you!"""
print(template)

template.format(name= 'Jakub')
print(template.format(name= "Jakub"))

pi = 3.14159265359
print(f"{pi}")
print("{:.2f}".format(pi))

print(format(pi))

