import pandas
from datetime import datetime
from re import sub
import visvis as vv
import MySQLdb as mdb

con = mdb.connect('localhost', 'movie_user1', 'movie616', 'movie_data')
movies1 = pandas.read_sql('select domestic, release_date, genre from BoxOfficeMojo;', con=con)
con.close()

#print movies1

movies1 = movies1[movies1['release_date'].str.contains(',')==True]#filter all bad dates and foreign only films
movies1['release_date']=map(lambda x:datetime.strptime(x, '%B %d, %Y'),movies1['release_date'])#get dates in correct format
movies1['week_number']=map(lambda x:datetime.strftime(x, '%W'),movies1['release_date'])#get the week number
movies1['week_number']=movies1['week_number'].convert_objects(convert_numeric=True)#change the type
#change the type

movies1['domestic']=map(lambda x:sub(r'[^\d.]', "",x),movies1['domestic'].astype('S32'))#clean up the domestic box office
movies1['BoxOffice']=movies1['domestic'].convert_objects(convert_numeric=True)#change the type

#movies1.groupby('genre')['BoxOffice'].mean().to_csv('genres.csv') #Want to see what all possible genres are
#collect the genres into some main groups (with overlap)
action= movies1[movies1['genre'].str.contains('Action')==True]
animation= movies1[movies1['genre'].str.contains('Animation')==True]
comedy= movies1[movies1['genre'].str.contains('Comedy')==True]
fantasy= movies1[movies1['genre'].str.contains('Fantasy')==True]
horror= movies1[movies1['genre'].str.contains('Horror')==True]
romance= movies1[movies1['genre'].str.contains('Romance')==True]
scifi= movies1[movies1['genre'].str.contains('Sci-Fi')==True]

all_by_week=movies1.groupby('week_number')
action_by_week=action.groupby('week_number')
animation_by_week=animation.groupby('week_number')
comedy_by_week=comedy.groupby('week_number')
fantasy_by_week=fantasy.groupby('week_number')
horror_by_week=horror.groupby('week_number')
romance_by_week=romance.groupby('week_number')
scifi_by_week=scifi.groupby('week_number')

norm1=all_by_week['BoxOffice'].mean().max()/30
norm2=fantasy_by_week['BoxOffice'].mean().max()/30
norm3=animation_by_week['BoxOffice'].mean().max()/30
norm4=romance_by_week['BoxOffice'].mean().max()/30

genres=pandas.DataFrame(all_by_week['BoxOffice'].mean()/norm1)
genres.columns=['All Genres']
genres=genres.join(fantasy_by_week['BoxOffice'].mean()/norm2)
genres.columns=['All Genres','Fantasy']
genres=genres.join(animation_by_week['BoxOffice'].mean()/norm3)
genres.columns=['All Genres','Fantasy','Animation']
genres=genres.join(romance_by_week['BoxOffice'].mean()/norm4)
genres.columns=['All Genres','Fantasy','Animation','Romance']

genres=genres.fillna(0)

columns_name = ['All Genres','Fantasy','Animation','Romance']
genres.columns = [ 0, 4, 8, 12]

x, y, z = genres.stack().reset_index().values.T
#print  genres.stack().reset_index().values.T  #debug
#print genres#debug

app = vv.use()
f = vv.clf()
a = vv.cla()
plot =vv.bar3(x, y, z)
plot.colors = ["b","g","y","r"] * 53
a.axis.xLabel = 'Week #'
a.axis.yTicks = dict(zip(genres.columns, columns_name))
a.axis.zLabel = 'Avg BoxOffice (Aribitrary Units)'
app.Run()



