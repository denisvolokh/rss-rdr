function HomeController($http, $scope, $log, $rootScope) {
	
	$http.get("/api/digest")
		.success(function(result) {			
			if (result.data && result.data.length > 0) {
				$rootScope.root.digest = result.data;
				
			} else {
				
			}
		})
		.error(function(error) {
			alert("Arghhh!!!")
		})

	$scope.onPostClick = function(post) {		
		$http.get("/api/posts/make_read/" + post._id.$oid)
			.success(function(result) {
        		post.read = true;
        		// window.scrollTo(0, 200)		
			}).error(function(error) {
				alert("Arghhhh!")
			})
	}

	$scope.onDigestPostClick = function(post) {
		$scope.selectedPost = post;
		$http.get("/api/posts?feed_id=" + post.feed_id.$oid)
			.success(function(result) {
        		$scope.posts = result.data;
        		$scope.selectedFeed = result.feed;
        		$scope.view = "read";
			}).error(function(error) {
				alert("Arghhhh!")
			})
	}

	$scope.itemClicked = function(post) {
		$http.get("/api/posts?feed_id=" + post.id.$oid)
			.success(function(result) {
        		$scope.posts = result.data;
        		$scope.selectedFeed = result.feed;
        		$scope.view = "read";
        		window.scrollTo(0, 0)
			}).error(function(error) {
				alert("Arghhhh!")
			})
	}

	$scope.getPostBlockquoteClass = function(post) {
		return (post.read == true) ? '' : 'unread'
	}
}