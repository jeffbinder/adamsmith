function create_top_topics_list()
{
    // CUSTOM: next and prev page links.
    html = [];
    var pagenum = parseInt(this_doc),
        prev_page = ("00" + (pagenum - 1)).slice(-3),
        next_page = ("00" + (pagenum + 1)).slice(-3);
    if (prev_page in doc_names) {
        html.push("<div style='float:left'><a id='prev-link' href='"
                  + prev_page
                  + ".html'>Previous page</a></div>");
    }
    html.push("<a href='index.html'>Table of contents</a> | "
              + "<a href='topic-index.html'>List of topics</a> | "
              + "<a href='smith-index.html'>1784 index</a>");
    if (next_page in doc_names) {
        html.push("<div style='float:right'><a id='next-link' href='"
                  + next_page
                  + ".html'>Next page</a></div>");
    }
    $(html.join("")).appendTo($("#prev-next-area"));

    $("#title-area").html("The Wealth of Nations - " + book + " - " + chapter
    					  + " - p. " + pagenum);

    var html = ["<div style='float:right;margin-right:15px'><div>",
                "Prominent topics:</div><table id='top-topic-table'>"];
    var ntopics = top_topics.length;
    var nrows = 3, ncols = 3;
    for (var i = 0; i < nrows; i++) {
        html.push("<tr>");
        for (var j = 0; j < ncols; j++) {
            var k = i + j * nrows;
            if (k >= ntopics) break;
            var topic = top_topics[k];
            var topic_name = topic_names[topic].split(" ").slice(0, 3).join(" ");
            /*// Determine if this page fails to appear under all of the correlated headings.
            var no_match = true;
            if (topic_matches[topic][0][1] < 0.15) {
                    no_match = false; // Don't expect a match if there is no correlation.
            } else {
                for (var i2 = 0; i2 < topic_matches[topic].length; i2++) {
                    var heading = topic_matches[topic][i2][0];
                    var nsubheadings = index[heading].length;
                    for (var j2 = 0; j2 < nsubheadings; j2++) {
                        if (index[heading][j2][1] == parseInt(this_doc)) {
                            no_match = false;
                            break;
                        }
                    }
                    if (no_match == false) break;
                }
            }*/
            html.push("<td>" + (k + 1) + ". "
                      //+ (no_match? "<b>": "")
                      + "<a class='explanation-link' id='explanation-link"
                      + topic + "' href='javascript:explain_topic("
                      + topic + ")'>" + topic_name
                      + "</a>"
                      //+ (no_match? "</b>": "")
                      + "</td>");
        }
        html.push("</tr>");
    }
    html.push("</table></div>");

    // CUSTOM: Index headings
    html.push("<div style='float:left'>"
              + "<div>Index headings:</div>"
              + "<table id='index-heading-table'>");
    var nheadings = index_headings.length;
    var nrows = 3, ncols;
    ncols = Math.ceil(nheadings * 1.0 / nrows);
    for (var i = 0; i < nrows; i++) {
        html.push("<tr>");
        for (var j = 0; j < ncols; j++) {
            var k = i + j * nrows;
            if (k >= nheadings) break;
            var heading = index_headings[k];
            /*// Determine if this page fails to match all of the correlated topics.
            var no_match = true;
            if (heading_matches[heading][0][1] < 0.15) {
                    no_match = false; // Don't expect a match if there is no correlation.
            } else {
                var nsubheadings = index[heading].length;
                for (var i2 = 0; i2 < heading_matches[heading].length; i2++) {
                    var topic = parseInt(heading_matches[heading][i2][0]);
                    for (var j2 = 0; j2 < nsubheadings; j2++) {
                        if (docs_by_topic[topic][j2][0] == this_doc) {
                            no_match = false;
                            break;
                        }
                    }
                    if (no_match == false) break;
                }
            }*/
            // Find the subheading for this page.
            var subheadings = "";
            for (var i2 = 0; i2 < index[heading].length; i2++) {
                if (index[heading][i2][1] == this_doc) {
                	if (!!subheadings) {
                		subheadings += "/";
                	}
                    subheadings += index[heading][i2][0];
                }
            }
            html.push("<td>" + (k + 1) + ". "
                      //+ (no_match? "<b>": "")
                      + "<a class='heading-link' id='heading-link"
                      + heading.replace(/ /g, '_')
                      + "' href='javascript:explain_heading(\""
                      + heading + "\")' title='"
                      + heading + ", " + subheadings
                      + "'>" + heading
                      + "</a>"
                      //+ (no_match? "<b>": "")
                      + "</td>");
        }
        html.push("</tr>");
    }
    html.push("</table></div>");

    $(html.join("")).appendTo($("#top-topic-area"));
}


var current_popup = null;
var current_popup_full = false;

function show_popup(topic, center)
{
    // CUSTOM: always use the full explanation popup.
    explain_topic(topic); return;
    hide_explanation();
    _show_popup(topic, false, false, 'center', center=center);

    $(document).unbind("mouseup");
    $(document).one("mouseup", hide_popup);
}

function hide_popup()
{
    $("#popup, #popup-content").animate({"width": 30}, duration=150,
                        complete=function () {
                            $("#popup").remove();
                            $(".topic-link").css("color", "");
                            $(".marginal-link a").css("color", "");
                            hide_explanation_quick();
                            current_popup = null;
                        });
}

function show_index_popup(topic)
{
    _show_popup(topic, true, false, 'top');

    $(document).unbind("mouseup");
    $(document).one("mouseup", hide_popup);
}

function coef_description(coef)
{
    if (coef < 0.15) return "Very weak";
    if (coef < 0.20) return "Weak";
    if (coef < 0.25) return "Moderate";
    if (coef < 0.30) return "Strong";
    return "Very strong";
}

function _show_popup(topic, full, fixed, notch_pos, center)
{
    if (topic == current_popup
        && current_popup_full == !!full) return;

    // Update link colors.
    $("#popup").remove();
    $(".topic-link").css("color", "");
    $(".marginal-link a").css("color", "");
    $("#" + topic + " a").css("color", "red");

    // Construct the popup contents.
    var html = [];

    html.push(topic_names[topic]);

    var docs = docs_by_pointed_topic[topic] || [];
    var ndocs = docs.length;

    // CUSTOM: exemplary passages disabled.
    /*if (full) {
        if (ndocs)
            html.push("<hr />Exemplary passages:<br />");
        else
            html.push("<hr />No exemplary passages for this topic.<br />");
    } else {
        if (ndocs > 1)
            html.push("<hr />Other exemplary passages for this topic:<br />");
        else
            html.push("<hr />No other exemplary passages for this topic.<br />");
    }

    var docs_listed = {};
    for (var i = 0; i < ndocs; i++) {
        var doc = docs[i];
        if (!full && doc == this_doc) {
            continue;
        }
        docs_listed[doc] = true;
        if (doc == this_doc)
            html.push("<a href='javascript:show_popup(" + topic + ")'>");
        else
            html.push("<a href='" + doc + ".html?topic" + topic + "'>");
        html.push(parseInt(doc));
        html.push("</a>");
        html.push(": ...");
        html.push(extracts[doc][topic]);
        html.push("...<br />");
    }*/

    var matches;
    if (full) {
        // CUSTOM: show matching index headings.
        matches = topic_matches[topic];
        html.push("<hr /><table>");
        if (matches[0][1] < 0.15) {
            html.push("<tr><td style='padding-right:20px'>Best-correlated heading:</td><td>Correlation:</td></tr>");
        } else {
            html.push("<tr><td style='padding-right:20px'>Associated headings (click to select):</td><td>Correlation:</td></tr>");
        }
        for (var i = 0; i < matches.length; i++) {
            var match = matches[i];
            html.push("<tr><td style='padding-right:20px'>");
            html.push("<span class='heading-selector' id='heading-sel-"
                      + match[0].replace(/ /g, '_') + "'>");
            if ('index_headings' in window && index_headings.some(function (x) {return x == match[0]})) {
                html.push("*");
            }
            html.push(match[0]);
            html.push("</span></td><td>");
            html.push(match[1].toFixed(2));
            html.push(" (");
            html.push(coef_description(match[1]));
            html.push(")</td></tr>");
        }
        html.push("</table><hr /><div id='match-details-area'></div>");
    } else {
        html.push('<hr /><a href="javascript:explain_topic('
                  + topic + ')">Explain the relevance of this topic</a>');
    }

    html = html.join('');

    var total_height = $(".index-entry").length
    	* ($(".first-row .index-entry").height() + 10) + 1;
    var popup = $("<div id='popup' class='popup'>"
                  + "<div id='popup-content'>"
                  + html + "</div></div>")
        .css("position", "relative")
        .appendTo("#popup-area");

    if (full) {
        // CUSTOM: set up the interactive elements of the popup.
        function select_heading(heading, coef)
        {
            $(".heading-selector")
                .css("background-color", "")
                .css("color", "");
            $("#heading-sel-" + heading.replace(/ /g, '_'))
                .css("background-color", "black")
                .css("color", "white");
            $(".heading-link")
                .css("color", "");
            $("#heading-link" + heading.replace(/ /g, '_'))
                .css("color", "red");

            var html = ["<table><tr><td style='padding-right:20px'>Top pages for topic:",
                        "</td><td>Indexed under \"", heading, "\"?</td></tr>"];
            var subheadings = index[heading];
            var indexed_pages = {};
            for (var i = 0; i < subheadings.length; i++) {
                indexed_pages[subheadings[i][1]] = subheadings[i][0];
            }
            var n_indexed_pages = 0;
            for (doc in indexed_pages) {
                n_indexed_pages++;
            }
            var docs = docs_by_topic[topic].slice(0, n_indexed_pages);
            for (var i = 0; i < docs.length; i++) {
                var doc = docs[i][0];
                html.push("<tr><td style='padding-right:20px'>" + (i+1) + ". ");
                if (doc == this_doc)
                    html.push("<a href='" + doc + ".html?explain" + topic + "' "
                              + "style='color:red'>");
                else
                    html.push("<a href='" + doc + ".html?explain" + topic + "'>");
                html.push(parseInt(doc) + "</a></td>");
                if (parseInt(doc) in indexed_pages) {
                    html.push("<td>yes</td>");
                    delete indexed_pages[parseInt(doc)];
                }
                html.push("</tr>");
            }
            var last_rank = i;
            var other_doc_ranks = {};
            var other_docs = [];
            var ndocs = docs_by_topic[topic].length;
            for (doc in indexed_pages) {
                for (var i = 0; i < ndocs; i++) {
                    if (parseInt(docs_by_topic[topic][i][0]) == doc)
                        break;
                }
                other_doc_ranks[doc] = i + 1;
                other_docs.push(doc);
            }
            other_docs.sort(function (a, b) {
                return other_doc_ranks[a] - other_doc_ranks[b]
                    || a - b;
            });
            for (var i = 0; i < other_docs.length; i++) {
                var doc = other_docs[i];
                if (other_doc_ranks[doc] == ndocs + 1) {
                    html.push("<tr><td>n/a. ");
                } else {
                    var rank = other_doc_ranks[doc];
                    if (rank > last_rank + 1)
                        html.push("<tr><td>...</td></tr><tr><td>");
                    else
                        html.push("<tr><td>");
                    last_rank = rank;
                    html.push(rank + ". ");
                }
                if (doc == parseInt(this_doc))
                    html.push("<a href='" + ("00" + doc).slice(-3)
                              + ".html?explain" + topic + "' style='color:red'>"
                              + doc + "</a>");
                else
                    html.push("<a href='" + ("00" + doc).slice(-3) + ".html?explain"
                              + topic + "'>" + doc + "</a>");
                html.push("</td><td>yes</td></tr>");
            }
            html.push("</table>");
            var notch_offset = parseInt($("#notch").css("top"));
            notch_offset += $("#popup-content").height();
            $("#match-details-area").html(html.join(""));
            notch_offset -= $("#popup-content").height();
            $("#notch").css("top", notch_offset);
        }
        for (var i = 0; i < matches.length; i++) {
            var heading = matches[i][0];
            $("#heading-sel-" + heading.replace(/ /g, '_'))
                .click((function (heading, coef) {
                            return function () {
                                select_heading(heading, coef);
                            }
                        })(heading, matches[i][1]));
        }
        select_heading(matches[0][0], matches[0]);
    }

    var popup_width = popup.width();
    if (current_popup === null)
        popup.css("width", 30); // Start out small for the animation.

    if (!fixed) {
        // Figure out where to position the popup.
        var rownum = $("#text-table > tbody").children()
            .index($("#" + topic).parent().parent());
        if (rownum == -1) 
            rownum = $("#text-table > tbody").children()
                .index($("#" + topic).parent());
        var nrows = $("#text-table .text-line").length 
            || $("#text-table .index-entry").length;
        var yoffset = total_height * rownum / nrows;

        // Figure out where to position the notch on the left.
        var notch_offset;
        if (notch_pos == 'center') {
            yoffset -= $("#popup-content").height() / 2;
            if (yoffset < 0)
                yoffset = 0;
            popup.css("top", yoffset);
            if (yoffset == 0)
                notch_offset = (total_height * (rownum + 0.5) / nrows
                                - $("#popup-area").height() - 15);
            else
                notch_offset = -($("#popup-area").height() / 2) - 15;
        } else if (notch_pos == 'top') {
            yoffset -= 30;
            if (yoffset < 0)
                yoffset = 0;
            popup.css("top", yoffset);
            if (yoffset == 0)
                notch_offset = (total_height * (rownum + 0.5) / nrows
                                - $("#popup-area").height() - 15);
            else
                notch_offset = -$("#popup-content").height() + 30 - 15;
            if (notch_offset + $("#popup-content").height() < 15) {
                // The notch is at the edge.  Don't round this corner.
                $("#popup-content").css("-moz-border-top-left-radius", 0)
                    .css("-webkit-border-top-left-radius", 0)
                    .css("-khtml-border-top-left-radius", 0)
                    .css("border-top-left-radius", 0);
            }
        }

        $("<img id='notch' src='notch-left.png'></img>")
            .css("position", "relative")
            .css("left", -14)
            .css("top", notch_offset)
            .appendTo("#popup");

        if (notch_pos == 'center') {
            // Auto-scroll so that the popup is as fully on-screen as possible.
            var sel = ($.browser['msie'] || $.browser['mozilla'])? "html": "body";
            if (center) {
                // Scroll so that the popup is centered.
                $(sel).scrollTop(Math.max($("#popup-content").offset().top
                                          + $("#popup-content").height() / 2
                                          - $(window).height() / 2,
                                          0))
            } else if ($(sel).scrollTop() > $("#popup-content").offset().top - 100) {
                $(sel).animate({
                    scrollTop: $("#popup-content").offset().top - 100
                }, 400);
            } else if ($(sel).scrollTop() + $(window).height()
                < $("#popup-content").offset().top + $("#popup-content").height() + 30) {
                $(sel).animate({
                    scrollTop: $("#popup-content").offset().top
                        + $("#popup-content").height() - $(window).height() + 30
                }, 400);
            }
        }
    } else {
        // Set up a fixed-position popup.
        var popup_height = popup.height();
        var max_height = $(window).height() - 210;
        if (popup_height > max_height) {
            $("#popup-content").css("height", max_height)
                .css("overflow-y", "scroll");
        }

        $("#popup-content").css("position", "fixed");
        $("#popup-content").css("top", 80);
    }

    if (current_popup === null)
        popup.animate({"width": popup_width}, duration=150);
    else
        popup.css("width", popup_width);

    $("#popup").mouseup(function () {return false;});
        
    current_popup = topic;
    current_popup_full = full;
}

// CUSTOM
function _show_heading_popup(heading, full, fixed)
{
    if (heading == current_popup
        && current_popup_full == !!full) return;

    // Update link colors.
    $("#popup").remove();
    $(".topic-link").css("color", "");
    $(".marginal-link a").css("color", "");
    $(".heading-link").css("color", "");
    $("#heading-link" + heading.replace(/ /g, '_')).css("color", "red");

    // Construct the popup contents.
    var html = [];

    html.push(heading);
    html.push(" (<a href='smith-index.html#");
    html.push(heading);
    html.push("'>show in index</a>)");

    // Find and add the subheading(s) for this page.
    html.push("<div style='width:400px; white-space:normal; text-indent:20px'>");
    var first = true;
    for (var i = 0; i < index[heading].length; i++) {
        if (index[heading][i][1] == this_doc) {
    		if (!first) html.push("</div><div style='width:400px; white-space:normal; text-indent:20px'>");
    		first = false;
            html.push(index[heading][i][0]);
        }
    }
    html.push("</div>");

    var matches;
    matches = heading_matches[heading];
    html.push("<hr /><table>");
    if (matches[0][1] < 0.15) {
        html.push("<tr><td style='padding-right:20px'>Best-correlated topic:</td><td>Correlation:</td></tr>");
    } else {
        html.push("<tr><td style='padding-right:20px'>Associated topics (click to select):</td><td>Correlation:</td></tr>");
    }
    for (var i = 0; i < matches.length; i++) {
        var match = matches[i];
        html.push("<tr><td style='padding-right:20px'>");
        if (top_topics.some(function (x) {return x == match[0]})) {
            html.push("*");
        }
        html.push("<span class='topic-selector' id='topic-sel-"
                  + match[0] + "'>");
        var topic_name = topic_names[match[0]].split(" ").slice(0, 3).join(" ");
        html.push(topic_name);
        html.push("</span></td><td>");
        html.push(match[1].toFixed(2));
        html.push(" (");
        html.push(coef_description(match[1]));
        html.push(")</td></tr>");
    }
    html.push("</table><hr /><div id='match-details-area'></div>");

    html = html.join('');

    var total_height = $("#popup-area").parent().height();
    var popup = $("<div id='popup' class='popup'>"
                  + "<div id='popup-content'>"
                  + html + "</div></div>")
        .css("position", "relative")
        .appendTo("#popup-area");

    function select_topic(topic, coef)
    {
        //$('[class^="topic"]').css("background-color", "");
        //$(".topic" + topic).css("background-color", "red");
        $(".topic-selector")
            .css("background-color", "")
            .css("color", "");
        $("#topic-sel-" + topic)
            .css("background-color", "black")
            .css("color", "white");
        $(".explanation-link")
            .css("color", "");
        $("#explanation-link" + topic)
            .css("color", "red");

        var html = ["<table><tr><td style='padding-right:20px'>Top pages for topic:",
                    "</td><td>Indexed under \"", heading, "\"?</td></tr>"];
        var subheadings = index[heading];
        var indexed_pages = {};
        for (var i = 0; i < subheadings.length; i++) {
            indexed_pages[subheadings[i][1]] = subheadings[i][0];
        }
        var n_indexed_pages = 0;
        for (doc in indexed_pages) {
            n_indexed_pages++;
        }
        var docs = docs_by_topic[topic].slice(0, n_indexed_pages);
        for (var i = 0; i < docs.length; i++) {
            var doc = docs[i][0];
            html.push("<tr><td style='padding-right:20px'>" + (i+1) + ". ");
            if (doc == this_doc)
                html.push("<a href='" + doc + ".html?heading" + heading + "' "
                          + "style='color:red'>");
            else
                html.push("<a href='" + doc + ".html?heading" + heading + "'>");
            html.push(parseInt(doc) + "</a></td>");
            if (parseInt(doc) in indexed_pages) {
                html.push("<td>yes</td>");
                delete indexed_pages[parseInt(doc)];
            }
            html.push("</tr>");
        }
        var last_rank = i;
        var other_doc_ranks = {};
        var other_docs = [];
        var ndocs = docs_by_topic[topic].length;
        for (doc in indexed_pages) {
            for (var i = 0; i < ndocs; i++) {
                if (parseInt(docs_by_topic[topic][i][0]) == doc)
                    break;
            }
            other_doc_ranks[doc] = i + 1;
            other_docs.push(doc);
        }
        other_docs.sort(function (a, b) {
            return other_doc_ranks[a] - other_doc_ranks[b]
                || a - b;
        });
        for (var i = 0; i < other_docs.length; i++) {
            var doc = other_docs[i];
            if (other_doc_ranks[doc] == ndocs + 1) {
                html.push("<tr><td>n/a. ");
            } else {
                var rank = other_doc_ranks[doc];
                if (rank > last_rank + 1)
                    html.push("<tr><td>...</td></tr><tr><td>");
                else
                    html.push("<tr><td>");
                last_rank = rank;
                html.push(rank + ". ");
            }
            if (doc == parseInt(this_doc))
                html.push("<a href='" + ("00" + doc).slice(-3)
                          + ".html?heading" + heading + "' style='color:red'>"
                          + doc + "</a>");
            else
                html.push("<a href='" + ("00" + doc).slice(-3) + ".html?heading"
                          + heading + "'>" + doc + "</a>");
            html.push("</td><td>yes</td></tr>");
        }
        html.push("</table>");
        $("#match-details-area").html(html.join(""));
    }
    for (var i = 0; i < matches.length; i++) {
        var topic = matches[i][0];
        $("#topic-sel-" + topic)
            .click((function (topic, coef) {
                        return function () {
                            select_topic(topic, coef);
                        }
                    })(topic, matches[i][1]));
    }
    select_topic(matches[0][0], matches[0]);

    var popup_width = popup.width();
    if (current_popup === null)
        popup.css("width", 30); // Start out small for the animation.

    if (!fixed) {
        // Figure out where to position the popup.
        var rownum = $("#text-table > tbody").children()
            .index($("#" + heading).parent().parent());
        if (rownum == -1)
            rownum = $("#text-table > tbody").children()
                .index($("#" + heading).parent());
        var nrows = $("#text-table .text-line").length 
            || $("#text-table .index-entry").length;
        var yoffset = total_height * rownum / nrows;

        // Figure out where to position the notch on the left.
        var notch_offset;
        if (notch_pos == 'center') {
            yoffset -= $("#popup-content").height() / 2;
            if (yoffset < 0)
                yoffset = 0;
            popup.css("top", yoffset);
            if (yoffset == 0)
                notch_offset = (total_height * (rownum + 0.5) / nrows
                                - $("#popup-area").height() - 15);
            else
                notch_offset = -($("#popup-area").height() / 2) - 15;
        } else if (notch_pos == 'top') {
            yoffset -= 30;
            if (yoffset < 0)
                yoffset = 0;
            popup.css("top", yoffset);
            if (yoffset == 0)
                notch_offset = (total_height * (rownum + 0.5) / nrows
                                - $("#popup-area").height() - 15);
            else
                notch_offset = -$("#popup-content").height() + 30 - 15;
            if (notch_offset + $("#popup-content").height() < 15) {
                // The notch is at the edge.  Don't round this corner.
                $("#popup-content").css("-moz-border-top-left-radius", 0)
                    .css("-webkit-border-top-left-radius", 0)
                    .css("-khtml-border-top-left-radius", 0)
                    .css("border-top-left-radius", 0);
            }
        }

        $("<img src='notch-left.png'></img>")
            .css("position", "relative")
            .css("left", -14)
            .css("top", notch_offset)
            .appendTo("#popup");

        if (notch_pos == 'center') {
            // Auto-scroll so that the popup is as fully on-screen as possible.
            var sel = ($.browser['msie'] || $.browser['mozilla'])? "html": "body";
            if (center) {
                // Scroll so that the popup is centered.
                $(sel).scrollTop(Math.max($("#popup-content").offset().top
                                          + $("#popup-content").height() / 2
                                          - $(window).height() / 2,
                                          0))
            } else if ($(sel).scrollTop() > $("#popup-content").offset().top - 100) {
                $(sel).animate({
                    scrollTop: $("#popup-content").offset().top - 100
                }, 400);
            } else if ($(sel).scrollTop() + $(window).height()
                < $("#popup-content").offset().top + $("#popup-content").height() + 30) {
                $(sel).animate({
                    scrollTop: $("#popup-content").offset().top
                        + $("#popup-content").height() - $(window).height() + 30
                }, 400);
            }
        }
    } else {
        // Set up a fixed-position popup.
        var popup_height = popup.height();
        var max_height = $(window).height() - 210;
        if (popup_height > max_height) {
            $("#popup-content").css("height", max_height)
                .css("overflow-y", "scroll");
        }

        $("#popup-content").css("position", "fixed");
        $("#popup-content").css("top", 80);
    }

    if (current_popup === null)
        popup.animate({"width": popup_width}, duration=150);
    else
        popup.css("width", popup_width);

    $("#popup").mouseup(function () {return false;});
        
    current_popup = heading;
    current_popup_full = full;
}


var current_explanation = null;
var current_explanation_has_density_fcn = false;

function explain_topic(topic)
{
    if (topic == current_explanation) return;

    $(".marginal-link a").css("color", "");
    $("#" + topic + " a").css("color", "red");

    $(".explanation-link").css("color", "");
    $(".heading-link").css("color", "");
    $("#explanation-link" + topic).css("color", "red");

    $('[class^="topic"]').css("background-color", "");
    $(".topic" + topic).css("background-color", "red");
    
    // CUSTOM: set prev and next links to keep this explanation open.
    if ($("#next-link").length) {
        var next_href = $("#next-link").attr("href").split("?")[0];
        $("#next-link").attr("href", next_href + "?explain" + topic);
    }
    if ($("#prev-link").length) {
        var prev_href = $("#prev-link").attr("href").split("?")[0];
        $("#prev-link").attr("href", prev_href + "?explain" + topic);
    }
    
    var canvas = $("#chart");
    var density_fcn = density_fcns[topic];
    var density_max = 0.0;

    if (density_fcn) {
                for (var i = 0; i < density_fcn.length; i++) {
                        if (density_fcn[i] > density_max) {
                                density_max = density_fcn[i];
                        }
                }

                if (current_explanation === null
                        || !current_explanation_has_density_fcn)
                        $("#chart-area").css("width", 10);

                var w = 100,
                        h = $("#chart-cell").height(),
                        x = pv.Scale.linear(0, density_max).range(0, w - 5),
                        y = pv.Scale.linear(-0.5, density_fcn.length - 0.5).range(h, 0);

                var vis = new pv.Panel()
                        .canvas("chart")
                        .width(w)
                        .height(h);

                vis.add(pv.Area)
                        .data(density_fcn)
                        .left(0)
                        .width(function (d) {return x(d)})
                        .bottom(function (d) {return y(this.index)})
                        .fillStyle("#fee")
                  .anchor("right").add(pv.Line)
                        .lineWidth(2)
                        .strokeStyle("red");

                vis.render();

                // Don't animate if there's already a chart visible.
                if (current_explanation === null
                        || !current_explanation_has_density_fcn) {
                        $("#chart-area").animate({"width": 100}, duration=15,
                                                 complete=(function (topic) {
                                                 return function () {
                                                         _show_popup(topic, true, true);
                                                 }
                                                 })(topic));
                } else {
                        _show_popup(topic, true, true);
                }
    } else {
                // No density function available.
                if (current_explanation !== null
                        && current_explanation_has_density_fcn) {
                        $("#chart-area").animate({"width": 10}, duration=150,
                                                 complete=(function (topic) {
                                                 return function () {
                                                         _show_popup(topic, true, true);
                                                         $("#chart").html('');
                                                         $("#chart-area").css("width", null);
                                                 }
                                                 })(topic));
                } else {
                        _show_popup(topic, true, true);
                }
    }

    $(document).unbind("mouseup");
    $(document).one("mouseup", hide_explanation_and_popup);

    current_explanation = topic;
    current_explanation_has_density_fcn = !!density_fcn;
}

// CUSTOM
function explain_heading(heading)
{
    if (heading == current_explanation) return;

    $(".marginal-link a").css("color", "");

    $(".explanation-link").css("color", "");
    $(".heading-link").css("color", "");
    $("#heading-link" + heading.replace(/ /g, '_')).css("color", "red");

    $('[class^="topic"]').css("background-color", "");

    if (current_explanation !== null
        && current_explanation_has_density_fcn) {
        $("#chart-area").animate({"width": 10}, duration=150,
                                 complete=(function (heading) {
                                     return function () {
                                         _show_heading_popup(heading, true, true);
                                         $("#chart").html('');
                                         $("#chart-area").css("width", null);
                                     }
                                 })(heading));
    } else {
        _show_heading_popup(heading, true, true);
    }

    $(document).unbind("mouseup");
    $(document).one("mouseup", hide_explanation_and_popup);

    current_explanation = heading;
    current_explanation_has_density_fcn = false;
}

function hide_explanation()
{
    if (current_explanation === null)
        return;
    $("#chart-area").animate({"width": 10}, duration=150,
                             complete=function () {
                                 $(".explanation-link").css("color", "");
                                 $(".heading-link").css("color", "");
                                 $('[class^="topic"]').css("background-color", "");
                                 $("#chart").html('');
                                 $("#chart-area").css("width", null);
                                 // CUSTOM: reset next and prev links
                                 if ($("#next-link").length) {
                                         var next_href = $("#next-link").attr("href").split("?")[0];
                                         $("#next-link").attr("href", next_href);
                                     }
                                 if ($("#prev-link").length) {
                                         var prev_href = $("#prev-link").attr("href").split("?")[0];
                                         $("#prev-link").attr("href", prev_href);
                                     }
                                 current_explanation = null;
                             });
}

function hide_explanation_quick()
{
    $(".explanation-link").css("color", "");
    $(".heading-link").css("color", "");
    $('[class^="topic"]').css("background-color", "");
    $("#chart").html('');
    $("#chart-area").css("width", null);
    // CUSTOM: reset next and prev links
    if ($("#next-link").length) {
        var next_href = $("#next-link").attr("href").split("?")[0];
        $("#next-link").attr("href", next_href);
    }
    if ($("#pref-link").length) {
        var prev_href = $("#prev-link").attr("href").split("?")[0];
        $("#prev-link").attr("href", prev_href);
    }
    current_explanation = null;
}

function hide_explanation_and_popup()
{
    hide_popup();
    hide_explanation_quick();
}

// CUSTOM
function draw_matches()
{
    var nrows = $("#text-table tr").length - 1;

    var matches = [];
    for (topic in topic_matches) {
        for (var i = 0; i < topic_matches[topic].length; i++) {
            var match = topic_matches[topic][i];
            if (match[1] < 0.20) continue;
            matches.push([parseInt(topic),
                          matched_headings.indexOf(match[0]),
                          match[1]]);
        }
    }

    var w = 100,
        h = $("#match-cell").height(),
        x = pv.Scale.linear(0, 1).range(0, w),
        y = pv.Scale.linear(-0.5, nrows - 0.5).range(5, h + 5),
        a = pv.Scale.linear(0.2, 0.35).range(0.25, 1.0);

    var vis = new pv.Panel()
        .canvas("match-area")
        .width(w)
        .height(h);

    vis.add(pv.Panel)
        .data(matches)
      .add(pv.Line)
        .data([0, 1])
        .left(x)
        .top(function (d, match) {
            if (d == 1) {
                return y(match[0]);
            } else {
                return y(match[1]);
            }
        })
        .lineWidth(2)
        .strokeStyle(function (d, match) {
            return "rgba(255,0,0," + a(match[2]) + ")"
        });

    vis.render();
}
