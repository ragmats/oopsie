#########################
#  Oopsie by Steven Coy #
#  stevencoy@gmail.com  #
#########################

# from re import X
from collections import namedtuple
from flask import Flask, render_template, request, session, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date, timedelta
import pytz

# Configure application
app = Flask(__name__)

# Learned SQLAlchemy from:
    # https://flask-sqlalchemy.palletsprojects.com/en/2.x/
    # https://www.youtube.com/watch?v=hbDRTZarMUw&ab_channel=Codemy.com
    # https://www.youtube.com/watch?v=UK57IHzSh8I&ab_channel=PrettyPrinted
    # https://www.youtube.com/watch?v=cYWiDiIUxQc&t=614s&ab_channel=CoreySchafer
    # https://stackoverflow.com/questions/67428672/how-to-display-specific-user-information-in-a-separate-page-using-flask-and-flas

# Learned datetime from:
    # https://www.youtube.com/watch?v=RjMbCUpvIgw&ab_channel=Socratica
    # https://www.youtube.com/watch?v=eirjjyP2qcQ&ab_channel=CoreySchafer
    # https://stackoverflow.com/questions/29779155/converting-string-yyyy-mm-dd-into-datetime-python

# Learned timezones/pytz from:
    # https://www.youtube.com/watch?v=eirjjyP2qcQ&t=1168s&ab_channel=CoreySchafer

# Learned session cookies from:
    # https://testdriven.io/blog/flask-sessions/

app.secret_key = "NDQc#@5~cgKT)mv2qG<c(B@!"

# Configure Flask session cookies
app.config["SESSION_PERMANENT"] = True
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=10000)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///oopsie.db"

# Initialize the database
db = SQLAlchemy(app)

class Methods(db.Model):
    """Database model"""
    id = db.Column(db.Integer, primary_key=True)
    method = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(20), nullable=False)
    chance = db.Column(db.Float, nullable=False)
    source = db.Column(db.String(100), nullable=False)
    info = db.Column(db.String(350), nullable=False)
    info_source = db.Column(db.String(100), nullable=False)
    source_name = db.Column(db.String(100), nullable=False)
    info_source_name = db.Column(db.String(100), nullable=False)

class Day():
    """Today and relative days"""
    def __init__(self, today):
        self.today = today
        self.tomorrow = today + timedelta(days=1)
        self.yesterday = today - timedelta(days=1)
        self.todayf = today.strftime("%A, %B %d, %Y")
        self.tomorrowf = self.tomorrow.strftime("%m/%d/%Y")
        self.yesterdayf = self.yesterday.strftime("%m/%d/%Y")

class Data():
    """Main method/prevention categories from the database"""
    def __init__(self):
        self.cycle_awareness = Methods.query.filter_by(type="cycle_awareness").order_by(Methods.id).all()
        self.contraception = Methods.query.filter_by(type="contraception").order_by(Methods.id).all()
        self.method = Methods.query.filter_by(type="method").order_by(Methods.id).all()
        self.surgical = Methods.query.filter_by(type="surgical procedure").order_by(Methods.id).all()

class Cycle():
    """Cycle elements"""
    def __init__(self, day):

        if session.get("cycle_start_str"):
            self.cycle_start = get_cycle_start(session.get("cycle_start_str"))
        else:
            self.cycle_start = None

        self.cycle_length = get_cycle_length(session.get("cycle_length"))
        self.period_length = get_period_length(session.get("period_length"))
        self.cycle_day_ovulation = get_cycle_day_ovulation(session.get("cycle_day_ovulation"), self.cycle_length)
        self.cycle_day = get_cycle_day(day.today, self.cycle_start, self.cycle_length)
        self.cycle_day_yesterday = get_cycle_day(day.yesterday, self.cycle_start, self.cycle_length)
        self.cycle_day_tomorrow = get_cycle_day(day.tomorrow, self.cycle_start, self.cycle_length)
        self.next_ovulation = get_next_ovulation(day.today, self.cycle_day, self.cycle_day_ovulation, self.cycle_length)
        self.next_period = get_next_period(day.today, self.cycle_day, self.cycle_length)
        self.period_today = check_period(self.cycle_day, self.period_length)
        self.period_yesterday = check_period(self.cycle_day_yesterday, self.period_length)
        self.period_tomorrow = check_period(self.cycle_day_tomorrow, self.period_length)
        self.ovulation_today = check_ovulation(self.cycle_day, self.cycle_day_ovulation)
        self.ovulation_yesterday = check_ovulation(self.cycle_day_yesterday, self.cycle_day_ovulation)
        self.ovulation_tomorrow = check_ovulation(self.cycle_day_tomorrow, self.cycle_day_ovulation)

        # If rhythm method is selected with a cycle start, calculate rhythm chance
        if session.get("selections") and "21" in session.get("selections") and self.cycle_start:
            self.rhythm_chance = get_rhythm_chance(self.cycle_day, self.cycle_day_ovulation)
            self.rhythm_chance_yesterday = get_rhythm_chance(self.cycle_day_yesterday, self.cycle_day_ovulation)
            self.rhythm_chance_tomorrow = get_rhythm_chance(self.cycle_day_tomorrow, self.cycle_day_ovulation)
        else:
            self.rhythm_chance = None
            self.rhythm_chance_yesterday = None
            self.rhythm_chance_tomorrow = None

class Oopsie():
    """Oopsie chances"""
    def __init__(self):
        if session.get("selections"):
            self.chance_today = get_oopsie(session.get("chances"))
            self.chance_yesterday = get_oopsie(session.get("chances_yesterday"))
            self.chance_tomorrow = get_oopsie(session.get("chances_tomorrow"))
        else:
            self.chance_today = default_oopsie

# Global Oopsie default value
default_oopsie = 3.44643

# make_session_permanent() learned from:
    # https://stackoverflow.com/questions/34118093/flask-permanent-session-where-to-define-them

@app.before_request
def make_session_permanent():
    """Makes session permanent before each request"""
    session.permanent = True


@app.route("/", methods=["GET"])
def index_get():
    """Returns homepage when no selections are remembered in the session or first-time visit"""

    # If no selections are remembered (or first-time visit), set oopsie chance and cycle to default
    if not session.get("selections"):

        #Get oopsie object
        oopsie = Oopsie()

        # Set cycle to None so correct template content loads
        cycle = None

        return render_template("index.html", oopsie=oopsie, cycle=cycle)

    # If selections are remembered in the session, load oopsie chance
    else:

        # Gather frequently used objects (today, day, and cycle) into a named tuple
        object = gather_objects()

        # Get methods object and save chances in session
        methods = get_methods(object)

        #Get oopsie object
        oopsie = Oopsie()

    return render_template("index.html", timezone=session.get("timezone"), day=object.day, oopsie=oopsie, cycle=object.cycle, methods=methods)


@app.route("/", methods=["POST"])
def index_post():
    """Returns homepage when user clicks "Save" from Methods page"""

    # Get user selections & remember in session
    session["selections"] = request.form.getlist("method_selected")
    session["cycle_start_str"] = request.form.get("cycle_start")
    session["cycle_length"] = request.form.get("cycle_length")
    session["period_length"] = request.form.get("period_length")
    session["cycle_day_ovulation"] = request.form.get("cycle_day_ovulation")
    session["timezone"] = request.form.get("timezone")

    # Gather frequently used objects (today, day, and cycle) into a named tuple
    object = gather_objects()

    # If methods were selected on methods page, get methods object and save chances in session
    if session.get("selections"):

        methods = get_methods(object)

    # Set methods to None so template still loads correctly
    else:
        methods = None

    #Get oopsie object
    oopsie = Oopsie()

    # Validate rhythm method inputs and return methods template if there are errors
    if "21" in session.get("selections") and (not session.get("cycle_start_str") or not check_date(session.get("cycle_start_str")) or object.cycle.cycle_length < 1 or object.cycle.period_length < 0 or object.cycle.cycle_day_ovulation < 1 or object.cycle.period_length > object.cycle.cycle_length or object.cycle.cycle_day_ovulation > object.cycle.cycle_length):

        # Create dictionary of rhythm method input errors
        rhythm_errors = {}

        # If cycle/period start is blank and Rhythm Method was selected, send back to Methods page with an error
        if "21" in session.get("selections") and not session.get("cycle_start_str"):
            rhythm_errors["cycle_start_error"] = "Last period start date is required if Rhythm Method is selected."

            # Remove and un-check rhythm method from the selections in case user navigates away from this page
            session.get("selections").remove("21")

        # If date is not a valid date, send back to Methods page with an error
        if not check_date(session.get("cycle_start_str")):
            rhythm_errors["date_error"] = "Please enter a valid date in format YYYY-MM-DD."

        # If cycle length is not greater than zero, send back to Methods page with an error
        if object.cycle.cycle_length != None and object.cycle.cycle_length < 1:
            rhythm_errors["cycle_length_error"] = "Cycle length must be greater than zero."

        # If period length is not greater than zero, send back to Methods page with an error
        if object.cycle.period_length < 0:
            rhythm_errors["period_length_error"] = "Period length can't a be negative number."

        # If cycle length is not greater than zero, send back to Methods page with an error
        if object.cycle.cycle_day_ovulation < 1:
            rhythm_errors["cycle_day_ovulation_error"] = "Cycle day of ovulation must be greater than zero."

        # If period length or cycle day of ovulation are more than the cycle length, send back to Methods page with an error
        if object.cycle.period_length > object.cycle.cycle_length or object.cycle.cycle_day_ovulation > object.cycle.cycle_length:
            rhythm_errors["length_error"] = "Period length and cycle day of ovulation must be within the cycle length."

        # Get data object for methods template
        data = Data()

        return render_template("methods.html", data=data, selections=session.get("selections"), cycle=object.cycle, rhythm_errors=rhythm_errors, timezones=pytz.all_timezones, timezone=session.get("timezone"))

    return render_template("index.html", timezone=session.get("timezone"), day=object.day, oopsie=oopsie, cycle=object.cycle, methods=methods)


@app.route("/methods")
def methods():
    """Returns methods page, where the user selects, saves, or clears method selections"""

    # Set selections if remembered in the session, otherwise set to empty
    if session.get("selections"):
        selections = session.get("selections")
    else:
        selections = []

    # Create instance of Data class
    data = Data()

    # Gather frequently used objects (today, day, and cycle) into a named tuple
    object = gather_objects()

    return render_template("methods.html", data=data, selections=selections, cycle=object.cycle, timezones=pytz.all_timezones, timezone=session.get("timezone"))


@app.route("/clear")
def clear():
    """Clears all data saved in the session and sets timezone to default UTC"""

    session.clear()
    session["timezone"] = "UTC"

    return redirect("/methods")


@app.route("/getlucky")
def getlucky():
    """Returns "Get Lucky" page, where the user simulates business time (intercourse) with today's Oopsie chance"""

    # Gather frequently used objects (today, day, and cycle) into a named tuple
    object = gather_objects()

    # If there is a rhythm chance, in case Get Lucky is reloaded first on a new day, refresh list of chances in the session with updated rhythm chance for today
    if object.cycle.rhythm_chance != None:
        session["chances"] = get_chances(session.get("selections"), object.cycle.rhythm_chance)

    #Get oopsie object
    oopsie = Oopsie()

    return render_template("get_lucky.html", oopsie=oopsie)


@app.route("/weekview")
def weekview():
    """Returns week view page, where the user views Oopsie chances, cycle days, ovulation days, and period days for the previous, current, and next weeks"""

    # Gather frequently used objects (today, day, and cycle) into a named tuple
    object = gather_objects()

    # If rhythm chance is None, disable week view
    if object.cycle.rhythm_chance == None:
        current_week = last_week = next_week = None

    # If selections are remembered in the session, load oopsie chance
    else:

        # Get the most recent Sunday as a starting point for the current week
        sunday = get_sunday(object.today)

        # Get week-view info for current week, last week, and next week
        current_week = get_week(sunday)
        last_week = get_week(sunday - timedelta(days=7))
        next_week = get_week(sunday + timedelta(days=7))

    return render_template("week_view.html", current_week=current_week, last_week=last_week, next_week=next_week, current_day=object.today.day, current_month=object.today.strftime("%B"), current_year=object.today.year)


@app.route("/lastweek")
def lastweek():
    """Returns last week page, where the user views Oopsie chances, cycle days, ovulation days, and period days for the previous week in narrow/mobile view"""

    # Gather frequently used objects (today, day, and cycle) into a named tuple
    object = gather_objects()

    # If rhythm chance is None, disable week view
    if object.cycle.rhythm_chance == None:
        last_week = None

    # If selections are remembered in the session, load oopsie chance
    else:

        # Get the most recent Sunday as a starting point for the current week
        sunday = get_sunday(object.today)

        # Get week-view info for current week, last week, and next week
        last_week = get_week(sunday - timedelta(days=7))

    return render_template("lastweek.html", last_week=last_week, current_day=object.today.day, current_month=object.today.strftime("%B"), current_year=object.today.year)


@app.route("/nextweek")
def nextweek():
    """Returns next week page, where the user views Oopsie chances, cycle days, ovulation days, and period days for the next week in narrow/mobile view"""

    # Gather frequently used objects (today, day, and cycle) into a named tuple
    object = gather_objects()

    # If rhythm chance is None, disable week view
    if object.cycle.rhythm_chance == None:
        next_week = None

    # If selections are remembered in the session, load oopsie chance
    else:

        # Get the most recent Sunday as a starting point for the current week
        sunday = get_sunday(object.today)

        # Get week-view info for current week, last week, and next week
        next_week = get_week(sunday + timedelta(days=7))

    return render_template("nextweek.html", next_week=next_week, current_day=object.today.day, current_month=object.today.strftime("%B"), current_year=object.today.year)


@app.route("/about")
def about():
    """Returns about page, with information about this app"""

    return render_template("about.html")


@app.route("/sources")
def sources():
    """Returns sources page, which lists all sources used in the database"""

    data = Methods.query.order_by(Methods.method).all()

    return render_template("sources.html", data=data)


@app.route("/disclaimer")
def disclaimer():
    """Returns disclaimer page."""

    return render_template("disclaimer.html")


@app.route("/contact")
def contact():
    """Returns contact page."""

    return render_template("contact.html")


def gather_objects():
    """Returns a named tuple of frequently used today, day, and cycle objects"""

    # Get today object with correct timezone and instances of Day and Cycle class
    today = get_today()
    day = Day(today)
    cycle = Cycle(day)

    #Create named tuple
    Object = namedtuple("Objects", ["today", "day", "cycle"])
    object = Object(today, day, cycle)

    return object


def get_today():
    """Sets session timezone to UTC if timezone hasn't been set and returns today object with timezone"""

    if not session.get("timezone"):
        session["timezone"] = "UTC"

    return datetime.now(tz=pytz.UTC).astimezone(pytz.timezone(session.get("timezone"))).date()


def get_methods(object):
    """Returns methods object based on user-selected method IDs and saves chances in the session"""

    # Get rows of methods from database based on user-selected method IDs
    methods = Methods.query.filter(Methods.id.in_(session.get("selections"))).order_by(Methods.method).all()

    # Get list of oopsie chances based on user-selected method IDs
    session["chances"] = get_chances(session.get("selections"), object.cycle.rhythm_chance)
    session["chances_yesterday"] = get_chances(session.get("selections"), object.cycle.rhythm_chance_yesterday)
    session["chances_tomorrow"] = get_chances(session.get("selections"), object.cycle.rhythm_chance_tomorrow)

    return methods


def get_cycle_day(day, cycle_start, cycle_length):
    """Returns the cycle day given cycle start and length"""

    if cycle_start == None or cycle_length == 0:
        return None
    else:
        # If cycle start is in the past...
        if ((day - cycle_start).days) >= 0:
            # If cycle start is more than one cycle away from day...
            if ((day - cycle_start).days + 1) > cycle_length:
                cycle_day = ((day - cycle_start).days) % cycle_length + 1
            # If cycle start is in the same cycle as day...
            else:
                cycle_day = (day - cycle_start).days + 1
            return cycle_day

        # If cycle start is in the future...
        else:
            # If cycle start is more than one cycle away from day...
            if ((day - cycle_start).days * -1) > cycle_length:
                # If duration/cycle length is zero, set cycle day to 1...
                if (((day - cycle_start).days * -1) % cycle_length) == 0:
                    cycle_day = 1
                else:
                    cycle_day = cycle_length - (((day - cycle_start).days * -1) % cycle_length) + 1
            # If cycle start is in the same cycle as day...
            else:
                cycle_day = (day - cycle_start).days + cycle_length + 1
            return cycle_day


def get_next_ovulation(today, cycle_day, cycle_day_ovulation, cycle_length):
    """Returns next ovulation date when cycle day matches cycle day ovulation"""

    if cycle_day == None:
        return None
    else:
        for day in range(cycle_length):
            # If value is within the cycle length
            if cycle_day + day <= cycle_length:
                if cycle_day + day == cycle_day_ovulation:
                    next_ovulation = date.strftime(today + timedelta(days=day), "%m/%d/%y")
                    return next_ovulation

            # If value exceeds cycle length
            else:
                if (cycle_day + day) % cycle_length == cycle_day_ovulation:
                    next_ovulation = date.strftime(today + timedelta(days=day), "%m/%d/%y")
                    return next_ovulation


def get_next_period(today, cycle_day, cycle_length):
    """Returns next period start date given cycle day and length"""

    if cycle_day == None:
        return None
    else:
        # Look for a cycle day 1 within a window of days equal to the cycle length
        for day in range(cycle_length):
            # If value is within the cycle length
            if cycle_day + day <= cycle_length:
                if cycle_day + day == 1:
                    next_period = date.strftime(today + timedelta(days=day), "%m/%d/%y")
                    return next_period
            # If value exceeds cycle length
            else:
                if (cycle_day + day) % cycle_length == 1:
                    next_period = date.strftime(today + timedelta(days=day), "%m/%d/%y")
                    return next_period


def check_date(date_str):
    """Returns True if given date string is a valid date"""

    # Return True if date string is a valid date, but allow for blank input without error
    if date_str:
        try:
            datetime.strptime(date_str, "%Y-%m-%d").date()
            return True
        except ValueError:
            return False
    else:
        return True


def get_cycle_start(cycle_start_session):
    """Returns cycle start as YYYY-MM-DD formatted date if it is saved in the session and a valid date, otherwise return None"""

    # Route check learned from:
        # https://stackoverflow.com/questions/21498694/flask-get-current-route

    # If cycle start date is in session and is a valid date, convert string to datetime
    if cycle_start_session and check_date(cycle_start_session):

        # If function call comes from "/" (index) route
        if str(request.url_rule) == "/":
            if "21" in session.get("selections"):
                cycle_start = datetime.strptime(session.get("cycle_start_str"), "%Y-%m-%d").date()
            else:
                cycle_start = None
        else:
            cycle_start = datetime.strptime(session.get("cycle_start_str"), "%Y-%m-%d").date()
    else:
        cycle_start = None

    return cycle_start


def get_cycle_length(cycle_length_session):
    """Returns cycle length as int if it is saved in the session, otherwise return default (28)"""

    # If cycle length is in session, convert string to int, otherwise set to default (28 days)
    if cycle_length_session:
        cycle_length = int(cycle_length_session)
    else:
        cycle_length = 28
    return cycle_length


def get_period_length(period_length_session):
    """Returns period length as int if it is saved in the session, otherwise return default (5)"""

    # If period length is in session, convert string to int, otherwise set to default (5 days)

    if period_length_session != None and period_length_session != "":
        period_length = int(period_length_session)
    else:
        period_length = 5
    return period_length


def get_cycle_day_ovulation(cycle_day_ovulation_session, cycle_length):
    """Returns ovulation cycle day if it is saved in the session, otherwise return default (cycle_length/2)"""

    # If ovulation cycle day is in session, convert string to int, otherwise default to half of cycle length
    if cycle_day_ovulation_session:
        cycle_day_ovulation = int(cycle_day_ovulation_session)
    else:
        cycle_day_ovulation = round(cycle_length/2)
    return cycle_day_ovulation


def check_period(cycle_day, period_length):
    """Returns True if given cycle day is within the period length"""

    # Return True if cycle is within the period length
    if cycle_day == None:
        return
    else:
        if cycle_day <= period_length:
            return True
        else:
            return False


def check_ovulation(cycle_day, cycle_day_ovulation):
    """Returns True if given cycle day is an ovulation day"""

    # Return True if cycle day is equal to ovulation day
    if cycle_day == cycle_day_ovulation:
        return True
    else:
        return False


def get_rhythm_chance(cycle_day, cycle_day_ovulation):
    """Returns Rhythm Method chance given cycle and ovulation day"""

    # Dictionary of rhythm chances relative to (on, after, and before) ovulation (ovulation = "0")
    rhythm_chances = {
        "-9": .0025,
        "-8": .005,
        "-7": .01,
        "-6": .02,
        "-5": .04,
        "-4": .13,
        "-3": .08,
        "-2": .28,
        "-1": .24,
        "0": .08,
        "1": .04,
        "2": .02,
        "3": .01,
        "4": .005,
        "5": .0025
    }

    rhythm_chance = 0

    # Loop 0 to 5 relative (current/future) days, checking if current cycle day matches cycle day of ovulation, then assign correct rhythm chance value
    # e.g. If current cycle day is 2 days after ovulation (cycle_day == cycle_day_ovulation + 2), assign rhythm chance for key "2" (.02)
    for i in range(6):
        if cycle_day == cycle_day_ovulation + i:
            rhythm_chance = rhythm_chances[str(i)]
            return rhythm_chance

    # Loop 1 to 9 relative (past) days, checking if current cycle day matches cycle day of ovulation, then assign correct rhythm chance value
    # e.g. If current cycle day is 2 days before ovulation (cycle_day == cycle_day_ovulation - 2), assign rhythm chance for key "-2" (.28)
    for i in range(1, 10):
        if cycle_day == cycle_day_ovulation - i:
            rhythm_chance = rhythm_chances[str(i * -1)]
            return rhythm_chance

    return rhythm_chance


def get_chances(selections, rhythm_chance):
    """Returns list of chances based on list of user-selected IDs"""

    chances = []
    for selection in selections:
        selected_rows = Methods.query.filter_by(id=selection).all()
        # If selection is rhythm method (ID = 21) and there is a custom rhythm chance, replace default value with this chance
        if (rhythm_chance or rhythm_chance == 0) and selection == "21":
            chances.append(rhythm_chance)
        else:
            for row in selected_rows:
                chances.append(row.chance)
    return chances


def get_oopsie(chances):
    """Calculates rounded chance of Oopsie pregnancy based on list of user-selected chances"""

    oopsie_chance = 1
    for chance in chances:
        oopsie_chance *= float(chance)
    oopsie_chance *= 100

    # Convert chance to int if not a float
    if round(oopsie_chance, 5) % 1 == 0:
        oopsie_chance = int(oopsie_chance)

    return round(oopsie_chance, 5)


def get_sunday(date):
    """Returns the most recent Sunday, as a date object, given a date object"""

    # If the date isn't Sunday (week day 6), find date of most recent Sunday
    if date.weekday() != 6:
        date -= timedelta(days=date.weekday() + 1)

    return date


def get_week(start_date):
    """Returns a dictionary for a week with week-view data given a starting date"""

    # Gather frequently used objects (today, day, and cycle) into a named tuple
    object = gather_objects()

    # Create empty week dictionary
    week = {}

    # Iterate through each day of week dictionary for 7 days
    for i in range(7):

        # Update cycle object for day i
        object.cycle.cycle_day = get_cycle_day(start_date + timedelta(days=i), object.cycle.cycle_start, object.cycle.cycle_length)
        object.cycle.rhythm_chance = get_rhythm_chance(object.cycle.cycle_day, object.cycle.cycle_day_ovulation)

        # Get list of oopsie chances based on user-selected method IDs
        session["chances"] = get_chances(session.get("selections"), object.cycle.rhythm_chance)

        # Calculate oopsie chance by multiplying chances values
        oopsie_chance = get_oopsie(session.get("chances"))

        week[i + 1] = {
            "day_letter": str((start_date + timedelta(days=i)).strftime("%A"))[0],
            "month_number": (start_date + timedelta(days=i)).month,
            "month_day": (start_date + timedelta(days=i)).day,
            "oopsie_chance": oopsie_chance,
            "cycle_day": object.cycle.cycle_day,
            "period": check_period(object.cycle.cycle_day, object.cycle.period_length),
            "ovulation": check_ovulation(object.cycle.cycle_day, object.cycle.cycle_day_ovulation)
        }

    return week