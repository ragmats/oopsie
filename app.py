#########################
#  Oopsie by Steven Coy #
#  stevencoy@gmail.com  #
#########################

from flask import Flask, render_template, request, session, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date, timedelta

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

# Learned session cookies from:
    # https://testdriven.io/blog/flask-sessions/

app.secret_key = "NDQc#@5~cgKT)mv2qG<c(B@!"

# Configure Flask session cookies
app.config["SESSION_PERMANENT"] = True
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=10000)
# app.config['SESSION_COOKIE_NAME'] = "my_session"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///oopsie.db"

# Initialize the database
db = SQLAlchemy(app)

# Create database model
class Methods(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    method = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(20), nullable=False)
    chance = db.Column(db.Float, nullable=False)
    source = db.Column(db.String(100), nullable=False)
    info = db.Column(db.String(350), nullable=False)
    info_source = db.Column(db.String(100), nullable=False)
    source_name = db.Column(db.String(100), nullable=False)
    info_source_name = db.Column(db.String(100), nullable=False)

# Global date variables
today = date.today()
tomorrow = date.today() + timedelta(days=1)
yesterday = date.today() - timedelta(days=1)
todayf = date.today().strftime("%A, %B %d, %Y")
tomorrowf = tomorrow.strftime("%m/%d/%Y")
yesterdayf = yesterday.strftime("%m/%d/%Y")

# Learned from:
    # https://stackoverflow.com/questions/34118093/flask-permanent-session-where-to-define-them


@app.before_request
def make_session_permanent():
    """Makes session permanent before each request"""
    session.permanent = True

@app.route("/", methods=["GET", "POST"])
def index():
    print(datetime.today())
    """Returns index, the homepage with an Oopsie chance summary based on selected options"""

    # When user clicks "Save" from Methods page...
    if request.method == "POST":

        # Get selections (method IDs) from user checkboxes & remember in session
        session["selections"] = request.form.getlist("method_selected")

        # Get rhythm method input(s) from user & remember in session
        session["cycle_start_str"] = request.form.get("cycle_start")
        session["cycle_length"] = request.form.get("cycle_length")
        session["period_length"] = request.form.get("period_length")
        session["cycle_day_ovulation"] = request.form.get("cycle_day_ovulation")

        # If selections, Rhythm Method data, and day are unchanged from previous save, quick load variables from session
        if session.get("selections_date_last_saved") and check_saved_data(session.get("selections_date_last_saved"), session.get("selections"), session.get("cycle_start_str"), session.get("cycle_length"), session.get("period_length"), session.get("cycle_day_ovulation")):
            print("Quick load!")
            oopsie_chance = session.get("oopsie_chance")
            oopsie_chance_yesterday = session.get("oopsie_chance_yesterday")
            oopsie_chance_tomorrow = session.get("oopsie_chance_tomorrow")
            period_today = session.get("period_today")
            period_yesterday = session.get("period_yesterday")
            period_tomorrow = session.get("period_tomorrow")
            ovulation_today = session.get("ovulation_today")
            ovulation_yesterday = session.get("ovulation_yesterday")
            ovulation_tomorrow = session.get("ovulation_tomorrow")
            methods = session.get("methods")
            cycle_day = session.get("cycle_day")
            cycle_day_yesterday = session.get("cycle_day_yesterday")
            cycle_day_tomorrow = session.get("cycle_day_tomorrow")
            cycle_day_ovulation = session.get("cycle_day_ovulation")
            next_ovulation = session.get("next_ovulation")
            next_period = session.get("next_period")
            rhythm_chance = session.get("rhythm_chance")

        # If new selections or day, reload
        else:
            # Set last save to today and reload saved session variables
            print("New load!")
            session["selections_date_last_saved"] = str(today)
            session["selections_saved"] = session.get("selections")
            session["cycle_start_str_saved"] = session.get("cycle_start_str")
            session["cycle_length_saved"] = session.get("cycle_length")
            session["period_length_saved"] = session.get("period_length")
            session["cycle_day_ovulation_saved"] = session.get("cycle_day_ovulation")

            # Get correct cycle start, cycle length, period length, and ovulation cycle day
            cycle_start = get_cycle_start(session.get("cycle_start_str"))
            cycle_length = get_cycle_length(session.get("cycle_length"))
            period_length = get_period_length(session.get("period_length"))
            cycle_day_ovulation = get_cycle_day_ovulation(session.get("cycle_day_ovulation"), cycle_length)

            # If there is a cycle start, get cycle day, next ovulation, next period, and rhythm method chance
            if cycle_start and "21" in session.get("selections"):
                cycle_day = session["cycle_day"] = get_cycle_day(today, cycle_start, cycle_length)
                cycle_day_yesterday = session["cycle_day_yesterday"] = get_cycle_day(yesterday, cycle_start, cycle_length)
                cycle_day_tomorrow = session["cycle_day_tomorrow"] = get_cycle_day(tomorrow, cycle_start, cycle_length)
                next_ovulation = session["next_ovulation"] = get_next_ovulation(today, cycle_day, cycle_day_ovulation, cycle_length)
                next_period = session["next_period"] = get_next_period(today, cycle_day, cycle_length)
                period_today = session["period_today"] = check_period(cycle_day, period_length)
                period_yesterday = session["period_yesterday"] = check_period(cycle_day_yesterday, period_length)
                period_tomorrow = session["period_tomorrow"] = check_period(cycle_day_tomorrow, period_length)
                ovulation_today = session["ovulation_today"] = check_ovulation(cycle_day, cycle_day_ovulation)
                ovulation_yesterday = session["ovulation_yesterday"] = check_ovulation(cycle_day_yesterday, cycle_day_ovulation)
                ovulation_tomorrow = session["ovulation_tomorrow"] = check_ovulation(cycle_day_tomorrow, cycle_day_ovulation)
                rhythm_chance = session["rhythm_chance"] = get_rhythm_chance(cycle_day, cycle_day_ovulation)
                rhythm_chance_yesterday = session["rhythm_chance_yesterday"] = get_rhythm_chance(cycle_day_yesterday, cycle_day_ovulation)
                rhythm_chance_tomorrow = session["rhythm_chance_tomorrow"] = get_rhythm_chance(cycle_day_tomorrow, cycle_day_ovulation)

            else:
                cycle_day = session["cycle_day"] = None
                cycle_day_yesterday = session["cycle_day_yesterday"] = None
                cycle_day_tomorrow = session["cycle_day_tomorrow"] = None
                next_ovulation = session["next_ovulation"] = None
                next_period = session["next_period"] = None
                period_today = session["period_today"] = False
                period_yesterday = session["period_yesterday"] = False
                period_tomorrow = session["period_tomorrow"] = False
                ovulation_today = session["ovulation_today"] = False
                ovulation_yesterday = session["ovulation_yesterday"] = False
                ovulation_tomorrow = session["ovulation_tomorrow"] = False
                rhythm_chance = session["rhythm_chance"] = None
                rhythm_chance_yesterday = session["rhythm_chance_yesterday"] = None
                rhythm_chance_tomorrow = session["rhythm_chance_tomorrow"] = None

            # If methods were selected on methods page...
            if session.get("selections"):
                # Get list of oopsie chances based on user-selected method IDs
                session["chances"] = get_chances(session.get("selections"), rhythm_chance)
                session["chances_yesterday"] = get_chances(session.get("selections"), rhythm_chance_yesterday)
                session["chances_tomorrow"] = get_chances(session.get("selections"), rhythm_chance_tomorrow)

                # Get rows of methods from database based on user-selected method IDs
                methods = Methods.query.filter(Methods.id.in_(session.get("selections"))).order_by(Methods.method).all()

                # Convert methods object to Python dictionary so it is JSON serializable (required for session["methods"])
                session["methods"] = make_serializable(methods)

                # Calculate oopsie chance by multiplying chances values
                oopsie_chance = session["oopsie_chance"] = get_oopsie(session.get("chances"))
                oopsie_chance_yesterday = session["oopsie_chance_yesterday"] = get_oopsie(session.get("chances_yesterday"))
                oopsie_chance_tomorrow = session["oopsie_chance_tomorrow"] = get_oopsie(session.get("chances_tomorrow"))

            # If no methods were selected on Methods page, set oopsie chance to default (40%)
            else:
                oopsie_chance = oopsie_chance_yesterday = oopsie_chance_tomorrow = 40
                session["oopsie_chance"] = session["oopsie_chance_yesterday"] = session["oopsie_chance_tomorrow"] = 40
                methods = session["methods"] = None

            # If date or length error
            if "21" in session.get("selections") and (not session.get("cycle_start_str") or not check_date(session.get("cycle_start_str")) or cycle_length < 1 or period_length < 0 or cycle_day_ovulation < 1 or period_length > cycle_length or cycle_day_ovulation > cycle_length):

                # If date is blank and Rhythm Method was selected, send back to Methods page with an error
                if "21" in session.get("selections") and not session.get("cycle_start_str"):
                    rhythm_error = "Last period start date is required for Rhythm Method."
                else:
                    rhythm_error = None

                # If date is not a valid date, send back to Methods page with an error
                if not check_date(session.get("cycle_start_str")):
                    date_error = "Please enter a valid date in format YYYY-MM-DD."
                else:
                    date_error = None

                # If cycle length is not greater than zero, send back to Methods page with an error
                if cycle_length < 1:
                    cycle_length_error = "Cycle length must be greater than zero."
                else:
                    cycle_length_error = None

                # If period length is not greater than zero, send back to Methods page with an error
                if period_length < 0:
                    period_length_error = "Period length can't a be negative number."
                else:
                    period_length_error = None

                # If cycle length is not greater than zero, send back to Methods page with an error
                if cycle_day_ovulation < 1:
                    cycle_day_ovulation_error = "Cycle day of ovulation must be greater than zero."
                else:
                    cycle_day_ovulation_error = None

                 # If period length or cycle day of ovulation are more than the cycle length, send back to Methods page with an error
                if period_length > cycle_length or cycle_day_ovulation > cycle_length:
                    length_error = "Period length and cycle day of ovulation must be within the cycle length."
                else:
                    length_error = None

                # Reset selections date last save in case the same wrong cycle start is saved more than once
                session["selections_date_last_saved"] = None

                # Get data from database for display on Methods page
                cycle_awareness = Methods.query.filter_by(type="cycle_awareness").order_by(Methods.id).all()
                contraception = Methods.query.filter_by(type="contraception").order_by(Methods.id).all()
                method = Methods.query.filter_by(type="method").order_by(Methods.id).all()
                surgical = Methods.query.filter_by(type="surgical procedure").order_by(Methods.id).all()

                return render_template("methods.html", contraception=contraception, cycle_awareness=cycle_awareness, method=method, surgical=surgical, selections=session.get("selections"), cycle_start=cycle_start, cycle_length=cycle_length, period_length=period_length, cycle_day_ovulation=cycle_day_ovulation, rhythm_chance=rhythm_chance, rhythm_error=rhythm_error, date_error=date_error, cycle_length_error=cycle_length_error, period_length_error=period_length_error, cycle_day_ovulation_error=cycle_day_ovulation_error, length_error=length_error)

    # When user navigates back to homepage without clicking "save" from Methods page...
    else:

        # If no selections are remembered in the session, or first-time visit, set oopsie chance to default (40%)
        if not session.get("selections"):
            oopsie_chance = oopsie_chance_yesterday = oopsie_chance_tomorrow = 40
            session["oopsie_chance"] = session["oopsie_chance_yesterday"] = session["oopsie_chance_tomorrow"] = 40
            methods = session["methods"] = None
            cycle_day = session["cycle_day"] = None
            cycle_day_yesterday = session["cycle_day_yesterday"] = None
            cycle_day_tomorrow = session["cycle_day_tomorrow"] = None
            cycle_day_ovulation = session["cycle_day_ovulation"] = None
            next_ovulation = session["next_ovulation"] = None
            next_period = session["next_period"] = None
            period_today = session["period_today"] = False
            period_yesterday = session["period_yesterday"] = False
            period_tomorrow = session["period_tomorrow"] = False
            ovulation_today = session["ovulation_today"] = False
            ovulation_yesterday = session["ovulation_yesterday"] = False
            ovulation_tomorrow = session["ovulation_tomorrow"] = False
            rhythm_chance = session["rhythm_chance"] = None
            rhythm_chance_yesterday = session["rhythm_chance_yesterday"] = None
            rhythm_chance_tomorrow = session["rhythm_chance_tomorrow"] = None

        # If selections are remembered in the session, load oopsie chance
        else:

            # If day is unchanged from previous save, quick load variables from session
            if session.get("selections_date_last_saved") == str(today):
                print("Quick load!")
                oopsie_chance = session.get("oopsie_chance")
                oopsie_chance_yesterday = session.get("oopsie_chance_yesterday")
                oopsie_chance_tomorrow = session.get("oopsie_chance_tomorrow")
                period_today = session.get("period_today")
                period_yesterday = session.get("period_yesterday")
                period_tomorrow = session.get("period_tomorrow")
                ovulation_today = session.get("ovulation_today")
                ovulation_yesterday = session.get("ovulation_yesterday")
                ovulation_tomorrow =session.get("ovulation_tomorrow")
                methods = session.get("methods")
                cycle_day = session.get("cycle_day")
                cycle_day_yesterday = session.get("cycle_day_yesterday")
                cycle_day_tomorrow = session.get("cycle_day_tomorrow")
                cycle_day_ovulation = session.get("cycle_day_ovulation")
                next_ovulation = session.get("next_ovulation")
                next_period = session.get("next_period")
                rhythm_chance = session.get("rhythm_chance")

            # If new day, reload
            else:
                # Set last save to today and reload saved session variables
                print("New load!")
                session["selections_date_last_saved"] = str(today)
                session["selections_saved"] = session.get("selections")
                session["cycle_start_str_saved"] = session.get("cycle_start_str")
                session["cycle_length_saved"] = session.get("cycle_length")
                session["period_length_saved"] = session.get("period_length")
                session["cycle_day_ovulation_saved"] = session.get("cycle_day_ovulation")

                # Get correct cycle start and cycle length
                cycle_start = get_cycle_start(session.get("cycle_start_str"))
                cycle_length = get_cycle_length(session.get("cycle_length"))
                period_length = get_period_length(session.get("period_length"))
                cycle_day_ovulation = get_cycle_day_ovulation(session.get("cycle_day_ovulation"), cycle_length)

                # If there is a cycle start, get cycle day, next ovulation, next period, and rhythm method chance
                if cycle_start and "21" in session.get("selections"):
                    cycle_day = session["cycle_day"] = get_cycle_day(today, cycle_start, cycle_length)
                    cycle_day_yesterday = session["cycle_day_yesterday"] = get_cycle_day(yesterday, cycle_start, cycle_length)
                    cycle_day_tomorrow = session["cycle_day_tomorrow"] = get_cycle_day(tomorrow, cycle_start, cycle_length)
                    next_ovulation = session["next_ovulation"] = get_next_ovulation(today, cycle_day, cycle_day_ovulation, cycle_length)
                    next_period = session["next_period"] = get_next_period(today, cycle_day, cycle_length)
                    period_today = session["period_today"] = check_period(cycle_day, period_length)
                    period_yesterday = session["period_yesterday"] = check_period(cycle_day_yesterday, period_length)
                    period_tomorrow = session["period_tomorrow"] = check_period(cycle_day_tomorrow, period_length)
                    ovulation_today = session["ovulation_today"] = check_ovulation(cycle_day, cycle_day_ovulation)
                    ovulation_yesterday = session["ovulation_yesterday"] = check_ovulation(cycle_day_yesterday, cycle_day_ovulation)
                    ovulation_tomorrow = session["ovulation_tomorrow"] = check_ovulation(cycle_day_tomorrow, cycle_day_ovulation)
                    rhythm_chance = session["rhythm_chance"] = get_rhythm_chance(cycle_day, cycle_day_ovulation)
                    rhythm_chance_yesterday = session["rhythm_chance_yesterday"] = get_rhythm_chance(cycle_day_yesterday, cycle_day_ovulation)
                    rhythm_chance_tomorrow = session["rhythm_chance_tomorrow"] = get_rhythm_chance(cycle_day_tomorrow, cycle_day_ovulation)

                else:
                    cycle_day = session["cycle_day"] = None
                    cycle_day_yesterday = session["cycle_day_yesterday"] = None
                    cycle_day_tomorrow = session["cycle_day_tomorrow"] = None
                    next_ovulation = session["next_ovulation"] = None
                    next_period = session["next_period"] = None
                    period_today = session["period_today"] = False
                    period_yesterday = session["period_yesterday"] = False
                    period_tomorrow = session["period_tomorrow"] = False
                    ovulation_today = session["ovulation_today"] = False
                    ovulation_yesterday = session["ovulation_yesterday"] = False
                    ovulation_tomorrow = session["ovulation_tomorrow"] = False
                    rhythm_chance = session["rhythm_chance"] = None
                    rhythm_chance_yesterday = session["rhythm_chance_yesterday"] = None
                    rhythm_chance_tomorrow = session["rhythm_chance_tomorrow"] = None

                # Get list of oopsie chances based on user-selected method IDs
                session["chances"] = get_chances(session.get("selections"), rhythm_chance)
                session["chances_yesterday"] = get_chances(session.get("selections"), rhythm_chance_yesterday)
                session["chances_tomorrow"] = get_chances(session.get("selections"), rhythm_chance_tomorrow)

                # Get rows of methods from database based on user-selected method IDs
                methods = Methods.query.filter(Methods.id.in_(session.get("selections"))).order_by(Methods.method).all()

                # Convert methods object to Python dictionary so it is JSON serializable (required for session["methods"])
                session["methods"] = make_serializable(methods)

                # Calculate oopsie chance by multiplying chances values
                oopsie_chance = session["oopsie_chance"] = get_oopsie(session.get("chances"))
                oopsie_chance_yesterday = session["oopsie_chance_yesterday"] = get_oopsie(session.get("chances_yesterday"))
                oopsie_chance_tomorrow = session["oopsie_chance_tomorrow"] = get_oopsie(session.get("chances_tomorrow"))

    return render_template("index.html", todayf=todayf, yesterdayf=yesterdayf, tomorrowf=tomorrowf, oopsie_chance=oopsie_chance, oopsie_chance_yesterday=oopsie_chance_yesterday, oopsie_chance_tomorrow=oopsie_chance_tomorrow, period_today=period_today, period_yesterday=period_yesterday, period_tomorrow=period_tomorrow, ovulation_today=ovulation_today, ovulation_yesterday=ovulation_yesterday, ovulation_tomorrow=ovulation_tomorrow, methods=methods, cycle_day=cycle_day, cycle_day_yesterday=cycle_day_yesterday, cycle_day_tomorrow=cycle_day_tomorrow, cycle_day_ovulation=cycle_day_ovulation, next_ovulation=next_ovulation, next_period=next_period, rhythm_chance=rhythm_chance)


@app.route("/methods")
def methods():
    """Returns methods page, where the user selects, saves, or clears method selections"""

    # Get data from database
    cycle_awareness = Methods.query.filter_by(type="cycle_awareness").order_by(Methods.id).all()
    contraception = Methods.query.filter_by(type="contraception").order_by(Methods.id).all()
    method = Methods.query.filter_by(type="method").order_by(Methods.id).all()
    surgical = Methods.query.filter_by(type="surgical procedure").order_by(Methods.id).all()

    # Set selections if remembered in the session, otherwise set to empty
    if session.get("selections"):
        selections = session.get("selections")
    else:
        selections = []

    # Get correct cycle start, cycle length, period length, and ovulation cycle day
    cycle_start = get_cycle_start(session.get("cycle_start_str"))
    cycle_length = get_cycle_length(session.get("cycle_length"))
    period_length = get_period_length(session.get("period_length"))
    cycle_day_ovulation = get_cycle_day_ovulation(session.get("cycle_day_ovulation"), cycle_length)

    # If day is the same, quick load rhythm chance for tooltip display
    if session.get("methods_date_last_saved") == str(today):
        print("Quick load!")
        if session.get("rhythm_chance") != None and cycle_start:
            rhythm_chance = session.get("rhythm_chance")
        else:
            rhythm_chance = None

    # If new day, reload
    else:
        # Set last save to today
        print("New load!")
        session["methods_date_last_saved"] = str(today)

        # If there is a cycle start, get cycle day and rhythm method chance
        if cycle_start and "21" in session.get("selections"):
            cycle_day = get_cycle_day(today, cycle_start, cycle_length)
            rhythm_chance = session["rhythm_chance"] = get_rhythm_chance(cycle_day, cycle_day_ovulation)
        else:
            cycle_day = None
            rhythm_chance = None

    return render_template("methods.html", cycle_awareness=cycle_awareness, contraception=contraception, method=method, surgical=surgical, selections=selections, cycle_start=cycle_start, cycle_length=cycle_length, period_length=period_length, cycle_day_ovulation=cycle_day_ovulation, rhythm_chance=rhythm_chance)


@app.route("/clear")
def clear():
    """Clears data saved in the session"""

    session["selections"] = session["calendar_selections_saved"] = session["saved_events"] = []
    session["cycle_start_str"] = session["cycle_start_str_saved"] = session["calendar_cycle_start_str_saved"] = None
    session["cycle_length"] = session["cycle_length_saved"] = session["calendar_cycle_length_saved"] = 28
    session["period_length"] = session["period_length_saved"] = session["calendar_period_length_saved"] = 5
    session["cycle_day_ovulation"] = session["cycle_day_ovulation_saved"] = session["calendar_cycle_day_ovulation_saved"] = 14
    session["selections_date_last_saved"] = session["lucky_date_last_saved"] = session["calendar_date_last_saved"] = str(today)

    return redirect("/methods")


@app.route("/get_lucky")
def get_lucky():
    """Returns "Get Lucky" page, where the user simulates business time (intercourse) with today's Oopsie chance"""

    # If no selections are remembered in the session, or first-time visit, set oopsie chance to default (40%)
    if not session.get("selections"):
        oopsie_chance = 40

    # If selections are remembered in the session, load oopsie chance
    else:

        # If day is unchanged from previous save, quick load variables from session
        if session.get("lucky_date_last_saved") == str(today):
            print("Quick load!")
            oopsie_chance = session.get("oopsie_chance")

        # If new day, reload
        else:
            # Set last save to today
            print("New load!")
            session["lucky_date_last_saved"] = str(today)

            # Get correct cycle start, cycle length, and ovulation cycle day
            cycle_start = get_cycle_start(session.get("cycle_start_str"))
            cycle_length = get_cycle_length(session.get("cycle_length"))
            cycle_day_ovulation = get_cycle_day_ovulation(session.get("cycle_day_ovulation"), cycle_length)

            # If there is a cycle start, get cycle day and rhythm method chance
            if cycle_start and "21" in session.get("selections"):
                cycle_day = get_cycle_day(today, cycle_start, cycle_length)
                rhythm_chance = session["rhythm_chance"] = get_rhythm_chance(cycle_day, cycle_day_ovulation)
            else:
                cycle_day = None
                rhythm_chance = None

            # Get list of oopsie chances based on user-selected method IDs
            session["chances"] = get_chances(session.get("selections"), rhythm_chance)

            # Calculate oopsie chance by multiplying chances values
            oopsie_chance = get_oopsie(session.get("chances"))

    return render_template("get_lucky.html", oopsie_chance=oopsie_chance)


@app.route("/calendar")
def calendar():
    """Returns calendar page, where the user views a calendar of Oopsie chances, cycle days, ovulation days, period days, etc."""

    # Calendar by:
    #     https://fullcalendar.io/

    # Learned Fullcalendar setup from:
        # https://www.youtube.com/watch?v=VXW2A4Q81Ok&t=2s&ab_channel=GordonChan

    # Quick load for calendar has been disabled because it exceeds the cookie file size. To re-enabled, un-comment the first if statement, comment/remove the second, and un-comment "session["saved_events"] = events" at end of function

    # # If selections are unchanged from previous save within 30 days, quick load events from session
    # if session.get("calendar_date_last_saved") and check_saved_calendar(session.get("selections"), session.get("cycle_start_str"), session.get("cycle_length"), session.get("period_length"), session.get("cycle_day_ovulation")):
    #     print("Quick load!")
    #     events = session.get("saved_events")
    #     rhythm_chance = session.get("rhythm_chance")

    # Quick load without using Session
    if session.get("rhythm_chance") == None:
        print("Quick load! (No Rhythm Chance)")
        events = None
        rhythm_chance = None

    # If different selections or calendar hasn't been saved within 30 days, reload session variables
    else:
        # Set last save to today
        print("New load!")
        session["calendar_date_last_saved"] = str(today)

        # If selections are remembered in the session, reload saved session variables
        if session.get("selections"):
            session["calendar_selections_saved"] = session.get("selections")
            session["calendar_cycle_start_str_saved"] = session.get("cycle_start_str")
            session["calendar_cycle_length_saved"] = session.get("cycle_length")
            session["calendar_period_length_saved"] = session.get("period_length")
            session["calendar_cycle_day_ovulation_saved"] = session.get("cycle_day_ovulation")
        else:
            session["calendar_selections_saved"] = []

        # Create empty events object for calendar
        events = []

        # Populate calendar events for X days past and future
        for i in range(-365, 365):

            # If no selections are remembered in the session, or first-time visit, set oopsie chance to default (40%)
            if not session.get("selections"):
                oopsie_chance = 40
                cycle_start = None
                rhythm_chance = None

            # If selections are remembered in the session, calculate oopsie chance
            else:

                # Get correct cycle start, cycle length, period length, and ovulation cycle day
                cycle_start = get_cycle_start(session.get("cycle_start_str"))
                cycle_length = get_cycle_length(session.get("cycle_length"))
                period_length = get_period_length(session.get("period_length"))
                cycle_day_ovulation = get_cycle_day_ovulation(session.get("cycle_day_ovulation"), cycle_length)

                # If there is a cycle start, get cycle day and rhythm method chance
                if cycle_start and "21" in session.get("selections"):
                    cycle_day = get_cycle_day(get_date(i), cycle_start, cycle_length)
                    rhythm_chance = session["rhythm_chance"] = get_rhythm_chance(cycle_day, cycle_day_ovulation)
                else:
                    cycle_day = None
                    rhythm_chance = None

                # Get list of oopsie chances based on user-selected method IDs
                session["chances"] = get_chances(session.get("selections"), rhythm_chance)

                # Calculate oopsie chance by multiplying chances values
                oopsie_chance = get_oopsie(session.get("chances"))

            # Add Oopsie % to calendar for the i'th day
            events.append({
                "title": str(oopsie_chance) + "% Oopsie!",
                "date": str(get_date(i)),
            })

            # Add cycle day text to calendar for the i'th day if Rhythm Method (ID = 21) has been selected
            if cycle_start and "21" in session.get("selections"):
                events.append({
                    "title": "Cycle Day " + str(cycle_day),
                    "date": str(get_date(i)) + "T00:00:00",
                })

            # Add period day text to calendar for the i'th day if Rhythm Method (ID = 21) has been selected
            if cycle_start and "21" in session.get("selections") and (check_period(cycle_day, period_length)):
                events.append({
                    "title": "Period Day",
                    "date": str(get_date(i)) + "T00:00:00",
                })

            # Add ovulation day text to calendar for the i'th day if Rhythm Method (ID = 21) has been selected
            if cycle_start and "21" in session.get("selections") and (check_ovulation(cycle_day, cycle_day_ovulation)):
                events.append({
                    "title": "Ovulation Day",
                    "date": str(get_date(i)) + "T00:00:00",
                })

        # Save events in session
        # session["saved_events"] = events

    return render_template("calendar.html", rhythm_chance=rhythm_chance, events=events)


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


def check_saved_data(date_last_saved, selections, cycle_start_str, cycle_length, period_length, cycle_day_ovulation):
    """Returns True if new selections match saved selections and the last save was today"""

    if str(today) == date_last_saved:
        if (selections == session.get("selections_saved") and
            cycle_start_str == session.get("cycle_start_str_saved") and
            cycle_length == session.get("cycle_length_saved") and
            period_length == session.get("period_length_saved") and
            cycle_day_ovulation == session.get("cycle_day_ovulation_saved")):
            return True
    else:
        return False


def check_saved_calendar(selections, cycle_start_str, cycle_length, period_length, cycle_day_ovulation):
    """Returns True if new selections match saved selections and the calendar has been reloaded in the last 30 days"""

    if ((datetime.strptime(session.get("calendar_date_last_saved"), "%Y-%m-%d").date() + timedelta(days=30)) - today).days > 0:
        if (selections == session.get("calendar_selections_saved") and
            cycle_start_str == session.get("calendar_cycle_start_str_saved") and
            cycle_length == session.get("calendar_cycle_length_saved") and
            period_length == session.get("calendar_period_length_saved") and
            cycle_day_ovulation == session.get("calendar_cycle_day_ovulation_saved")):
            return True
    else:
        return False


def get_date(relative_days):
    """Returns the date in relation to the number of days from the current day"""

    relative_date = date.today() + timedelta(days=relative_days)
    return relative_date


def get_cycle_day(day, cycle_start, cycle_length):
    """Returns the cycle day given cycle start and length"""

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
    """Returns cycle start as YYYY-MM-DD formated date if it is saved in the session and a valid date, otherwise return None"""

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
    """Returns True if given cycle day is a period day"""

    # Return True if cycle is within the period length
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
    """Returns Rhythm Method chance given cycle and and ovulation day"""

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


def make_serializable(object):
    """Returns JSON serializable value given database object"""

    session_dict = {}
    session_list=[]

    for row in object:
        session_dict = {
            "id": row.id,
            "method": row.method,
            "type": row.type,
            "chance": row.chance,
            "source": row.source,
            "info": row.info,
            "info_source": row.info_source,
            "source_name": row.source_name,
            "info_source_name": row.info_source_name}

        session_list.append(session_dict)

    # Return a list of dictionaries
    return session_list