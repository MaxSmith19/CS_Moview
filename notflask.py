import tweepy, mysql.connector, re, csv, os,time

from flask import Flask, render_template, request,redirect
app = Flask(__name__)

@app.route('/main')
def main():
   return render_template('hello.html')

@app.route("/handle_data", methods=["GET","POST"])
def handle_data():
    projectpath= request.form['projectFilePath']
    return projectpath
@app.route("/main/<movie>")      
def displayMovie(projectpath):
    return render_template("displayMovie.html",movie = projectpath)

    
if __name__ == '__main__':
   app.run(debug = True)
#extracted from StackOverflow   
#overwrites a method within the tweepy "streamListener" class so that the data can be written to a json file.
# class MyStreamListener(tweepy.StreamListener):

#     def __init__(self, time_limit=60):
#         self.start_time = time.time()
#         self.limit = time_limit
#         self.saveFile = open('abcd.csv','a')
#         super(MyStreamListener, self).__init__()

#     def on_data(self, data):
#         if (time.time() - self.start_time) < self.limit:
#             self.saveFile.write(data)
#             self.saveFile.write('\n')
#             print("data received")
#             return True
#         else:
#             self.saveFile.close()
#             return False

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
    print(type(api))

def appendTable(movieChoice):
    #host="databases.suffolkone.ac.uk",
    #user="MS42220",
    #passwd="6vIKXUlf",
    #database="ms42220_results"
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="bilbobaggins",
        database="mydb"
        )
    mycursor= mydb.cursor(buffered=True)
    sql="SELECT * FROM movie ORDER BY movieID DESC"
    mycursor.execute(sql)
    myresult = mycursor.fetchone() #Should get the final ID, so that i can assign the next ID number and not have the need for auto increment
    intID=int(myresult[0])+1
    sql="INSERT INTO movie(MovieID, Name) VALUES (%s, %s)"
    values = (intID, movieChoice)
    mycursor.execute(sql, values)
    mydb.commit()
    print(mycursor.rowcount, "record inserted.")
    mydb.close()
    
def mining(api):
    PositiveTweets=0
    NegativeTweets=0
    finalRating=0
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="bilbobaggins",
        database="mydb"
        )
    mycursor= mydb.cursor(buffered=True)
    sql="SELECT * FROM movie ORDER BY movieID DESC"
    mycursor.execute(sql)
    myresult = mycursor.fetchone() #Should get the final ID, so that i can assign the next ID number and not have the need for auto increment
    intID=int(myresult[0])+1
        
    print("What movie would you like to review?")
    movieChoice=input("... ")
    sql = "SELECT * FROM movie WHERE Name = %s"
    values= movieChoice, 
    mycursor.execute(sql, values)
    row_count = mycursor.rowcount
    if row_count ==0:
        for tweet in tweepy.Cursor(api.search,q=movieChoice+"-filter:retweets",count=10,lang="en",wait_on_rate_limit=True,tweet_mode="extended").items(100):
            newTweet= removeEmoji(tweet.full_text)
            FinalTweet=CharOnly(newTweet)
            analysis = TextBlob(FinalTweet)
            print(analysis.sentiment.polarity)
            if analysis.sentiment.polarity > 0:
                PositiveTweets=PositiveTweets+1
            if analysis.sentiment.polarity < 0:
                NegativeTweets=NegativeTweets+1
            finalRating=50+PositiveTweets-NegativeTweets #Need to confirm this. (P/N)*100??
            print("Percentage Rating = "+finalRating)
    else:
        print("This Movie already exists within the database.")
    appendTable(movieChoice)
        
#Stack overflow  - removes emojis from text, changing them to ascii instead.
def removeEmoji(inputString):
    return inputString.encode('ascii', 'ignore').decode('ascii')
def CharOnly(inputString):
    #Also sourced from Stack Overflow
    return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t]) |(\w+:\/\/\S+)", " ", inputString).split()) 


# Movie TABLE CONSISTS OF: MovieID, name
# tweets TABLE CONSISTS OF: TweetID, TweetText, MovieID - Removed, due to lack of necessity, as i can analyse them as i get them.
# %s refers to a parameterized query, in which the user cannot use sql injection and destroy the database, or drop any tables which will be needed.