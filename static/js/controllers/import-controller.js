function ImportController($log, $scope, $rootScope, $routeParams, $http) {
	$http.defaults.headers.post["Content-Type"] = "application/x-www-form-urlencoded";
	
	var uploadFile;

	$scope.setFile = function(element) {
		uploadFile = element.files[0];
	};	

	$scope.submitFile = function() {
		$scope.uploading = true;

		var formData = new FormData();
		if (angular.isDefined(uploadFile))
			formData.append("file", uploadFile);

		var xhr = new XMLHttpRequest;
		xhr.addEventListener("load", function(e) {

			// $http.get("/listfiles")
			// 	.success(function(data) {
			// 		$scope.datasets = data.reverse();
			// })	
		})

		xhr.open('POST', '/api/upload', true);	
	    xhr.send(formData);
	}
}