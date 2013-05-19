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
		
	}

	$http.get("/api/feeds")
		.success(function(result) {			
			if (result.data && result.data.length > 0) {
				$rootScope.root.feeds = result.data;
				$location.path("/")	
			} else {
				$location.path("/import");		
			}
		})
		.error(function(error) {
			alert("Arghhh!!!")
		})
});
