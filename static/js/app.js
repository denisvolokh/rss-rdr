var app = angular.module("app", ['ngResource', "$strap.directives", "ngCookies"]);

app.config(function($interpolateProvider) {
	$interpolateProvider.startSymbol('{[{');
  	$interpolateProvider.endSymbol('}]}');
});

app.config(function($routeProvider) {
	$routeProvider.when("/", {
		templateUrl: "static/partials/home.html",
		controller: "HomeController"
	}).when("/import", {
		templateUrl: "static/partials/import.html",
		controller: "ImportController" 
	}).otherwise({
		redirectTo: "/"
	});
});

app.run(function($rootScope, $location, $http, $log, $cookieStore) {
	$log.info("[+] App is running!")
	
	$rootScope.root = {
		navigation: "digest"
	}

	var closedGroups = $cookieStore.get("closed-groups") || [];

	$http.get("/api/feeds")
		.success(function(result) {			
			if (result.data && result.data.length > 0) {
				$rootScope.root.feeds = result.data;
				angular.forEach($rootScope.root.feeds, function(feed) {
					var isClosed = (closedGroups.indexOf(feed["group"]) != -1);
					feed["isGroupOpen"] = !isClosed;
					angular.forEach(feed.items, function(item) {
						item["isGroupOpen"] = !isClosed;
					})
				})
				$location.path("/")	
			} else {
				$location.path("/import");		
			}
		})
		.error(function(error) {
			alert("Arghhh!!!")
		})
});

app.filter("isLong", function isLong() {
      return function (text, length, end) {
      		text = text.replace(/^\s+/, '').replace(/\s+$/, '')
            if (isNaN(length))
                length = 19;

            if (end === undefined)
                end = "...";

            if (text.length <= length || text.length - end.length <= length) {
                return text;
            }
            else {
                return String(text).substring(0, length-end.length) + end;
            }

      };
});
