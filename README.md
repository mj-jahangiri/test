1)To set this up, go into your virtual environment if needed, if and then check this out into some folder:
```
cd ...wherever...
git clone https://github.com/mj-jahangiri/test.git
cd test
pip install -r requirements.txt
```
2)Create a postgres database and then Open the settings.py file and enter your postgres information in the (DATABASES) field.

3)Create the database:

```
python manage.py makemigrations
python manage.py migrate
```


4)Finally, run the development server:

`python manage.py runserver`

