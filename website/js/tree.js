$(document).ready(function() {
	// Create a jQuery hook to catch any form submission attempts
	$("form").submit(function(e) {
		// Prevent the default form submission behaviour
		e.preventDefault();
		// Extract the input line from the HTML
		var input = $("input[name='syntax']").val();
		// Call the generate Tree api to extract the syntax tree
		$.get('/api/generate_tree', {input: input}, function(res) {
				// Parse the response into JavaScript
				res = JSON.parse(res);
				// Check if the response is valid
				if(res.valid) {
					// Indicate to the Frontend that the syntax tree will generate
					$("#result").text("Generated!");
					// Force the SVG container to be the size of the parent container
					$("svg").attr("width", $(".svg-container").width())
					// Empty the internal graph SVG
					$("svg g").empty();
					// Create the input graph
					var g = new dagreD3.graphlib.Graph({directed:true}).setGraph({});
					// Create a recursive function to traverse our syntax tree
					var func = function(elem, parent) {
						// Resolve the current element in our descent
						const currElem = elem[0];
						// Register the current node with the given ID and label
						g.setNode(currElem[1], {label: currElem[0]})
						// Check if the node has a parent. I.E. Node is not root
						if(parent) {
							// Set the parent and child element edge
							g.setEdge(parent, currElem[1], {});
						}
						// If the element has a left child, recursively call
						if(elem.length > 1) {func(elem[1], currElem[1])}
						// If the element has a right child, recusively call on that
						if(elem.length > 2) {func(elem[2], currElem[1])}
					}
					// Call the recursive function on the root
					func(res.tree, null);
					// Create the renderer
					var render = new dagreD3.render();
					// Set up an SVG group so that we can translate the final graph.
					var svg = d3.select("svg"),
					// Append the 'g' element to the SVG tag
					inner = svg.append("g");
					// Run the renderer. This is what draws the final graph.
					render(inner, g);
					// Center the graph
					var xCenterOffset = (svg.attr("width") - g.graph().width) / 2;
					// Perform a transformation on centering the X
					inner.attr("transform", "translate(" + xCenterOffset + ", 20)");
					// Set the height to fit the graph within a small margin
					svg.attr("height", g.graph().height + 40);
				} else {
					// If an error occurred, indicate.
					$("#result").text(res.reason);
				}
		});
	});
});
