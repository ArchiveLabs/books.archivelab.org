var Collection, Book, Sequence, User, search;

(function() {
    var redux = {
	last_search: "",
	triggered: false
    };

    var shrink = function(s) {
	if (s.length > 65) {
	    return s.slice(0, 65) + ' ...';
	}
	return s
    }

    var listify = function(authors) {
	var res = [];
	for (a in authors) {
	    res.push(['<a class="author-url yellow" href="/a/' + authors[a].id +  '">' + authors[a].name + '</a>']);
	}
	return res.join(', ');
    }
    
    var highlight = function(matches) {
	var results = '<ul>';
	for (i in matches) {
	    var match = matches[i];
	    while(match.indexOf('{{{') > -1) {
		match = match.replace('{{{', '<span style="font-weight: bold;">');
		match = match.replace('}}}', '</span>')
	    }
	    results += '<li>' + match + '</li>';
	}
	results += '</ul>';
	if (results !== '<ul></ul>') {
	    return '<div class="matched-region" style="font-size: .9em;" >' +
		'Fulltext matches:' + results + 
  		'</div>';
	} else {
	    return '';
	}
    }

    var renderResults = function(results) {
	console.log(results);

	// $('#results').append('<div id="collections"><ul></ul></div>');

	for (var b in results.books) {
	    var book = results.books[b];

	    // for (var c in book.collections) {
	    //   collection = book.collections[c];
	    //   $('#collections ul').append('<li>' + collection + '</li>');
	    // }

	    // 9 col, 2 cover, 5 desc, 3 fulltext results

	    $('#results').append(
		'<div class="book">' + 
		    '<h4><a href="/b/' + book.archive_id + '#'
		    + book.id + '">' + shrink(book.name) + '</a>' +
		    '</h4>' + 
		    '<div class="cover">' +
  		      '<a href="/b/' + book.archive_id + '">' +
  		        '<img src="' + book.cover_url + '"/>' +
		      '</a>' + 
		    '</div>' +
		    '<div class="content">' +
		    '<p class="bookurl">' +
		        '<a href="/b/' + book.archive_id + '#' + book.id  + '">' +
		          window.location.protocol + '//' + window.location.host + 
		          '/b/' + book.archive_id + '#' + book.id +
		        '</a>' +
		      '</p>' +
		      '<span>by ' + listify(book.authors) + '</span> - ' +
		      '<span style="color: #999;">' + book.data.date + '</span>' + 
		      '<div class="desc">' +
		      '<p class="description">' + book.data.description + '</p>' +
		      '</div>' +		
		        highlight(book.matches) + 
		      '<div class="coming-soon">' +
		        //'<p>In collection(s): ' + book.collections + '</p>' +
		        //'<p>In sequences(s) -- show to right:</p>' +
		        //'<p>People read this before:</p>' +
		        //'<p>This book unlocks:</p>' +
  		        //'<p>Book highlights:</p>' +
		      '</div>' +
		    '</div>' +
		'</div>'
	    );
	$('#results').append('<div class="clearfix"></div>');
	}

	/*
	if (results.collections) {
	    $('#results').append('<h2>Collections</h2>');
	    for (var c in results.collections) {
		var co = results.collections[c];
		$('#results').append(
		    '<div class="collection">' + co.name + '</div>'
		);
	    }
	    $('#results').append('<div class="clearfix"></div>');
	}

	if (results.sequences) {
	    $('#results').append('<h2>Sequences</h2>');
	    for (var s in results.sequences) {
		var seq = results.sequences[s];
		$('#results').append(
		    '<div class="sequence">' + seq.name + '</div>'
		);
	    }
	    $('#results').append('<div class="clearfix"></div>');
	}
	*/
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
	    $('#results').css('width', '800px');
	    $('#results').css('margin', '0px');
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
    }, 300, false));


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
	    if (results.books.length || results.authors.length ||
		results.collections.length || results.sequences.length) {
		renderResults(results);
	    } else {
		$('#results').append(no_results);
	    }
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
