import pandas
import numpy as np
from re import sub
import matplotlib as mpl
import pylab
from mpl_toolkits.mplot3d import Axes3D
from sklearn import linear_model

movies2=pandas.read_csv('movie_data.csv',usecols=[1,2,3,23,24])
#print movies2
movies2['domestic']=map(lambda x:sub(r'[^\d.]', "",x),movies2['domestic'].astype('S32'))#clean up the domestic box office,
movies2['BoxOffice']=movies2['domestic'].convert_objects(convert_numeric=True)#change the type

#for simplicity, just going to look at writer and director to start
#can do something simliar for actors, composer, producers, etc

#first need table to convert writers to a numerical value(using there avg boxoffice track record in this case)
movies2=movies2[movies2['domestic'].notnull()]#remove films with only foreign release
movies2=movies2[movies2['BoxOffice']>0]#remove low boxoffice movies as a test
movies2=movies2[movies2['writer1'].notnull()] #remove entries with incomplete records
movies2=movies2[movies2['director1'].notnull()] #remove entries with incomplete records
movies2=movies2.fillna(0) #avoid errors, will have to remove the "0" writers/directors later

writers_list1=pandas.DataFrame()
writers_list1['writer']=movies2['writer1']
writers_list1['BoxOffice']=movies2['BoxOffice']
writers_list2=pandas.DataFrame()
writers_list2['writer']=movies2['writer2']
writers_list2['BoxOffice']=movies2['BoxOffice']
#writers_list2=writers_list2[writers_list2['writer'].notnull()]
writers_list=writers_list1.append(writers_list2)#use writers from both columns

writers_list=writers_list.groupby('writer')['BoxOffice'].mean()/10000000
print writers_list #debug

#do same thing for directors
directors_list1=pandas.DataFrame()
directors_list1['director']=movies2['director1']
directors_list1['BoxOffice']=movies2['BoxOffice']
directors_list2=pandas.DataFrame()
directors_list2['director']=movies2['director2']
directors_list2['BoxOffice']=movies2['BoxOffice']
#directors_list2=directors_list2[directors_list2['director'].notnull()]
directors_list=directors_list1.append(directors_list2)

directors_list=directors_list.groupby('director')['BoxOffice'].mean()/10000000
#print directors_list #debug
movies2['writer_score']=map(lambda x:writers_list.loc[x],movies2['writer1'])
movies2['director_score']=map(lambda x:directors_list.loc[x],movies2['director1'])

#now fix those cases that have two directors, or two writers
#first find the scores for writer2/director2 (including the dummy "0")
movies2['writer_score2']=map(lambda x:writers_list.loc[x],movies2['writer2'])
movies2['director_score2']=map(lambda x:directors_list.loc[x],movies2['director2'])
#only update the writer/director score for cases where there are more then 1, and in those cases use the average score
movies2.ix[movies2.writer2!=0, 'writer_score'] =0.5*(movies2['writer_score']+movies2['writer_score2'])
movies2.ix[movies2.director2!=0, 'director_score'] =0.5*(movies2['director_score']+movies2['director_score2'])

plotframe=pandas.DataFrame()
plotframe['BoxOffice']=movies2['BoxOffice']
plotframe['writer_score']=movies2['writer_score']
plotframe['director_score']=movies2['director_score']

plot_array = np.asarray(plotframe)
X, Y = plot_array[:, 1:], plot_array[:, 0]

my_fit = linear_model.LinearRegression()
my_fit=my_fit.fit(X,Y)
x = np.arange(0, 60, 10)                # generate a mesh
y = np.arange(0, 60, 10)
x, y = np.meshgrid(x, y)

my_mesh= pandas.core.frame.DataFrame({'writers_score': x.ravel(), 'director_score': y.ravel()})
fit_surface = my_fit.predict(my_mesh)

fig = pylab.figure()
ax = Axes3D(fig)

ax.scatter( movies2.writer_score, movies2.director_score, movies2.BoxOffice, c=movies2.writer_score, cmap=mpl.cm.gist_rainbow)
ax.plot_surface(x,y,fit_surface.reshape(x.shape),rstride=1,cstride=1,color='blue',alpha = 0.5)
ax.set_xlim3d(0, 60)
ax.set_ylim3d(0, 60)
ax.set_zlim3d(0, 1500000000)

ax.set_xlabel('Director Score')
ax.set_ylabel('Writer Score')
ax.set_zlabel('Box Office (USD)')

