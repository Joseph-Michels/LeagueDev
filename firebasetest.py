import pyrebase

config = {
	'apiKey': "AIzaSyBkiDeRm6ZKergpdVH_zSBceTLNsLCrMLQ",
	'authDomain': "leaguedev-57c5d.firebaseapp.com",
	'databaseURL': "https://leaguedev-57c5d.firebaseio.com",
	'projectId': "leaguedev-57c5d",
	'storageBucket': "leaguedev-57c5d.appspot.com",
	'messagingSenderId': "44032877576",
	'appId': "1:44032877576:web:df52a4cd48875ecd"
}

firebase = pyrebase.initialize_app(config)
print(firebase)

auth = firebase.auth()
print(auth)


email = input("enter your email: ")
password = input("enter your password: ")
user = auth.sign_in_with_email_and_password(email, password)

database = firebase.database()

data = {
    "name": "Mortimer 'Morty' Smith"
}

# To save data with a unique, auto-generated, timestamp-based key, use the push() method.
push_result = database.child("users").push(data, user['idToken'])
print(push_result)

# To create your own keys use the set() method. The key in the example below is "Morty".
# Think it just updates if it already exists
set_result = database.child("users").child("Morty").set(data, user['idToken'])
print(set_result)

# To update data for an existing entry use the update() method.
update_result = database.child("users").child("Morty").update({"name": "Mortiest Morty"}, user['idToken'])
print(update_result)

# To delete data for an existing entry use the remove() method.
remove_result = database.child("users").child("Morty").remove(user['idToken'])
print(remove_result)

data = {
    "users/Morty/": {
        "name": "Mortimer 'Morty' Smith"
    },
    "users/Rick/": {
        "name": "Rick Sanchez"
    }
}

multi_result = database.update(data, user['idToken'])
print(multi_result)


users = database.child("users").get(user['idToken'])
print(users.val()) # key
print(users.key()) # val