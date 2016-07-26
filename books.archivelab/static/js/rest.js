var Collection, Book, Sequence, User, search;

(function() {
    var apiurl = "https://api.archivelab.org/search/books";

    var requests = {
	get: function(url, callback, options) {
	    $.get(url, options || {}, function(results) {
	    }).done(function(data) {
		if (callback) { callback(data); }
	    });
	},

	post: function(url, data, callback) {
	    $.post(url, data, function(results) {
	    }).done(function(data) {
		if (callback) { callback(data); }
	    });
	},

	put: function(url, data, callback) {
	    $.put(url, data, function(results) {
	    }).done(function(data) {
		if (callback) { callback(data); }
	    });
	},

	delete: function(url, data, callback) {
	    $.delete(url, data, function(results) {
	    }).done(function(data) {
		if (callback) { callback(data); }
	    });
	}

    };

    search = function(query, callback) {
	var url = apiurl + '?text=' + query + '&fields=names,ids';
	requests.get(url, callback);
    }

}());
