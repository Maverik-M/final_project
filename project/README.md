# Somos2 Web app
#### Video Demo:  <[URL HERE](https://youtu.be/AJDeJZDBU1Q)>
#### Description:

This project is a Web app made in python using flask as framework and SQLite3 as db language that basically allows a company named Somos2 (a company that focuses in dog training)
to add and modify human clients and dog clients data into a database and retrive all of that data. The app allows the company to add courses and sessions per dog and allows to track the status of that course.

First, based on the finance pset, I created a login and registration page that checks for user and password. There is not much to talk about that.

I also created a function to check if a password complies with the criteria (5 characters long, 1 lowercase letter, 1 uppercase letter and 1 special character).
That function is used for registering and for changing the password

Once inside, I created the option to change the password taking into account the current password for the user logged in. That option checks that both passwords comply with the password criteria (using the function described above) and also check if both passwords match. If every thing is ok, the page is going to do a POST request in which a change to the database is going to be made to the current user password. It's important to highlight that as finance ps, I used the same hashing for storage of passwords.

The first page that the user is going to see is the index page, in which the user can find some basic instructions about the app usage. For that page I used bootstrap's according.

In the navegation bar can be found two buttons (Usuarios and Cursos) the following is the explaination for all of them:

**Usuarios(users):**

This button, when clicked, extends a dropdown menu that has the following options:

***Buscar peludo(Search dog):*** When this option is clicked there is a users.html that is rendered and allows two inputs (dog name and human name). The dog name gives suggestions (coded using javascript) of the dog names that contains the letters typed. Once the name is selected, the human name associated to that dog is inmediatly selected. Once submit is click a POST request is sent with the information and in the backend all of the data is used to identify what dog the user is try to search. Once found, a userd.html is rendered and all the dog information is displayed including an rounded image of the dog, the courses taken or that are being taken by the time of the search and sessions applicable to each course.

Aditionally, each session has a button that allows its own edition. The button is a get request to edit_session.html that when gets a GET request, renders a page with inputs that are pre-filled with the current values of the session using flask and jinja. That same page allows for edition and deletion of the session and gets an alert when either button is pressed. Once the edition/deletion is done, the app goes back to the userd page using a function defined in helpers by me to render the userd page taking as arguments the database, the dog id and human id.

Each course also has a button that allows its own status editions (only applicable to the dog that is taking the course). The button is a get request to modify.c_course.html that when gets a GET request, renders a page with inputs that are pre-filled with the current values of the session using flask and jinja. That same page allows for edition of the course status and gets an alert when the button is pressed. Once the edition is done, the app goes back to the userd page using the same get_userd function described above.

***Ver usuarios(Clients view):*** This options allows the view of all the users using a table that uses jinja to handle data passed by flask using for loops. That table is the current data of the clients database.

***Crear tutor(Create human):*** This option allows user to create a human. When pressed the system gets a GET requests which renders the create_human.html file and displays the required inputs. When submited a POST request is generated and all data (if valid) is included in the database.

***Crear peludo(Create dog):*** This option is almost the same as the create human one, but the difference is that takes into account more data and allow the upload of an image. The image is uploaded directly into the database. for this the image get encoded using the base64 library and then included in the database.

***Modificar tutor(Modify dog):*** This option allows user to modify a dog. When pressed the system gets a GET requests which renders the modify_dog.html file and displays the required inputs. When submited a POST request is generated and all data (if valid) is included in the database. Only the required modification fields need to be filled, if not, can be left in blank.

***Modificar peludo(Modify human):*** The same as in modify dog with the difference that the dog one allows for the image upload as well in case that an image modification is wanted.


**Cursos(courses):**

***Ver cursos(Course view):*** This options allows the view of all the courses using a table that uses jinja to handle data passed by flask using for loops. That table is the current data of the courses database.

***Crear curso(Create course):*** This option allows user to create a course. When pressed the system gets a GET requests which renders the create_course.html file and displays the required inputs. When submited a POST request is generated and all data (if valid) is included in the database.

***Modificar curso(Modify course):*** This option allows user to modify a course. When pressed the system gets a GET requests which renders the modify_course.html file and displays two inputs. One is the course to be modified (which is a select element with options that are looped thru every course to give all the courses options) and the new name that is going to be modified in the course database.


Is worth noting that everyinput is checked and that in case of an error, the same apology from finance get renderd using the function. The apology function image was changed but basically has the same funnctionality.

References:

Duck debugger: For debugging and JS questions.
Gemini: For debugging and JS questions.
Finance: For initial framework and page templetes. (only used as reference, everything was edited and costumized)
