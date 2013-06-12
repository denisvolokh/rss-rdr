function FeedController($http, $scope, $rootScope, $log, $routeParams) {
	$log.info("[+] Feed Controller!")

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
			if (callback) {
				callback();
			}
		}).error(function(error) {

		})	
	}

	$(".fullheight").height($(document).height() - 75);
	
	$(".fullheight2")[0].addEventListener("scroll", self.scroll);

	self.fetchPosts(1);	

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

	$scope.onAddTagsClick = function(post) {
		$http.get("/api/tags")
			.success(function(result) {
				var tags = []	
				angular.forEach(result.data, function(tag) {
					if (post.tags.indexOf(tag.name) == -1)
						tags.push(tag.name)
				})
				$scope.tagPopoverData = {
					tagname: "",
					post: post,
					tags: tags
				}
			}).error(function(error) {
				alert("Arghhhh!")
			})		
	}	

	$scope.onCreateTagClick = function(data) {
		if (data.tagname != "") {
			tags = data.post.tags || [];
			tags.push(data.tagname);	
			
			$http({
				url: "/api/posts/" + data.post._id.$oid + "/add_tags",
				data: {
					tags : tags.join(",")
				},
				method: "POST"
			}).success(function(result) {
	    		
			}).error(function(error) {
				alert("Arghhhh!")
			})	
		}

		$scope.tagPopoverData = {
			tagname: "",
			post: null
		}
	}

	$scope.onRemoveTagClick = function(post, tag) {
		tags = post.tags;
		tags.splice(tags.indexOf(tag), 1);
		
		$http({
			url: "/api/posts/" + post._id.$oid + "/add_tags",
			data: {
				tags : tags.join(",")
			},
			method: "POST"
		}).success(function(result) {
    		
		}).error(function(error) {
			alert("Arghhhh!")
		})		
	}
}
