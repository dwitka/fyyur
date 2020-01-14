#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
from dateutil.parser import parse
from datetime import datetime, timezone
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify, abort
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# TODO: connect to a local postgresql database---DONE!-----DONE!-------DONE!--

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    genres = db.Column(db.String, nullable=False)
    website = db.Column(db.String(500))
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(500))
    upcoming_shows_count = db.Column(db.Integer, default=0)
    past_shows_count = db.Column(db.Integer, default =0)
    show = db.relationship('Show', backref='venueshow', lazy=True)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'Artist'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String)
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(120))
    past_shows_count = db.Column(db.Integer, default=0)
    upcoming_shows_count = db.Column(db.Integer, default=0)
    show = db.relationship('Show', backref='artistshow', lazy=True)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Show(db.Model):
    __tablename__ = 'Show'
    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.String, nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)

# TODO Implement Show and Artist models, and complete all model relationships 
# and properties, as a database migration.

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):#DONEDONEDONE
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime


#  Helper Functions
#  ----------------------------------------------------------------

def form_error():
  error_message = 'Please fill out all form fields to proceed. Thank you.'
  return error_message

def populate_venue_form_data(form,name,city,state,address,phone,genres,facebook_link):
  form.name.data = name
  form.city.data = city
  form.state.data = state
  form.address.data = address
  form.phone.data = phone
  form.genres.data = genres
  form.facebook_link.data = facebook_link
  return form
  

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data. num_shows should be 
  # aggregated based on number of upcoming shows per venue.
  data = []
  datad = {}
  sub_datad = {}
  indicator = False
  count = 0
  try:
    venues = Venue.query.all()
    shows_list = Show.query.all()
    for venue in venues:
      #find the number of shows
      past_shows_count = 0
      upcoming_shows_count = 0
      for show in shows_list:
        if venue.id == show.venue_id:
          #using time feature determine past shows and upcoming shows
          if parse(show.start_time) < parse(str(datetime.now(timezone.utc))):
            past_shows_count = past_shows_count + 1
          else:
            upcoming_shows_count = upcoming_shows_count + 1
      #set past and upcoming show attributes
      venue.past_shows_count = past_shows_count
      venue.upcoming_shows_count = upcoming_shows_count
      db.session.commit()
      #add the first venue to dictionary
      #this block is done during first run-thru
      if data == []:
        sub_datad['id'] = venue.id
        sub_datad['name'] = venue.name
        sub_datad['num_upcoming_shows'] = venue.upcoming_shows_count
        datad['city'] = venue.city
        datad['state'] = venue.state
        datad['venues'] = [sub_datad]
        data.append(datad)
      #this block only if there is data in data list
      #but have to skip this block on first iteration
      if data != [] and count > 0:
        #check to see if this city already has a listing
        #if it does we add the venue to the listing under venues
        for dictionary in data:
          if venue.city == dictionary['city']:
            dictionary['venues'].append({'id':venue.id, 'name':venue.name, 'num_upcoming_shows':venue.upcoming_shows_count})
            indicator = True
      #enter this block only if we didnt enter the previous block
      #skip this block on first iteration on account of count
      if indicator == False and count > 0:
        sub_datad['id'] = venue.id
        sub_datad['name'] = venue.name
        sub_datad['num_upcoming_shows'] = venue.upcoming_shows_count
        datad['city'] = venue.city
        datad['state'] = venue.state
        datad['venues'] = [sub_datad]
        data.append(datad)
      datad = {}
      sub_datad = {}
      indicator = False
      count = count + 1
  except:
    abort (404)
  finally:
    db.session.close()
  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure search is
  # case-insensitive. Search for Hop should return "The Musical Hop". Search for 
  # "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search = str.lower(request.form['search_term'])
  count = 0
  response = {}
  data_lex = {}
  response['data'] = []
  try:
    venues = Venue.query.all()
    for venue in venues:
      if search in str.lower(venue.name):
        count = count + 1
        response['count'] = count
        data_lex['id'] = venue.id
        data_lex['name'] = venue.name 
        data_lex['num_upcoming_shows'] = venue.upcoming_shows_count
        response['data'].append(data_lex)
        data_lex = {}
  except:
    abort (404)
  finally:
    db.session.close()
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  data = {}
  # retrieve venue by venue_id
  try:
    venue = Venue.query.get(venue_id)
    # populate key/value pairs to data dictionary from venue retrieved
    data['id'] = venue.id
    data['name'] = venue.name
    data['city'] = venue.city
    data['address'] = venue.address
    data['genres'] = venue.genres.split(",")
    data['state'] = venue.state
    data['image_link'] = venue.image_link
    data['phone'] = venue.phone
    data['website'] = venue.website
    data['facebook_link'] = venue.facebook_link
    data['seeking_talent'] = venue.seeking_talent
    data['seeking_description'] = venue.seeking_description
    data['upcoming_shows_count'] = venue.upcoming_shows_count
    data['past_shows_count'] = venue.past_shows_count
    data['past_shows'] = []
    data['upcoming_shows'] = []

    def show_data(show):
      # get data on the shows for key values past_shows or upcoming_shows
      if show:
        artist = Artist.query.get(show.artist_id)
        sub_data = {}
        sub_data['artist_id'] = artist.id
        sub_data['artist_name'] = artist.name
        sub_data['artist_image_link'] = artist.image_link
        sub_data['start_time'] = show.start_time
        return sub_data
      else:
        pass

    # extrapolate past_shows and upcoming_shows show data for the given venue
    shows = Show.query.filter(Show.venue_id==venue_id).all()
    for show in shows:
      if parse(show.start_time) < parse(str(datetime.now(timezone.utc))):
        data['past_shows'].append(show_data(show))
      else:
        data['upcoming_shows'].append(show_data(show))
  except:
    abort (404)
  finally:
    db.session.close()
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  error = False
  try:
    venues = Venue.query.all()
    #find the next highest id number in venues
    number = 0
    for venue in venues:
      if venue.id >= number:
        number = venue.id
    new_venue_id = number + 1
    #retrieve all form data
    name = request.form['name']
    city = request.form['city']
    state = request.form['state']
    address= request.form['address']
    phone = request.form['phone']
    facebook_link = request.form['facebook_link']
    #convert genres list into a csv string
    genres_list = request.form.getlist('genres')
    genres_string = ""
    for item in genres_list:
      genres_string = genres_string + item + ","
    genres = genres_string.strip(",")
    #create new_venue with form data and add to database
    if name and city and state and address and genres:
      new_venue = Venue(id=new_venue_id)
      new_venue.name = name
      new_venue.city = city
      new_venue.state = state
      new_venue.address = address
      new_venue.phone = phone
      new_venue.genres = genres
      new_venue.facebook_link = facebook_link
      db.session.add(new_venue)
      db.session.commit()
      # on successful db insert, flash success
      flash('Venue ' + request.form['name'] + ' was successfully listed!')
    else:
      error = True
  except:
    # TODO: on unsuccessful db insert, flash an error instead.
    flash('An error occurred. Venue ' + name + ' could not be listed.')
    db.session.rollback()
  finally:
    db.session.close()
  if error:
    form = VenueForm()
    form = populate_venue_form_data(form,name,city,state,address,phone,genres,facebook_link)
    flash(form_error())
    return render_template('forms/new_venue.html', form=form)
  else:
    return show_venue(new_venue_id)

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  error = False
  try:
    venue = Venue.query.get(venue_id)
    db.session.delete(venue)
    db.session.commit()
  except:
    db.session.rollback()
    error = True
  finally:
    db.session.close()
  if error:
    abort (404)
  else:
    return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  data = []
  sub_data = {}
  try:
    artists = Artist.query.all()
    shows_list = Show.query.all()
    for artist in artists:
      #find the number of shows
      past_shows_count = 0
      upcoming_shows_count = 0
      for show in shows_list:
        if artist.id == show.artist_id:
          #using time feature determine past shows and upcoming shows
          if parse(show.start_time) < parse(str(datetime.now(timezone.utc))):
            past_shows_count = past_shows_count + 1
          else:
            upcoming_shows_count = upcoming_shows_count + 1
      #set past and upcoming show attributes
      artist.past_shows_count = past_shows_count
      artist.upcoming_shows_count = upcoming_shows_count
      db.session.commit()
      #fill in data list with artist data retrieved
      sub_data['id'] = artist.id
      sub_data['name'] = artist.name
      data.append(sub_data)
      sub_data = {}
  except:
    abort (404)
  finally:
    db.session.close()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure search is
  # case-insensitive. Search for "A" should return "Guns N Petals", "Matt Quevado",
  # and "The Wild Sax Band". Search for "band" should return "The Wild Sax Band".
  try:
    artists = Artist.query.all()
    search_term = str.lower(request.form['search_term'])
    count = 0
    response = {}
    data_lex = {}
    response['data'] = []
    for artist in artists:
      if search_term in str.lower(artist.name):
        count = count + 1
        response['count'] = count
        data_lex['id'] = artist.id
        data_lex['name'] = artist.name 
        data_lex['num_upcoming_shows'] = artist.upcoming_shows_count
        response['data'].append(data_lex)
        data_lex = {}
  except:
    abort (404)
  finally:
    db.session.close()
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artists table, using artist_id
  data = {}
  try:
    artist = Artist.query.get(artist_id)
    # populate key/value pairs to data dictionary from artist retrieved
    data['id'] = artist.id
    data['name'] = artist.name
    data['city'] = artist.city
    data['genres'] = artist.genres.split(",")
    data['state'] = artist.state
    data['image_link'] = artist.image_link
    data['phone'] = artist.phone
    data['website'] = artist.website
    data['facebook_link'] = artist.facebook_link
    data['seeking_venue'] = artist.seeking_venue
    data['seeking_description'] = artist.seeking_description
    data['upcoming_shows_count'] = artist.upcoming_shows_count
    data['past_shows_count'] = artist.past_shows_count
    data['past_shows'] = []
    data['upcoming_shows'] = []

    def show_data(show):
      # get data on the shows for key values past_shows or upcoming_shows
      venue = Venue.query.filter(Venue.id==show.venue_id).first()
      sub_data = {}
      sub_data['venue_id'] = show.venue_id
      sub_data['venue_name'] = venue.name
      sub_data['venue_image_link'] = venue.image_link
      sub_data['start_time'] = show.start_time
      return sub_data

    # extrapolate past_shows and upcoming_shows data for the given artist
    shows = Show.query.filter(Show.artist_id==artist_id).all()
    for show in shows:
      if parse(show.start_time) < parse(str(datetime.now(timezone.utc))):
        data['past_shows'].append(show_data(show))
      else:
        data['upcoming_shows'].append(show_data(show))
  except:
    abort (404)
  finally:
    db.session.close()
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
   # TODO: populate form with fields from artist with ID <artist_id>
  form = ArtistForm()
  try:
    artist = Artist.query.get(artist_id)
    form.name.data = artist.name
    form.city.data = artist.city
    form.state.data = artist.state
    form.phone.data = artist.phone
    form.genres.data = artist.genres
    form.facebook_link.data = artist.facebook_link
  except:
    flash("Artist with id: " + str(artist_id) + " has not been created yet.")
    abort (404)
  finally:
    db.session.close()
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted
  error = False
  name = request.form['name']
  city = request.form['city']
  state = request.form['state']
  phone = request.form['phone']
  facebook_link = request.form['facebook_link']
  # retrieve genres data from genres list field
  genres_list = request.form.getlist('genres')
  genres_string = ""
  for item in genres_list:
    genres_string = genres_string + item + ","
  genres = genres_string.strip(",")
  # TODO: update existing artist record with ID <artist_id> using the new attributes
  try:
    if name and city and state and phone and genres and facebook_link:
      artist = Artist.query.get(artist_id)
      artist.name = name
      artist.city = city
      artist.state = state
      artist.phone = phone
      artist.genres = genres
      artist.facebook_link = facebook_link
      db.session.commit()
    else:
      error = True
  except:
    db.session.rollback()
    abort (404)
  finally:
    db.session.close()
  if error:
    form = ArtistForm()
    form.name.data = name
    form.city.data = city
    form.state.data = state
    form.phone.data = phone
    form.genres.data = genres
    form.facebook_link.data = facebook_link
    flash(form_error())
    return render_template('/forms/edit_artist.html', form=form, artist=Artist.query.get(artist_id))
  else:
    return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  # TODO: populate form with values from venue with ID <venue_id>
  form = VenueForm()
  try:
    venue = Venue.query.get(venue_id)
    form.name.data = venue.name
    form.city.data = venue.city
    form.state.data = venue.state
    form.address.data = venue.address
    form.phone.data = venue.phone
    form.genres.data = venue.genres
    form.facebook_link.data = venue.facebook_link
  except:
    flash("Venue with id: " + str(venue_id) + " has not been created yet.")
    abort (404)
  finally:
    db.session.close()
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted
  error = False
  name = request.form['name']
  city = request.form['city']
  state = request.form['state']
  address = request.form['address']
  phone = request.form['phone']
  facebook_link = request.form['facebook_link']
  # get genres data from genres list field
  genres_list = request.form.getlist('genres')
  genres_string = ""
  for item in genres_list:
    genres_string = genres_string + item + ","
  genres = genres_string.strip(",")
  # TODO: update existing venue record with ID <venue_id> using the new attributes.
  try:
    if name and city and state and address and genres:
      venue = Venue.query.get(venue_id)
      venue.name = name
      venue.city = city
      venue.state = state
      venue.address = address
      venue.phone = phone
      venue.genres = genres
      venue.facebook_link = facebook_link
      db.session.commit()
    else:
        error = True
  except:
    db.session.rollback()
    abort (404)
  finally:
    db.session.close()
  if error:
    form = VenueForm()
    form = populate_venue_form_data(form,name,city,state,address,phone,genres,facebook_link)
    flash(form_error())
    return render_template('/forms/edit_venue.html', form=form, venue=Venue.query.get(venue_id))
  else:
    return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  error = False
  try:
    artists = Artist.query.all()
    number =0
    for artist in artists:
      if artist.id >= number:
        number = artist.id
    new_artist_id = number + 1
    # retrieve artist form data
    name = request.form['name']
    city = request.form['city']
    state = request.form['state']
    phone = request.form['phone']
    facebook_link = request.form['facebook_link']
    # retrieve genres data from genres list field
    genres_list = request.form.getlist('genres')
    genres_string = ""
    for item in genres_list:
      genres_string = genres_string + item + ","
    genres = genres_string.strip(",")
    # create new artist onlyif essential fields are filled
    if name and city and state and genres:
      new_artist = Artist(id=new_artist_id)
      new_artist.name = name
      new_artist.city = city
      new_artist.state = state
      new_artist.phone = phone
      new_artist.genres = genres
      new_artist.facebook_link = facebook_link
      db.session.add(new_artist)
      db.session.commit()
      # on successful db insert, flash success
      flash('Artist ' + request.form['name'] + ' was successfully listed!')
    else:
      error = True
  except:
    # TODO: on unsuccessful db insert, flash an error instead.
    flash('An error occurred. Artist ' + name + ' could not be listed.')
    db.session.rollback()
  finally:
    db.session.close()
  if error:
    # if essential fields are not filled, flash error and reload page 
    # with data already given
    form = ArtistForm()
    form.name.data = name
    form.city.data = city
    form.state.data = state
    form.phone.data = phone
    form.genres.data = genres
    form.facebook_link.data = facebook_link
    flash(form_error())
    return render_template('/forms/new_artist.html', form=form)
  else:
    return show_artist(new_artist_id)


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  data = []
  datad={}
  try:
    shows=Show.query.all()
    for show in shows:
      datad['venue_id'] = show.id
      datad['venue_name'] = Venue.query.get(show.venue_id).name
      datad['artist_id'] = show.artist_id
      artist = Artist.query.get(show.artist_id)
      datad['artist_name'] = artist.name
      datad['artist_image_link'] = artist.image_link
      datad['start_time'] = show.start_time
      data.append(datad)
      datad = {}
  except:
    abort (404)
  finally:
    db.session.close()
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  error = False
  try:
    shows = Show.query.all()
    number = 0
    for show in shows:
      if show.id >= number:
        number = show.id
    new_show_id = number + 1
    # retrieve form data
    artist_id = request.form['artist_id']
    venue_id = request.form['venue_id']
    start_time = request.form['start_time']
    start_time = (str(start_time))[:10] + "T" + (str(start_time))[-8:] + ".000Z"
    # create new show with retrieved data
    if artist_id and venue_id and start_time:
      new_show = Show(id=new_show_id)
      new_show.artist_id = artist_id
      new_show.venue_id = venue_id
      new_show.start_time = start_time
      # add show to database and commit
      db.session.add(new_show)
      db.session.commit()
      flash('Show was successfully listed!')
    else:
      error = True
  except:
    # TODO: on unsuccessful db insert, flash an error instead.
    db.session.rollback()
    flash('An error occurred. Show could not be listed.')
    abort (404)
  finally:
    db.session.close()
  if error:
    # if essential fields are not filled, flash error and reload page 
    # with data already given
    form = ShowForm()
    form.artist_id.data = artist_id
    form.venue_id.data = venue_id
    form.start_time.data = start_time
    flash(form_error())
    return render_template('/forms/new_show.html', form=form)
  else:
    return render_template('pages/home.html')


#  Error Handlers
#  ----------------------------------------------------------------

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
