var Collection, Book, Sequence, User, search;

(function() {
    var apiurl = "https://books.archivelab.org";

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
	var url = apiurl + '/search?q=' + query;
	requests.get(url, callback);
    }

    User = function(id) {
	this.email = email;
    }

    User.prototype = {
	get: function(id, callback) {
	    var url = apiurl + '/artists/' + this.id;
	    requests.get(url, callback);
	},

	//  login: function(email, password, callback) { }

    };

    Book = {
	create: function(data, callback) {
	    var url = apiurl + '/b';
	    requests.post(url, data, callback);	
	}
    };

    Author = {
	create: function(data, callback) {
	    var url = apiurl + '/a';
	    requests.post(url, data, callback);	
	}
    };

    Fulltext = {
	search: function(text, callback) {
	    var url = 'https://api.archivelab.org/v2/search/books?text="' + data.text + '"';
	    requests.get(url, callback);
	}
    }

}());
