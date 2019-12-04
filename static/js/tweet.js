function Tweet(data) {
    this.id = ko.observable(data.id);
    this.username = ko.observable(data.tweetedby);
    this.body = ko.observable(data.body);
    this.timestamp = ko.observable(data.timestamp);
}

function UserListViewModel() {
    var self = this;
    self.tweets_list = ko.observableArray([]);
    self.username = ko.observable();
    self.body = ko.observable();
    self.timestamp = ko.observable();
    
    self.addTweet = function () {
        self.save();
        self.username('');
        self.body('');
    };

    $.getJSON('/api/v1/tweets', function(userModels) {
        var t = $.map(userModels.tweets_list, function (item) {
            return new Tweet(item);
        });
        self.tweets_list(t);
    });

    self.save = function () {
        return $.ajax({
            url: '/api/v1/tweets',
            contentType: 'application/json',
            type: 'POST',
            data: JSON.stringify({
                'username': self.username(),
                'body': self.body()
            }),
            success: function(data) {
                alert('success');
                self.tweets_list.push(new Tweet({ username: data.username,body: data.body}));
                return;
            },
            error: function() {
                return console.log('Falied');
            }
        });
    };
}

ko.applyBindings(new UserListViewModel());
