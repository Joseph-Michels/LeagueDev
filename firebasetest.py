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

results = database.child("users").push(data, user['idToken'])