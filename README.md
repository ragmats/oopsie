// what each of the files you wrote for the project contains and does, and if you debated certain design choices, explaining why you made them. //
# OOPSIE
#### Video Demo:  <URL HERE>
#### Description:
Oopsie is a web-based anti-fertility application that celebrates, with tongue in cheek, the wonderful, life-altering event of not getting pregnant. The app allows the user to select any combination of currently used preventative methods and receive an "oopsie" chance for the day (as well as other days). It was built using Flask, Python, JavaScript, and SQL as a final project for CS50x 2021. Oopsie also uses [Bootstrap](https://getbootstrap.com/) and [FullCalendar](https://fullcalendar.io/).

## Files:
### <span>app.py</span>
This is the controller of my web-application, written in Python and using the Flask framework. I chose to use Flask-SQLAlchemy because I wanted to know how to get along without cs50.SQL. Data comes from an SQLite database, oopsie.db, which contains all the prevention methods, their "oopsie" chances, and the source where I researched that oopsie chance. Originally, I imagined this application would have a login system, which would also be stored in a database, and would allow each user to add/remove/customize multiple partner profiles, but decided this was unjustified and overly complicated, given that Oopsie is basically a calculator. I didn't think people would actually need or want to register or login, and used sessions to remember the data.

I had to learn how to use Python's datetime module, which allowed me to reference today's date and to caculate figures (like oopsie chance, cycle day, ovulation day, etc.) in relation to today. Using timedelta, I was able to add and subtract days and populate an entire calendar of anti-fertility events.

Once the user saves selections from the methods page, a number of calculations ocurr. At first, these calculations were re-curring any time a page that needed them was loaded (Index, Methods, Get Lucky, and Month View). However, the data didn't need to be reloaded every time a page was loaded, especially if it were the same day and no selections had been changed. To avoid this, I implemented a quickload system that would check both the day and the selections upon page load. If it is a new day (i.e. the last save != Today) the data would need to be loaded at least once (except for Month View, which I set to require a reload only after 30 days); however, once reloaded, the data would be saved in the session, along with the data of the save. Then, upon page load, if the day is the same, and the current selections match the saved selections, then the page could just quick load the session variables, instead of re-calculating them. I believe this saves a lot of needless re-calculation and load time, especially with the month view, which populates a full year of calculations both into the future and past whenever upon new load.

Some challenges:
- Getting started: It took a good number of days to figure out my own coding environment without the use of CS50 IDE. (I wanted to make sure I could complete a project without it as a crutch.) I am coding on a Windows 10 PC, using VS Code as my text editor. Setting up Python, Flask, and a virtual environment were all hurdles in the beginning, which I got over with the help of many YouTube tutorials (Caleb Curry, Codemy, Socratica Python, Pretty Printed).
- Condensing my code: I was able to clean up a lot of repeptition with functions, but there are still some areas where many variables are declared and this feels unideal. This is even sometimes repeated, like where the home page can be navigated to via POST or GET. I would like to know how to condense and clean my code further.
- Some features (tooltips, "Get Lucky" JavaScript, etc.) do not work in older browsers. Safari does not support a date input, so I had to add validation for the date input.
- Deployment was an unexpected nightmare. My sessions were not persisting on Heroku because I was using the filesystem. Once I switched to cookies, I had to convert my database object to a list of Python dictionaries so it would be JSON serializable. Then, any date object that entered the session would come out with a different format, so I converted all the dates to strings before passing them to the session as a quick fix. My session was still not persisting. I learned that SESSION_PERMANENT is a feature of flask-session, not flask itself. Adding the function make_session_permanent finally made my sessions permanent.
- Session size - I was hoping to store the events dictionary that populates the calendar section in the session cookie, for quick loading, however the cookie was exceeding the file size limit, so I had to turn off this quick loading feature. Therefore, the calendar re-populates on each request, which can be slow and inefficient. A better approach would be to use a server-side session, like redis, or a login/user system with a database, but I did not want a login to be required for this app. These are lessons learned for my next project.

<span>app.py</span> contains the following functions:

0. make_session_permanent - Makes session permanent before each request.
1. Index - Returns index, the homepage with an Oopsie chance summary based on selected options.
2. methods - Returns methods page, where the user selects, saves, or clears method selections.
3. clear - Clears data saved in the session.
4. get_lucky - Returns "Get Lucky" page, where the user simulates business time (intercourse) with today's Oopsie chance.
5. month_view - Returns calendar page, where the user views a calendar of Oopsie chances, cycle days, ovulation days, period days, etc.
6. about - Returns about page, with information about this app.
7. sources - Returns sources page, which lists all sources used in the database.
8. disclaimer - Returns disclaimer page.
9. contact - Returns contact page.
10. check_saved_data - Returns True if new selections match saved selections and the last save was today.
11. check_saved_calendar - Returns True if new selections match saved selections and the calendar has been reloaded in the last 30 days.
12. get_date - Returns the date in relation to the number of days from the current day.
13. get_cycle_day - Returns the cycle day given cycle start and length.
14. get_next_ovulation - Returns next ovulation date when cycle day matches cycle day ovulation.
15. get_next_period - Returns next period start date given cycle day and length.
16. check_date - Returns True if given date string is a valid date
17. get_cycle_start - Returns cycle start as YYYY-MM-DD formated date if it is saved in the session and a valid date, otherwise return None
18. get_cycle_length - Returns cycle length as int if it is saved in the session, otherwise return default (28).
19. get_period_length - Returns period length as int if it is saved in the session, otherwise return default (5).
20. get_cycle_day_ovulation - Returns ovulation cycle day if it is saved in the session, otherwise return default (cycle_length/2).
21. check_period - Returns True if given cycle day is a period day.
22. check_ovulation - Returns True if given cycle day is an ovulation day.
23. get_rhythm_chance - Returns Rhythm Method chance given cycle and and ovulation day.
24. get_chances - Returns list of chances based on list of user-selected IDs.
25. get_oopsie - Calculates rounded chance of Oopsie pregnancy based on list of user-selected chances.
26. make_serializable - Returns JSON serializable value given database object

## Static Files:
### styles.css
Used this for basic styling, notably adjustments for the tooltips and logo SVG.

## Templates:
### layout.html
Contains the navbar from Bootstrap and extends to other HTML pages. Footer contains scripts for tooltips.

### index.html
The homepage, which displays the current oopsie chance (and other details) based on user selections. If rhythm method has been selected, then time-based calculations will display for the current day, yesterday, and tomorrow.

### methods.html
The user can select any number of methods via checkboxes and save. Data is stored in session cookies. A "Clear All Saved Data" button resets all session variables. A "Check all" checkbox selects and de-selects all checkboxes via JavaScript.

### month_view.html
Uses Full Callendar, a JavaScript calendar (https://fullcalendar.io/), to display the varying oopsie chances (and other details) of each day on a calendar. Details are populated on the backend and passed as a single "events" variable.

### get_lucky.html
A JavaScript simulation based on the current oopsie chance. Can adjust multiplier x1, x10, x100, and x1,000. Number of rolls are tracked. When an oopsie occurs, an emoji is added and a total count is incremented. The user can reset the simulation, or navigate away (state not saved in session).

### about.html
Gives information about this application that may be of interest to users.

### sources.html
Provides all the sources used in the database formatted in a table. There is probably a better way to format this but I did not prioritize the formatting of this section.

### disclaimer.html
With the last class on ethics in mind, I wanted to make sure it is clear that I'm not a doctor or fertility expert, or even an expert researcher, and that, while I did my best to research and calculate with clarity and accuracy, all results should be taken with a grain of salt.

### contact.html
A simple note about where to send feedback.