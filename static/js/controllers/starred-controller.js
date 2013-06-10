function StarredController($http, $scope, $rootScope, $log, $routeParams) {
	$log.info("[+] Starred Controller!")
	$scope.posts = [];

	$http({
			url: "/api/posts/starred",
			method: "POST"
		}).success(function(result) {
			// $scope.feed = result.feed;
			angular.forEach(result.data, function(item) {
				var prop = "published";
				if (item.published == null) {
					item.published = {
						$date : "",
						time_ago: ""
					}
					prop = "created";
				}

				var date = moment(item[prop].$date)
				item.published.$date = date.format("MMM Do YYYY, HH:mm");
				item.published.time_ago = date.fromNow();
			})
			$scope.posts = $scope.posts.concat(result.data);
			$scope.page = result.page;
		}).error(function(error) {

		})	



}	