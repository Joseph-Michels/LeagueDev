import pyrebase
from time import time

firebase = None
try:
    with open("credentials/firebase_config.txt", 'r') as f:
        firebase = pyrebase.initialize_app(eval(f.read()))
except FileNotFoundError:
    raise FileNotFoundError('Missing firebase config in "credentials/firebase_config.txt"')

print(firebase)
auth = firebase.auth()


email = input("enter your email: ")
password = input("enter your password: ")
user = auth.sign_in_with_email_and_password(email, password)
print(type(user))

database = firebase.database()

data = {
    "name": "Mortimer 'Morty' Smith"
}

s = time()
# To save data with a unique, auto-generated, timestamp-based key, use the push() method.
push_result = database.child("tests").push(data, user['idToken'])
e = time()
print(f"push {push_result}: {e-s}")


s = time()
not_push_result = database.child(f"tests/{database.generate_key()}").set(data, user['idToken'])
e = time()
print(f"not push {not_push_result}: {e-s}")


s = time()
# To create your own keys use the set() method. The key in the example below is "Morty".
# Think it just updates if it already exists
set_result = database.child("tests").child("Morty").set(data, user['idToken'])
e = time()
print(f"set {set_result}: {e-s}")

s = time()
# To update data for an existing entry use the update() method.
update_result = database.child("tests").child("Morty").update({"name": "Mortiest Morty"}, user['idToken'])
e = time()
print(f"update {update_result}: {e-s}")

s = time()
# To delete data for an existing entry use the remove() method.
remove_result = database.child("tests").child("Morty").remove(user['idToken'])
e = time()
print(f"rem {remove_result}: {e-s}")

data = {
    "tests/Morty/": {
        "name": "Mortimer 'Morty' Smith"
    },
    "tests/Rick/": {
        "name": "Rick Sanchez"
    }
}

s = time()
multi_result = database.update(data, user['idToken'])
e = time()
print(f"multi_update {multi_result}: {e-s}")

s = time()
tests = database.child("tests").get(user['idToken'])
e = time()
print(f"get: {e-s}")
print(tests.val()) # key
print(tests.key()) # val

