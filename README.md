# Bubble

Bubble is a website which which aims to make visitors discover topics they may never had the possiblity to encounter due
to the [Filter bubble](https://en.wikipedia.org/wiki/Filter_bubble) phenomenon

The website display a random video (using the Random.org API) from the differents links submitted by visitors.
To fill the database with new interesting videos, it is required to submit a video you find interessting in order to get 
random video someone else found interesting and submited in order to get 
random video someone else found interesting and submited in order to get 
random video someone else found interesting and submited etc...

Bubble is written in Python 3 with Django, HTML5 and CSS3.

## External resources

The project rely on Random.org API.

## Dependencies

Use the package manager [pip](https://pip.pypa.io/en/stable/) to 
install all the dependencies. Here are the steps :

1. Open the command prompt.  
2. cd to the directory where requirements.txt is located.  
3. Run this command in your shell:  

```bash
pip install -r requirements.txt
```


## Configuration :

You will need to provide theses environment variables :

SECRET_KEY : the Django secret key  
DEBUG_PROD : The value should be False  
DEBUG : The value should be True  
DB_NAME : The name of the database  
DB_USER : The user associated to the database  
DB_PASSWORD : The password associated to the user  
DB_HOST : Host of your database  
RANDOM_API_KEY= The Random.org API Key  
CAPTCHA_SECRET_KEY= A secret key (4 is enough) which helps encrypt the captcha value before it's stored in user session  
SENTRY_DSN : The sentry url used to monitor the app

Once transferred to your host, you will need to use theses commands:

   
1°) _In order to set the database:_    
```bash
python3 manage.py makemigrations

python3 manage.py migrate 
```

2°) _Then we take care of the static files:_
```bash
python3 manage.py collectstatic
```
It may give you a warning, don't worry just say yes:
```bash
You have requested to collect static files at the destination
location as specified in your settings:

    [...]/core/static

This will overwrite existing files!
Are you sure you want to do this?

```
3°) _We then need to create a superuser:_
```bash
python3 manage.py createsuperuser
```

You're now good to go. Nevertheless we advise you to "prime" the website by filling the database with some videos you 
deem interesting so that first users get some interesting videos which will encourage them to see more and therefore 
post some more videos etc...

## Contributing
Pull requests are welcome. For major changes, please open an issue first to 
discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[Copyleft](https://www.gnu.org/licenses/copyleft.fr.html)