import datetime
from flask import Flask, request, make_response, render_template, redirect, jsonify
import constants
import json
from google.cloud import datastore
from requests_oauthlib import OAuth2Session
from google.oauth2 import id_token
from google.auth import crypt, jwt
from google.auth.transport import requests

# This disables the requirement to use HTTPS so that you can test locally.
import os 
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

#code to set up basic vars to use Flask
app = Flask(__name__)
app.config.from_object(__name__)

#setting up datastore client
client = datastore.Client()


#used only for testing purposes!!!!! deletes entries in datastore
# @app.route('/cleardatastore')
# def clear_datastore():

	# query = client.query(kind=constants.boats)
	# results = list(query.fetch())
	
	# for boat in results:
		# boat_key = client.key(constants.boats, int(boat.key.id))
		# boat = client.delete(key=boat_key)
	
	# errorMsg = {"Finished": "Datastore data is cleared"}
	# return (json.dumps(errorMsg), 200)

#renders welcome page on index.html
@app.route('/')
def index():
	return render_template("index.html")

	
@app.route('/exercises', methods=['POST', 'GET'])
def exercises_get_post():
	#used to add a exercise
	if request.method == "POST":		
		#get request 
		req = requests.Request()
		
		#check that the request has some content in it
		try:
			content = request.get_json() 
		except ValueError:
			#404 error json
			error = {}
			error={"Error": "Bad Request"}
			return (json.dumps(error), 400)
		
		#check the request content has all required properties
		if len(content) !=4  or content["name"] == None or content["description"] == None or \
		content["calorieBurnFactor"]== None or content["videoURL"] == None:
			#404 error json
			errorMsg= {"Error": "The request object is missing at least one of the required attributes or has too many attributes"}
			return (json.dumps(errorMsg), 400)
	
		#store newly created wokrout in datastore
		newExercise = datastore.entity.Entity(key=client.key(constants.exercises))
		newExercise.update({"name": content["name"], "description": content["description"],\
		"calorieBurnFactor": content["calorieBurnFactor"], "videoURL": content["videoURL"] })
		client.put(newExercise)
		
		#format the return JSON message, adding the id and self attribute in the return message
		result = {}
		result={'id': str(newExercise.key.id)}
		for prop in newExercise:
			#no need to iterate through loads since it will be set to None 
			result[prop] = newExercise[prop]
		result["self"] = str(constants.url + "/exercises/" + str(newExercise.key.id))

		return (json.dumps(result), 201, {'Content-Type': 'application/json'})
	
	#to get all exercises
	elif request.method == "GET":
		#fetch all exercises
		query = client.query(kind=constants.exercises)
		results = list(query.fetch())
		#foratting results to return in JSON after successful fetch
		exercise_arr = []
		data = {}
		for entry in results:
			data={"id": entry.key.id}
			for prop in entry:
				data[prop] = entry[prop]
			data["self"]= constants.url + "/exercises/" + str(entry.key.id)
			exercise_arr.append(data)
		
		#returns JSON of all exercises 
		return (json.dumps(exercise_arr), 200, {'Content-Type': 'application/json'})

@app.route('/sets', methods=['POST', 'GET'])
def sets_get_post():
	#used to add a set
	if request.method == "POST":		
		#get request 
		req = requests.Request()
		
		#check that the request has some content in it
		try:
			content = request.get_json() 
		except ValueError:
			#404 error json
			error = {}
			error={"Error": "Bad Request"}
			return (json.dumps(error), 400)
		
		#check the request content has all required properties
		if len(content) !=3  or content["exercise"] == None or content["reps"] == None or \
		content["resistenceWeight"]== None:
			#404 error json
			errorMsg= {"Error": "The request object is missing at least one of the required attributes or has too many attributes"}
			return (json.dumps(errorMsg), 400)
	
		#store newly created wokrout in datastore
		newSet= datastore.entity.Entity(key=client.key(constants.sets))
		newSet.update({"exercise": content["exercise"], "reps": content["reps"],\
		"resistenceWeight": content["resistenceWeight"] })
		client.put(newSet)
		
		#format the return JSON message, adding the id and self attribute in the return message
		result = {}
		result={'id': str(newSet.key.id)}
		for prop in newSet: 
			result[prop] = newSet[prop]
		result["self"] = str(constants.url + "/sets/" + str(newSet.key.id))

		return (json.dumps(result), 201, {'Content-Type': 'application/json'})
	
	#to get all sets
	elif request.method == "GET":
		#fetch all sets
		query = client.query(kind=constants.sets)
		results = list(query.fetch())
		#foratting results to return in JSON after successful fetch
		set_arr = []
		data = {}
		for entry in results:
			data={"id": entry.key.id}
			for prop in entry:
				data[prop] = entry[prop]
			data["self"]= constants.url + "/sets/" + str(entry.key.id)
			set_arr.append(data)
		
		#returns JSON of all sets 
		return (json.dumps(set_arr), 200, {'Content-Type': 'application/json'})
		
		
@app.route('/workouts', methods=['POST', 'GET'])
def workouts_get_post():
	#used to add a workout
	if request.method == "POST":		
		#get request 
		req = requests.Request()
		
		#check that the request has some content in it
		try:
			content = request.get_json() 
		except ValueError:
			#404 error json
			error = {}
			error={"Error": "Bad Request"}
			return (json.dumps(error), 400)
		
		#check the request content has all required properties
		if len(content) !=2  or content["setList"] == None or content["name"] == None :
			#404 error json
			errorMsg= {"Error": "The request object is missing at least one of the required attributes or has too many attributes"}
			return (json.dumps(errorMsg), 400)
	
		#store newly created workout in datastore
		newWorkout= datastore.entity.Entity(key=client.key(constants.workouts))
		newWorkout.update({"name": content["name"], "setList": content["setList"] })
		client.put(newWorkout)
		
		#format the return JSON message, adding the id and self attribute in the return message
		result = {}
		result={'id': str(newWorkout.key.id)}
		for prop in newWorkout:
			result[prop] = newWorkout[prop]
		result["self"] = str(constants.url + "/workouts/" + str(newWorkout.key.id))

		return (json.dumps(result), 201, {'Content-Type': 'application/json'})
	
	#to get all workouts
	elif request.method == "GET":
		#fetch all workouts
		query = client.query(kind=constants.workouts)
		results = list(query.fetch())
		#foratting results to return in JSON after successful fetch
		workout_arr = []
		data = {}
		for entry in results:
			data={"id": entry.key.id}
			for prop in entry:
				data[prop] = entry[prop]
			data["self"]= constants.url + "/workouts/" + str(entry.key.id)
			workout_arr.append(data)
		
		#returns JSON of all workouts 
		return (json.dumps(workout_arr), 200, {'Content-Type': 'application/json'})
		
		
@app.route('/users', methods=['POST', 'GET'])
def users_get_post():
	#used to add a user
	if request.method == "POST":		
		#get request 
		req = requests.Request()
		
		#check that the request has some content in it
		try:
			content = request.get_json() 
		except ValueError:
			#404 error json
			error = {}
			error={"Error": "Bad Request"}
			return (json.dumps(error), 400)
		
		#check the request content has all required properties
		if len(content) !=3  or content["userName"] == None or content["password"] == None or \
		content["email"]== None:
			#404 error json
			errorMsg= {"Error": "The request object is missing at least one of the required attributes or has too many attributes"}
			return (json.dumps(errorMsg), 400)
	
		#store newly created user in datastore
		newUser = datastore.entity.Entity(key=client.key(constants.users))
		newUser.update({"userName": content["userName"], "password": content["password"],\
		"email": content["email"] })
		client.put(newUser)
		
		#format the return JSON message, adding the id and self attribute in the return message
		result = {}
		result={'id': str(newUser.key.id)}
		for prop in newUser:
			result[prop] = newUser[prop]
		result["self"] = str(constants.url + "/users/" + str(newUser.key.id))

		return (json.dumps(result), 201, {'Content-Type': 'application/json'})
	
	#to get all users
	elif request.method == "GET":
		#fetch all users
		query = client.query(kind=constants.users)
		results = list(query.fetch())
		#foratting results to return in JSON after successful fetch
		user_arr = []
		data = {}
		for entry in results:
			data={"id": entry.key.id}
			for prop in entry:
				data[prop] = entry[prop]
			data["self"]= constants.url + "/exercises/" + str(entry.key.id)
			user_arr.append(data)
		
		#returns JSON of all exercises 
		return (json.dumps(user_arr), 200, {'Content-Type': 'application/json'})
		
		
		
#get or delete an individual exercise, just an example code to look at when needed. 
#will need to use PATCH here to add the users workoutPlan later on. 	
@app.route('/exercises/<id>', methods=['GET', 'DELETE'])
def get_delete_exercise(id):
	if request.method == "GET":
		exercise_key= client.key(constants.exercises, int(id))
		exercise = client.get(key=exercise_key)

		if exercise == None:
			errorMsg = {}
			errorMsg["Error"]= "No exercise with this exercise_id exists"
			return (json.dumps(errorMsg), 404)
		else:
			data = {}
			data={'id': str(id)}
			for prop in exercise:
				data[prop] = exercise[prop]
			data["self"]= constants.url + "/exercises/" + str(id)
			return (json.dumps(data), 200)
			
	elif request.method == "DELETE":
		exercise_key= client.key(constants.exercises, int(id))
		exercise = client.get(key=exercise_key)
		if exercise == None:
			error = {}
			error={"Error": "No exercise with this exercise_id exists"}
			return (json.dumps(error), 404)
			
		exercise = client.delete(key=exercise_key)		
		return ('', 204)

if __name__ == '__main__':
	app.run(host='127.0.0.1', port=8080, debug=True)