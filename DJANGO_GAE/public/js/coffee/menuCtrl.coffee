window.myApp.controller 'MenuCtrl', ['$scope', '$http', 'App', (scope, http, app) ->
	TAG = "menu"
	scope.well = app.well

	scope.initCookie = () ->
		URL = "/get_cookie"
		http.get(URL)
		.success (data, status, headers, config) ->
			app.log.info(TAG, "csrf cookie set via GET request")
		.error (data, status, headers, config) ->
			app.log.httpError(TAG, URL)
	]