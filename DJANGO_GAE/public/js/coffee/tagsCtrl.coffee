window.myApp.controller 'TagsCtrl', ['$scope', '$http', 'App', (scope, http, app) ->
	TAG = "tags"

	scope.d = {}
	scope.d.well = app.well
	scope.d.tags = []
	scope.d.experts = []

	scope.initTags = () ->
		http
			method: 'GET'
			url: "/tags"
		.success (data, status, headers, config) ->
			scope.d.tags = data
			app.log.info TAG, "tags downloaded"
		.error (data, status, headers, config) ->
			app.log.httpError TAG, status, config

	scope.getExperts = (tag) ->
		http
			method: 'GET'
			url: "/tag/experts/" + tag.id_
		.success (data, status, headers, config) ->
			scope.d.experts = data
			app.log.info TAG, "experts downloaded"
		.error (data, status, headers, config) ->
			app.log.httpError TAG, status, config

	scope.updateTag = (tag) ->
		http
			method: 'POST'
			url: "/tag/update/" + tag.id_
			data: tag
		.success (data, status, headers, config) ->
			app.log.info TAG, "task updated"
		.error (data, status, headers, config) ->
			app.log.httpError TAG, status, config

	scope.createTag = () ->
		http
			method: 'GET'
			url: "/tag/create"
		.success (data, status, headers, config) ->
			app.log.info TAG, "new tag created"
		.error (data, status, headers, config) ->
			app.log.httpError TAG, status, config
	
	scope.deleteTag = (tag) ->
		http
			method: 'GET'
			url: "/tag/delete/" + tag.id_
		.success (data, status, headers, config) ->
			scope.initTags()	
			app.log.info TAG, "task deleted"
		.error (data, status, headers, config) ->
			app.log.httpError TAG, status, config

	scope.removeSearchString = (tag, s) ->
		index = tag.search_strings.indexOf(s)
		tag.search_strings.splice(index, 1)
	]