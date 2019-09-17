import tweepy, mysql.connector, re
"""
from flask import Flask, render_template, request
app = Flask(__name__)

@app.route('/')
def main():
   return render_template('hello.html')

@app.route("/handle_data", methods=["GET","POST"])
def handle_data():
    if request.method == "POST":
        projectpath=request.form["projectFilePath"]
    return render_template("displayMovie.html",movieName=projectpath)


    
if __name__ == '__main__':
   app.run(debug = True)
"""
def oAuth():
    consumer_token="DofAPsDVn3kOFxx3tlsRpZEag"
    consumer_secret="gKEmykLbzTQjEr9VR7fcWuSFwtnhlns1vFNkd8qCxrVPWaa5f0"
    access_token="1131545136549289986-gEsRdBgaBk0B1bi5XfUSNx5eY15ZMa"
    access_secret="AEVSYMf7aZ1WQ7iDcpov8CV7Yc0KEgCPduvIoZntdCl7X"

    #OAUTH and setting the API
    auth = tweepy.OAuthHandler(consumer_token, consumer_secret)
    auth.set_access_token(access_token, access_secret)
    api = tweepy.API(auth)
    print("Authenticated")
    mining(api)

def appendTable(movieChoice):
    mydb= mysql.connector.connect(
        host="databases.suffolkone.ac.uk",
        user="MS42220",
        passwd="6vIKXUlf",
        database="ms42220_moview"
    )
    # mydb = mysql.connector.connect(
    #     host="localhost",
    #     user="root",
    #     passwd="bilbobaggins",
    #     database="mydb"
    #     )
    mycursor= mydb.cursor(buffered=True)
    sql="SELECT * FROM movie ORDER BY movieID DESC"
    mycursor.execute(sql)
    myresult = mycursor.fetchone() #Should get the final ID, so that i can assign the next ID number and not have the need for auto increment
    intID=int(myresult[0])+1
    sql="INSERT INTO movie(MovieID,MovieName) VALUES (%s, %s)"
    values = (intID,movieChoice)
    mycursor.execute(sql, values)
    mydb.commit()
    print(mycursor.rowcount, "record inserted.")
    mydb.close()

def mining(api):
    mydb = mysql.connector.connect(
        host="databases.suffolkone.ac.uk",
        user="MS42220",
        passwd="6vIKXUlf",
        database="ms42220_moview"
        )
    mycursor= mydb.cursor(buffered=True)
    sql="SELECT * FROM movie ORDER BY movieID DESC"
    mycursor.execute(sql)
    myresult = mycursor.fetchone() #Should get the final ID, so that i can assign the next ID number and not have the need for auto increment
    intID=int(myresult[0])+1
        
    print("What movie would you like to review?")
    movieChoice=input("... ")
    sql = "SELECT * FROM movie WHERE movieName = %s"
    values= movieChoice, 
    mycursor.execute(sql, values)
    row_count = mycursor.rowcount
    movieRating = 0
    if row_count ==0:
        for tweet in tweepy.Cursor(api.search,q=movieChoice+"-filter:retweets",count=10,lang="en",wait_on_rate_limit=True,tweet_mode="extended").items(100):
            newTweet= removeEmoji(tweet.full_text) 
            FinalTweet=CharOnly(newTweet) #removes unnecessary emojis and unreadable items from the string, to make it easier to analyse.           
            splitTweet=FinalTweet.split()
            with open(r"Dictionary\\positiveWords.txt","r") as positiveDict:
                pLine=positiveDict.readlines()
            with open(r"Dictionary\\negativeWords.txt","r") as negativeDict:
                nLine=negativeDict.readlines()
            for i in pLine:
                for word in splitTweet:
                    word=word.lower()
                    i=i.lower()
                    if i==word:
                        movieRating=movieRating+1
            for i in nLine:
                for word in splitTweet:
                    word=word.lower()
                    i=i.lower()
                    if i == word:  
                        movieRating=movieRating-1
            print(movieRating)
                        #currently it is only determined if it's good or bad, not how good or bad it is.
    else:
        print("This Movie already exists within the database.")
        appendTable()
#Stack overflow  - removes emojis from text, changing them to ascii instead.
def removeEmoji(inputString):
    return inputString.encode('ascii', 'ignore').decode('ascii')
def CharOnly(inputString):
    #Also sourced from Stack Overflow
    return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t]) |(\w+:\/\/\S+)", " ", inputString).split()) 

oAuth()
# Movie TABLE CONSISTS OF: MovieID, name
# tweets TABLE CONSISTS OF: TweetID, TweetText, MovieID - Removed, due to lack of necessity, as i can analyse them as i get them.
# %s refers to a parameterized query, in which the user cannot use sql injection and destroy the database, or drop any tables which will be needed.