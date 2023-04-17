# Script to run extract the data from the IMDb database to a json format which could 

#!/usr/bin/python3

import fileinput, csv, pprint, json, time, urllib.request
import unidecode as ud #pip install unidecode

start_time = time.time()
pp = pprint.PrettyPrinter(indent=4)

#_______________read the official tsv dataset files from imdb.com_____________________
#1[titleRatings] ratings file
titleRatings = open('imdb_data/title.ratings.tsv/data.tsv')
readerRatings = csv.DictReader(titleRatings,delimiter='\t')

#2[titleBasic] 
titleBasic = open('imdb_data/title.basics.tsv/data.tsv',encoding="utf8")
readerBasic = csv.DictReader(titleBasic,delimiter='\t')

#3[titlePrincipals] 
titlePrincipal = open('imdb_data/title.principals.tsv/data.tsv',encoding="utf8")
readerPrincipal = csv.DictReader(titlePrincipal,delimiter='\t')

#4[titleCrew] 
titleCrew = open('imdb_data/title.crew.tsv/data.tsv',encoding="utf8")
readerCrew = csv.DictReader(titleCrew,delimiter='\t')

#6[names] 
humans = open('imdb_data/name.basics.tsv/data.tsv',encoding="utf8")
readerHumans = csv.DictReader(humans,delimiter='\t')

humanListAux = set()

#__________________________creating the dictionaries____________________________________
#1[titleRatings] titles with 10,000+ votes (but have titles that aren't movies)
ratings_dict = {} 
for row in readerRatings:
	if int(row['numVotes']) > 10000:
		ratings_dict[row['tconst']] = {'averageRating' : row['averageRating'],'numVotes' : row['numVotes']}
print("ratings_dict criado | %s"  % (time.time() - start_time))

#2[titleBasic] 
basic_dict = {}
for row in readerBasic:
	if row['titleType'] == 'movie':
		basic_dict[row['tconst']] = {'primaryTitle' : row['primaryTitle'], 'startYear' : row['startYear'], 'genres' : row['genres'].split(","), 'runtimeMinutes' : row['runtimeMinutes']}
		#print(basic_dict[row['tconst']])
print("basic_dict criado | %s"  % (time.time() - start_time))

#3[titlePrincipals] 
actor_dict = {}    
for row in readerPrincipal:
	if row['category'] == 'actor' or row['category'] == 'actress':   
		if row['tconst'] in actor_dict:  						#if this movie already exists 
			actor_dict[row['tconst']]['actors'].append(row['nconst'])
		else:													
			actor_dict[row['tconst']] = {'actors' : [row['nconst']]}
print("actor_dict criado | %s"  % (time.time() - start_time))


#4[titleCrew] 
crew_dict = {}  
for row in readerCrew:
	crew_dict[row['tconst']]={'directors' : row['directors'].split(","), 'writers' : row['writers'].split(",")}
print("crew_dict criado | %s"  % (time.time() - start_time))

# here movies with more than 10000 rating are taken into account 
for key,val in basic_dict.items(): 
	if key in ratings_dict:		# (>10.000 votos) 
		ratings_dict[key]['genres'] = basic_dict[key]['genres']
		ratings_dict[key]['primaryTitle'] = basic_dict[key]['primaryTitle']
		ratings_dict[key]['startYear'] = basic_dict[key]['startYear']
		ratings_dict[key]['runtimeMinutes'] = basic_dict[key]['runtimeMinutes']
print("uniao de basic_dict com ratings_dict criado | %s"  % (time.time() - start_time))				

#clear from the dictionary titles that have more than 10,000 votes, but are not movies. We know that 'movies' have 6 fields
for key in ratings_dict.copy():
	if len(ratings_dict[key])<6:
		del ratings_dict[key]
	else:
		# add actors
		if key in actor_dict:
			ratings_dict[key]['primaryActors']=actor_dict[key]['actors']
			# insert these actors into the list of useful people
			for ator in ratings_dict[key]['primaryActors']:
				humanListAux.add(ator)
		#add directors and writers
		if key in crew_dict:
			ratings_dict[key]['directors']=crew_dict[key]['directors']
			#insert these directors in the list of useful people
			for drctr in ratings_dict[key]['directors']:
				humanListAux.add(drctr)
			ratings_dict[key]['writers']=crew_dict[key]['writers']
			# add these writers to the list of helpful people
			for wrtr in ratings_dict[key]['writers']:
				humanListAux.add(wrtr)
print("limpado ratings_dict, adicionado os atores, realizadores e escritores | %s"  % (time.time() - start_time) )


humans_dict = {}
for row in readerHumans:
	# add only people who are useful
	if row['nconst'] in humanListAux:
		humans_dict[row['nconst']]={'primaryName' : row['primaryName'], 'birthYear' : row['birthYear'], 'deathYear' : row['deathYear'],'primaryProfession' : row['primaryProfession'].split(","),'knownForTitles' : row['knownForTitles'].split(",")}
print("humans_dict criado | %s"  % (time.time() - start_time))

#remove from the 'knownForTitle' fields the titles that are not in ratings_dict
for key in humans_dict:
	for tit in humans_dict[key]['knownForTitles']:
		if tit not in ratings_dict:
			humans_dict[key]['knownForTitles'].remove(tit)
print("removido do campo 'knownForTitle' os titulos que nao estao no ratings_dict | %s"  % (time.time() - start_time))

#________writing and creating a movies.json file that contains all the movies with the above fields, just the ones in the imdb________
movies_json = json.dumps(ratings_dict)
f = open("movies.json","w")
f.write(movies_json)
f.close()

print("ficheiro movie.json criado | %s"  % (time.time() - start_time))


#_______write and create a humans.json file that contains the information of all the people listed in movies.json_____________
human_json = json.dumps(humans_dict)
f = open("humans.json","w")
f.write(human_json)
f.close()


api_dict = {}
movies = json.load(open('movies.json'))
api_movies = json.load(open('api_movies.json'))

api_aux = set() #contains the ids of the movies already drawn
for key in api_movies:
	api_aux.add(key)

api_key1 = '&apikey=5aec35de'
api_key2 = '&apikey=ef28afd8'
api_key3 = '&apikey=2fb13c99'
api_key4 = '&apikey=a1d3e574'

api_key_aux = api_key4

i=0
j=0
for key in movies:
	if key not in api_aux:    
		url = 'http://www.omdbapi.com/?i=' + key + api_key_aux
		response = urllib.request.urlopen(url)
		data = response.read()
		text = data.decode('utf-8')
		d = json.loads(text)
		api_dict[d['imdbID']] = d
		
		print("movie " + str(j))
		i+=1
		
		if api_key_aux == api_key1:
			api_key_aux = api_key2
		else:
			if api_key_aux == api_key2:
				api_key_aux = api_key1
			else:
				if api_key_aux == api_key3:
					api_key_aux = api_key1
		j+=1
		if j>2:
			break


if bool(api_dict):
	api_movies.update(api_dict)
	with open('imdb_data/api_movies.json', 'w') as f:
		json.dump(api_movies, f)
else:
	print("acabou")


def conv_IMD(str):
	lista = str.split('/')
	a = lista[0]
	return (float(a)/1.0)

def conv_RT(str):
	lista = str.split('%')
	a = lista[0]
	return (int(a)/10.0)

def conv_MC(str):
	lista = str.split('/')
	a = lista[0]
	return (int(a)/10.0)

for title in movies:
	i=0
	for rating in movies[title]["ratings"]:
		if rating["Source"] == "Internet Movie Database":
			valor = rating["Value"]
			movies[title]["ratings"][i]["Value"] = conv_IMD(valor)
			i+=1
		if rating["Source"] == "Rotten Tomatoes":
			valor = rating["Value"]
			movies[title]["ratings"][i]["Value"] = conv_RT(valor)
			i+=1
		if rating["Source"] == "Metacritic":
			valor = rating["Value"]
			movies[title]["ratings"][i]["Value"] = conv_MC(valor)
			i+=1

json = json.dumps(movies)
f = open("movies_ids.json","w")
f.write(json)
f.close()


	

