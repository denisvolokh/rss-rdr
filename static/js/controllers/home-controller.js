function HomeController($http, $scope, $log, $rootScope, $cookieStore) {
	
	$(document).ready(function(){
	    $(".fullheight").height($(document).height() - 65);
	    $(".fullheight2").height($(document).height() - 75);
	});

	var fetchDigest = function() {
		$http.get("/api/digest")
			.success(function(result) {
				$scope.view = "";			
				if (result.data && result.data.length > 0) {
					$rootScope.root.digest = result.data;
					
				} else {
					
				}
			})
			.error(function(error) {
				alert("Arghhh!!!")
			})
	}

	var fetchStarred = function() {
		$scope.selectedFeed = {title : "Starred Items"}
		$http.get("/api/posts/starred")
			.success(function(result) {
				$scope.view = "read";			
				if (result.data && result.data.length > 0) {
					$scope.posts = result.data;
				} 
			})
			.error(function(error) {
				alert("Arghhh!!!")
			})	
	}

	fetchDigest();

	$scope.onStarClick = function(post) {
		$http({
			url: "/api/posts/update_star/" + post._id.$oid,
			method: "UPDATE"
		}).success(function(result) {
    		post.starred = !post.starred;
    		post.read = true;
		}).error(function(error) {
			alert("Arghhhh!")
		})
	}

	$scope.onPostClick = function(post) {		
		$http.get("/api/posts/make_read/" + post._id.$oid)
			.success(function(result) {
        		post.read = true;

        		angular.forEach($rootScope.root.feeds, function(group) {
					angular.forEach(group.items, function(item) {
						if (item.id.$oid == result.feed.$oid) {
							item.unread_count = result.unread_count;
							group.unread_count = result.group_unread_count;
						}
					})
				})
			})
			.error(function(error) {
				alert("Arghhhh!")
			})
	}

	$scope.onDigestClick = function() {
		$rootScope.root.navigation = "digest";

		fetchDigest();
	}

	$scope.onStarredClick = function() {
		$rootScope.root.navigation = "starred";

		fetchStarred();
	}

	$scope.onTagsClick = function() {
		$rootScope.root.navigation = "tags";
		$scope.view = "tags";

		$http.get("/api/tags")
			.success(function(result) {
        		$scope.tags = result.data;
			}).error(function(error) {
				alert("Arghhhh!")
			})		
	}

	$scope.onTagClick = function(tag) {
		tag["selected"] = true;
	}

	$scope.onDigestPostClick = function(post) {
		$scope.selectedPost = post;
		$http.get("/api/posts?feed_id=" + post.feed_id.$oid)
			.success(function(result) {
				$rootScope.root.navigation = post.feed_id.$oid;
        		$scope.posts = result.data;
        		$scope.selectedFeed = result.feed;
        		$scope.view = "read";
			}).error(function(error) {
				alert("Arghhhh!")
			})
	}

	$scope.onGroupHeaderClick = function(feed) {
		var closedGroups = $cookieStore.get("closed-groups") || [];
		var index = closedGroups.indexOf(feed["group"]);
		feed["isGroupOpen"] = !feed["isGroupOpen"];

		if (index != -1) {
			closedGroups.splice(index, 1);
		}
		if (feed["isGroupOpen"] == false) {
			closedGroups.push(feed["group"])	
		} 

		angular.forEach(feed.items, function(item) {
			item["isGroupOpen"] = feed["isGroupOpen"];
		});

		$cookieStore.put("closed-groups", closedGroups);
	}

	$scope.onFeedItemClicked = function(feed) {
		$rootScope.root.navigation = feed.id.$oid;
		$http.get("/api/posts?feed_id=" + feed.id.$oid)
			.success(function(result) {
        		$scope.posts = result.data;
        		$scope.selectedFeed = result.feed;
        		$scope.view = "read";
        		window.scrollTo(0, 0)
			}).error(function(error) {
				alert("Arghhhh!")
			})
	}

	$rootScope.root.makeFeedAllRead = function(feed_id) {
		$http({
			url: "/api/feed/make_read/" + feed_id,
			method: "UPDATE"
		})
		.success(function(result) {
			angular.forEach($scope.posts, function(post) {
				post.read = true;
			});

			angular.forEach($rootScope.root.feeds, function(group) {
				angular.forEach(group.items, function(item) {
					if (item.id.$oid == result.feed) {
						item.unread_count = result.unread_count;
						group.unread_count = result.group_unread_count;
					}
				})
			})
		}).error(function(error) {
			alert("Arghhhh!")
		})	
	}

	$rootScope.root.unsubscribeFeed = function(feed_id) {
		$http({
			url: "/api/feed/unsubscribe/" + feed_id,
			method: "DELETE"
		})
		.success(function(result) {
			angular.forEach($rootScope.root.feeds, function(group) {
				if (group.group == result.group.group) {
					group.unread_count = result.group.unread_count;
					group.items = result.group.items;
					angular.forEach(group.items, function(item) {
						item["isGroupOpen"] = true;
					})
				}
			})	

			$rootScope.root.navigation = "digest";
			fetchDigest();
		}).error(function(error) {
			alert("Arghhhh!")
		})		
	}

	$scope.getNavigationMenuState = function(actual, expected) {
		if (actual == expected) {
			return "active"
		} else {
			return ""
		}
	}

	$scope.getPostBlockquoteClass = function(post) {
		return (post.read == true) ? '' : 'unread'
	}
}