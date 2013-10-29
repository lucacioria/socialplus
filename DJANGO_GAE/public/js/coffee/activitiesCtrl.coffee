window.myApp.controller 'ActivitiesCtrl', ['$scope', '$http', 'App',  (scope, http, app) ->
	TAG = "activities"

	scope.d = {}
	scope.d.simpleSearchData = []
	scope.d.keywords = ""
	scope.d.advSearchData = []
	scope.d.well = app.well
	scope.d.tabName = 'advanced'
	scope.d.isCollapsed = false
	scope.d.adv =
		content_: {value: "", negate: false, name: "content"}
		author_: {value: undefined, negate: false, name: "author"}
		published_: {value: "", negate: false, name: "published"}
		verb_: {value: undefined, negate: false, name: "verb", options: ["post", "share"]}
		restricted_: {value: undefined, negate: false, name: "restricted", options: ["yes", "no"]}
		visibility_: {value: undefined, negate: false, name: "visibility", options: ["shared privately", "extended circles", "public", "domain", "private community", "public community", "restricted community"]}
		community_: {value: undefined, negate: false, name: "community", options: []}
		provider_: {value: undefined, negate: false, name: "provider"}

	scope.d.viewCreateReport = false
	scope.d.createReportName = "new report"

	scope.d.createReportButton =
		creating: false
	scope.d.viewReportButton =
		visible: false

	scope.$watch 'd.createReportName', (newValue, oldValue) ->
		scope.d.viewReportButton.visible = false

	scope.$watch 'd.well.communities', (newValue, oldValue) ->
		scope.d.adv.community_.options = (x.name for x in newValue)

	scope.$watch 'd.well.providers', (newValue, oldValue) ->
		scope.d.adv.provider_.options = (x.name for x in newValue)

	scope.emails = () ->
		(person.user_primaryEmail for person in app.well.people)

	getFieldValue = (field) ->
		out = ""
		if field.value and field.value != ""
			out += " NOT " if field.negate
			val = field.value
			if field.options
				val = "\"" + field.value + "\""
			out += " " + field.name + ":(" + val + ")"
		out

	scope.getSearchString = () ->
		if scope.d.tabName == 'simple'
			scope.d.keywords
		else if scope.d.tabName == 'advanced'
			(getFieldValue(value) for key, value of scope.d.adv).join('')

	scope.getActivities = () ->
		scope.d.loading = true
		http
			method: 'GET'
			url: "/activities"
			params:
				q: scope.getSearchString()
		.success (data, status, headers, config) ->
			scope.d.loading = false
			if scope.d.tabName == 'simple'
				scope.d.simpleSearchData = data
			else if scope.d.tabName == 'advanced'
				scope.d.advSearchData = data
		.error (data, status, headers, config) ->
			app.log.httpError(TAG, status, config)

	scope.getNextPage = () ->
		scope.d.loading = true
		http
			method: 'GET'
			url: "/activities"
			params:
				q: scope.getSearchString()
				nextPageCursor: scope.d.advSearchData.cursor
		.success (data, status, headers, config) ->
			scope.d.loading = false
			if scope.d.tabName == 'simple'
				scope.d.simpleSearchData = data
			else if scope.d.tabName == 'advanced'
				scope.d.advSearchData = data
		.error (data, status, headers, config) ->
			app.log.httpError(TAG, status, config)

	scope.createReport = () ->
		scope.d.createReportButton.creating = true
		http
			method: 'POST'
			url: "/reports"
			data:
				searchString: scope.getSearchString()
				name: scope.d.createReportName
		.success (data, status, headers, config) ->
			scope.d.createReportButton.creating = false
			scope.d.viewReportButton.visible = true
			scope.d.createdReportID = data.id_
		.error (data, status, headers, config) ->
			app.log.httpError(TAG, status, config)

	scope.viewPerson = (id_) ->
		app.state.go('person', {personId: id_})

		# http.get "/data/person/" + id_
		# .success (data, status, headers, config) ->
		# 	scope.d.loading = false
		# 	scope.d.person = data
		# .error (data, status, headers, config) ->
		# 	app.log.httpError(TAG, status, config)

	scope.initActivities = () ->
		app.getPeople()
		app.getCommunities()
		app.getProviders()

	]