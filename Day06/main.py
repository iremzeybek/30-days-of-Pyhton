# Functions & Python Modules

print("Hello World!")

def my_print(txt):
    print(txt)

my_print("Hello World!")

msg_template = """Hello {name}.
Thank you for joining {website}
We're very happy to have you with us!
"""

def format_msg(my_name="İrem", my_website="github.com"):
    my_msg = msg_template.format(name=my_name, website=my_website)
    print(my_msg)
    return my_msg
format_msg()

names = ["İrem", "Jakub", "Tomi", "Georgi"]
for name in names:
    this_person_msg = format_msg(my_name=name)
    print(this_person_msg)

def base_function(*args, **kwargs):
    print(args, kwargs)