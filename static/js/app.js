var app = angular.module("app", ['ngResource', "$strap.directives", "ngCookies", 'ui.bootstrap', "infinite-scroll"]);

app.config(function($interpolateProvider) {
	$interpolateProvider.startSymbol('{[{');
  	$interpolateProvider.endSymbol('}]}');
});

app.config(function($routeProvider) {
	$routeProvider.when("/digest", {
		templateUrl: "static/partials/digest.html",
		controller: "DigestController" 
	}).when("/feed/:id", {
		templateUrl: "static/partials/feed.html",
		controller: "FeedController" 
	}).when("/tags", {
		templateUrl: "static/partials/tags.html",
		controller: "TagsController" 
	}).when("/starred", {
		templateUrl: "static/partials/starred.html",
		controller: "StarredController" 
	}).when("/import", {
		templateUrl: "static/partials/import.html",
		controller: "ImportController" 
	}).otherwise({
		redirectTo: "/"
	});
});

app.run(function($rootScope, $location, $http, $log, $cookieStore, $templateCache) {
	$log.info("[+] App is running!")
	
	$(".fullheight").height($(document).height() - 65);
	$(".fullheight2").height($(document).height() - 75);

	$rootScope.$on("$viewContentLoaded", function() {
		$templateCache.removeAll();
	})

	$rootScope.root = {};

	$http.get("/api/feeds/groups")
		.success(function(result) {			
			if (result.data && result.data.length > 0) {
				angular.forEach(result.data, function(feed) {
					feed["open"] = false;
				})
				$rootScope.feeds = result.data;

				$location.path("/digest")	
			} else {
				$location.path("/import");		
			}
		})
		.error(function(error) {
			alert("Arghhh!!!")
		})

	$rootScope.$watch("feeds", function(feeds) {
		angular.forEach(feeds, function(feed) {
			if (feed["open"] == true) {
				if (feed.items.length == 0) {
					$http({
						url: "/api/feeds",
						data: {
							group: feed.group
						},
						method: "POST"
					}).success(function(result) {
						feed.items = result.data
					}).error(function() {	
						alert("Arghhh!")	
					})
				}		
			}
		})
	}, true);	
});

app.filter("isLong", function isLong() {
      return function (text, length, end) {
      		text = text.replace(/^\s+/, '').replace(/\s+$/, '')
            if (isNaN(length))
                length = 29;

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
