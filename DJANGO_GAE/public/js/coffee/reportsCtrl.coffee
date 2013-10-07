window.myApp.controller 'ReportsCtrl', ['$scope', '$http', 'App',  (scope, http, app) ->
	TAG = "reports"

	scope.d = {}
	scope.d.well = app.well
	scope.d.currentReport = null
	scope.d.reportData = null
	scope.d.popularActivities =
		ever: []
		byDay: []
		byMonth: []
		byYear: []
	
	scope.$watch 'd.currentReport', (newValue, oldValue) ->
		app.state.go('reports.detail.ever', {reportName: newValue.id}) if newValue
		getReport()

	scope.$watch 'd.well.reports.reports.items', (newValue, oldValue) ->
		return if not scope.d.reportData
		for r in newValue
			if r.id == scope.d.reportData.id				
				scope.d.currentReport = r

	scope.deleteCurrentReport = () ->
		scope.d.loading = true
		return if not scope.d.currentReport
		http
			method: 'GET'
			url: "/report/delete/" + scope.d.currentReport.id
		.success (data, status, headers, config) ->
			scope.d.currentReport = null
			scope.d.reportData = null
			cleanCharts()
			scope.d.loading = false
			app.getReports()
		.error (data, status, headers, config) ->
			app.log.httpError(TAG, status, config)

	scope.initReports = () ->
		app.getReports()

	getReport = (reportId) ->
		reportId = scope.d.currentReport.id if scope.d.currentReport
		return if not reportId
		app.log.info(TAG, "getting report " + reportId)
		http
			method: 'GET'
			url: "/reports/"+reportId
		.success (data, status, headers, config) ->
			scope.d.reportData = data
			populateCharts()
			app.log.info TAG, "report " + data.name + " downloaded"
		.error (data, status, headers, config) ->
			app.log.httpError TAG, status, config

	cleanCharts = () ->
		scope.d.chartActivePeopleEver.data.rows = []
		scope.d.chartRestrictedVsPublicByDay.data.rows = []
		scope.d.chartRestrictedVsPublicByMonth.data.rows = []
		scope.d.chartRestrictedVsPublicByYear.data.rows = []
		scope.d.chartRestrictedVsPublicEver.data.rows = []
		scope.d.popularActivities.ever = []

	populateCharts = () ->
		cleanCharts()
		scope.d.chartRestrictedVsPublicEver.data.rows = [
			{c: [{v: "Public"},{v: scope.d.reportData.dataEver.restrictedVsPublic.public}]},
			{c: [{v: "Restricted"}, {v: scope.d.reportData.dataEver.restrictedVsPublic.restricted}]}
		]

		for activePerson in scope.d.reportData.dataEver.activePeople
			scope.d.chartActivePeopleEver.data.rows.push {c: [{v: activePerson.person.displayName}, {v: activePerson.total}]}
		scope.d.popularActivities.ever = (x.activity for x in scope.d.reportData.dataEver.popularActivities)

		for day in scope.d.reportData.dataByDay
			scope.d.chartRestrictedVsPublicByDay.data.rows.push {c: [{v: day.interval}, {v: day.restrictedVsPublic.restricted}, {v: day.restrictedVsPublic.public}]}

		for month in scope.d.reportData.dataByMonth
			scope.d.chartRestrictedVsPublicByMonth.data.rows.push {c: [{v: month.interval.substring(0,7)}, {v: month.restrictedVsPublic.restricted}, {v: month.restrictedVsPublic.public}]}

		for year in scope.d.reportData.dataByYear
			scope.d.chartRestrictedVsPublicByYear.data.rows.push {c: [{v: year.interval.substring(0,4)}, {v: year.restrictedVsPublic.restricted}, {v: year.restrictedVsPublic.public}]}

	scope.onActivePersonSelected = (selection) ->
		console.log scope.d.reportData.dataEver.activePeople[selection[0].row].person.displayName

	scope.onDaySelected = (selection) ->
		scope.d.chartActivePeopleByDay.data.rows = []
		for activePerson in scope.d.reportData.dataByDay[selection[0].row].activePeople
			scope.d.chartActivePeopleByDay.data.rows.push {c: [{v: activePerson.person.displayName}, {v: activePerson.total}]}
		scope.d.popularActivities.byDay = (x.activity for x in scope.d.reportData.dataByDay[selection[0].row].popularActivities)
		scope.$digest()

	scope.onMonthSelected = (selection) ->
		scope.d.chartActivePeopleByMonth.data.rows = []
		for activePerson in scope.d.reportData.dataByMonth[selection[0].row].activePeople
			scope.d.chartActivePeopleByMonth.data.rows.push {c: [{v: activePerson.person.displayName}, {v: activePerson.total}]}
		scope.d.popularActivities.byMonth = (x.activity for x in scope.d.reportData.dataByMonth[selection[0].row].popularActivities)
		scope.$digest()

	scope.onYearSelected = (selection) ->
		scope.d.chartActivePeopleByYear.data.rows = []
		for activePerson in scope.d.reportData.dataByYear[selection[0].row].activePeople
			scope.d.chartActivePeopleByYear.data.rows.push {c: [{v: activePerson.person.displayName}, {v: activePerson.total}]}
		scope.d.popularActivities.byYear = (x.activity for x in scope.d.reportData.dataByYear[selection[0].row].popularActivities)
		scope.$digest()

	scope.d.chartRestrictedVsPublicEver =
		type: "PieChart"
		displayed: true
		cssStyle: "height:600px; width:600px;"
		data:
			cols: [
				id: "type"
				label: "Type"
				type: "string"
			,
				id: "quantity"
				label: "Quantity"
				type: "number"
			]
			rows: []

		options:
			title: "Public VS Restricted posts"
			isStacked: "true"
			fill: 20
			displayExactValues: true

	scope.d.chartRestrictedVsPublicByDay =
		type: "ColumnChart"
		displayed: true
		cssStyle: "height:600px; width:600px;"
		data:
			cols: [
				id: "day"
				label: "Day"
				type: "string"
			,
				id: "restricted"
				label: "Restricted"
				type: "number"
			,
				id: "public"
				label: "Public"
				type: "number"
			]
			rows: []

		options:
			title: "Public VS Restricted posts"
			isStacked: "true"
			fill: 20

	scope.d.chartRestrictedVsPublicByMonth =
		type: "ColumnChart"
		displayed: true
		cssStyle: "height:600px; width:600px;"
		data:
			cols: [
				id: "month"
				label: "Month"
				type: "string"
			,
				id: "restricted"
				label: "Restricted"
				type: "number"
			,
				id: "public"
				label: "Public"
				type: "number"
			]
			rows: []

		options:
			title: "Public VS Restricted posts"
			isStacked: "true"
			fill: 20

	scope.d.chartRestrictedVsPublicByYear =
		type: "ColumnChart"
		displayed: true
		cssStyle: "height:600px; width:600px;"
		data:
			cols: [
				id: "year"
				label: "Year"
				type: "string"
			,
				id: "restricted"
				label: "Restricted"
				type: "number"
			,
				id: "public"
				label: "Public"
				type: "number"
			]
			rows: []

		options:
			title: "Public VS Restricted posts"
			isStacked: "true"
			fill: 20

	scope.d.chartActivePeopleEver =
		type: "BarChart"
		displayed: true
		cssStyle: "height:600px; width:600px;"
		data:
			cols: [
				id: "person"
				label: "Person"
				type: "string"
			,
				id: "total"
				label: "total number of posts"
				type: "number"
			]
			rows: []

		options:
			title: "Most active people"
			isStacked: "true"
			fill: 20

	scope.d.chartActivePeopleByDay =
	type: "BarChart"
	displayed: true
	cssStyle: "height:600px; width:600px;"
	data:
		cols: [
			id: "person"
			label: "Person"
			type: "string"
		,
			id: "total"
			label: "total number of posts"
			type: "number"
		]
		rows: []

	options:
		title: "Most active people"
		isStacked: "true"
		fill: 20

	scope.d.chartActivePeopleByMonth =
	type: "BarChart"
	displayed: true
	cssStyle: "height:600px; width:600px;"
	data:
		cols: [
			id: "person"
			label: "Person"
			type: "string"
		,
			id: "total"
			label: "total number of posts"
			type: "number"
		]
		rows: []

	options:
		title: "Most active people"
		isStacked: "true"
		fill: 20

	scope.d.chartActivePeopleByYear =
	type: "BarChart"
	displayed: true
	cssStyle: "height:600px; width:600px;"
	data:
		cols: [
			id: "person"
			label: "Person"
			type: "string"
		,
			id: "total"
			label: "total number of posts"
			type: "number"
		]
		rows: []

	options:
		title: "Most active people"
		isStacked: "true"
		fill: 20

	# initialize report if coming directly from details url 
	if app.stateParams.reportName != undefined
		getReport(app.stateParams.reportName)

	]