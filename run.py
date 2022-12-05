# Import syntax checker to use in endponits
import logic_syntax_checker as syntaxChecker
# Import flask module
from flask import Flask
# Import request to use query string from get requests
from flask import request
# Import json to load/dump responses
import json
# Import os for path module
import os
# Import random for array shuffling
import random

# Create base flask application. Set static server to our website folder
app = Flask(__name__, static_url_path= '/', static_folder='./website')

# Manually set the root to be the index file
@app.route('/')
def root():
	# Send a static index.html
	return app.send_static_file('index.html')

# Create endpoint for checking Syntax of an expression
@app.route("/api/syntax_checker", methods = ['GET'])
def checker(pass_through = None):
	# Check if an expression is explicitely passed in
	if pass_through:
		# Set the input
		input = pass_through
	else:
		# Set the input from the GET query string
		input = request.args.get('input')
	# Test to see if input exists
	if input:
		try:
			# Try to displayResult on syntax Checker
			result = syntaxChecker.displayResult(input)
			# If Exception wasn't thrown, return that the syntax is valid
			return "Syntax is valid, great work!"
		except Exception as e:
			# Return the reason the syntax was invalid
			return 'Syntax Invalid. Reason: ' + str(e)
	else:
		# Return indication that input wasn't provided
		return "Input was not provided"

# Create endpoint for getting questions from questions.json file
@app.route("/api/get_questions", methods = ['GET'])
def getQuestions(preserve_answers = False, return_as_dict = False):
	# Check to see if the JSON file questions.json exists
	if(not os.path.isfile('questions.json')):
		# If not, return failure
		print("Questions Not Found")
		# Return no questions
		return []
	# Open the JSON file
	file = open('questions.json')
	# Use the JSON load instruction to extract the file's contents
	questions = json.load(file)
	# Enumerate over each question
	for q_num, q in enumerate(questions):
		# Set the ID of a particular question to it's ordered place in the array
		q['id'] = q_num
		# Iterate through each answer
		for a_num, a in enumerate(q['answers']):
			# If the user doesn't wish to preserve output answers`
			if(not preserve_answers):
				# Delete whether the answer is correct
				del a['correct']
				# Delete why the answer is incorrect
				del a['reason']
			# Set an id for that answer
			a['id'] = a_num
	# If the user wishes to return a Python Dictionary
	if(return_as_dict):
		# Return the dictionary
		return questions
	#If the user wishes to return a JSON string
	else:
		# Iterate through each of the questions
		for q in questions:
			# Shuffle each of the answers
			random.shuffle(q['answers'])
		# Shuffle each of the questions
		random.shuffle(questions)
		# Return the shuffled question/answers as JSON
		return json.dumps(questions)

# Create endpoint for scoring questions
@app.route("/api/score_questions", methods=['GET'])
def scoreQuestions():
	# Get the list of preserved-answer questions from questions.json
	questions = getQuestions(preserve_answers=True, return_as_dict=True)
	# Extract the user's answers
	user_answers = json.loads(request.args.get('input'))
	# Keep track of the # of questions reads
	question_count = 0
	# Keep track of the # of questions correct
	correct_count = 0
	# Keep a list of error codes to return to the frontend
	error_codes = []
	# Iterate through each of the user's answers
	for question_id in user_answers:
		# Extract the question id from the user's answer
		q_id = int(question_id)
		# Extract the answer id from the user's answer
		a_id = int(user_answers[question_id])
		# Increment the number of questions seen by 1
		question_count += 1
		# Get the true answer
		selected = questions[q_id]['answers'][a_id]
		# Determine if the answer supplied was correct
		if(selected['correct']):
			# Add 1 to the correct answer count
			correct_count += 1
		else:
			# Append to return the reason the answer was incorrect
			error_codes.append({'q_id': str(q_id), 'reason': selected['reason']})
	# Return the error codes to the user
	return json.dumps(error_codes)

# Create endpoint for the truth table generator
@app.route("/api/truthtable_generator", methods = ['GET'])
def truthtable_generator():
	# Extract the desired expression
	input = request.args.get('input')
	# Verify if all syntax is correct
	if input and checker(pass_through = input) == "Syntax is valid, great work!":
		# Call and return from the get_truth_table function
		return json.dumps({'valid': True, 'table': syntaxChecker.get_truth_table(input)})
	else:
		# Invalid / not provided input is returned with error
		return json.dumps({'valid': False, 'reason': "Input was not provided or invalid"})

# Create endpoint for the tree generator
@app.route("/api/generate_tree", methods = ['GET'])
def tree_generator():
	# Extract the input from the frontend
	input = request.args.get('input')
	# Verify if all syntax is correct
	if input and checker(pass_through = input) == "Syntax is valid, great work!":
		# Call and return from the get_tree function
		return json.dumps({'valid': True, 'tree': syntaxChecker.get_tree(input)})
	else:
		# Invalid / not provided input is returned with error
		return json.dumps({'valid': False, 'reason': "Input was not provided or invalid"})

# Hook to check if the program is being run from the CLI / executable
if __name__ == "__main__":
	# Call the run function to listen on localhost:9999
	app.run(host='0.0.0.0', port=9999, debug=True)
