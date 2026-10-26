# Labour Management Django Project

Python/Django repository. Its `manage.py` entry point refers to the `labour_project.settings` settings module.

## Verified structure

- Django management entry point: `manage.py`
- Configured settings module: `labour_project.settings`

## Local development

Clone the repository and open its root directory:

```bash
python -m venv .venv
```

Activate the virtual environment and install the dependencies compatible with this project (use `pip install -r requirements.txt` if the file exists). Review settings and database configuration, then execute:

```bash
python manage.py migrate
python manage.py runserver
```

## Further documentation

Check Django URL routes, views, models and templates to identify supported features and roles. The app has not been run or functionally tested during this README update. Keep credentials and personal data out of version control.
