import omdb
OMDB_API_KEY = "9537ab6c"
omdb.set_default('apikey', OMDB_API_KEY)

movieChoice = "The lion king"

movieInfo=omdb.get(title=movieChoice, tomatoes=True, fullplot=True)
for i in movieInfo:
    print(i)
    print(movieInfo[i])