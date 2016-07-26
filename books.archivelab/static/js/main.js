var Collection, Book, Sequence, User, search;

(function() {
    var redux = {
	last_search: "",
	triggered: false
    };

    var shrink = function(s) {
	if (s.length > 75) {
	    return s.slice(0, 75) + ' ...';
	}
	return s
    }

    var listify = function(authors) {
	var res = [];
	for (a in authors) {
	    res.push(['<a href="/a/' + authors[a].id +  '">' + authors[a].name + '</a>']);
	}
	return res.join(', ');
    }
    
    var renderResults = function(results) {
	console.log(results);
	for (var archive_id in results) {
	    var key = archive_id;
	    var title = results[archive_id];
	    $('#results').append(
		'<div class="book">' + 
		    '<a href="https://archive.org/details/' + archive_id + '">' + 
		    title + '</a>' +
	    '</div>'
	    );
	}
	$('#results').append('<div class="clearfix"></div>');
    }    


    var debounce = function (func, threshold, execAsap) {
	var timeout;
	return function debounced () {
	    var obj = this, args = arguments;
	    function delayed () {
		if (!execAsap)
		    func.apply(obj, args);
		timeout = null;
	    };
	    
	    if (timeout)
		clearTimeout(timeout);
	    else if (execAsap)
		func.apply(obj, args);
	    
	    timeout = setTimeout(delayed, threshold || 100);
	};
    }

    // On search typing
    $('#content form').submit(function(event) {
	// bring up more comprehensive results in resultsbox
	event.preventDefault();
    });

    var clear_splash = function() {
	if (!redux.triggered) {
	    $('header').remove();
	    $('#content').css('padding', '10px');
	    $('#content').css('background', '#eee');
	    $('#content.form').css('border-bottom', '1px solid #ddd');
	    $('.wbs__searchbox').css('margin', '0px');
	    redux.triggered = true;
	}
    }

    var no_results = '<div>' + 
	'<p>' + 
	'No results found. Want to <a href="/map">explore a map</a> ' +
	'of all available categories?</p><p>If the book you\'re ' + 
	'looking for is on Archive.org, you can add it using ' + 
	'<a href="/admin">this form</a>!' +
	'</p>' +
	'</div>';

    $('.wbs__searchInput').keyup(debounce(function(event) {
	clear_splash();
	var $this = $(this);
	var this_search = $('.wbs__searchInput').val()
	change_url(this_search);
	if (jQuery.trim(this_search) === "") {
	    $('#results').empty();	    
	    $('#results').append(no_results);
	} else if (redux.last_search != this_search && jQuery.trim(this_search) !== "") {
	    _search(this_search);
	}
    }, 175, false));


    var change_url = function(query) {
	var getUrl = window.location;
	var baseUrl = getUrl .protocol + "//" + getUrl.host + "/" + getUrl.pathname.split('/')[1];
	window.history.pushState({
	    "html": document.html,
	    "pageTitle": document.title + " " + query,
	}, "", baseUrl + "?search=" + query);
    }

    var _search = function(query) {
	search(query, function(results) {
	    $('#results').empty();
	    redux.last_search = query;
	    renderResults(results);
	});
    }

    var getJsonFromUrl = function () {
	var query = location.search.substr(1);
	var result = {};
	query.split("&").forEach(function(part) {
	    var item = part.split("=");
	    result[item[0]] = decodeURIComponent(item[1]);
	});
	return result;
    }

    /* Parse GET parameters */
    var options = getJsonFromUrl();
    console.log(options);
    if (options.search) {
	$('.wbs__searchInput').val(options.search)
	redux.last_search = options.search;
	_search(options.search);
    }

    $('.wbs__searchInput').focus();

}());
