# Iterations & Loops

my_list = [1, 2, 3, 4, 5]
print(my_list)

for my_var in my_list:
    print(my_var)

print(my_var)

for my_var in range(10):
    print(my_var)

for i in "abcde":
    print(i)

for i in "abc":
    print(i)
    print(i)

user_1 = {"name": "İrem", "surname": "Zeybek", "age": 20}
user_2 = {"name": "Zümra", "surname": "Zeybek", "age": 10}
my_users = [user_1, user_2]
for user in my_users:
    print(user)
    print(user["name"])
selected_user = {}
my_user_lookup = 10
for user in my_users:
    if user["age"] == my_user_lookup:
        selected_user = user
print(selected_user)

for x in range(15, 30):
   for user in my_users:
         if user["age"] == x:
             selected_user = user
             print(selected_user)
