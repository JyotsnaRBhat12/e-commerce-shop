# Deployment Guide: E-Commerce Shop

This guide outlines the steps taken to deploy the Django E-Commerce backend to Render, configure a production PostgreSQL database, set up environment variables, and configure AWS S3 for media storage.

## 1. Hosting & Infrastructure (Render)
The application is deployed on **Render** using a Web Service and a managed PostgreSQL database.

### Prerequisites:
- A GitHub repository containing the Django project.
- A Render.com account.
- An AWS account (for S3 media storage).

## 2. Setting Up the Production Database
Render uses PostgreSQL for production instead of the local SQLite database used during development.

1. In the Render Dashboard, create a new **PostgreSQL Database**.
2. Copy the **Internal Database URL** provided by Render.
3. In `settings.py`, the `dj-database-url` package is used to dynamically parse this URL:
   ```python
   import dj_database_url
   import os
   
   database_url = os.environ.get('DATABASE_URL', '').strip()
   if not database_url:
       database_url = f"sqlite:///{BASE_DIR / 'db.sqlite3'}"
   
   DATABASES = {
       'default': dj_database_url.parse(database_url, conn_max_age=600)
   }
   ```

## 3. Environment Variables Configuration
To keep secrets safe, sensitive information is supplied to the Render Web Service via Environment Variables rather than hardcoding them in the repository.

Navigate to the **Environment** tab in your Render Web Service and configure the following:
- `DATABASE_URL`: Your Render PostgreSQL Internal URL.
- `SECRET_KEY`: A long, random cryptographic string.
- `DEBUG`: `False` (Disables the developer error pages).
- `ALLOWED_HOSTS`: `<your-app-name>.onrender.com`
- `AWS_ACCESS_KEY_ID`: Your AWS IAM User access key.
- `AWS_SECRET_ACCESS_KEY`: Your AWS IAM User secret.
- `AWS_STORAGE_BUCKET_NAME`: The name of your S3 bucket.

## 4. Serving Static and Media Files

### Static Files (WhiteNoise)
Static files (CSS, JS, Admin styling) are served using the `whitenoise` middleware, which is fast and requires no external servers.
1. Make sure `whitenoise` is in `requirements.txt`.
2. Ensure `whitenoise.middleware.WhiteNoiseMiddleware` is in the `MIDDLEWARE` setting.
3. Configure `STATIC_ROOT = BASE_DIR / 'staticfiles'` to collect files during the build.

### Media Files (AWS S3) - Bonus Requirement
Because Render's disk is ephemeral (it resets on every deploy), user-uploaded product images must be stored externally.

1. Ensure `boto3` and `django-storages` are in `requirements.txt`.
2. Add `'storages'` to `INSTALLED_APPS`.
3. The following configuration connects Django to AWS S3:
   ```python
   AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')   
   AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
   AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')
   
   if AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY:
       AWS_S3_REGION_NAME = 'us-east-1' 
       AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
       DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
   ```

## 5. Build and Start Commands
In Render, the Web Service is configured with the following commands:
- **Build Command:** 
  `pip install -r requirements.txt && python manage.py collectstatic --no-input && python manage.py migrate`
- **Start Command:** 
  `gunicorn shop.wsgi:application`

Once deployed to Render, an admin user must be created using the Render Shell (`python manage.py createsuperuser`) to begin adding products to the new production database.
