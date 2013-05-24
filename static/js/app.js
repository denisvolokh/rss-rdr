var app = angular.module("app", ['ngResource', "$strap.directives"]);

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

app.run(function($rootScope, $location, $http, $log) {
	$log.info("[+] App is running!")
	
	$rootScope.root = {
		navigation: "digest"
	}

	$http.get("/api/feeds")
		.success(function(result) {			
			if (result.data && result.data.length > 0) {
				$rootScope.root.feeds = result.data;
				angular.forEach($rootScope.root.feeds, function(feed) {
					feed["isGroupOpen"] = true;
					angular.forEach(feed.items, function(item) {
						item["isGroupOpen"] = true;
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
