# Docs on session basics
# https://docs.sqlalchemy.org/en/13/orm/session_basics.html

import numpy as np
import os
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, inspect, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
#engine = create_engine("sqlite:///titanic.sqlite")
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
# reflect an existing database into a new model
Base = automap_base()
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start_date<br/>"
        f"/api/v1.0/start_date/end_date<br/>"
    )


@app.route("/api/v1.0/<start_date>/<end_date>")
def date_search(start_date, end_date):
    """Return the list of dates and  temp observation"""
    # Query 
    print(start_date)
    print(end_date)
    session = Session(engine)
#    results = session.query(Measurement).all()
    results = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).group_by(Measurement.date).all()
    # close the session to end the communication with the database
    session.close()

    # Convert list of tuples into normal list
    #all_names = list(np.ravel(results))
    all_tops = []
    for tops in results:
        
        tops_dict = {}
        tops_dict["DATE"] = tops[0]
        tops_dict["TMIN"] = tops[1]
        tops_dict["TAVG"] = tops[2]
        tops_dict["TMAX"] = tops[3]
     
        all_tops.append(tops_dict)

    return jsonify(all_tops)
  

@app.route("/api/v1.0/<start_date>")
def date_search_start(start_date):
    """Return the list of dates and temp observation """
    # Query 
    print(start_date)
    session = Session(engine)
#    results = session.query(Measurement).all()
    results = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).group_by(Measurement.date).all()
    # close the session to end the communication with the database
    session.close()

    # Convert list of tuples into normal list
    #all_names = list(np.ravel(results))
    all_tops = []
    for tops in results:
        
        tops_dict = {}
        tops_dict["DATE"] = tops[0]
        tops_dict["TMIN"] = tops[1]
        tops_dict["TAVG"] = tops[2]
        tops_dict["TMAX"] = tops[3]
     
        all_tops.append(tops_dict)

    return jsonify(all_tops)
  




@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return the list of dates and precepitaiton"""
    # Query 
    session = Session(engine)
#    results = session.query(Measurement).all()
    results = session.query(Measurement.date, func.avg(Measurement.prcp))\
        .group_by(Measurement.date)\
        .all()
    # close the session to end the communication with the database
    session.close()

    # Convert list of tuples into normal list
    #all_names = list(np.ravel(results))
    all_precipitation = []
    for precipitation in results:
        precipitation_dict = {}
        precipitation_dict["date"] = precipitation[0]
        precipitation_dict["precipitaion"] = precipitation[1]
#        precipitation_dict["station"] = precipitation.station
     
        all_precipitation.append(precipitation_dict)

    return jsonify(all_precipitation)
  


@app.route("/api/v1.0/stations")
def stations():
    """Return a list of stations data including the stations, name, latitued, longitude,amd elvation"""

    # Open a communication session with the database
    session = Session(engine)

    # Query all passengers
    results = session.query(Station).all()

    # close the session to end the communication with the database
    session.close()

    # Convert list of tuples into normal list
    # all_names = list(np.ravel(results))

    # return jsonify(all_names)

    # Create a dictionary from the row data and append to a list of all_stations
    all_stations = []
    for stations in results:
        stations_dict = {}
        stations_dict["station"] = stations.station
        stations_dict["name"] = stations.name
        stations_dict["latitude"] = stations.latitude
        stations_dict["longitude"] = stations.longitude
        stations_dict["elevation"] = stations.elevation
        all_stations.append(stations_dict)

    return jsonify(all_stations)


@app.route("/api/v1.0/tobs")
def tobs_data():
    """Return a list of  temp observation"""

    # Open a communication session with the database
    session = Session(engine)

    # Query all passengers
    results = session.query(Station).all()

    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    print(last_date)
    #last month date
    last_date_dt = dt.datetime.strptime(last_date[0], '%Y-%m-%d')
    last_twelve_month_date = last_date_dt - dt.timedelta(days=365)
    print(last_twelve_month_date)

    tobs_scores = session.query(Measurement.date, func.avg(Measurement.tobs))\
        .filter(Measurement.date >= last_twelve_month_date)\
        .group_by(Measurement.date)\
        .all()
    # close the session to end the communication with the database
    session.close()

    # # Convert list of tuples into normal list
    # all_names = list(np.ravel(tobs_scores))

    # return jsonify(all_names)

    # # Create a dictionary from the row data and append to a list of all_tobs
    all_tobs = []
    for tobs in tobs_scores:
        # print(tobs)
        tobs_dict = {}
        tobs_dict["date"] = tobs[0]
        tobs_dict["tobs"] = tobs[1]
        # tobs_dict["longitude"] = tobs.longitude
        all_tobs.append(tobs_dict)

    return jsonify(all_tobs)


if __name__ == '__main__':
    app.run(debug=True)
