class User:

    def __init__(self, name, birthyear):
        self.name = name
        self.birthyear = birthyear


    def get_name(self):
        return self.name.upper()

    def age(self, current_year):
        age = current_year - self.birthyear
        return age

John = User(name= "John",birthyear=1999)

print(John.age(current_year=2025))
print(John.get_name())





