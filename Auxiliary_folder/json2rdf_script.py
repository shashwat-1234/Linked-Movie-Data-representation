import fileinput, csv, pprint, json, time, urllib.request
import unidecode as ud

def prepare_human_rdf(file):
    
#_______________________________________manage individuals humans

    # """<!-- http://miei.di.uminho.pt/prc2018/hollywood#nm0000375 -->
    #     <owl:NamedIndividual rdf:about="http://miei.di.uminho.pt/prc2018/hollywood#nm0000375">
    #         <rdf:type rdf:resource="http://miei.di.uminho.pt/prc2018/hollywood#Actor"/>
    #         <rdf:type rdf:resource="http://miei.di.uminho.pt/prc2018/hollywood#Person"/>
    #         <hollywood:knownFor rdf:resource="http://miei.di.uminho.pt/prc2018/hollywood#tt1515091"/>
    #         <hollywood:birthYear rdf:datatype="http://www.w3.org/2001/XMLSchema#integer">1965</hollywood:birthYear>
    #         <hollywood:name>Robert Downey Jr.</hollywood:name>
    #         <hollywood:sex>M</hollywood:sex>
    #     </owl:NamedIndividual>"""

    final_rdf = ""
    for x in file:
        hm = file[x]
        #comment
        string_comment = "\t<!-- http://miei.di.uminho.pt/prc2018/hollywood#" + x + "-->\n\n"
        #id
        string_id = "\t<owl:NamedIndividual rdf:about=\"http://miei.di.uminho.pt/prc2018/hollywood#" + x + "\">\n"
        #type Person (in all)
        string_type_person = "\t\t<rdf:type rdf:resource=\"http://miei.di.uminho.pt/prc2018/hollywood#Person\"/>\n"
        #type actor ou producer ou writer
        professions = hm.get("primaryProfession",None)
        string_types = ""
        if professions != None:
            if "actor" or "actress" in professions:
                string_types = "\t\t<rdf:type rdf:resource=\"http://miei.di.uminho.pt/prc2018/hollywood#Actor\"/>\n"
            if "producer" in professions:
                string_types += "\t\t<rdf:type rdf:resource=\"http://miei.di.uminho.pt/prc2018/hollywood#Director\"/>\n"
            if "writer" in professions:
                string_types += "\t\t<rdf:type rdf:resource=\"http://miei.di.uminho.pt/prc2018/hollywood#Writer\"/>\n"
            if "composer" in professions:
                string_types += "\t\t<rdf:type rdf:resource=\"http://miei.di.uminho.pt/prc2018/hollywood#Composer\"/>\n"
        #KnownFor relationship
        y = hm.get("knownForTitles",None)
        string_knownFor = ""
        if y!=None:
            for tt in file[x]["knownForTitles"]:
                string_knownFor += "\t\t<hollywood:knownFor rdf:resource=\"http://miei.di.uminho.pt/prc2018/hollywood#" + tt + "\"/>\n"
        #birthYear
        string_birthYear = ""
        if hm["birthYear"] != "null":
            string_birthYear = "\t\t<hollywood:birthYear rdf:datatype=\"http://www.w3.org/2001/XMLSchema#integer\">" + hm["birthYear"] + "</hollywood:birthYear>\n"
        #deathYear
        string_deathYear = ""
        if hm["deathYear"]!= "null":
            string_deathYear = "\t\t<hollywood:deathYear rdf:datatype=\"http://www.w3.org/2001/XMLSchema#integer\">" + hm["deathYear"] + "</hollywood:deathYear>\n"
        #name
        string_nome = "\t\t<hollywood:name>" + hm["primaryName"] + "</hollywood:name>\n"
        #sex: if you have an actor it's m, if you have an actress it's F
        string_sex = ""
        if "actor" in hm["primaryProfession"]:
            string_sex = "\t\t<hollywood:sex>M</hollywood:sex>\n"
        else:
            if "actress" in hm["primaryProfession"]:
                string_sex = "\t\t<hollywood:sex>F</hollywood:sex>\n"
        #string close
        string_date = "\t</owl:NamedIndividual>\n\n"
        

        final = string_comment + string_id + string_type_person + string_types + string_knownFor + string_birthYear + string_deathYear + string_nome + string_sex + string_fecha
        final_rdf = final_rdf + final
    return final_rdf

def prepare_movie_rdf(file):
    
#__________________________________generate individuals movies_____________________________
    # <owl:NamedIndividual rdf:about="http://miei.di.uminho.pt/prc2018/hollywood#tt1515091">
    #     <rdf:type rdf:resource="http://miei.di.uminho.pt/prc2018/hollywood#Movie"/>
    #     <hollywood:fromCountry rdf:resource="http://miei.di.uminho.pt/prc2018/hollywood#cntry87_USA"/>
    #     <hollywood:fromStudio rdf:resource="http://miei.di.uminho.pt/prc2018/hollywood#corp_808"/>
    #     <hollywood:hasActor rdf:resource="http://miei.di.uminho.pt/prc2018/hollywood#nm0000375"/>
    #     <hollywood:hasActor rdf:resource="http://miei.di.uminho.pt/prc2018/hollywood#nm0000179"/>
    #     <hollywood:hasActor rdf:resource="http://miei.di.uminho.pt/prc2018/hollywood#nm0364813"/>
    #     <hollywood:hasActor rdf:resource="http://miei.di.uminho.pt/prc2018/hollywood#nm1046097"/>
    #     <hollywood:hasDirector rdf:resource="http://miei.di.uminho.pt/prc2018/hollywood#nm0005363"/>
    #     <hollywood:hasWriter rdf:resource="http://miei.di.uminho.pt/prc2018/hollywood#nm1802251"/>
    #     <hollywood:hasWriter rdf:resource="http://miei.di.uminho.pt/prc2018/hollywood#nm0612487"/>
    #     <hollywood:hasWriter rdf:resource="http://miei.di.uminho.pt/prc2018/hollywood#nm0236279"/>
    #     <hollywood:hasGenre rdf:resource="http://miei.di.uminho.pt/prc2018/hollywood#gnr11_Action"/>
    #     <hollywood:hasGenre rdf:resource="http://miei.di.uminho.pt/prc2018/hollywood#gnr21_Adventure"/>
    #     <hollywood:hasGenre rdf:resource="http://miei.di.uminho.pt/prc2018/hollywood#gnr7_Crime"/>
    #     <hollywood:hasLanguage rdf:resource="http://miei.di.uminho.pt/prc2018/hollywood#lang118_English"/>
    #     <hollywood:hasLanguage rdf:resource="http://miei.di.uminho.pt/prc2018/hollywood#lang123_Italian"/>
    #     <hollywood:hasLanguage rdf:resource="http://miei.di.uminho.pt/prc2018/hollywood#lang126_Romany"/>
    #     <hollywood:hasLanguage rdf:resource="http://miei.di.uminho.pt/prc2018/hollywood#lang137_French"/>
    #     <hollywood:hasLanguage rdf:resource="http://miei.di.uminho.pt/prc2018/hollywood#lang45_German"/>
    #     <hollywood:mpaa_rated rdf:resource="http://miei.di.uminho.pt/prc2018/hollywood#mpaa3_PG-13"/>
    #     <hollywood:boxOffice rdf:datatype="http://www.w3.org/2001/XMLSchema#decimal">186830669.0</hollywood:boxOffice>
    #     <hollywood:name>Sherlock Holmes: A Game of Shadows</hollywood:name>
    #     <hollywood:numVotes rdf:datatype="http://www.w3.org/2001/XMLSchema#integer">374880</hollywood:numVotes>
    #     <hollywood:plot>Sherlock Holmes and his sidekick Dr. Watson join forces to outwit and bring down their fiercest adversary, Professor Moriarty.</hollywood:plot>
    #     <hollywood:poster>https://ia.media-imdb.com/images/M/MV5BMTQwMzQ5Njk1MF5BMl5BanBnXkFtZTcwNjIxNzIxNw@@._V1_SX300.jpg</hollywood:poster>
    #     <hollywood:premiereYear rdf:datatype="http://www.w3.org/2001/XMLSchema#integer">2011</hollywood:premiereYear>
    #     <hollywood:rating_IMD rdf:datatype="http://www.w3.org/2001/XMLSchema#decimal">7.5</hollywood:rating_IMD>
    #     <hollywood:rating_META rdf:datatype="http://www.w3.org/2001/XMLSchema#decimal">4.8</hollywood:rating_META>
    #     <hollywood:rating_RT rdf:datatype="http://www.w3.org/2001/XMLSchema#decimal">5.9</hollywood:rating_RT>
    #     <hollywood:runtime rdf:datatype="http://www.w3.org/2001/XMLSchema#integer">129</hollywood:runtime>
    #     <hollywood:website>http://www.sherlockholmes2.com</hollywood:website>
    # </owl:NamedIndividual>


    final_rdf = ""
    for key in file:
        tit = file[key]
        s_comment = "\t<!-- http://miei.di.uminho.pt/prc2018/hollywood#" + key + "-->\n\n"
        s_abre = "\t<owl:NamedIndividual rdf:about=\"http://miei.di.uminho.pt/prc2018/hollywood#" + key + "\">\n"
        s_type = "\t\t<rdf:type rdf:resource=\"http://miei.di.uminho.pt/prc2018/hollywood#Movie\"/>\n"
        #fromCountry
        s_country= ""
        for cntr in tit["country"]:
            s_country += "\t\t<hollywood:fromCountry rdf:resource=\"http://miei.di.uminho.pt/prc2018/hollywood#" + cntr + "\"/>\n"
        #fromStudio
        s_studio = ""
        if tit["corporation"] != "null":
            s_studio = "\t\t<hollywood:fromStudio rdf:resource=\"http://miei.di.uminho.pt/prc2018/hollywood#" + tit["corporation"] + "\"/>\n"
        #hasGenre
        s_genre = ""
        for gnr in tit["genres"]:
            s_genre += "\t\t<hollywood:hasGenre rdf:resource=\"http://miei.di.uminho.pt/prc2018/hollywood#" + gnr + "\"/>\n"
        #hasLanguage
        s_language = ""
        for lng in tit["language"]:
            s_language += "\t\t<hollywood:hasLanguage rdf:resource=\"http://miei.di.uminho.pt/prc2018/hollywood#" + lng +  "\"/>\n"
        #mpaa_rated
        s_mpaa = "\t\t<hollywood:mpaa_rated rdf:resource=\"http://miei.di.uminho.pt/prc2018/hollywood#" + tit["mpaa_rate"] + "\"/>\n"
        #hasActor
        s_ator = ""
        x = tit.get("primaryActors",None)
        if x!=None:
            for actr in tit["primaryActors"]:
                s_ator += "\t\t<hollywood:hasActor rdf:resource=\"http://miei.di.uminho.pt/prc2018/hollywood#" + actr + "\"/>\n"
        #hasWriter 
        s_writer = ""
        for wrtr in tit["writers"]:
            if wrtr != "null":
                s_writer += "\t\t<hollywood:hasWriter rdf:resource=\"http://miei.di.uminho.pt/prc2018/hollywood#" + wrtr +  "\"/>\n"
        #hasDirector
        s_drtr = ""
        for drct in tit["directors"]:
            if drct != "null":
                s_drtr += "\t\t<hollywood:hasDirector rdf:resource=\"http://miei.di.uminho.pt/prc2018/hollywood#" + drct +  "\"/>\n"
        #______data properties
        #name
        s_name = "\t\t<hollywood:name>" +tit["primaryTitle"] + "</hollywood:name>\n"
        #numVotes
        s_votes = "\t\t<hollywood:numVotes rdf:datatype=\"http://www.w3.org/2001/XMLSchema#integer\">"+ tit["numVotes"] +"</hollywood:numVotes>\n"
        #plot
        s_plot = "\t\t<hollywood:plot>" + tit["plot"] + "</hollywood:plot>\n"
        #poster
        s_poster = "\t\t<hollywood:poster>" + tit["poster"] +  "</hollywood:poster>\n"
        #premiere year
        s_year = "\t\t<hollywood:premiereYear rdf:datatype=\"http://www.w3.org/2001/XMLSchema#integer\">"+ tit["startYear"] + "</hollywood:premiereYear>\n"
        #tres ratings
        s_rating = ""
        for rating in tit["ratings"]:
            #rating_IMD
            if rating["Source"] == "Internet Movie Database":
                s_rating += "\t\t<hollywood:rating_IMD rdf:datatype=\"http://www.w3.org/2001/XMLSchema#decimal\">" + str(rating["Value"]) + "</hollywood:rating_IMD>\n"
            else:
                #rating_RT
                if rating["Source"] == "Rotten Tomatoes":
                    s_rating += "\t\t<hollywood:rating_RT rdf:datatype=\"http://www.w3.org/2001/XMLSchema#decimal\">"+ str(rating["Value"]) + "</hollywood:rating_RT>\n"
                else:
                    #rating_META
                    if rating["Source"] == "Metacritic":
                        s_rating += "\t\t<hollywood:rating_META rdf:datatype=\"http://www.w3.org/2001/XMLSchema#decimal\">"+ str(rating["Value"]) + "</hollywood:rating_META>\n"
        #runtime
        s_runtime = "\t\t<hollywood:runtime rdf:datatype=\"http://www.w3.org/2001/XMLSchema#integer\">" + tit["runtimeMinutes"] + "</hollywood:runtime>\n"
        #website
        s_website =""
        if tit["website"] != "N/A":
            s_website = "\t\t<hollywood:website>" +tit["website"] + "</hollywood:website>\n"
        #boxOffice
        s_boxoffice=""
        if tit["boxoffice"] != "N/A":
            s_boxoffice = "\t\t<hollywood:boxOffice rdf:datatype=\"http://www.w3.org/2001/XMLSchema#decimal\">" + str(tit["boxoffice"]) + "</hollywood:boxOffice>\n"
        #to close
        s_fecha = "\t</owl:NamedIndividual>\n\n"
        final = s_comment + s_abre + s_type + s_country + s_studio + s_genre + s_language + s_mpaa + s_ator + s_writer + s_drtr + s_name + s_votes + s_plot + s_poster + s_year + s_rating + s_runtime + s_website + s_boxoffice + s_fecha
        final_rdf = final_rdf + final

    return final_rdf
    

def main():
    
    movies = json.load(open('imdb_data_file/movies_ids.json'))
    humans = json.load(open('imdb_data_file/humans.json'))
    movie_rdf = prepare_movie_rdf(movies)
    human_rdf = prepare_human_rdf(humans)

    with open('full_ontology.rdf', 'a', encoding='utf-8') as file:
        file.write(movie_rdf)
        file.write(human_rdf)
    

if __name__ == '__main__':
    main()
