Handlebars.registerHelper('slugify', function(text) {
    text = Handlebars.Utils.escapeExpression(text);
    text = text.replace(/\s+/g, '-').toLowerCase();
    return new Handlebars.SafeString(text);
});
Handlebars.registerHelper('default', function(value, defaultValue) {
  return value == null
    ? defaultValue
    : value;
});
Handlebars.registerHelper("formatDateTime", function(timestamp, format) {
    timestamp = moment(timestamp);
    return timestamp.format(format);
});
Handlebars.registerHelper("timeSince", function(then) {
    var then = moment(then);
    var now = moment(new Date());
    return moment.duration(now.diff(then)).humanize()
});
Handlebars.registerHelper("timeDiff", function(a,b) {
    var a = moment(a);
    var b = moment(b);
    return moment.duration(a.diff(b)).humanize()
});
Handlebars.registerHelper('compare', function (lvalue, operator, rvalue, options) {
    // Source: http://doginthehat.com.au/2012/02/comparison-block-helper-for-handlebars-templates/#comment-44
    var operators, result;

    if (arguments.length < 3) {
        throw new Error("Handlerbars Helper 'compare' needs 2 parameters");
    }

    if (options === undefined) {
        options = rvalue;
        rvalue = operator;
        operator = "===";
    }

    operators = {
        '==': function (l, r) { return l == r; },
        '===': function (l, r) { return l === r; },
        '!=': function (l, r) { return l != r; },
        '!==': function (l, r) { return l !== r; },
        '<': function (l, r) { return l < r; },
        '>': function (l, r) { return l > r; },
        '<=': function (l, r) { return l <= r; },
        '>=': function (l, r) { return l >= r; },
        'typeof': function (l, r) { return typeof l == r; }
    };

    if (!operators[operator]) {
        throw new Error("Handlerbars Helper 'compare' doesn't know the operator " + operator);
    }

    result = operators[operator](lvalue, rvalue);

    if (result) {
        return options.fn(this);
    } else {
        return options.inverse(this);
    }

});

function update_appointment_status(appointment_id, status){
    $.ajax({
        url: AJAX_UPDATE_APPOINTMENT_VIEW_URL,
        method: 'PUT',
        data: {'appointment': appointment_id, 'status': status}
    }).done(function(data){
        var html = assignment_template(data);
        $('[data-appointment-id='+appointment_id+']').replaceWith(html);
    });
}

function reload(){
    $('#refresh-button').prop('disabled','disabled');
    $('#refresh-button i').show();
    load_appointments().done(function(){
        $('#refresh-button').prop('disabled',false);
        $('#refresh-button i').hide();
    });
}

function load_appointments(){
    return $.ajax({
        url: AJAX_GET_APPOINTMENTS_URL,
    }).done(function(data){
        var results = data['results'];
        var appointment_html = "";
        appointment_html += "<button id='refresh-button' class='pull-right btn btn-default' onclick='reload();'><i class='fa fa-cog fa-spin fa-fw'></i> Refresh</button>";
        appointment_html += "<h3>Appointments:</h3><hr>";
        if(results.length > 0){
            for(var i=0; i<results.length; i++){
                var appointment = results[i];
                var html = assignment_template(appointment);
                appointment_html += html;
            }
        }
        else{
            appointment_html = "No appointments."
        }
        $('#appointment-row').html(appointment_html);
    });
}

$(document).ready(function(){
    assignment_template =  Handlebars.compile($("#appointment-template").html());
    $('#appointment-row').masonry();
    reload();
});