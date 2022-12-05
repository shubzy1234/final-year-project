$(document).ready(function() {
	// Hook into the form submission
	$("form").submit(function(e) {
		// Prevent the default submission
		e.preventDefault();
		// Extract the input expression from the HTML
		var input = $("input[name='syntax']").val();
		// Call the Syntax checking expression endpoint
		$.get('/api/syntax_checker', {input: input}, function(res) {
				// Update the HTML with the response
				$("#result").text(res);
		});
	});


});
