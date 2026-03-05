# Nexus Roze Tattoo Studio
#### Video Demo:  <[Link to video](https://youtu.be/ez-SLrni7P0?si=MIeRjWGttd8iDiz3)>

## Features
- Simple account registration and secure login with password hashing.
- Client and artist roles with role-based access to schedules and management pages.
- Booking flow that captures description, requested date, and server-side timestamp for requests.
- Account management and administrative tools for approving artist registrations and removing accounts or appointments.

#### Description:
Created an application for the purpose of advertising and booking tattoos for a small business. My wife runs a tattoo shop and doesn't currently have a website, so the idea was to make something simple that would work on any device. With the ability to advertise the tattoo work, give basic contact information and give the ability to book tattoos as well as checking a schedule for tattoos. I also implemented delete database functions to rid of excess old data and giving admin requirements from removing a user and that users scheduled tattoos.

#### Homepage:
Here i created a homepage where a client or an artist can view the main logo and read a summary about the tattoo studio. From this homepage you can also access most of the website excluding sections that require a login. I wanted clients to have the capability to view information about the company without being forced to login, so i emplemented the login function where it would be needed for booking or account managment. Without logging in, users can view the gallery check pricing and view the homepage. The footer holds contact information that can be viewed on any page, with links to address of shop and link to phone number to make contacting as easy as possible.

#### Flask/Python:
I used flask to create a layout.html file to store the design of the header and footer, that carries on to each page. I used a navigation bar design that also shrinks to a hamburger drop down menu when page is on a small device to make it easier to access on all platforms. Using flask also gave me the ability to use python programming for functions that are stored in helpers.py and webpage commands in app.py. I enjoyed using javascript but wanted to try using flask and python more since it was in our last week prior. With python i was able to create functions for buttons to redirect to the corresponding pages and making commands to the database using sqlite.

#### SQLite3 db:
I used the knowledge from the SQL week to create a database with tables holding information for username, passwords, contact info, wether the user is an artist and scheduling. As well as linking the two tables (users and schedule) with primary and foriegn keys. Using SQLite commands through the python file, I was able to created visual tables showing a clients scheduled tattoos and if that account is an artist. Where if the account belongs to an artist, they would having access to the full schedule as well as deleting scheduled tattoos when it has passed.

#### Register/Login:
I created both login and register pages. There is a simple check if the user is an artist at registration but in order to prevent any user from having an artists access, they will be prompted to have an admin approve their registration. Admin login information is also required to deleted any account on the page. Unless the logged in user is wanting to delete their own account, they will be able to do so from the account page.

#### Booking/Schedule:
There is a page for booking but to access it requires a login. If user is not logged in, then they will be redirected to login. After user has logged in, they will have access to scheduling a tattoo with a tattoo description, date of schedule, as well as the date they requested the schedule. In the booking page I made sure to put that user will be contacted for confirmation on appointment. After returning to account any client can see their own scheduled tattoos, and has the ability to delete their account but only an artist can delete scheduled tattoos.

#### Testing:
Manual testing was used to validate registration, login, booking, and deletion flows. Apology htmls were created with error responses to let user know what they did wrong, wether it was no password, phone number, etc.

##### Side-Note:
I did enjoy working on this project a ton. I am still thinking of ways I could improve the site. The more challenging part was taking off the cs50 'training wheels' and figuring out how to get flask and sqlite3 working without cs50's codespace. I already had visual studio code and some coding languages installed. Also learning how to give commands through sqlite without cs50's db.execute command. Having the ability to get it all working without the codespace was a real treat. Though i do enjoy cs50s codespace due to the fact that i was able to focus on going straight to coding instead of facing the challenge of installing and testing programs that i hadn't yet seen.