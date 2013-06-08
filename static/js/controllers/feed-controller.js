function FeedController($http, $scope, $rootScope, $log, $routeParams) {
	var self = this;

	$scope.posts = [];

	var container = angular.element.find(".fullheight2")[0];

	self.scroll = function(event) {
		if (event.currentTarget.scrollTop + event.currentTarget.clientHeight == event.currentTarget.scrollHeight) {
			console.log("load more for page: ", $scope.page);
			
			if ($scope.page != undefined) {
				container.removeEventListener("scroll", self.scroll);
				self.fetchPosts($scope.page + 1, function() {
					container.addEventListener("scroll", self.scroll);					
				});				
			}
		}
	};

	self.fetchPosts = function(page, callback) {
		$http({
			url: "/api/posts",
			data: {
				feed_id: $routeParams.id || "0",
				page: page
			},
			method: "POST"
		}).success(function(result) {
			$scope.feed = result.feed;
			$scope.posts = $scope.posts.concat(result.data);
			$scope.page = result.page;
			if (callback) {
				callback();
			}
		}).error(function(error) {

		})	
	}

	$(".fullheight").height($(document).height() - 75);
	
	$(".fullheight2")[0].addEventListener("scroll", self.scroll);

	self.fetchPosts(1);	

	$scope.myPagingFunction = function() {
		console.log("load more");
	}

	$rootScope.root.makeFeedAllRead = function() {
		$http({
			url: "/api/feed/make_read/" + $routeParams.id,
			method: "POST"
		})
		.success(function(result) {
			angular.forEach($scope.posts, function(post) {
				post.read = true;
			});

			angular.forEach($rootScope.feeds, function(feed) {
				angular.forEach(feed.items, function(item) {
					if (item._id.$oid == $routeParams.id) {
						item.unread_count = result.unread_count;
						feed.unread_count = result.group_unread_count;
					}
				})
			})
		}).error(function(error) {
			alert("Arghhhh!")
		})	
	}

	$rootScope.root.unsubscribeFeed = function() {
		$http({
			url: "/api/feed/unsubscribe/" + $routeParams.id,
			method: "POST"
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
}
