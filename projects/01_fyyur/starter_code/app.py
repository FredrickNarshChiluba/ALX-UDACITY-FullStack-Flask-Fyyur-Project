#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
from ast import dump
from asyncio.windows_events import NULL
import json
from sre_parse import State
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
import sys
from datetime import datetime
from markupsafe import Markup
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#
from models import*
#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale='en')


app.jinja_env.filters['datetime'] = format_datetime

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
    # TODO: replace with real venues data.
    # num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
    distinct_city_state = Venue.query.distinct(Venue.city, Venue.state).all()
    # city_state_venues=Venue.query.filter_by(Venue.city==NULL,Venue.state==NULL).all()
    listofdata = []
    listofdata_dictionary = {}
    venuelist = []
    venuelist_dictionary = {}

    for res in distinct_city_state:
        # city and state with empty venue
        listofdata_dictionary['city'] = res.city
        listofdata_dictionary['state'] = res.state

        city_state_venues = Venue.query.filter_by(
            city=res.city, state=res.state).all()

        for res1 in city_state_venues:
            venuelist_dictionary['id'] = res1.id
            venuelist_dictionary['name'] = res1.name
            venuelist_dictionary['num_upcoming_shows'] = 0

            venuelist.append(venuelist_dictionary)
            venuelist_dictionary = {}
        listofdata_dictionary['venues'] = venuelist
        listofdata.append(listofdata_dictionary)
        listofdata_dictionary = {}
        venuelist = []
    # the data is listofdata
    print(listofdata)

    # data = [{
    #     "city": "San Francisco",
    #     "state": "CA",
    #     "venues": [{
    #         "id": 1,
    #         "name": "The Musical Hop",
    #         "num_upcoming_shows": 0,
    #     }, {
    #         "id": 3,
    #         "name": "Park Square Live Music & Coffee",
    #         "num_upcoming_shows": 1,
    #     }]
    # }, {
    #     "city": "New York",
    #     "state": "NY",
    #     "venues": [{
    #         "id": 2,
    #         "name": "The Dueling Pianos Bar",
    #         "num_upcoming_shows": 0,
    #     }]
    # }]
    return render_template('pages/venues.html', areas=listofdata)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    # TODO: implement search on venues with partial string search. Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    item_to_search = request.form.get('search_term', '')
    search_results = Venue.query.filter(
        Venue.name.like('%'+item_to_search+'%')).all()
    response1_dictionary = {}
    response1_data_list = []
    data_list_dictionary = {}

    coun_ter = 0
    for res in search_results:
        coun_ter += 1
        data_list_dictionary['id'] = res.id
        data_list_dictionary['name'] = res.name
        data_list_dictionary['num_upcoming_shows'] = 0

        response1_data_list.append(data_list_dictionary)
        data_list_dictionary = {}

    response1_dictionary['counter'] = coun_ter
    response1_dictionary['data'] = response1_data_list
    print(response1_dictionary)

    # response = {
    #     "count": 1,
    #     "data": [{
    #         "id": 2,
    #         "name": "The Dueling Pianos Bar",
    #         "num_upcoming_shows": 0,
    #     }]
    # }
    return render_template('pages/search_venues.html', results=response1_dictionary, search_term=item_to_search)


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id
    venue_result = Venue.query.filter(Venue.id == venue_id).first()
    venue_past_shows=db.session.query(Show).join(Venue).filter(Show.venue_id==venue_id).filter(Show.start_time<datetime.now()).all()
    print('pastshows:::::::')
    print(venue_past_shows)
    venue_upcoming_shows=db.session.query(Show).join(Venue).filter(Show.venue_id==venue_id).filter(Show.start_time>datetime.now()).all()
    print('upcomingshows:::::::')
    print(venue_upcoming_shows)

    data_list = []
    data_list_dictionary = {}
    past_shows_list = []
    past_shows_data_dictionary = {}
    upcoming_shows_list = []
    upcoming_shows_data_dictionary = {}
    print(venue_result.name)

    # venue_shows = venue_result.show
    past_show_count = 0
    upcoming_show_count = 0
    
    for a_show in venue_upcoming_shows:
        upcoming_show_count+=1
        upcoming_shows_data_dictionary['artist_id'] = a_show.artist.id
        upcoming_shows_data_dictionary['artist_name'] = a_show.artist.name
        upcoming_shows_data_dictionary['artist_image_link'] = a_show.artist.image_link
        upcoming_shows_data_dictionary['start_time'] = a_show.start_time.strftime(
                "%m/%d/%Y, %H:%M:%S")
        
        upcoming_shows_list.append(upcoming_shows_data_dictionary)
        upcoming_shows_data_dictionary = {}
    # print(upcoming_shows_list)
    
    for a_show1 in venue_past_shows:
        past_show_count += 1
        past_shows_data_dictionary['artist_id'] = a_show1.artist.id
        past_shows_data_dictionary['artist_name'] = a_show1.artist.name
        past_shows_data_dictionary['artist_image_link'] = a_show1.artist.image_link
        past_shows_data_dictionary['start_time'] = a_show1.start_time.strftime(
                "%m/%d/%Y, %H:%M:%S")

        past_shows_list.append(past_shows_data_dictionary)
        past_shows_data_dictionary = {}

    data_list_dictionary['id'] = venue_result.id
    data_list_dictionary['name'] = venue_result.name
    data_list_dictionary['genres'] = [venue_result.genre]
    data_list_dictionary['address'] = venue_result.address
    data_list_dictionary['city'] = venue_result.city
    data_list_dictionary['state'] = venue_result.state
    data_list_dictionary['phone'] = venue_result.phone
    data_list_dictionary['website'] = venue_result.website_link
    data_list_dictionary['facebook_link'] = venue_result.facebook_link
    data_list_dictionary['seeking_talent'] = venue_result.seeking_talent
    data_list_dictionary['seeking_description'] = venue_result.seeking_description
    data_list_dictionary['image_link'] = venue_result.image_link
    data_list_dictionary['past_shows'] = past_shows_list
    data_list_dictionary['upcoming_shows'] = upcoming_shows_list
    data_list_dictionary['past_shows_count'] = past_show_count
    data_list_dictionary['upcoming_shows_count'] = upcoming_show_count

    data_list.append(data_list_dictionary)


    # data1 = {
    #     "id": 1,
    #     "name": "The Musical Hop",
    #     "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    #     "address": "1015 Folsom Street",
    #     "city": "San Francisco",
    #     "state": "CA",
    #     "phone": "123-123-1234",
    #     "website": "https://www.themusicalhop.com",
    #     "facebook_link": "https://www.facebook.com/TheMusicalHop",
    #     "seeking_talent": True,
    #     "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    #     "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
    #     "past_shows": [{
    #         "artist_id": 4,
    #         "artist_name": "Guns N Petals",
    #         "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    #         "start_time": "2019-05-21T21:30:00.000Z"
    #     }],
    #     "upcoming_shows": [],
    #     "past_shows_count": 1,
    #     "upcoming_shows_count": 0,
    # }
    # data2 = {
    #     "id": 2,
    #     "name": "The Dueling Pianos Bar",
    #     "genres": ["Classical", "R&B", "Hip-Hop"],
    #     "address": "335 Delancey Street",
    #     "city": "New York",
    #     "state": "NY",
    #     "phone": "914-003-1132",
    #     "website": "https://www.theduelingpianos.com",
    #     "facebook_link": "https://www.facebook.com/theduelingpianos",
    #     "seeking_talent": False,
    #     "image_link": "https://images.unsplash.com/photo-1497032205916-ac775f0649ae?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=750&q=80",
    #     "past_shows": [],
    #     "upcoming_shows": [],
    #     "past_shows_count": 0,
    #     "upcoming_shows_count": 0,
    # }
    # data3 = {
    #     "id": 3,
    #     "name": "Park Square Live Music & Coffee",
    #     "genres": ["Rock n Roll", "Jazz", "Classical", "Folk"],
    #     "address": "34 Whiskey Moore Ave",
    #     "city": "San Francisco",
    #     "state": "CA",
    #     "phone": "415-000-1234",
    #     "website": "https://www.parksquarelivemusicandcoffee.com",
    #     "facebook_link": "https://www.facebook.com/ParkSquareLiveMusicAndCoffee",
    #     "seeking_talent": False,
    #     "image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
    #     "past_shows": [{
    #         "artist_id": 5,
    #         "artist_name": "Matt Quevedo",
    #         "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
    #         "start_time": "2019-06-15T23:00:00.000Z"
    #     }],
    #     "upcoming_shows": [{
    #         "artist_id": 6,
    #         "artist_name": "The Wild Sax Band",
    #         "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    #         "start_time": "2035-04-01T20:00:00.000Z"
    #     }, {
    #         "artist_id": 6,
    #         "artist_name": "The Wild Sax Band",
    #         "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    #         "start_time": "2035-04-08T20:00:00.000Z"
    #     }, {
    #         "artist_id": 6,
    #         "artist_name": "The Wild Sax Band",
    #         "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    #         "start_time": "2035-04-15T20:00:00.000Z"
    #     }],
    #     "past_shows_count": 1,
    #     "upcoming_shows_count": 1,
    # }
    # data = list(filter(lambda d: d['id'] ==
    #             venue_id, [data1, data2, data3]))[0]
    return render_template('pages/show_venue.html', venue=data_list_dictionary)

#  Create Venue
#  ----------------------------------------------------------------


@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    # genre=request.form.getlist('genres')
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion

    # on successful db insert, flash success
    # flash('Venue ' + request.form['name'] + ' was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    form = VenueForm(request.form)
    # retrieving form data

    try:
        venue = Venue(
            name=form.name.data,
            city=form.city.data,
            state=form.state.data,
            phone=form.phone.data,
            image_link=form.image_link.data,
            genre=form.genres.data,
            facebook_link=form.facebook_link.data,
            website_link=form.website_link.data,
            seeking_talent=form.seeking_talent.data,
            seeking_description=form.seeking_description.data
        )
        db.session.add(venue)
        db.session.commit()
        flash('Venue ' + form.name.data + ' was successfully listed!')
    except:
        db.session.rollback()
        flash('An error occurred. Venue ' +
              form.name.data + ' could not be listed.')
        print(sys.exc_info())
    finally:
        db.session.close()

    return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    print(venue_id)
    try:
        Venue.query.filter_by(id=venue_id).delete()
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()
    return redirect(url_for('index'))
    # return None

#  Artists
#  ----------------------------------------------------------------


@app.route('/artists')
def artists():
    # TODO: replace with real data returned from querying the database
    artists = Artist.query.all()
    artist_dictionary = {}
    artist_list_data = []
    for res in artists:
        artist_dictionary['id'] = res.id
        artist_dictionary['name'] = res.name

        artist_list_data.append(artist_dictionary)
        artist_dictionary = {}
    # print(artist_list_data)
    # data = [{
    #     "id": 4,
    #     "name": "Guns N Petals",
    # }, {
    #     "id": 5,
    #     "name": "Matt Quevedo",
    # }, {
    #     "id": 6,
    #     "name": "The Wild Sax Band",
    # }]
    return render_template('pages/artists.html', artists=artist_list_data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    item_to_search = request.form.get('search_term', '')
    search_results = Artist.query.filter(
        Artist.name.like('%'+item_to_search+'%')).all()
    response1_dictionary = {}
    response1_data_list = []
    data_list_dictionary = {}

    coun_ter = 0
    for res in search_results:
        coun_ter += 1
        data_list_dictionary['id'] = res.id
        data_list_dictionary['name'] = res.name
        data_list_dictionary['num_upcoming_shows'] = 0

        response1_data_list.append(data_list_dictionary)
        data_list_dictionary = {}

    response1_dictionary['counter'] = coun_ter
    response1_dictionary['data'] = response1_data_list
    print(response1_dictionary)

    # response = {
    #     "count": 1,
    #     "data": [{
    #         "id": 4,
    #         "name": "Guns N Petals",
    #         "num_upcoming_shows": 0,
    #     }]
    # }
    return render_template('pages/search_artists.html', results=response1_dictionary, search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the artist page with the given artist_id
    # TODO: replace with real artist data from the artist table, using artist_id
    artist_result = Artist.query.filter(Artist.id == artist_id).first()
    artist_past_shows=db.session.query(Show).join(Artist).filter(Show.artist_id==artist_id).filter(Show.start_time<datetime.now()).all()
    # print('pastshows:::::::')
    # print(artist_past_shows)
    artist_upcoming_shows=db.session.query(Show).join(Artist).filter(Show.artist_id==artist_id).filter(Show.start_time>datetime.now()).all()
    # print('upcomingshows:::::::')
    # print(artist_upcoming_shows)
    
    data_list = []
    data_list_dictionary = {}
    past_shows_list = []
    past_shows_data_dictionary = {}
    upcoming_shows_list = []
    upcoming_shows_data_dictionary = {}
    # print(artist_result.name)

    # artist_shows = artist_result.show
    past_show_count = 0
    upcoming_show_count = 0

    for a_show in artist_upcoming_shows:
        # upcoming shows
        upcoming_show_count += 1
        upcoming_shows_data_dictionary['artist_id'] = a_show.venue.id
        upcoming_shows_data_dictionary['venue_name'] = a_show.venue.name
        upcoming_shows_data_dictionary['venue_image_link'] = a_show.venue.image_link
        upcoming_shows_data_dictionary['start_time'] = a_show.start_time.strftime(
                "%m/%d/%Y, %H:%M:%S")

        upcoming_shows_list.append(upcoming_shows_data_dictionary)
        upcoming_shows_data_dictionary = {}
            
    for a_show2 in artist_past_shows:
        # past shows
        past_show_count += 1
        print('past shows')
        past_shows_data_dictionary['venue_id'] = a_show2.venue.id
        past_shows_data_dictionary['venue_name'] = a_show2.venue.name
        past_shows_data_dictionary['venue_image_link'] = a_show2.venue.image_link
        past_shows_data_dictionary['start_time'] = a_show2.start_time.strftime(
                "%m/%d/%Y, %H:%M:%S")

        past_shows_list.append(past_shows_data_dictionary)
        past_shows_data_dictionary = {}
        
    data_list_dictionary['id'] = artist_result.id
    data_list_dictionary['name'] = artist_result.name
    data_list_dictionary['genres'] = [artist_result.genre]
    data_list_dictionary['city'] = artist_result.city
    data_list_dictionary['state'] = artist_result.state
    data_list_dictionary['phone'] = artist_result.phone
    data_list_dictionary['website'] = artist_result.website_link
    data_list_dictionary['facebook_link'] = artist_result.facebook_link
    data_list_dictionary['seeking_venue'] = artist_result.seeking_venue
    data_list_dictionary['seeking_description'] = artist_result.seeking_description
    data_list_dictionary['image_link'] = artist_result.image_link
    data_list_dictionary['past_shows'] = past_shows_list
    data_list_dictionary['upcoming_shows'] = upcoming_shows_list
    data_list_dictionary['past_shows_count'] = past_show_count
    data_list_dictionary['upcoming_shows_count'] = upcoming_show_count

    data_list.append(data_list_dictionary)
    # print('Data to show:::')
    # print(data_list)

    # data1 = {
    #     "id": 4,
    #     "name": "Guns N Petals",
    #     "genres": ["Rock n Roll"],
    #     "city": "San Francisco",
    #     "state": "CA",
    #     "phone": "326-123-5000",
    #     "website": "https://www.gunsnpetalsband.com",
    #     "facebook_link": "https://www.facebook.com/GunsNPetals",
    #     "seeking_venue": True,
    #     "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    #     "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    #     "past_shows": [{
    #         "venue_id": 1,
    #         "venue_name": "The Musical Hop",
    #         "venue_image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
    #         "start_time": "2019-05-21T21:30:00.000Z"
    #     }],
    #     "upcoming_shows": [],
    #     "past_shows_count": 1,
    #     "upcoming_shows_count": 0,
    # }
    # data2 = {
    #     "id": 5,
    #     "name": "Matt Quevedo",
    #     "genres": ["Jazz"],
    #     "city": "New York",
    #     "state": "NY",
    #     "phone": "300-400-5000",
    #     "facebook_link": "https://www.facebook.com/mattquevedo923251523",
    #     "seeking_venue": False,
    #     "image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
    #     "past_shows": [{
    #         "venue_id": 3,
    #         "venue_name": "Park Square Live Music & Coffee",
    #         "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
    #         "start_time": "2019-06-15T23:00:00.000Z"
    #     }],
    #     "upcoming_shows": [],
    #     "past_shows_count": 1,
    #     "upcoming_shows_count": 0,
    # }
    # data3 = {
    #     "id": 6,
    #     "name": "The Wild Sax Band",
    #     "genres": ["Jazz", "Classical"],
    #     "city": "San Francisco",
    #     "state": "CA",
    #     "phone": "432-325-5432",
    #     "seeking_venue": False,
    #     "image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    #     "past_shows": [],
    #     "upcoming_shows": [{
    #         "venue_id": 3,
    #         "venue_name": "Park Square Live Music & Coffee",
    #         "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
    #         "start_time": "2035-04-01T20:00:00.000Z"
    #     }, {
    #         "venue_id": 3,
    #         "venue_name": "Park Square Live Music & Coffee",
    #         "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
    #         "start_time": "2035-04-08T20:00:00.000Z"
    #     }, {
    #         "venue_id": 3,
    #         "venue_name": "Park Square Live Music & Coffee",
    #         "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
    #         "start_time": "2035-04-15T20:00:00.000Z"
    #     }],
    #     "past_shows_count": 0,
    #     "upcoming_shows_count": 3,
    # }
    # data = list(filter(lambda d: d['id'] == artist_id, [data1, data2, data3]))[0]
    return render_template('pages/show_artist.html', artist=data_list_dictionary)

#  Update
#  ----------------------------------------------------------------


@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    artist_result = Artist.query.filter(Artist.id == artist_id).first()
    artist_data = {}
    artist_data['id'] = artist_result.id
    artist_data['name'] = artist_result.name
    artist_data['genres'] = artist_result.genre
    artist_data['city'] = artist_result.city
    artist_data['state'] = artist_result.state
    artist_data['phone'] = artist_result.phone
    artist_data['website'] = artist_result.website_link
    artist_data['facebook_link'] = artist_result.facebook_link
    artist_data['seeking_venue'] = artist_result.seeking_venue
    artist_data['seeking_description'] = artist_result.seeking_description
    artist_data['image_link'] = artist_result.image_link

    # artist = {
    #     "id": 4,
    #     "name": "Guns N Petals",
    #     "genres": ["Rock n Roll"],
    #     "city": "San Francisco",
    #     "state": "CA",
    #     "phone": "326-123-5000",
    #     "website": "https://www.gunsnpetalsband.com",
    #     "facebook_link": "https://www.facebook.com/GunsNPetals",
    #     "seeking_venue": True,
    #     "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    #     "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
    # }
    # TODO: populate form with fields from artist with ID <artist_id>
    return render_template('forms/edit_artist.html', form=form, artist=artist_data)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):

    print(artist_id)
    # TODO: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes
    form = ArtistForm(request.form)
    try:
        query = db.session.query(Artist)
        queried_artist = query.filter(Artist.id == artist_id).first()

        queried_artist.name = form.name.data
        queried_artist.city = form.city.data
        queried_artist.state = form.state.data
        queried_artist.phone = form.phone.data
        queried_artist.image_link = form.image_link.data
        queried_artist.genre = form.genres.data
        queried_artist.facebook_link = form.facebook_link.data
        queried_artist.website_link = form.website_link.data
        queried_artist.seeking_venue = form.seeking_venue.data
        queried_artist.seeking_description = form.seeking_description.data

        db.session.commit()
        flash('Artist '+queried_artist.name+' edited successfully.')
    except:
        db.session.rollback()
        flash('Artist '+queried_artist.name+' failed to edit.')
        print(sys.exc_info())
    finally:
        db.session.close()

    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()

    venue_result = Venue.query.filter(Venue.id == venue_id).first()

    venue_data = {}

    venue_data['id'] = venue_result.id
    venue_data['name'] = venue_result.name
    venue_data['genres'] = venue_result.genre
    venue_data['address'] = venue_result.address
    venue_data['city'] = venue_result.city
    venue_data['state'] = venue_result.state
    venue_data['phone'] = venue_result.phone
    venue_data['website'] = venue_result.website_link
    venue_data['facebook_link'] = venue_result.facebook_link
    venue_data['seeking_talent'] = venue_result.seeking_talent
    venue_data['seeking_description'] = venue_result.seeking_description
    venue_data['image_link'] = venue_result.image_link

    # venue = {
    #     "id": 1,
    #     "name": "The Musical Hop",
    #     "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    #     "address": "1015 Folsom Street",
    #     "city": "San Francisco",
    #     "state": "CA",
    #     "phone": "123-123-1234",
    #     "website": "https://www.themusicalhop.com",
    #     "facebook_link": "https://www.facebook.com/TheMusicalHop",
    #     "seeking_talent": True,
    #     "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    #     "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
    # }
    # TODO: populate form with values from venue with ID <venue_id>
    return render_template('forms/edit_venue.html', form=form, venue=venue_data)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
    form = VenueForm(request.form)
    try:
        query = db.session.query(Venue)
        queried_venue = query.filter(Venue.id == venue_id).first()

        queried_venue.name = form.name.data
        queried_venue.city = form.city.data
        queried_venue.state = form.state.data
        queried_venue.address = form.address.data
        queried_venue.phone = form.phone.data
        queried_venue.image_link = form.image_link.data
        queried_venue.genre = form.genres.data
        queried_venue.facebook_link = form.facebook_link.data
        queried_venue.website_link = form.website_link.data
        queried_venue.seeking_talent = form.seeking_talent.data
        queried_venue.seeking_description = form.seeking_description.data

        db.session.commit()
    except:
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
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
    # TODO: insert form data as a new Artist record in the db, instead
    # TODO: modify data to be the data object returned from db insertion

    # on successful db insert, flash success
    # flash('Artist ' + request.form['name'] + ' was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
    form = ArtistForm(request.form)

    try:
        artist = Artist(
            name=form.name.data,
            city=form.city.data,
            state=form.state.data,
            phone=form.phone.data,
            image_link=form.image_link.data,
            genre=form.genres.data,
            facebook_link=form.facebook_link.data,
            website_link=form.website_link.data,
            seeking_venue=form.seeking_venue.data,
            seeking_description=form.seeking_description.data
        )
        db.session.add(artist)
        db.session.commit()
        flash('Artist ' + request.form['name'] + ' was successfully listed!')
    except:
        db.session.rollback()
        flash('An error occurred. Artist ' +
              form.name.data + ' could not be listed.')
    finally:
        db.session.close()
    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows
    # TODO: replace with real venues data.
    show_data = Show.query.join(Artist).join(Venue).all()
    show_list_data = []
    show_dictionary_data = {}

    for each_show in show_data:
        show_dictionary_data['venue_id'] = each_show.venue_id
        show_dictionary_data['venue_name'] = each_show.venue.name
        show_dictionary_data['artist_id'] = each_show.artist_id
        show_dictionary_data['artist_name'] = each_show.artist.name
        show_dictionary_data['artist_image_link'] = each_show.artist.image_link
        show_dictionary_data['start_time'] = each_show.start_time

        show_list_data.append(show_dictionary_data)
        show_dictionary_data = {}
    # print(show_list_data)

    # data = [{
    #     "venue_id": 1,
    #     "venue_name": "The Musical Hop",
    #     "artist_id": 4,
    #     "artist_name": "Guns N Petals",
    #     "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    #     "start_time": "2019-05-21T21:30:00.000Z"
    # }, {
    #     "venue_id": 3,
    #     "venue_name": "Park Square Live Music & Coffee",
    #     "artist_id": 5,
    #     "artist_name": "Matt Quevedo",
    #     "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
    #     "start_time": "2019-06-15T23:00:00.000Z"
    # }, {
    #     "venue_id": 3,
    #     "venue_name": "Park Square Live Music & Coffee",
    #     "artist_id": 6,
    #     "artist_name": "The Wild Sax Band",
    #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    #     "start_time": "2035-04-01T20:00:00.000Z"
    # }, {
    #     "venue_id": 3,
    #     "venue_name": "Park Square Live Music & Coffee",
    #     "artist_id": 6,
    #     "artist_name": "The Wild Sax Band",
    #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    #     "start_time": "2035-04-08T20:00:00.000Z"
    # }, {
    #     "venue_id": 3,
    #     "venue_name": "Park Square Live Music & Coffee",
    #     "artist_id": 6,
    #     "artist_name": "The Wild Sax Band",
    #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    #     "start_time": "2035-04-15T20:00:00.000Z"
    # }]
    return render_template('pages/shows.html', shows=show_list_data)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    # TODO: insert form data as a new Show record in the db, instead

    # on successful db insert, flash success
    # flash('Show was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Show could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    form = ShowForm(request.form)
    show = Show(
        venue_id=form.venue_id.data,
        artist_id=form.artist_id.data,
        start_time=form.start_time.data
    )
    try:
        db.session.add(show)
        db.session.commit()
        flash('Show was successfully listed!')
    except:
        db.session.rollback()
        flash('An error occurred. Show could not be listed.')
    finally:
        db.session.close()
    return render_template('pages/home.html')


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
# if __name__ == '__main__':
#     app.run()

# Or specify port manually:
# '''
# if __name__ == '__main__':
#     port = int(os.environ.get('PORT', 5000))
#     app.run(host='0.0.0.0', port=port)
# '''

if __name__ == '__main__':
    #  app.debug = True
    app.run(host="0.0.0.0")
