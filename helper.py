# This file contains helper functions
import requests
from requests_toolbelt.utils import dump
from SPARQLWrapper import SPARQLWrapper, JSON
import urllib.request
import datetime
# from collections import Counter
import locale
locale.setlocale( locale.LC_ALL, '' ) # to format currency

# DEFAULT PROXY
http_proxy  = "http://172.16.2.30:8080"
proxyDict = { 
        "http"  : http_proxy, 
        "https" : http_proxy, 
        "ftp"   : http_proxy
    }

def cap(str):
    # capitalises each word of a string
    return ' '.join(s[:1].upper() + s[1:] for s in str.split(' '))

def get_movie_poster(movie_name, proxy=proxyDict):
    # this function fetches the movie posters using TheMovieDataBase
    movie_path = "https://api.themoviedb.org/3/search/movie/"
    params = {
        "api_key" : "1332a724cdfb99d5c9a2b600d4012951",
        "query" : movie_name
    }
    movie = requests.get(movie_path, params=params, proxies=proxy).json()
    # data = dump.dump_all(movie)
    # print(data.decode('utf-8'))
    if movie['total_results'] == 0:
        # handle failure
        return None
    # fetch the url for movie poster and return it
    # get the rating
    rating = movie['results'][0]['vote_average']
    poster_path = "https://image.tmdb.org/t/p/w500/" + movie['results'][0]['poster_path']
    return (poster_path, rating)

class Sparql:
    def __init__(self, proxy = proxyDict):
        self.agent = SPARQLWrapper("https://query.wikidata.org/sparql")
        self.agent.setTimeout(40)
        self.proxy_support = urllib.request.ProxyHandler(proxy)
        self.opener = urllib.request.build_opener(self.proxy_support)
        urllib.request.install_opener(self.opener)

    def formatDate(self, dateString, needYear=False):
        # format the XML date format and returns nicely formatted date with Age too
        # no error handling is done here :)
        date = [int(d) for d in dateString.split('T')[0].split('-')]
        monthDict = {
            1: 'January',2: 'February', 3: 'March', 4: 'April', 5: 'May', 6: 'June',
            7: 'July', 8: 'August', 9: 'September', 10: 'October', 11: 'November', 12: 'December'
        }
        if(needYear):
            return date[0]
        return f"{date[2]} - {monthDict[int(date[1])]} - {date[0]} ({datetime.datetime.now().year - date[0]}  Years old)"

    def getMovieDetails(self, movieName):
        queryString = """
        PREFIX wd: <http://www.wikidata.org/entity/>
        PREFIX wdt: <http://www.wikidata.org/prop/direct/>
        PREFIX wikibase: <http://wikiba.se/ontology#>
        PREFIX p: <http://www.wikidata.org/prop/>
        PREFIX ps: <http://www.wikidata.org/prop/statement/>
        PREFIX pq: <http://www.wikidata.org/prop/qualifier/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX bd: <http://www.bigdata.com/rdf#>

        SELECT DISTINCT ?label ?boxLabel ?genreLabel ?dateLabel ?vactorLabel ?awardsLabel ?directorLabel ?musicLabel ?companyLabel ?actorLabel ?runtime {
        ?movie wdt:P31/wdt:P279* wd:Q11424 .
        ?movie rdfs:label ?label 
        """ +f"FILTER(?label = \"{cap(movieName)}\"@en)"+"""
        ?movie wdt:P136 ?genre ;
                wdt:P577 ?date ;
                wdt:P57  ?director ;
                wdt:P86  ?music ;
                wdt:P2142 ?box;
                wdt:P2047  ?runtime;
                wdt:P272  ?company ;
        OPTIONAL{
            ?movie wdt:P161 ?actor .
        }
        OPTIONAL{
            ?movie wdt:P725 ?vactor .
        }
        OPTIONAL{
            ?movie wdt:P166 ?awards .
        }
        SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
        }LIMIT 100"""
        # print(queryString)
        self.agent.setQuery(queryString)
        self.agent.setReturnFormat(JSON)
        results = self.agent.query().convert()['results']['bindings']
        # if no results are found, print a log and return Empty dict
        if len(results) == 0:
            print(f"No results found for {movieName.title()}")
            return "FAIL"
        # if results are found, build a dictionary and return it
        movie_dict = {}
        movie_dict['name'] = results[0]['label']['value'].title()
        movie_dict['year'] = self.formatDate(results[0]['dateLabel']['value'], needYear=True)
        movie_dict['ML'] = []
        movie_dict['BOX'] = locale.currency(int(results[0]['boxLabel']['value']), grouping=True)
        movie_dict['GENRE'] = []
        voice_actors = []
        actors = []
        movie_dict['DIR'] = []
        movie_dict['CL'] = []
        movie_dict['RTIME'] = results[0]['runtime']['value'] + " minutes"
        movie_dict['AWS'] = []
        VactorExists = 'vactorLabel' in results[0].keys()
        ActorExists = 'actorLabel' in results[0].keys()

        for result in results:
            if VactorExists:
                voice_actors.append(result['vactorLabel']['value'].title())
            if ActorExists:
                actors.append(result['actorLabel']['value'].title())

            if 'genreLabel' in result.keys():
                movie_dict['GENRE'].append(result['genreLabel']['value'].title())
            if 'directorLabel' in result.keys():
                movie_dict['DIR'].append(result['directorLabel']['value'].title())
            if 'companyLabel' in result.keys():
                movie_dict['CL'].append(result['companyLabel']['value'].title())
            if 'awardsLabel' in result.keys():
                movie_dict['AWS'].append(result['awardsLabel']['value'].title())
            if 'musicLabel' in result.keys():
                movie_dict['ML'].append(result['musicLabel']['value'].title())

        movie_dict['GENRE'] = list(set(movie_dict['GENRE']))
        voice_actors = list(set(voice_actors))
        actors = list(set(actors))
        movie_dict['cast'] = voice_actors + actors
        movie_dict['CL'] = list(set(movie_dict['CL']))
        movie_dict['DIR'] = list(set(movie_dict['DIR']))
        movie_dict['ML'] = list(set(movie_dict['ML']))
        movie_dict['AWS'] = list(set(movie_dict['AWS']))
        return movie_dict

    def getDirectorDetails(self, director):
    # returns the details of a director based on director name
        queryString = """
            PREFIX wd: <http://www.wikidata.org/entity/>
            PREFIX wdt: <http://www.wikidata.org/prop/direct/>
            PREFIX wikibase: <http://wikiba.se/ontology#>
            PREFIX p: <http://www.wikidata.org/prop/>
            PREFIX ps: <http://www.wikidata.org/prop/statement/>
            PREFIX pq: <http://www.wikidata.org/prop/qualifier/>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX bd: <http://www.bigdata.com/rdf#>

            SELECT DISTINCT ?label ?GDLabel ?CZLabel ?IMGLabel ?DOBLabel ?movieLabel ?awardsLabel  {
            ?director wdt:P106 wd:Q2526255 .
            ?director rdfs:label ?label
            FILTER(lang(?label) = 'en')
            FILTER(?label = \"""" + cap(director) + """\"@en)
            ?director wdt:P21 ?GD ;
                    wdt:P27 ?CZ ;
                    wdt:P569  ?DOB ;
                    wdt:P18 ?IMG.
            OPTIONAL{
                ?movie wdt:P31/wdt:279* wd:Q11424.
                ?movie wdt:P57 ?director.
            }    
            OPTIONAL{
                ?director wdt:P166 ?awards.
                ?awards wdt:P31/wdt:P279* wd:Q618779
            }    
            SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
            }
            """
        # print(queryString)
        self.agent.setQuery(queryString)
        self.agent.setReturnFormat(JSON)
        results = self.agent.query().convert()['results']['bindings']
        # if no results are found, print a log and return Empty dict
        if len(results) == 0:
            print(f"No results found for {director.title()}")
            return "FAIL"
        # if results are found, build a dictionary and return it
        dir_dict = {}
        dir_dict['name'] = results[0]['label']['value'].title()
        dir_dict['DOB'] = self.formatDate(results[0]['DOBLabel']['value'])
        dir_dict['CZ'] = results[0]['CZLabel']['value'].title()
        dir_dict['GD'] = results[0]['GDLabel']['value'].title()
        dir_dict['IMG'] = results[0]['IMGLabel']['value']
        dir_dict['movies'] = list([])
        dir_dict['awards'] = list([])
        for result in results:
            try:
                movie = result['movieLabel']['value']
            except KeyError:
                movie = None
            try:
                award = result['awardsLabel']['value']
            except KeyError:
                award = None
            if movie is not None:
                dir_dict['movies'].append(movie.title())
                if award is not None:
                    dir_dict['awards'].append(award.title() + " for " + movie)
            if award is not None:
                    dir_dict['awards'].append(award.title())

        dir_dict['movies'] = list(set(dir_dict['movies']))
        dir_dict['awards'] = list(set(dir_dict['awards']))
        if(len(dir_dict['awards']) > 15):
            dir_dict['awards'] = dir_dict['awards'][:14]
        # print(dir_dict)
        return dir_dict
    
    def getActorDetails(self, actorName):
        # returns the details of an actor if found on wikidata
        queryString = """
            PREFIX wd: <http://www.wikidata.org/entity/>
            PREFIX wdt: <http://www.wikidata.org/prop/direct/>
            PREFIX wikibase: <http://wikiba.se/ontology#>
            PREFIX p: <http://www.wikidata.org/prop/>
            PREFIX ps: <http://www.wikidata.org/prop/statement/>
            PREFIX pq: <http://www.wikidata.org/prop/qualifier/>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX bd: <http://www.bigdata.com/rdf#>


            SELECT DISTINCT ?label ?GDLabel ?CZLabel ?DOBLabel ?IMGLabel ?movieLabel ?awardsLabel  {
            ?actor wdt:P106 wd:Q10800557 .
            ?actor rdfs:label ?label
            FILTER(lang(?label) = 'en') 
            FILTER(?label = \"""" + cap(actorName) + """\"@en) 
            ?actor wdt:P21 ?GD ;
                    wdt:P27 ?CZ ;
                    wdt:P569  ?DOB ;
                    wdt:P18 ?IMG.
            OPTIONAL{
                ?movie wdt:P31/wdt:279* wd:Q11424.
                ?movie wdt:P161 ?actor.
            }     
            OPTIONAL{
                ?actor wdt:P166 ?awards.
                ?awards wdt:P31/wdt:P279* wd:Q618779
            }     
            SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
            }
        """
        # print(queryString)
        self.agent.setQuery(queryString)
        self.agent.setReturnFormat(JSON)
        results = self.agent.query().convert()['results']['bindings']
        # if no results are found, print a log and return empty dict
        if len(results) == 0:
            print(f"No results found for {actorName.title()}")
            return "FAIL"
        # if results are found, build a dictionary and return it
        actor_dict = {}
        actor_dict['name'] = results[0]['label']['value'].title()
        actor_dict['DOB'] = self.formatDate(results[0]['DOBLabel']['value'])
        actor_dict['CZ'] = results[0]['CZLabel']['value'].title()
        actor_dict['GD'] = results[0]['GDLabel']['value'].title()
        actor_dict['IMG'] = results[0]['IMGLabel']['value']
        actor_dict['movies'] = []
        actor_dict['awards'] = []
        for result in results:
            try:
                movie = result['movieLabel']['value']
                if movie[0] == 'Q':
                    movie = None
            except KeyError:
                movie = None
            try:
                award = result['awardsLabel']['value']
            except KeyError:
                award = None
            if movie is not None:
                actor_dict['movies'].append(movie.title())
                if award is not None:
                    actor_dict['awards'].append(award.title() + " for " + movie)
            if award is not None:
                    actor_dict['awards'].append(award.title())

        actor_dict['movies'] = list(set(actor_dict['movies']))
        actor_dict['awards'] = list(set(actor_dict['awards']))
        if(len(actor_dict['awards']) > 15):
            actor_dict['awards'] = actor_dict['awards'][:14]
        return actor_dict
   


if __name__ == '__main__':

    sparql = Sparql(proxyDict)
    results = sparql.getActorDetails(input("Enter name: "))
    print(results)