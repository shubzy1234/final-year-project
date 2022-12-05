$(document).ready(function() {
	// Create a hook on the form submission
	$("form").submit(function(e) {
		// Prevent the default form submission
		e.preventDefault();
		// Get the input text from the HTML
		var input = $("input[name='syntax']").val();
		// Call the to truth table generator with our desired string
		$.get('/api/truthtable_generator', {input: input}, function(res) {
				// Parse out the response into JSON
				res = JSON.parse(res);
				// Verify that the response is valid
				if(res.valid) {
					// Indicate to the frontend that the value is generated
					$("#result").text("Generated!");
					// Extract the actual truth table
					var truth_table = res.table.truth_table;
					// Extract the variables / result name
					var truth_variables = res.table.variables;
					// Empty out the head of the table
					$("table thead tr").empty();
					// Empty out the body of the HTML table
					$("table tbody").empty();
					// Create an incrememnting variable
					var i = 0;
					// Loop through each variable in the truth table
					for(i = 0; i < truth_variables.length; i++) {
						// Append the variable name to the head of the table
						$("table thead tr").append($("<th />").addClass("text-center").text(truth_variables[i]));
					}

					// Create the outer loop incrementing variable
					var i = 0;
					// Create the inner loop incrementing variable
					var j = 0;
					// Loop through each row of the truth table
					for(i = 0; i < truth_table.length; i++) {
						// Create a table row
						var row = $("<tr />");
						// Loop through each column of the row
						for(j = 0; j < truth_table[i].length; j++) {
							// Append a T or F to correspond to the truth value of this particular column
							row.append($("<td />").text(truth_table[i][j] ? "T" : "F"));
						}
						// Append the row to the body of the truth table
						row.appendTo($("table tbody"))
					}
				} else {
					// If an error, indicate the resaon for failure.
					$("#result").text(res.reason);
				}
		});
	});




});
