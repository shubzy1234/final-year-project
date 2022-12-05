$(document).ready(function() {
	// Begin by calling the question endpoint to load our questions
	$.get('/api/get_questions', function(res) {
		// Parse the input into JSON readable form
		obj = JSON.parse(res);
		// Create an incrementing variable for our for loop
		var i = 0;
		// Loop over each question
		for(i = 0; i < obj.length; i++) {
			// Extract the current question from our obj list
			var question = obj[i]
			// Create a list element to hold each question answer
			var question_list = $('<ol />');
			// Create a selection element to hold each selection answer
			var select_form = $('<select />').attr('name', question.id);
			// Create an incrementing variable for our for loop
			var j = 0;
			// Loop over each possible answer
			for(j = 0; j < question.answers.length; j++) {
				// Extract the currently looked at answer
				var answer = question.answers[j];
				// Append it's text to the question list
				question_list.append($('<li />').text(answer.answer));
				// Append it's answer value / text to our selection
				select_form.append($('<option />').attr('value', answer.id).text(answer.answer));
			}
			// Create a div to store our question, and connect it's question id
			var div = $("<div />").addClass('question ' + 'q-'+question.id);
			// Append the main question to the div
			div.append($("<h5 />").text(i+1 + ': ' + question.question));
			// Append all the possible answers to the div
			div.append(question_list);
			// Append a span which states 'Select Your Answer'
			div.append($('<span />').text('Select Your Answer: '));
			// Append our selection input form
			div.append(select_form);
			// Append a hidden area which will act as the error readout in the event of a wrong question
			div.append($('<p />').addClass('error'));
			// Append a horizontal line to separate questions
			div.append($('<hr />'));
			// Append the question div to our list of questions
			$('.questions').append(div);
		}
	});

	// Create function on when form is submitted
	$("form").submit(function(e) {
		// Prevent default submission behaviour
		e.preventDefault();
		// Prepare a JSON objec to submit to server
		var to_send = {};
		// Select all select input fields on the page
		var input = $("select");
		// Create an incrementing variable for our for loop
		var i = 0;
		// Loop over each of the selection prompts
		for (i=0; i<input.length;i++) {
			// Extract the current selection
			var elem = $(input[i]);
			// Extract the current selection's answer id
			var question_answer = elem.val();
			// Extract the current selection's question id
			var question_number = elem.attr("name");
			// Place the question / answer into the reponse json
			to_send[question_number] = question_answer;
		}
		// Convert the json object into a json string
		to_send = JSON.stringify(to_send);
		// Package and send our questions/answers to the score questions api
		$.get('/api/score_questions', {input: to_send}, function(res) {
				// Automatically assume every answer is correct
				$('.error').text('Correct!');
				// Parse through the response and convert to workable javascript object
				res = JSON.parse(res);
				// Create incrementing variable for our for loop
				var i = 0;
				// Loop through each fo the error responses
				for(i = 0; i < res.length; i++) {
					// Find the question id class
					var q_id = '.q-'+res[i].q_id;
					// Extrac the reason the question was incorrect
					var reason = res[i].reason;
					// Append the reason the question was wrong to the question on the HTML
					$(q_id + ' .error').text(reason);
				}
		});
	});


});
