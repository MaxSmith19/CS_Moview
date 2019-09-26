import tweepy, mysql.connector, re, math
from flask import Flask, render_template, request
app = Flask(__name__)


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
    myresult = mycursor.fetchone() #Should get the final ID, so that i can assign the next ID number and not have the need for auto increment
    intID=int(myresult[0])+1
    sql="INSERT INTO movie(MovieID,MovieName) VALUES (%s, %s)"
    values = (intID,movieChoice)
    mycursor.execute(sql, values)
    mydb.commit()
    print(mycursor.rowcount, "record inserted.")
    mydb.close()

def mining(movieChoice):
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
    
    oAuth()
    movieChoice=input("... ")
    sql = "SELECT * FROM movie WHERE movieName = %s"
    values= movieChoice, 
    mycursor.execute(sql, values)
    row_count = mycursor.rowcount
    movieRating = 0
    ratingList=[]
    movieAverage=1
    count=100
    movieP=0
    movieN=0
    movieTotal=0
    try:
        if row_count ==0:
            for tweet in tweepy.Cursor(api.search,q=movieChoice+"-filter:retweets",count=count,lang="en",wait_on_rate_limit=True,tweet_mode="extended").items(count):
                newTweet= removeEmoji(tweet.full_text) 
                FinalTweet=CharOnly(newTweet) #removes unnecessary emojis and unreadable items from the string, to make it easier to analyse.           
                splitTweet=FinalTweet.split()
                with open(r"Dictionary\\positiveWords.txt","r") as positiveDict:
                    pLine=positiveDict.readlines() #CHANGE THIS TO USE THE WEIGHTED FILE
                with open(r"Dictionary\\negativeWords.txt","r") as negativeDict:
                    nLine=negativeDict.readlines()
                for word in splitTweet: #for each word in tweet
                    for pw in pLine: #for each positive word in the positive file
                        word=word.lower().strip() #lowercase
                        pw=pw.lower().strip()#lowercase
                        if pw in word:
                            movieRating=movieRating+3
                            break
                    for iw in nLine:
                        word=word.lower().strip()
                        iw=iw.lower().strip()
                        if iw in word:
                            movieRating=movieRating-1
                            break
                    movieTotal=movieTotal+movieRating
            #     if movieRating>0:
            #         ratingList.append("Positive")
            #     if movieRating<=0:
            #         ratingList.append("Negative")
            # movieP = ratingList.count("Positive")
            # movieN = ratingList.count("Negative")
            # movieAverage=movieP/movieN 
            print(movieTotal/100)
            print(movieAverage)
        else:
            print("This Movie already exists within the database.")
            appendTable(movieChoice)
    except ZeroDivisionError:
        movieAverage+1
    finally:
        appendTable(movieChoice)
    #currently it is only determined if it's good or bad, not how good or bad it is.

#Stack overflow  - removes emojis from text, changing them to ascii instead.
def removeEmoji(inputString):
    return inputString.encode('ascii', 'ignore').decode('ascii')
def CharOnly(inputString):
    #Also sourced from Stack Overflow
    return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t]) |(\w+:\/\/\S+)", " ", inputString).split()) 


@app.route('/') 
def main():
    return render_template('hello.html')

@app.route("/handle_data", methods=["GET","POST"])
def handle_data():
    if request.method == "POST":
        projectpath=request.form["projectFilePath"]
        return render_template("displayMovie.html",movieName=projectpath)
    elif request.method == "GET":
        print(projectpath)
        mining(projectpath)
        return render_template("displayMovie.html",movieName=projectpath)

    
if __name__ == '__main__':
   app.run(debug = True)



# Movie TABLE CONSISTS OF: MovieID, name
# tweets TABLE CONSISTS OF: TweetID, TweetText, MovieID - Removed, due to lack of necessity, as i can analyse them as i get them.
# %s refers to a parameterized query, in which the user cannot use sql injection and destroy the database, or drop any tables which will be needed.