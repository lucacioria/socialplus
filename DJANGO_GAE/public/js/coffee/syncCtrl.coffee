window.myApp.controller 'SyncCtrl', ['$scope', '$http', 'App', (scope, http, app) ->
	TAG = "sync"

	scope.d = {}
	scope.d.well = app.well
	scope.d.runningTasks = []
	scope.d.currentReport = null
	scope.d.orgUnit = ""

	scope.initTaskRefresh = () ->
		scope.getRunningTasks()
		app.getReports()

	scope.getRunningTasks = () ->
		if not app.state.includes('sync')
			console.log "skip"
			return
		http
			method: 'GET'
			url: "/tasks"
		.success (data, status, headers, config) ->
			scope.d.runningTasks = data.items
			app.log.info TAG, "task refreshed"
		.error (data, status, headers, config) ->
			app.log.httpError TAG, status, config

	scope.deleteAll = (what) ->
		http
			method: 'GET'
			url: "/delete_all/" + what
		.success (data, status, headers, config) ->
			app.log.info TAG, data
			app.toastSuccess data
		.error (data, status, headers, config) ->
			app.log.httpError TAG, status, config

	scope.clearCompleted = () ->
		http
			method: 'DELETE'
			url: "/tasks/completed"
		.success (data, status, headers, config) ->
			app.log.info TAG, "completed tasks deleted"	
		.error (data, status, headers, config) ->
			app.log.httpError TAG, status, config

	scope.resetDomain = () ->
		http
			method: 'GET'
			url: "/reset_domain"
		.success (data, status, headers, config) ->
			app.log.info TAG, data
			app.toastSuccess data
		.error (data, status, headers, config) ->
			app.log.httpError TAG, status, config

	scope.startSyncTask = (taskName, options = {}) ->
		# for n in [0..2]
			http
				method: 'POST'
				url: "/tasks"
				data:
					name: taskName
					options: options
			.success (data, status, headers, config) ->
				app.log.info "task started"	
				scope.getRunningTasks()
			.error (data, status, headers, config) ->
				app.log.httpError TAG, status, config
	]