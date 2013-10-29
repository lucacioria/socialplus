window.myApp.directive "activity",  [ '$sce', ($sce) ->
  restrict: "E"
  transclude: false
  templateUrl: "/public/html/partials/activity.html"
  link: ($scope, $element, $attrs) ->
    $scope.asHtml = (input) ->
      return $sce.trustAsHtml(input)
  ]

window.myApp.directive "activityBox", [ '$http', 'App', ($http, app) ->
  transclude: false
  
  scope: 
    searchString: "@searchString"
    activities: "=activities"
  
  link: ($scope, $element, $attrs) ->
    TAG = "activityBox directive"
    $scope.d = {activities: {}, page: 1, cursors: [], loading: false}
    $scope.getFirstPage = () ->
      $scope.d.loading = true
      $http
        method: 'GET'
        url: "/activities"
        params:
          q: $scope.searchString
      .success (data, status, headers, config) ->
        $scope.d.loading = false
        $scope.d.activities = data
      .error (data, status, headers, config) ->
        $scope.d.loading = false
        app.log.httpError(TAG, status, config)
    $scope.getNextPage = () ->
      return if $scope.d.activities.cursor == 'null'
      $scope.d.loading = true
      $http
        method: 'GET'
        url: "/activities"
        params:
          q: $scope.searchString
          nextPageCursor: $scope.d.activities.nextPageCursor
      .success (data, status, headers, config) ->
        $scope.d.loading = false
        $scope.d.cursors.push($scope.d.activities.nextPageCursor)
        $scope.d.activities = data
        $scope.d.page += 1
        scroll(0,300);
      .error (data, status, headers, config) ->
        $scope.d.loading = false
        app.log.httpError(TAG, status, config)
    $scope.getPreviousPage = () ->
      return if $scope.d.activities.cursor == 'null'
      $scope.d.loading = true
      $http
        method: 'GET'
        url: "/activities"
        params:
          q: $scope.searchString
          nextPageCursor: $scope.d.cursors[-1]
      .success (data, status, headers, config) ->
        $scope.d.loading = false
        $scope.d.cursors.pop()
        $scope.d.activities = data
        $scope.d.page -= 1
        scroll(0,300);
      .error (data, status, headers, config) ->
        $scope.d.loading = false
        app.log.httpError(TAG, status, config)
    # init activity box
    $scope.$watch 'activities', (newValue, oldValue) ->
      if newValue and newValue.length > 0
        $scope.d.activities.items = newValue
    $scope.$watch 'searchString', (newValue, oldValue) ->
      if newValue != undefined
        if newValue != ""
          $scope.getFirstPage()
        else
          $scope.d.activities = {}

  templateUrl: "/public/html/partials/activity_box.html"
]

window.myApp.directive "task", ->
  restrict: "E"
  transclude: false
  templateUrl: "/public/html/partials/task.html"

window.myApp.directive "loading", ->
  restrict: "E"
  transclude: false
  templateUrl: "/public/html/partials/loading.html"