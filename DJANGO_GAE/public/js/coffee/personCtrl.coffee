window.myApp.controller 'PersonCtrl', ['$scope', '$http', 'App',  (scope, http, app) ->
	TAG = "person"

	scope.d = {}
	scope.d.well = app.well
	scope.d.currentPerson = null
	scope.d.personData = null
	
	scope.$watch 'd.currentPerson', (newValue, oldValue) ->
		app.state.go('person.detail', {personId: newValue.id_}) if newValue
		getPerson()

	scope.initPerson = () ->
		app.getPeople()

	getPerson = (personId) ->
		personId = scope.d.currentPerson.id_ if scope.d.currentPerson
		return if not personId
		app.log.info(TAG, "getting person " + personId)
		http
			method: 'GET'
			url: "/people/"+personId
		.success (data, status, headers, config) ->
			scope.d.personData = data
			app.log.info TAG, "person " + data.displayName + " downloaded"
		.error (data, status, headers, config) ->
			app.log.httpError TAG, status, config

	# initialize person if coming directly from details url 
	if app.stateParams.personId != undefined
		getPerson(app.stateParams.personId)

	]