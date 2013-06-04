function TagsController($rootScope, $scope, $http) {
	console.log("[+] TagsController");

	var selectedTags = [];	

	$http.get("/api/tags")
		.success(function(result) {
			angular.forEach(result.data, function(tag) {
				tag["selected"] = false;		
			})
    		$scope.tags = result.data;
		}).error(function(error) {
			alert("Arghhhh!")
		})		

	$scope.applyFilter = function() {
		$http({
			url: "/api/posts",
			data: {
				tags : selectedTags.join(",")
			},
			method: "POST"
		}).success(function(result) {
    		$scope.posts_by_tags = result.data;
		}).error(function(error) {
			alert("Arghhhh!")
		})	
	}

	$scope.onTagClick = function(tag) {
		tag["selected"] = !tag["selected"];

		if (tag["selected"] == true) {
			selectedTags.push(tag.name);
		} else {
			selectedTags.splice(selectedTags.indexOf(tag.name), 1);
		}
	}

}