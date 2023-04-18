# Linked-Movie-Data-representation

The above repository contains the code for Linked Movie Data representation. 
It consists of majorly three parts:
1. Data has been taken from the IMDb databse. 
2. It was then converted from TSV to json using script.py present in the imdb_data_folder, the resultant files could be seen there. 
3. Auxiliary folder consists of the json2rdf_script.py which converts the json file into its equivalent rdf representation. 
4. Ontology folder consists of the main turtle file that is used as our database. 

The turtle file was hosted over Apache Jena Fuseki Server, the endpoint then created from it was used by our frontend to show the effectiveness of search and result through graph database. 
# [Youtube Video Link ](https://youtu.be/NFRNrF0GzwE)



