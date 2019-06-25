from firebase import firebase

firebase = firebase.FirebaseApplication('https://leaguedev-57c5d.firebaseio.com/')

print(firebase)

getres = firebase.get('/users', None)
print(getres)
getpos = firebase.post('/users', "taiwanlul")
print(getpos)