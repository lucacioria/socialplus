window.myApp.controller 'CirclesCtrl', ['$scope', '$http', 'App', (scope, http, app) ->
	TAG = "circles"

	scope.d = {}
	scope.d.well = app.well
	scope.d.circles = []

	scope.initAutocircles = () ->
		http
			method: 'GET'
			url: "/autocircles"
		.success (data, status, headers, config) ->
			scope.d.circles = data
			app.log.info TAG, "autocircles downloaded"
		.error (data, status, headers, config) ->
			app.log.httpError TAG, status, config

	scope.syncAutocircles = () ->
		http
			method: 'GET'
			url: "/autocircles/sync_all"
		.success (data, status, headers, config) ->
			app.log.info TAG, "autocircles synced for all users"
		.error (data, status, headers, config) ->
			app.log.httpError TAG, status, config

	scope.updateAutocircle = (autocircle) ->
		http
			method: 'POST'
			url: "/autocircle/update/" + autocircle.id_
			data: autocircle
		.success (data, status, headers, config) ->
			app.log.info TAG, "autocircle updated"
		.error (data, status, headers, config) ->
			app.log.httpError TAG, status, config

	scope.createAutocircle = () ->
		http
			method: 'GET'
			url: "/autocircle/create"
		.success (data, status, headers, config) ->
			app.log.info TAG, "new autocircle created"
		.error (data, status, headers, config) ->
			app.log.httpError TAG, status, config
	
	scope.deleteAutocircle = (autocircle) ->
		http
			method: 'GET'
			url: "/autocircle/delete/" + autocircle.id_
		.success (data, status, headers, config) ->
			scope.initAutocircles()	
			app.log.info TAG, "task deleted"
		.error (data, status, headers, config) ->
			app.log.httpError TAG, status, config

	scope.removeSearchString = (autocircle, s) ->
		index = autocircle.search_strings.indexOf(s)
		autocircle.search_strings.splice(index, 1)
	]