import datetime
from flask import Flask, request, make_response, render_template, redirect, jsonify, url_for, flash
import constants
import json
import random
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

#gets all data for a workout
def getData(id):

	#fetch workout information
	workout_key= client.key(constants.workouts, int(id))
	workout = client.get(key=workout_key)
	if workout == None:
		errorMsg = {}
		errorMsg["Error"]= "No workout with this workout_id exists"
		return (json.dumps(errorMsg), 404)
	else:
		data = {}
		data={'id': str(id)}

		for prop in workout:
			if prop != 'setList':
				data[prop] = workout[prop]
		data["self"]= constants.url + "/workouts/" + str(id)
		
	#get set list exercises and valies
	setList = workout['setList'].split()
	for setID in setList:
		data['setList'] = {}
		data['setList'][setID] = {}
		#get exercise, rep, and weight
		set_key= client.key(constants.sets, int(setID))
		set = client.get(key=set_key)
		# #get exercise name
		# exercise_key=client.key(constants.exercises, int(set['exercise']))
		# exercise = client.get(key=exercise_key)
		# set['exercise'] = exercise['name']
		
		#format data to display
		set_data = {'exercise': set['exercise'], 'rep': set['reps'], 'resistenceWeight': set['resistenceWeight']}
		data['setList'][setID] = set_data
	return data

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
		if len(content) !=4  or content["userName"] == None or content["password"] == None or \
		content["email"]== None or content['workoutPlan'] == None:
			#404 error json
			errorMsg= {"Error": "The request object is missing at least one of the required attributes or has too many attributes"}
			return (json.dumps(errorMsg), 400)
	
		#store newly created user in datastore
		newUser = datastore.entity.Entity(key=client.key(constants.users))
		newUser.update({"userName": content["userName"], "password": content["password"],\
		"email": content["email"], "workoutPlan": content["workoutPlan"] })
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


@app.route('/dailySummary', methods=['GET', 'POST'])
def summary_wo_id():
	#404 error json
	errorMsg= {"Error": "The user id is missing, please add a valid id (5638186843766784) to the end of the url."}
	return (json.dumps(errorMsg), 400)

	
@app.route('/dailySummary/<id>', methods=['GET'])
def view_summary(id):
	count = 0
	user_key= client.key(constants.users, int(id))
	user = client.get(key=user_key)

	workoutList = user['workoutPlan']
	workoutList = workoutList.split()
	for w in workoutList:
		w.replace(',', '')
	
	dailyWorkout = workoutList[0].replace(',', '')
	workout_key= client.key(constants.workouts, int(dailyWorkout))
	workout = client.get(key=workout_key)	
	
	setList = workout['setList'].split()
	setArr = []
	for setID in setList:
		count += 1
		setID = setID.replace(',', '')
		data = {}
		set_key= client.key(constants.sets, int(setID))
		set = client.get(key=set_key)
		
		data['id'] = set.key.id
		data['num'] = count
		data['exercise'] = set['exercise']
		for prop in set:
			data[prop] = set[prop]
		setArr.append(data)
	
	
	
	calorieCount = random.randint(0,50000)
	stepCount = random.randint(0,40000)
	
	return render_template('dailySummary.html', workout = setArr, calorieCount = calorieCount, stepCount = stepCount)
	

@app.route('/editWorkout', methods=['GET', 'POST'])
def edit_workout_wo_id():
	#404 error json
	errorMsg= {"Error": "The workout id is missing, please add 5633226290757632 to the end of the url."}
	return (json.dumps(errorMsg), 400)
	
@app.route('/editWorkout/<id>', methods=['GET', 'POST'])
def edit_workout(id):

	if request.method == "POST":
		try :
			if request.form['setID']:
				setID = request.form['setID']
				workout_key= client.key(constants.workouts, int(id))
				workout = client.get(key=workout_key)	
				

				setList = workout['setList'].split()
				if str(setID) in setList:
					setList.remove(str(setID))
				
				workout['setList'] = ' '.join(setList)
				# workout['setList'].replace(setID, '')
				client.put(workout)
		except:
				
				#check the form content has all required properties
				if request.form.get("exercise") == None or request.form["reps"] == None or \
				request.form["resistenceWeight"]== None:
					#404 error json
					errorMsg= {"Error": "The request object is missing at least one of the required attributes or has too many attributes"}
					return (json.dumps(errorMsg), 400)
			
				#store newly created wokrout in datastore
				newSet= datastore.entity.Entity(key=client.key(constants.sets))
				newSet.update({"exercise": request.form["exercise"], "reps": request.form["reps"],\
				"resistenceWeight": request.form["resistenceWeight"] })
				client.put(newSet)
				
				#format the return JSON message, adding the id and self attribute in the return message
				result = {}
				result={'id': str(newSet.key.id)}
				for prop in newSet: 
					result[prop] = newSet[prop]
				result["self"] = str(constants.url + "/sets/" + str(newSet.key.id))
				
				newSetID = newSet.key.id
				workout_key= client.key(constants.workouts, int(id))
				workout = client.get(key=workout_key)
				workout['setList'] += ' '
				workout['setList'] += str(newSetID)
				client.put(workout)




	workout_key= client.key(constants.workouts, int(id))
	workout = client.get(key=workout_key)	
	
	setList = workout['setList'].split()
	setArr = []
	for setID in setList:
		setID = setID.replace(',', '')
		data = {}
		set_key= client.key(constants.sets, int(setID))
		set = client.get(key=set_key)
		
		data['id'] = set.key.id
		for prop in set:
			data[prop] = set[prop]
		setArr.append(data)
	
	
	query = client.query(kind=constants.exercises)
	results = list(query.fetch())
	#render html using data
	return render_template('updateWorkout.html', exercises=results, data=setArr, id=id)
	
	
		




if __name__ == '__main__':
	app.run(host='127.0.0.1', port=8080, debug=True)