# Oopsie
#### Video Demo:  https://youtu.be/flOwjttW78A
#### Description:
Oopsie is a web-based anti-fertility application that celebrates, with tongue in cheek, the wonderful, life-altering event of not getting pregnant. The app allows the user to select any combination of currently used preventative methods and receive an "oopsie" chance for the day (as well as other days). It was built using Flask, Python, JavaScript, and SQL as a final project for CS50x 2021.

## Files:
### <span>app.py</span>
This is the controller of my web-application, written in Python and using the Flask framework. I chose to use Flask-SQLAlchemy because I wanted to know how to get along without cs50.SQL. Data comes from an SQLite database, oopsie.db, which contains all the prevention methods, their "oopsie" chances, and all my sources from research. Originally, I imagined this application would have a login system, which would also be stored in a database and would allow each user to add/remove/customize multiple partner profiles, but decided this was unjustified and overly complicated (given that Oopsie is basically a calculator). I didn't think people would actually need/want to register or login, so I opted to use sessions for improved user engagement.

I had to learn how to use Python's datetime module, which allowed me to reference today's date and to calculate figures (like oopsie chance, cycle day, ovulation day, etc.) in relation to today. Later, when I deployed my app to Heroku, which has a different server time than my local server, I learned about timezone localization issues. I used the pytz library to localize my app, allowing the user to set their timezone or to leave UTC as the default.

Essentially, once the user saves selections from the methods page, a number of calculations ocurr. At first, these calculations were recurring any time a page that needed them was loaded (Index, Methods, Get Lucky, and Week View). However, the data didn't need to be re-calculated every time a page was loaded, especially if it were the same day and no selections had been changed. To avoid this, I implemented a "quick load" system that would check both the day and the selections upon page load. I believe this saves a lot of needless re-calculation and load time. I was not able to do this with Week View because the dictionary is too large for a session cookie; however, that section seems to load quick enough each time without it, so I decided to accept this compromise.

Some challenges:
- Getting started: It took a good number of days to figure out my own coding environment without the use of CS50 IDE. (I wanted to make sure I could complete a project without it as a crutch.) I am coding on a Windows 10 PC, using VS Code as my text editor. Setting up Python, Flask, and a virtual environment were all hurdles in the beginning, which I got over with the help of many YouTube tutorials (Caleb Curry, Codemy, Socratica Python, Pretty Printed, Corey Schafer).
- Condensing my code: I was able to clean up a lot of repetition with functions, but there are still some areas where many variables are declared and this feels unideal. This is even sometimes repeated, like where the home page can be navigated to via POST or GET. I would like to know how to condense and clean my code further.
- Some features (tooltips, "Get Lucky" JavaScript, etc.) may not work in older browsers. Safari does not support a date input, so I had to add validation for the date input.
- Deployment was an unexpected nightmare. My sessions were not persisting on Heroku because I was using the filesystem, the method presented in class. Once I switched to cookies, I had to convert my database object to a list of Python dictionaries so it would be JSON serializable. Then, any date object that entered the session would come out with a different format, so I converted all the dates to strings before passing them to the session as a quick fix. My session was still not persisting. I learned that SESSION_PERMANENT is a feature of flask-session, not flask itself. Adding the function make_session_permanent finally made my sessions permanent!
- Session size - I was hoping to store the Week View dictionary in the session cookie, for quick loading, however the cookie was exceeding the file size limit, so I had to turn off this quick loading feature. A better approach would be to use a server-side session, like redis, or a login/user system with a database, but I did not want a login to be required for this app. These are lessons learned for my next project.
- Calendar - Originally, I was using Full Calendar (https://fullcalendar.io/) but I decided against it because it did not look good on mobile and I didn't like the customization options. It was also slow to load since I'm not using a database, and storing it in the session made the cookie too large. So, I made my own "week view" from scratch, which uses media queries for responsive design.

<span>app.py</span> contains the following functions:

1. make_session_permanent - Makes session permanent before each request.
2. Index - Returns index, the homepage with an Oopsie chance summary based on selected options.
3. methods - Returns methods page, where the user selects, saves, or clears method selections.
4. clear - Clears all data saved in the session and sets timezone to default UTC.
5. get_lucky - Returns "Get Lucky" page, where the user simulates business time (intercourse) with today's Oopsie chance.
6. weekview - Returns week view page, where the user views Oopsie chances, cycle days, ovulation days, and period days for the previous, current, and next weeks.
7. lastweek - Returns last week page, where the user views Oopsie chances, cycle days, ovulation days, and period days for the previous week in narrow/mobile view
8. nextweek - Returns next week page, where the user views Oopsie chances, cycle days, ovulation days, and period days for the next week in narrow/mobile view"
9. about - Returns about page, with information about this app.
10. sources - Returns sources page, which lists all sources used in the database.
11. disclaimer - Returns disclaimer page.
12. contact - Returns contact page.
13. get_today - Sets session timezone to UTC if timezone hasn't been set and returns today object with timezone
14. check_saved_data - Returns True if new selections match saved selections and the last save was today.
15. get_cycle_day - Returns the cycle day given cycle start and length.
16. get_next_ovulation - Returns next ovulation date when cycle day matches cycle day ovulation.
17. get_next_period - Returns next period start date given cycle day and length.
18. check_date - Returns True if given date string is a valid date
19. get_cycle_start - Returns cycle start as YYYY-MM-DD formatted date if it is saved in the session and a valid date, otherwise return None
20. get_cycle_length - Returns cycle length as int if it is saved in the session, otherwise return default (28).
21. get_period_length - Returns period length as int if it is saved in the session, otherwise return default (5).
22. get_cycle_day_ovulation - Returns ovulation cycle day if it is saved in the session, otherwise return default (cycle_length/2).
23. check_period - Returns True if given cycle day is a period day.
24. check_ovulation - Returns True if given cycle day is an ovulation day.
25. get_rhythm_chance - Returns Rhythm Method chance given cycle and ovulation day.
26. get_chances - Returns list of chances based on list of user-selected IDs.
27. get_oopsie - Calculates rounded chance of Oopsie pregnancy based on list of user-selected chances.
28. get_Sunday - Returns the most recent Sunday, as a date object, given a date object
29. get_week - Returns a dictionary for a week with week-view data given a starting date
30. make_serializable - Returns JSON serializable value given database object

## Static Files:
### styles.css
Used this for basic styling, notably adjustments for the tooltips and logo SVG. I also learned how to use media queries for responsive design in some sections (namely Week View).

## Templates:
### about.html
Gives information about Oopsie that may be of interest to users.

### contact.html
A simple note about where to send feedback.

### disclaimer.html
This section gives some transparency to my methods and assumptions. Also, with the last class on ethics in mind, I wanted to make sure it is clear that I'm not a doctor or fertility expert, or even an expert researcher, and that, while I did my best to research and calculate with clarity and accuracy, all results should be taken with a grain of salt.

### get_lucky.html
A JavaScript simulation based on the current oopsie chance. Can adjust multiplier x1, x10, x100, and x1,000. Number of rolls are tracked. When an oopsie occurs, an emoji is added and a total count is incremented. The user can reset the simulation, or navigate away (state not saved in session).

### index.html
The homepage, which displays the current oopsie chance (and other details) based on user selections. If rhythm method has been selected with a start date, then time-based calculations will display for the current day, yesterday, and tomorrow.

### lastweek.html
Shows last weekview only - is only accessible if on mobile (with a screen less than 768px wide).

### layout.html
Contains the navbar from Bootstrap and extends to other HTML pages. Footer contains scripts for tooltips.

### methods.html
The user can select any number of methods via checkboxes, as well as timezones via a selection menu, and save. Data is stored in session cookies. A "Clear All Saved Data" button resets all session variables and resets timezone to UTC. A "Check all" checkbox selects and de-selects all checkboxes via JavaScript. Error messages will appear if the user submits an invalid input (such as an invalid date format, Rhytm method with no cycle start date, or a period length that is greater than cycle length).

### nextweek.html
Shows next weekview only - is only accessible if on mobile (with a screen less than 768px wide).

### sources.html
Provides all the sources used in the database formatted in a table. There is probably a better way to format this but I did not prioritize the formatting of this section.

### week_view.html
Week view shows Oopsie data (Oopsie chance, cycle day, period status, and ovulation status) for the current week, last week, and next week. This section replaced my original implementation of (https://fullcalendar.io/), which didn't work out. Data for last week, current week, and next week are each stored in a dictionary of dictionaries which are passed to the template. The current day gets a blue circle background and is updated upon each reload (was too large to store in session). Reload times seemed reasonable. This section forced me to learn how to use divs instead of tables. I then replaced most of the tables throughout my html templates with divs. Additionally, I also learned about media queries because I wasn't happy with how this page was appearing on mobile. So, the default design is for desktop (with all 3 weeks are visible on one page), but mobile users (screen sizes less than 768px wide) will only see the current week with links to previous and next week, which I implemented as separate routes. It may have been better to do this with JavaScript to avoid a page load, but I already knew how to do it this way and was ready to be done with this project!