google.load "visualization", "1",
	packages: ["corechart"]


window.myApp = angular.module 'myApp', ['ui.bootstrap', 'googlechart.directives', 'ui.router', 'ngAnimate']

window.myApp.run ['$rootScope', '$state', '$stateParams', (rootScope, state, stateParams) ->

	# add references to $state and $stateParams to the $rootScope
	rootScope.$state = state
	rootScope.$stateParams = stateParams
	]

window.myApp.config ['$httpProvider', '$stateProvider', '$urlRouterProvider',
	(httpProvider, stateProvider, urlRouterProvider) ->

		# Cross-Site request forgery protection for Django
		httpProvider.defaults.xsrfCookieName = 'csrftoken'
		httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken'

		# Routes
		urlRouterProvider.otherwise "/activities"
		urlRouterProvider.when "/reports/{id}", "reports/{id}/ever"
		urlRouterProvider.when "/activities", "activities/simple"

		stateProvider.state "activities",
			abstract: true
			url: "/activities"
			controller: 'ActivitiesCtrl'
			templateUrl: "/public/html/pages/activities.html"
		.state "activities.simple",
			url: "/simple"
			templateUrl: "/public/html/pages/activities/simple.html"
		.state "activities.advanced",
			url: "/advanced"
			templateUrl: "/public/html/pages/activities/advanced.html"
		
		.state "sync",
			url: "/sync"
			templateUrl: "/public/html/pages/sync.html"

		.state "reports",
			url: "/reports"
			templateUrl: "/public/html/pages/reports.html"
		.state "reports.detail",
			abstract: true
			url: "/{reportName}"
			template: '<div ui-view></div>'
		.state "reports.detail.ever",
			url: "/ever"
			templateUrl: "/public/html/pages/reports/ever.html"
		.state "reports.detail.byDay",
			url: "/by_day"
			templateUrl: "/public/html/pages/reports/by_day.html"
		.state "reports.detail.byMonth",
			url: "/by_month"
			templateUrl: "/public/html/pages/reports/by_month.html"
		.state "reports.detail.byYear",
			url: "/by_year"
			templateUrl: "/public/html/pages/reports/by_year.html"
		
		stateProvider.state "tags",
			abstract: true
			url: "/tags"
			controller: 'TagsCtrl'
			templateUrl: "/public/html/pages/tags.html"
		.state "tags.edit",
			url: "/edit"
			templateUrl: "/public/html/pages/tags/edit.html"
		.state "tags.experts",
			url: "/experts"
			templateUrl: "/public/html/pages/tags/experts.html"

		.state "person",
			url: "/person"
			templateUrl: "/public/html/pages/person.html"
		.state "person.details",
			url: "/details/{personId}"
			templateUrl: "/public/html/pages/person/details.html"

	]

window.myApp.factory 'Well', ['$http', (http) ->
	alerts:
		successMessage: ""
		errorMessage: ""
	people: []
	communities: []
	providers: []
	reports: {}
	]

window.myApp.factory 'Log', ['$http', (http) ->
	info: (tag, message) ->
		this.log(tag, message, 'I')

	debug: (tag, message) ->
		this.log(tag, message, 'D')

	error: (tag, message) ->
		this.log(tag, message, 'E')

	httpError: (tag, status, config) ->
		this.error(tag, status + " ERROR in " + config.method + " " + config.url)

	warning: (tag, message) ->
		this.log(tag, message, 'W')

	log: (tag, message, level) ->
		console.log level + ": [" + tag + "] " + message
		null

	]

window.myApp.factory 'App', ['$http', 'Well', 'Log', '$state', '$stateParams', '$timeout', (http, well_, log_, state_, stateParams_, $timeout) ->

	TAG = "App Service"

	stateParams: stateParams_
	state: state_
	well: well_
	log: log_

	getPeople: () ->
		if well_.people.length == 0
			http
				method: 'GET'
				url: "/people"
			.success (data, status, headers, config) ->
				well_.people = data.items
				log_.info(TAG, "list of people retrieved")
			.error (data, status, headers, config) ->
				log_.httpError(TAG, status, config)

	getCommunities: () ->
		if well_.communities.length == 0
			http
				method: 'GET'
				url: "/communities"
			.success (data, status, headers, config) ->
				well_.communities = data.items
				log_.info(TAG, "list of communities retrieved")
			.error (data, status, headers, config) ->
				log_.httpError(TAG, status, config)

	getProviders: () ->
		if well_.providers.length == 0
			http
				method: 'GET'
				url: "/providers"
			.success (data, status, headers, config) ->
				well_.providers = data.items
				log_.info(TAG, "list of providers retrieved")
			.error (data, status, headers, config) ->
				log_.httpError(TAG, status, config)

	getReports: () ->
		http
			method: 'GET'
			url: "/reports"
		.success (data, status, headers, config) ->
			well_.reports.reports = data
			log_.info(TAG, "list of reports retrieved")
		.error (data, status, headers, config) ->
			log_.httpError(TAG, status, config)

	toastSuccess: (message) ->
		well_.alerts.successMessage = message
		$timeout (-> well_.alerts.successMessage = ""), 5000
	
	toastError: (message) ->
		well_.alerts.errorMessage = message
		$timeout (-> well_.alerts.errorMessage = ""), 5000

	]