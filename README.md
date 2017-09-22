# The "Ideal Solution"

## Preface

With regards to what is considered an ideal solution, there is no real clear answer. Some may argue readability is key while others will argue that modularity is paramount. Ideally, we'd like to strive for both, but in the process of modularizing parts of the code base into separate files, readability is sacrificed (in general modularized code is less beginner friendly).

With this solution, I aimed to provide the best of both worlds, while also mirroring (to some extent) the structure of our flask based projects. I initially start out with a non-ideal solution and work towards the final version in this repository (because after all, reworking your code is a cornerstone of software development). 

With that in mind, let's get started.

## Section 0: Problem Review & Description  

So the writeup should provide some detail about how to approach the problem, but let's break it down into its technical components. 

#### Basics

At the basic level we want to make a web interface that allows a user to navigate through a maze (which they can't see) and is located on a server in "the cloud". At the end of said maze, they'll get a link to a youtube video containing something. Additionally, we'd like for the application to store the previous moves a user has made and display them to the user. If the user decides to close the page for some reason (i.e. they were having way too much fun with this application), they should be able to reload the website and have their previous moves displayed to them.

Cool beans, moving on.

#### The Technical Flow

This section is going to get a bit weird. Some of the terms I mention will assume that you understand the concepts mentioned in bootcamp. If you do not understand something or are unclear on anything * DO NOT WAIT * and contact the Hack4Impact member nearest you. I am also available via slack @abhisuri97 for unhealthy periods of time (from 8AM to 3AM). I'm also available via fb messenger, email, and carrier pigeon (but please give advance notice if you plan to use that option). 

Moving on...

When a person visits our website (lets call it h4imaze.com), they'll be served a page that will contain their previous moves if any. These moves will contain the x, y coordinate of the starting position, the direction the person turned, and whether that move was valid or not.

e.g. If I make a move from (0,0) to the right I should see an entry like 

```
"You started at 0,0 and moved to the right. This move was valid".
```

I should clarify that a valid move doesn't mean a move that's along the right path, it just means that that moving from (referring to the above example) 0,0 1 space to the right (going to 1,0 as a result), does not run the user into a wall. After I know the move is valid, I can then move somewhere else starting at 1,0 (or whatever your new position is). If the move I made from 0,0 was invalid, my next move would need to start at 0,0 since there are no ways to move into a wall (unless you are at platform 9 and 3/4...but we will assume you are a muggle for the moment). 

##### Brief Interlude

But what is actually telling us that a move is valid/invalid in the first place? 

Well we have an API (application programming interface) server set up that takes in a x,y position, the direction you want to go and returns a JSON object in the format 

```
{
    validMove: false,
    data: 'EmptyStringHereOrSomeOtherContent'
}
```

If the validMove parameter is true, then you can update your position, if it is false...well you can't still update your position,  but you'd be stuck in a wall and any direction you go to would result in you being "locked in". If the validMove is true and data is not an empty string, then you have the youtube video link as the data parameter and you're done.

##### Back to business

So let's clarify the whole flow from the perspective of a user.

1. Visit h4imaze.com and present them with a page that contains buttons for directions as well as the previous moves they made (which can be done by querying our database). 
2. When a user clicks on these buttons, we want to send a request to the API server (either directly throug the frontend of our website or indirectly through the backend) and update the position accordingly on the page.
3. Additionally, when someone makes a new move, it should be dynamically updated on the page as well. 
4. Each time a move is made, it should be entered into a database. This database record should contain the x,y position, the direction, and the validity of the move. 
5. Once a user solves the maze, display the youtube link to them.

With that let's get started at the first step.

## Section 1: Project Setup & First Steps

First of all, create a folder and run git init to create a github repository. Also create a virtual environment with `virtualenv venv -p  python3` (you can replace `venv` with whatever you want the environment folder to have, also install python3 if you haven't with `brew install python3`). From here, run `source venv/bin/activate` to activate the virtualenv (which will allow you to have an isolated python3 installation running on your system). Also install `Flask` with `pip install Flask`. Flask will handle our webserver logic. 

First we are going to approach the project by doing everything in a single file. After that, we'll modularize it to the final state. 

Begin by creating a file `app.py` under your main directory. In that file, paste the following.

```python
from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run()
```

Next, create a separate folder named `templates` under your main directory and add a file called `index.html` in it. Within index.html put the following code.

```html
<html>
    <head>
        <title>Hi there</title>
    </head>
    <body>
        <h1>Hi</h1>
    </body>
</html>
```

Run  `python app.py` and you should see a page saying `Hi` when accessing `localhost:5000` in your web browser.

Really exciting right? But what the flip is happening here? 

Okay in app.py, we are importing `Flask` and `render_template` from `flask`. Flask allows us to create a web server in the first place which we definitely need in the first place. We instantiate the server with `Flask(__name__)` which scopes the server to the current module (which is going to be our whole application...don't worry about it). We assign this new flask instance to a variable `app` which will now old a reference to the new flask instance. 

We then add a `route` to our application from lines 5-7 which will allow us to listen for requests to the app at the `/` route and then execute a method `index()` which will return a rendered template (i.e. a page) called `index.html`. When we create the flask application, we implicityly  specify that the application will serve template pages out of the `templates` folder. So when a request to `localhost:5000/` is made, it will hit the `/` route, execute the `index` method and return the rendered template (page) in `template/index.html`.

Now that's actually exciting. 

But we are nowhere close to done. 

## Section 2: Setting up a Database Model

So now that we know how to set up a route and serve a page, we should give some through to how to actually display previous moves in a database (and access those moves).  

We are going to begin by creating a database model in our application. 

This database model will be storing many Coordinate objects. A Coordinate has `x`, `y`, `dir`, and `valid` characteristics (`dir` is direction and `valid` is whether the move is valid or not).

Let's adjust our app.py to the following.

```python 
import os

from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIR, 'app.db')
db = SQLAlchemy(app)


class Coordinate(db.Model):
    __tablename__ = 'coordinates'
    id = db.Column(db.Integer, primary_key=True)
    x = db.Column(db.Integer)
    y = db.Column(db.Integer)
    dir = db.Column(db.String(64))
    valid = db.Column(db.Boolean)

    def __init__(self, x, y, dir, valid):
        self.x = x
        self.y = y
        self.dir = dir
        self.valid = valid

    def __repr__(self):
        return '<Coordinate {},{},{},{}>'.format(self.x, self.y,
                                                 self.dir, self.valid)

# ... rest of file is the same
```

You will also need to run `pip install Flask-SQLAlchemy` to make sure this runs (which means you need to quit the terminal process, pip install, and restart it).

But wait! Just laying out the database knowledge doesn't mean that you'll actually you've created it yet!

Run `python` from the command line and do the following commands (`>>>` indicates a new line).

```bash
>>> from app import db
>>> db.create_all()
>>> from app import Coordinate
>>> c1 = Coordinate(0,0,'right',True)
>>> db.session.add(c1)
>>> db.session.commit()
>>> Coordinate.query.all()
# we expect something like [<Coordinate 0,0,right,True>] to be printed out here
```

So now your application database is located in the main directory and is called `app.db`. But wait...what just happened. 

So we are specifying the logic for creating our database. The first thing we do is `import os` which allows us to specify a `BASE_DIR` constant which contains the current directory we are in. After we instantiate the flask app, we specify a configuration variable called `SQLALCHEMY_DATABASE_URI` that contains a sqllite url on the local file system to create a database file `app.db` in the current directory (using `os.path.join(BASE_DIR, 'app.db')`). We then assign `db` to refer to SQLALchemy instance wrapped around the main `app`. 

the `class Coordinate(db.Model)` allows us to specify the logic of our Coordinate model. Every time we want to add a new Coordinate, we must create a model through this class which inherits from `db.Model`. We first specify a tablename `coordinates` and specify an `id` column which will be the primary_key and auto incrementing (by definition of a primary_key). Next we specify that `x` and `y` must both be integer, the `dir` (i.e. direction) must be a string, and `valid` is a boolean. We then specify an `__init__` function which is a constructor which takes in `x,y,dir,valid` args. Lastly we make a `__repr__` method which is used for SQLAlchemy to print a string representation of a coordinate. 

In the command line stuff, we import the `db` variable which contains the SQLAlchemy wrapped application. We then create a database with `db.create_all()` which will look for all classes that inherit from `db.Model` and create a database table for them. Next we import the `Coordinate` class, and create a `c1` instance of it. The important thing to note about the next couple of lines is that we add this `c1` instance to a `db.session` and then `commit()` the session. Any changes we make to our database should be added and the committed (which is a great way to handle adding and modifying the database bc nothing is added until it is all good to go and there aren't any app crashes preventing it from doing so). Next, to check we are sane, we just query the Coordinate model for all its records and sure enough we find the string representation of our `c1` instance.

Now we need to use it.

## Section 3: Rendering a page and pulling from the database

Next, let's take a look at displaying previous database entries on the page when a user loads the page. 

This will involve a couple of changes. The first change is that we need to query the database for all Coordinates before we return a page to the user. Then we need to pass that resulting array of Coordinate objects to the page we render and iterate through the array to display it. So let's get started.

We already saw earlier how to query for Coordinate objects, so let's just adjust our route logic accordingly.

```python 
# ... previous stuff
@app.route('/')
def index():
    coors = Coordinate.query.order_by(Coordinate.id.desc()).all()
    return render_template('index.html', coors=coors)
# ... ending stuff
```

Let's just go over what is happening here. When a user visits `localhost:5000/` the `index()` method will run. We create a `coors` variable which contains the Coordinates in our database model ordered by their `id` in a descending order (greatest id first). This means that we will be seeing coordinates most recent to oldest. Then we render the template and pass a variable `coors` )with the `coors` value we assigned earlier) into the template file `index.html`.

Next in `index.html` include the following logic.

```html
<html>
    <head>
        <title>Hi there</title>
    </head>
    <body>
        <h1>Hi</h1>
        <div id="prevCoors">
            {% for c in coors %}
                <p>You moved from {{c.x}},{{c.y}} in the direction {{c.dir}} - This move is {{c.valid}}</p>
            {% endfor %}
        </div>
    </body>
</html>
```

So this is a bit weird and not regular HTML. Recall earlier we said that `render_template` basically served a page to the user, well that was an over simplification. When render_template is called on a file (say `index.html`), the file is passed through a `Jinja` renderer which will go through the file, look for jinja syntax (i.e. the stuff like `{% for foo in bar %}` `{{ foo.baz }}`, and `{% endfor %}`) and evaluate those expressions into HTML. It also makes available to the Jinja renderer any variables we passed with `render_template` 

A closer look at `index.html` would indicate that for each of the coordinates `c` in `coor` we are making a `<p>` element that is formatted to say something like `You moved from X_POSITION_HERE, Y_POSITION_HERE in the direction DIRECTION_HERE - This move is VALIDITY_BOOLEAN_HERE`.

Let's also add another coordinate into our database to demonstrate the ordering of coordinates. Bring up a python shell.

```bash
>>> from app import Coordinate, db
>>> c2 = Coordinate(0,1,'left',False)
>>> db.session.add(c2)
>>> db.session.commit()
```

Let's rerun the application.  

If all goes well you should see something like

```html
<html>
    <head>
        <title>Hi there</title>
    </head>
    <body>
        <h1>Hi</h1>
        <div id="prevCoors">
            
                <p>You moved from 0,1 in the direction left - This move is False</p>
            
                <p>You moved from 0,0 in the direction right - This move is True</p>
            
        </div>
    </body>
</html>
```

when you look at the page source (by right clicking).

Now let's get to the nitty gritty of adjusting our routes to add records to our Coordinates database and query the main API server to see if moves are valid.

## Section 4: Route params and Coordinate checking

Now we need to start thinking about how we are going to communicate with this API server that we have and save the moves we make along the way. One way to do this would be to do AJAX requests on the frontend to the API Server url and then send a separate AJAX request to our server to a route which will then update our database. This is a valid solution; however, it does put a lot of reliance upon the frontend to handle requests and changes. Plus it means that we need to create two methods on our backend to handle the two different requests.

I propose that we instead create a new route on the backend called `walk` that takes in `x`, `y`, and the `direction` you want to go to. We then read these parameters, make a request to the API, get the response, and then create + save a Coordinate object to our database. At the end, we return the result of the query to our frontend.

Let's see what this new route will look like.

```python
# ... old stuff
from flask import Flask, render_template, jsonify
import requests
import json

app = Flask(__name__)
app.config['QUERY_URL'] = 'http://h4ibootcamp2k17.herokuapp.com'
# ... other stuff 

@app.route("/")
def index():
    coors = Coordinate.query.order_by(Coordinate.id.desc())
    return render_template('index.html', coors=coors)


@app.route("/walk/<x>/<y>/<dir>")
def walk(x, y, dir):
    query = requests.get(app.config['QUERY_URL'] +
                         '/{}/{}/{}'.format(x, y, dir))
    result = json.loads(query.content)
    new_coordinate = Coordinate(x, y, dir, result['validMove'])
    db.session.add(new_coordinate)
    db.session.commit()
    return jsonify(result)

# ... end of file stuff
```

for the `/walk/<x>/<y>/<dir>` route, the parameters we specify are `x`,`y`,`dir` and correspond to the method `walk(x,y,dir)` parameters. We then initiate a `requests.get` reqest with the python library `requests`. The `request.get` function accepts a URL to send the request to. In this case, it would be the API server URL concatenated with the parameters specified in the writeup. E.g. a request would be

```
# URL to GET
http://h4ibootcamp2k17.herokuapp.com/0/1/right

# Returns
{"validMove":false,"data":""}

```

We then store this result (well...the JSON result is actually in `query.content`) in `query` and use `json.loads(query.content)` to convert the returned string into a JSON object which we can then parse with python as a hash. 

Next, we create a new Coordinate object with the x, y, and direction paramters we passed in, as well as the validMove key of the resulting json object we got from the request to our API Server. We then add and commit this new object to database memory and return to the user the result in a json format with the `jsonify` module in `flask` lib (so we can parse it later on with javascript). 

Before we rerun our server we will need to do `pip install requests`. Then we we can access `localhost:5000/` which will return the original HTML we had in the previous step since we didn't add new database records.

When we visit `localhost:5000/walk/1/0/up` we get the following returned:

```html
{
  "data": "", 
  "validMove": true
}
```

If all goes well, this means that we should see the new coordinate in our list when we reload the main `/` route.

```html
<html>
    <head>
        <title>Hi there</title>
    </head>
    <body>
        <h1>Hi</h1>
        <div id="prevCoors">
            
                <p>You moved from 1,0 in the direction up - This move is True</p>
            
                <p>You moved from 0,1 in the direction left - This move is False</p>
            
                <p>You moved from 0,0 in the direction right - This move is True</p>
            
        </div>
    </body>
</html>
```

Yay it works! But we aren't done yet...


## Section 5: Dynamic Requests with AJAX & Frontend JS

Currently, when a user wants to make a move on the map, they need to make a request to `localhost:5000/walk/xCoordinateHere/yCoordinateHere/directionHere` and then go to `localhost:5000` to see their previous moves...

This really sucks.

Now let's focus a bit on improving this experience. Ideally we'd have some buttons with directions on the `localhost:5000` page. When a user initially loads a page, we'll figure out some way to get their most recent x, y position (or set it to 0, 0 if there is no previous position). When a user clicks on a button, we should then send a request to our `walk/x/y/dir` route with the x and y coordinates as well as the direction from the button click. We want this request to run in the background and not trigger a page reload (to optimze the user experience). When the request to our `walk` route returns the result in JSON, we want to add it to the page so the user can see the result of the move. 

How do we do the "requests in the background"? Well, we can use AJAX requests (asynchronous javascript and XML requests), which allow us to send a request to a URL and handle the results from that request all without having to access separate URLs or reload the page (like what happens when you do a form submission). So let's get started by restructuring our index.html file to the following.

```html
<html>
  <head>
    <title>Maze Runner</title>
  </head>
  <body>
    <h1>Hi there</h1>
    <button id="movement">left</button>
    <button id="movement">right</button>
    <button id="movement">up</button>
    <button id="movement">down</button>
    <div id="prevCoors">
      {% for c in coors %}
      <p>You moved from {{c.x}},{{c.y}} in the direction {{c.dir}} - This move is {{c.valid}}</p>
      {% endfor %}
    </div>


  </body>

  <script src="{{ url_for('static', filename='scripts/jquery-3.2.1.min.js') }}"></script>
  <script src="{{ url_for('static', filename='scripts/main.js') }}"></script>
  <script>
    window.x = {{ coors[0].x if coors[0] else 0 }}
    window.y = {{ coors[0].y if coors[0] else 0 }}
  </script>

</html>
```

So there are quite a few new aspects of this page. First of all we have added 4 new movement buttons (and changed the title as well). The buttons have ids of `movement` which we will use to refer to them later on (note we also added an id to the div containing previous coordinates) At the bottom of the page we have some new scripts. The first script will import jQuery into our page (which will allow us to manipulate the page with javascript more easily). The second script will contain the logic for doing an AJAX request and updating the page. The last script serves the purpose of initializing the variables `window.x` and `window.y` based on the coordinate array passed in (if there is something at `coors[0]` set the variable to the corresponding `x` or `y` otherwise just set it to 0). Also note that we use `window.variableName` so the variable is accessible to all scripts running on the page (which is more relevant when we want to access thoses variables in `main.js`).

Note the jinja syntax `{{ url_for('static', filename="..." ) }}`. This is a departure from the regular `{{ url_for('route.method', query_param1='foo' query_param2='bar') }}` syntax seen with jinja normally (note that `url_for` will just return the corresponding full  URL for the page e.g. `{{ url_for('app.walk'), x=1, y=2, dir='right' }}` will evaluate as `http://localhost:5000/walk/1/2/right`). Jinja create a `static` route behind the scenes that takes in a single query parameter containing the path to the file you want to load relative to a `static` directory under your main application.

That being said, we need to add these files to our application. Under the main folder, create a folder called `static`. In this folder, create another folder called `scripts` and [download jQuery](https://code.jquery.com/jquery-3.2.1.min.js) to the `static/scripts` directory. In the same directory, also create a file called `main.js`. 

Right now, including these files in your page won't do much. But if you reload your page and go to the console (right click > Inspect Element > Look for the console tab)
and type 

```js
$('body').text()
```

it should print out the entire text of the page (use of `$` means that you are using `jQuery`). This line finds the html element identified by the `<body>` tag and gets the text of it using the method `.text()`. 

Now, let's do some stuff with javascript. In `main.js` paste the following.

```js
$(document).ready(function() {

  var x = window.x;
  var y = window.y;
  var dir = '';

  $('button#movement').on('click', function(e) {
    e.preventDefault();
    var dir = $(this).text();
    sendRequest(x, y, dir);
  })

  var sendRequest = function(x,y,dir) {
    $.ajax({
      type: "POST",
      url: "/walk/" + x + "/" + y + "/" + dir,
      data: "",
      success: function(result) {
        handleResult(result, dir);
      },
    });
  }

  var handleResult = function(result, dir) {
    if (result.validMove === true) {
      switch (dir) {
        case 'left':
          x--;
          break;
        case 'up':
          y++;
          break;
        case 'right':
          x++;
          break;
        case 'down':
          y--;
          break;
        default:
      }
    }
    $('#prevCoors').prepend('<p> You moved from ' + x + ', ' + y + ' in the direction ' + 
        dir + ' - This move is ' + result.validMove + '</p>');

    if (result.data.length > 0) {
      $('#prevCoors').prepend('<a href="' + result.data + '"">Click here</a>');
    }
  }
});
```

Let's go through what is happening in this file line(ish) by line. 

```js
$(document).ready(function() { ... })
```

All of the code in this file is wrapped in an anonymous function passed as an argument to `.ready`. As you can probably intuit, this function will be called when the document is ready (in jQuery speak, this means that the document object model _DOM_ has been created and been injected with jquery properties i.e. we can do jquery methods on the DOM). 

```js
var x = window.x;
var y = window.y;
var dir = '';
```

Here we are creating variables `x`, `y`, and `dir` to keep track of the current position and direction we are heading in. We are using the `window.x` and `window.y` variables declared in `index.html` which were initialized to the first value in the coordinates array. But why not just use Jinja syntax here instead? Well, Jinja only works on files that are non static and have been included (with jinja macros) or have been explicitly called to render with `render_template`. Unfortunately, since `main.js` is a `static` file, it does not get jinja processed so all the jinja syntax would just trigger javascript errors (this is why we set global variables in the index.html file i.e. so we can access them in `main.js` without needing jinja at all).

```js
$('button#movement').on('click', function(e) {
    e.preventDefault();
    var dir = $(this).text();
    sendRequest(x, y, dir);
}}
```

This snippet is a bit harder to understand. Recall that for jquery, if you want to select an element by its `id` attribute you prepend `#` to the id (e.g. if I have an element `<p id="foo"></p>`, I can access it with `$('#foo')`). So now we are targeting buttons with the id `movement` (you may ask, can't we just do `$('#movement')`?...unfortunately, if you have multiple elements of the same id, you must use the syntax `$('elem#id')`...at least that's what I know of). On the buttons, we add a `.on` listener that will listen for `click`s. When a `click` on the button occurs, the anonymous function will execute (I pass in a single argument `e` that refers to the event object itself). `e.preventDefault()` prevents the default action of a button (i.e. to reload a page and submit to a URL with a POST request if there is a form element specified). We want to prevent this from  happening so we can do more on the click! Next, we change our `dir` variable to be equal to the text within the button element that was clicked (`$(this)` refers to the current element clicked and `.text()` gets the text within it). Lastly, we call a method `sendRequest` with the `x`, `y` coordinates and the direction.

```js
var sendRequest = function(x,y,dir) {
    $.ajax({
      type: "GET",
      url: "/walk/" + x + "/" + y + "/" + dir,
      data: "",
      success: function(result) {
        handleResult(result, dir);
      },
    });
}
```

`sendRequest` is a function that takes in `x` `y` and `dir` parameters. It then initiates an ajax request with `$.ajax({ configurationObjectHere })` with an object specifying how to do the request. Recall an ajax function asychronously requests a URL i.e. it all happens in the background, no refreshes necessary. We are sending a `POST` request (i.e. we are `GET`ing something from the server...this isn't a huge deal) and are specifying the URL to the route we want to query (in this case an implcit `http://localhost:5000` + `/walk/xparam/yparam/dirparam`). When we get a response back (look at `success`), we must use an anonymous function that takes ONE argument (containing the result). We then call `handleResult` with the result parameter and current direction. Note that the `result` will be in the format

```js
{
  "data": "", 
  "validMove": true
}
```

which is a JSON object. Let's move to `handleResult`

```js
var handleResult = function(result, dir) {
if (result.validMove === true) {
      switch (dir) {
        case 'left':
          x--;
          break;
        case 'up':
          y++;
          break;
        case 'right':
          x++;
          break;
        case 'down':
          y--;
          break;
        default:
      }
    }
    $('#prevCoors').prepend('<p> You moved from ' + x + ', ' + y + ' in the direction ' + dir + ' - This move is ' + result.validMove + '</p>');

    if (result.data.length > 0) {
      $('#prevCoors').prepend('<a href="' + result.data + '"">Click here</a>');
    }
}
```

If the `validMove` key of the `result` object is `true` then we adjust our `main.js` `x` and `y` positions accordingly based off of the direction. So the next time we click a button, it'll be calling everything on a new starting location.

Then we prepend a paragraph element to the `<div>` with `id` `prevCoors` (prepending puts most recent first). If the `data` attribute of `result` has a length `> 0` that means that we have our final video and we prepend it to the same div to display it to the user.

## Section 6: Modularization

So we are technically done now...but nothing is really modularized into its own file on the backend. Basically everything has been compiled into one large `app.py` file. Moreover there are some functions that should be abstracted away and configurations that need to be centralized.

Let's start out by figuring out what should be separated into its own module. For this application it would be the configuration for the app (i.e. SQLAlchemy URL, API URL, DEBUG, etc), the logic for Coorindate database model, and lastly the routes.

So let's modulularize! 

Under the main folder you've been working on, create a folder called `app`. Inside of `app` create a file `__init__.py` and paste teh following.

```python
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
# instantiate flask app
app = Flask(__name__)

app.config.from_object('config')

db = SQLAlchemy(app)

from app.models.coordinates import *
from app.views.routes import *
```

The first three lines are fairly straightforward. The `app.config...` line specifies that we are going to be specifying a config file named `config.py` from which we will get our configuration variables and load them into the app (we'll get to this later on). I also initialize the db object inside this file so it is accessible everywhere in the application. In the last two lines, I import some modules which I will soon define...

Since the application is going to be initialized within the application folder, you need to make sure that `templates` and `static` are on the same level as the initiate file (so move `templates` and `static` into `app`). 

Create two folders `models` and `views`. In both, create `__init__.py` files (note that `__init__.py` establishes a folder as a python module). 

Inside of `modules`, create a file called `coordinates.py` and paste the following

```python
from app import db


class Coordinate(db.Model):
    __tablename__ = 'coordinates'
    id = db.Column(db.Integer, primary_key=True)
    x = db.Column(db.Integer)
    y = db.Column(db.Integer)
    dir = db.Column(db.String(64))
    valid = db.Column(db.Boolean)

    def __init__(self, x, y, dir, valid):
        self.x = x
        self.y = y
        self.dir = dir
        self.valid = valid

    def __repr__(self):
        return '<Coordinate {},{},{},{}>'.format(self.x, self.y,
                                                 self.dir, self.valid)
```

This file just contains the database logic (with just an added import statement). Note that all python packages are imported at the top level by default. 

Inside of `views` create a file called `routes.py`. Paste the following in it

```python
from flask import render_template, jsonify
from app import app, db
from app.models.coordinates import Coordinate

import requests
import json

@app.route("/", methods=["GET", "POST"])
def index():
    coors = Coordinate.query.order_by(Coordinate.id.desc()).all()
    return render_template('index.html', coors=coors)


@app.route("/walk/<x>/<y>/<dir>", methods=["POST"])
def walk(x, y, dir):
    query = requests.get(app.config['QUERY_URL'] +
                         '/{}/{}/{}'.format(x, y, dir))
    result = json.loads(query.content)
    new_coordinate = Coordinate(x, y, dir, result['validMove'])
    db.session.add(new_coordinate)
    db.session.commit()
    return jsonify(result)
```

This file more or less contains the same code we originally had in the main `app.py` file. The only difference is that we need to import the `Coordinate` model from the module itself (and change the app import) Otherwise, everything is the same! 

Lastly, at the top level, we are going to do a couple of things.

First, we will define a config file that contains some configuration variables in a single place. Create a file `config.py` on the same level as the `app` folder (i.e. not within it, but "next" to it). Paste the following.

```
import os

DEBUG = True

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'app.db')
SQLALCHEMY_TRACK_MODIFICATIONS = False

SECRET_KEY = 'secretshhhh'
QUERY_URL = 'http://h4ibootcamp2k17.herokuapp.com'
```

The variables are fairly straightforward. `DEBUG` dynamically reloads your app if it is true. `SQLALCHEMY_DATABASE_URI` was convered earlier. `SQLALCHEMY_TRACK_MODIFICATION` is used to keep track of every stage of the database before and after commits (we will turn this off because we don't need that level of commits). We also make a `SECRET_KEY` because Flask will require it once we move to production. Lastly, the `QUERY_URL` contains the url for the API server. All of these variables are accessible via the app.config object.

Next, we will create a `manage` file that will contain two commands to run our app.

At the same level as `config.py` create a file `manage.py` and paste the following

```python
from app import app, db
from flask_script import Manager

manager = Manager(app)


@manager.command
def recreate_db():
    db.drop_all()
    db.create_all()
    db.session.commit()

if __name__ == '__main__':
    manager.run()
```

You will also need to run `pip install flask_script`

Manager allows us to make a mini command line interface to run our application. If you create multiple manager commands, they are all accessible via `python manager.py commandNameHere param1 param2...`. Here we are importing our app and db files into the manager and importing Manager itself (which we instantiate with the `app` instance). 

Next we are creating a command `recreate_db` which will allow us to wipe our db and start on a clean slate should we ever need to do so (or just want to look through the maze from the start again). The `recreate_db` method is fairly straightforward (drop all the tables, create all the tables from the logic outlined in the app, and commit the result). 

Lastly, if the manager module is called from the command line, it should be run. Manager also creates an implicit command `runserver` which runs the `app` instance passed into it at port 5000. So doing `python manage.py runserver` will get the app up and running! 

To run the app from scratch run:

```
python manage.py recreate_db
python manage.py runserver
```

## Section 7: Hosting

While sending a link to your friends with `http://localhost:5000` makes you look like a cool hacker, you'll soon realize that this effort to gain notoriety will backfire against you as people get page not available errors...because after all, not many people are running this exact same application on port 5000 of their computer (much to Hack4Impact's dismay). Let's host this on heroku so you have something to actually share. 

Some housekeeping first, run `pip install gunicorn` and `pip install psycopg2` then run

```
pip freeze > requirements.txt
```

This command will save all the requirements to the `requirements.txt` file. You can actually just run `pip install requirements.txt` to install these requirements if you ever need to again. 

Also create a file called `Procfile` and paste the following in

```
web: gunicorn manage:app
```

You don't need to worry about the details, but heroku looks for a `Procfile` when instantiating an app. This basically means create a `web` instance that runs `gunicorn` (a web server handler) with the app in `manage.py`

Next, [create a heroku account on Heroku's website](http://heroku.com), [set up the CLI](https://devcenter.heroku.com/articles/heroku-cli), and log in. Go back to your project directory and run 

```
$ heroku create app-name-here
```

Then create a `.gitignore` file and paste the following in

```
venv
app.db
__pycache__
*.pyc
.DS_Store
```
This will just specify files for git to ignore while it is tracking changes. 

Do `git add .gitignore`, `git commit -m "added gitignore"`. Next `git add .` which will add all the files not in git ignore `git commit -m "initialized app"`. 

Lastly run `git push heroku master` and wait for everything to settle down. When you 

