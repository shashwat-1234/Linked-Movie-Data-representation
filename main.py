from flask import Flask, render_template, request
from helper import get_movie_poster, Sparql

app = Flask(__name__)

# global variables
filters = ['Movie', 'Actor', 'Director']
current_filter = filters[0]

genres= ["Romance","Comedy","Fantasy","Thriller"]
current_genre= genres[0]



@app.route('/', methods=['GET','POST'])
def index():
    global current_filter
    current_filter = request.args.get('filter')
    search_term = request.args.get('searchInput')

    # if loading page without any args
    if request.method == "GET" and current_filter == None:
        return render_template('index.html', filters=filters, current_filter="Movie", results=None)

    if request.method == "GET":
        print(current_filter)
        print(search_term)
        # if searchTerm is empty
        if search_term == "":
            return render_template('index.html', filters=filters,current_filter=current_filter, results=None)
        # instantiate a Sparql Object
        sp_inst = Sparql()
        if current_filter == 'Movie':
            results = sp_inst.getMovieDetails(search_term)
            if results == 'FAIL':
                # if results not fouud in SPARQL, return error
                return render_template('index.html', filters=filters, current_filter=current_filter, results=results)
            poster_res = get_movie_poster(search_term)
            if poster_res is None:
                image = None
                rating = "N/A"
            else:
                image,rating = poster_res   
            print(image)             
            print(rating)
            results['image'] = image
            results['rating'] = rating
            return render_template('index.html', filters=filters, current_filter=current_filter, results=results)
        elif current_filter == 'Actor':
            results = sp_inst.getActorDetails(search_term)
            return render_template('index.html', filters=filters, current_filter=current_filter, results=results)
        elif current_filter == 'Director':
            results = sp_inst.getDirectorDetails(search_term)
            return render_template('index.html', filters=filters, current_filter=current_filter, results=results)

@app.route('/analyse', methods=['GET','POST'])
def analyse():
    global current_genre
    current_genre = request.args.get('genre')
    if request.method == "GET" and current_genre == None:
        return render_template('analysis.html', filters=genres, current_filter="Romance",data= [12, 19, 3, 5, 2, 3], label=['Red', 'Blue', 'Yellow', 'Green', 'Purple', 'Orange'])

    return render_template('analysis.html', label=['Red', 'Blue', 'Yellow', 'Green', 'Purple', 'Orange'])

if __name__ == '__main__':
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.config['DEBUG'] = True
    app.run()