###############################
####### SETUP (OVERALL) #######
###############################

## Import statements
# Import statements
import os
from flask import Flask, render_template, session, redirect, url_for, flash, request
from flask_wtf import FlaskForm
from wtforms import StringField,SubmitField,ValidationError, IntegerField # Note that you may need to import more here! Check out examples that do what you want to figure out what.
from wtforms.validators import Required, Length
from flask_sqlalchemy import SQLAlchemy
import omdb


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




##################
##### MODELS #####
##################



class MovieTitle(db.Model):
    __tablename__= 'movies'
    id= db.Column(db.Integer, primary_key=True)
    movies= db.Column(db.String(64))
    years= db.relationship('Year', backref= 'MovieTitle')
    def __repr__(self):
        return "{} (ID: {})".format(self.movies, self.id)

class Year(db.Model):
    __tablename__= 'years'
    id= db.Column(db.Integer, primary_key= True)
    year= db.Column(db.Integer)
    year_id=db.Column(db.Integer,db.ForeignKey('movies.id'))
    def __repr__(self):
        return "{} (ID: {})".format(self.year, self.id)
        
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
    years= IntegerField('Enter the year the movie was released: ', validators=[Required(),Length(min=2,max=4)])
    submit= SubmitField('Submit')

    def validate_movie_title(self,field):
        if field.data[0] is '~':
            return ValidationError('Title Invalid')

class NameForm(FlaskForm):
    name = StringField("Please enter your name:",validators=[Required(),Length(min=1,max=280)])
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
    if form.validate_on_submit():
        name = form.name.data
        newname = Name(name)
        db.session.add(newname)
        db.session.commit()
        return redirect(url_for('all_names'))
    return render_template('base.html',form=form)

@app.route('/names')
def all_names():
    names = Name.query.all()
    return render_template('name_example.html',names=names)  

@app.route('/movie_titles', methods= ['GET','POST'])
def movies():
    form1=MovieForm(request.form)
    if form.validate_on_submit():
        movies=form.movies.data
    return render_template('movie_titles.html',form=form1)

@app.route('/release_years', methods=['GET','POST'])
def years():
    form1=MovieForm(request.form) 
    if form.validate_on_submit():
        years= form.years.data
    return render_template('release_years.html',form=form1)


## Code to run the application...
if __name__ == '__main__':
    db.create_all() # Will create any defined models when you run the application
    app.run(use_reloader=True,debug=True) # The usual
# Put the code to do so here!
# NOTE: Make sure you include the code you need to initialize the database structure when you run the application!
