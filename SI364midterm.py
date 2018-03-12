###############################
####### SETUP (OVERALL) #######
###############################

## Import statements
# Import statements
import os
from flask import Flask, render_template, session, redirect, url_for, flash, request
from flask_wtf import FlaskForm
from wtforms import StringField,SubmitField,ValidationError # Note that you may need to import more here! Check out examples that do what you want to figure out what.
from wtforms.validators import Required, Length
from flask_sqlalchemy import SQLAlchemy
import omdb
import requests
import json

#api= 'http://www.omdbapi.com/?i=tt3896198&apikey=12fe4e3b'

## App setup code
app = Flask(__name__)
app.debug = True
app.use_reloader = True

## All app.config values
# app = Flask(__name__)
# app.debug = True

app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://localhost/amrgomezSI364midterm"
app.config['SECRET_KEY'] = 'hardtoguessstringfromsi364thisisnotsupersecurebutitsok'

## Statements for db setup (and manager setup if using Manager)


app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db = SQLAlchemy(app)
######################################
######## HELPER FXNS (If any) ########
######################################
def get_or_create_movie(movies):
    title= db.session.query(MovieTitle).filter_by(movies=movies).first()
    if not title:
        title= MovieTitle(movies= movies)
        db.session.add(title)
        db.session.commit()
        flash("Movie successfully added!")
        return title
    else:
        flash("Movie already added!")
        return title

##################
##### MODELS #####
##################



class MovieTitle(db.Model):
    __tablename__= 'movies'
    id= db.Column(db.Integer, primary_key=True)
    movies= db.Column(db.String(64))
    years= db.relationship('Years', backref= 'MovieTitle')
    def __repr__(self):
        return "{}".format(self.movies)

class Years(db.Model):
    __tablename__= 'years'
    id= db.Column(db.Integer, primary_key= True)
    year= db.Column(db.String(64))
    movie_id=db.Column(db.Integer,db.ForeignKey('movies.id'))
    def __repr__(self):
        return "{}".format(self.year)
        
class Name(db.Model):
    __tablename__ = "names"
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(64))
    def __repr__(self):
        return "{} (ID: {})".format(self.name, self.id)



###################
###### FORMS ######
###################
class MovieForm(FlaskForm):
    movie_title= StringField('Enter a movie: ',validators= [Required(),Length(min=1,max=280)])
    submit= SubmitField('Submit')

    def validate_movie_title(self,field):
        if field.data[0] is '~':
            return ValidationError('Title Invalid')
    def validate_release_year(self,field):
        if field.data[0] is '0':
            return ValidationError('Invalid Year')

class NameForm(FlaskForm):
    name = StringField("Please enter your name: ",validators=[Required(),Length(min=1,max=280)])
    submit = SubmitField('Submit')

    def validate_name(self,field):
        if field.data[0] is '0':
            return ValidationError('Invalid Response')



#ERROR HANDLING ROUTES
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


#######################
###### VIEW FXNS ######
#######################

@app.route('/',methods=['GET'])
def home():
    form = NameForm() # User should be able to enter name after name and each one will be saved, even if it's a duplicate! Sends data with GET
    return render_template('base.html',form=form)

@app.route('/names')
def all_names():
    if request.args:
        name = request.args['name']
        newname = Name(name=name)
        db.session.add(newname)
        db.session.commit()
        return redirect(url_for('all_names'))
    return render_template('name_example.html',names=Name.query.all())  

@app.route('/movie_titles', methods= ['GET','POST'])
def movies():
    form=MovieForm()
    if request.method == "POST" and form.validate_on_submit():
        movies1=form.movie_title.data
        url= 'http://www.omdbapi.com/?apikey=12fe4e3b&t={}'.format(movies1)
        req=requests.get(url)
        txt= req.json()
        all_movies=get_or_create_movie(txt['Title'])
        add_year= Years(year=txt['Year'], movie_id= all_movies.id)
        db.session.add(add_year)
        db.session.commit()
        redirect(url_for('years'))
    return render_template('movie_titles.html',form=form)

@app.route('/release_years', methods=['GET', 'POST'])
def years():
    all_years= Years.query.all()
    return render_template('years_released.html',all_years= all_years)



## Code to run the application...
if __name__ == '__main__':
    db.create_all() # Will create any defined models when you run the application
    app.run(use_reloader=True,debug=True) # The usual
# Put the code to do so here!
# NOTE: Make sure you include the code you need to initialize the database structure when you run the application!
