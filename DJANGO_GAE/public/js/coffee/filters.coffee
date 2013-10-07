window.myApp.filter "formatUTC", ->
	(input) ->
		# parse datetime 2013-08-26T14:01:02Z
		if input and input != ""
			moment(input, "YYYY-MM-DDThh:mm:ssZ").fromNow()
		else
			""

window.myApp.filter "formatUTCLong", ->
	(input) ->
		# parse datetime 2013-08-26T14:01:02Z
		if input and input != ""
			moment(input, "YYYY-MM-DDThh:mm:ssZ").format('MMMM Do YYYY, hh:mm:ss')
		else
			""

window.myApp.filter "trim", ->
	(input) ->
		if input and input != ""
			input.trim()