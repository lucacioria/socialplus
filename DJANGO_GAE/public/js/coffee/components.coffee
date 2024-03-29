window.myApp.directive "activity", ->
  restrict: "E"
  transclude: false
  templateUrl: "/public/html/partials/activity.html"

window.myApp.directive "activityBox", [ '$http', 'App', ($http, app) ->
  transclude: false
  
  scope: 
    searchString: "@searchString"
    activities: "=activities"
  
  link: ($scope, $element, $attrs) ->
    TAG = "activityBox directive"
    $scope.d = {activities: {}, page: 1, loading: false}
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
          nextPageCursor: $scope.d.activities.cursor
      .success (data, status, headers, config) ->
        $scope.d.loading = false
        $scope.d.activities = data
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
