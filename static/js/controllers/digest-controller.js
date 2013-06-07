function DigestController($http, $scope, $location, $rootScope, $cookieStore) {

	$http.get("/api/digest")
		.success(function(result) {
			if (result.data && result.data.length > 0) {
				$scope.posts = result.data;
				
			} 
		})
		.error(function(error) {
			alert("Arghhh!!!")
		})


	$scope.onDigestPostClick = function(post) {
		$location.path("/feed/" + post.feed_id.$oid)	
	}
}