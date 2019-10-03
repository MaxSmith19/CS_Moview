import tweepy, mysql.connector, re, omdb, json, werkzeug, string
from flask import Flask, render_template, request, redirect, url_for
app = Flask(__name__)

OMDB_API_KEY = "9537ab6c"
omdb.set_default('apikey', OMDB_API_KEY)
omdb.set_default('tomatoes', True)


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
    return api


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
    myresult = mycursor.fetchone() #Should get the final ID, so that i can assign the next ID number 
                                   #and not have the need for auto increment
    intID=int(myresult[0])+1
    #This will get the next movieID required for the movie table
    sql="INSERT INTO movie(MovieID,MovieName) VALUES (%s, %s)"
    values = (intID,movieChoice)
    mycursor.execute(sql, values)
    mydb.commit()
    print(mycursor.rowcount, "record inserted.")
    #visual help, to show how many records have been inserted into the database
    mydb.close()
    #close the database

def mining(api,movieChoice):
    mydb = mysql.connector.connect(
        host="databases.suffolkone.ac.uk",
        user="MS42220",
        passwd="6vIKXUlf",
        database="ms42220_moview"
        )
    mycursor= mydb.cursor(buffered=True)
    sql="SELECT * FROM movie ORDER BY movieID DESC"
    #select everything and order it by movieID descending.
    mycursor.execute(sql)
    sql = "SELECT * FROM movie WHERE movieName = %s"
    # %s is used to create parameterised queries, so that any tweets containing "drop table movie" doesnt delete 
    # my table.
    values= movieChoice, #<-- DO NOT REMOVE THIS COMMA
    #select all information where the movieName is equal to movieChoice    
    mycursor.execute(sql, values)
    #executes the above SQL
    row_count = mycursor.rowcount
    #row count is the amount of rows the sql gave back.
    tweetRating = 0 #Rating of the tweet (int)
    movieTotal=0 #rating of the movie before being averaged
    movieAverage=1 #final rating of the movie  (int)
    COUNT=100 #constant containing the amount of tweets per review
    try:
        if row_count ==0: #If the movie has not been reviewed before THEN
            for tweet in tweepy.Cursor(api.search,q=movieChoice+"-filter:retweets",count=COUNT,lang="en",wait_on_rate_limit=True,tweet_mode="extended").items(COUNT):
                #Tweepy cursor creates an instance temporarily which allows tweets to be taken from the api
                newTweet= removeEmoji(tweet.full_text) 
                FinalTweet=CharOnly(newTweet)   #removes unnecessary emojis and unreadable items from the string, 
                                                #to make it easier to analyse
                splitTweet=FinalTweet.split() #splits the tweet into each seperate word
                with open(r"Dictionary\\positiveWords.txt","r") as positiveDict:
                    pLine=positiveDict.readlines()
                    #reads every line in the file (in this case, each line is one word.)
                with open(r"Dictionary\\negativeWords.txt","r") as negativeDict:
                    nLine=negativeDict.readlines()
                for word in splitTweet: #for each word in tweet
                    for pw in pLine: #for each positive word in the positive file
                        word=word.lower().strip() #lowercase
                        pw=pw.lower().strip()#lowercase
                        if pw in word:
                            #if the word in the file is equal to the word in the tweet.
                            tweetRating=tweetRating+3
                            #I felt this was a good weight, as there are over 2x more 
                            # negative words than positive within the file.
                            break
                            #out of the loop, so that it can continue onto the next word to analyse.
                    for iw in nLine:
                        word=word.lower().strip()
                        iw=iw.lower().strip()
                        if iw in word:
                            tweetRating=tweetRating-1
                            break
                    movieTotal=movieTotal+tweetRating
            #     if tweetRating>0:
            #         ratingList.append("Positive")
            #     if tweetRating<=0:
            #         ratingList.append("Negative")
            # movieP = ratingList.count("Positive")
            # movieN = ratingList.count("Negative")
            # movieAverage=movieP/movieN 
            appendTable(movieChoice)
        else:
            print("This Movie already exists within the database.")
    except ZeroDivisionError:
        movieAverage+1
    
    #currently it is only determined if it's good or bad, not how good or bad it is.

#Stack overflow  - removes emojis from text, changing them to ascii instead.
def removeEmoji(inputString):
    return inputString.encode('ascii', 'ignore').decode('ascii')
def CharOnly(inputString):
    #Also sourced from Stack Overflow
    return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t]) |(\w+:\/\/\S+)", " ", inputString).split()) 


@app.route('/') 
def main():
    return render_template('main.html')

@app.route("/handle_data", methods=["GET","POST"])
def handle_data():
    try:
        movieChoice=request.form["projectFilePath"]
        movieChoice=movieChoice.upper()
        api=oAuth()
        movieInfo=omdb.search_movie(movieChoice)
        raw=movieInfo[0]
        for i in raw:
            raw[i].split(" ")
            noPunc=raw[i].translate(str.maketrans(".,;!£$%^&*()'", '             ', string.punctuation))
            if noPunc.upper() == movieChoice or raw[i].upper() == movieChoice:
                mining(api, movieChoice)
                return render_template("DisplayMovie.html", movieName=movieChoice)
            else:
                return render_template("mainError.html", error="This movie does not exist, try again.")
    except werkzeug.exceptions.BadRequestKeyError:
        return redirect(url_for("main"))
    except IndexError:
       return render_template("mainError.html", error="This movie does not exist, try again.")
    except KeyError:
        return redirect(url_for("main"))  

    
if __name__ == '__main__':
   app.run(debug = True)



# Movie TABLE CONSISTS OF: MovieID, name
# tweets TABLE CONSISTS OF: TweetID, TweetText, MovieID - Removed, due to lack of necessity, as i can analyse them as i get them.
# %s refers to a parameterized query, in which the user cannot use sql injection and destroy the database, or drop any tables which will be needed.