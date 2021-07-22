To set this up, go into your virtual environment if needed, if and then check this out into some folder:
```
cd ...wherever...
git clone https://github.com/mj-jahangiri/test.git
cd test
pip3 install -r requirements.txt
```
Create a postgres database and then Open the settings.py file and enter your postgres information in the (DATABASES) field.

Create the database:

`python manage.py migrate`


Finally, run the development server:

`python manage.py runserver`

