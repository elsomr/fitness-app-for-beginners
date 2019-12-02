@app.route('/daily_summary', methods=['GET'])
def summary_get
	#used to display daily summary
	if request.method == "GET":
			#get request results - first 
			query = client.query(kind = constants.summary)
			results_plan = list(query.fetch(workoutPlan))
			#format results to return in JSON
			summary_arr = []
			data = {}

			# get the workouts
			for entry in results_plan:
					data = {"id": entry.key.id}
					for prop in entry:
						# get the first workout from the user's list
						if prop == 1:
							data[prop] = entry[prop]

			ex_list = {}
			# get the exercises from the latest plan
			for exercise in data.setlist:
				# add exercises to list
				ex_list[exercise] = data.setlist[exercise]

			data["self"] = constants.url + "/daily_summary" + str(entry.key.id)
			summary_arr.append(data)
			summary_arr.append(ex_list)


			return(json.dumps(summary_arr), 200, {'Content-Type': 'application/json'})