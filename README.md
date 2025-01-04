# Godam-Find
Godam find is a electronic store godam . in which different kinds of electronic product are stored . it help user find and explore godam based on their tastes and user friendly interface.this project is complete backend part where diffent feature are available,like read review and connect with electronic mini/macro essential person in community with Godam Find!!

# Features
Google Auth : Login/Signup is managed through Google Auth
Admin pannel: Manage and monitor Godam product listing and  image viewing through admin pannel
Providing review : User can leave review and rank fo godam as they visit
Add to Favourites : user can save the favorite godam to acess easily
Map location: 
Search and Route : Search for  Godam and view the route and distance from your location.
Bill : Access Godam also by available product list
User profile section

# Installation steps for Backend
pip install -r requirements.txt

# Set up the database
python manage.py makemigrations
python manage.py migrate

# Create and admin user
python manage.py createsuperuser

# Run the development server
python manage.py runserver

# open your crome/browser and goto 
localhost:8000/admin to see the admin section 
localhost:8000/api to see the detail in json format
