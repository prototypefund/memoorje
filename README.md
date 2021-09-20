# memoorje

safe, self-determined digital inheritance for everyone.

## Quick Development Setup

Bootstrap your venv and project (you’ll need to do this only once):

```shell
# Create a virtual environment
python3 -m venv --system-site-packages ~/.virtualenvs/memoorje
# Activate your venv
. ~/.virtualenvs/memoorje/bin/activate
# Install dependencies
pip install --editable pylib/memoorje_crypto --editable .
```

In the future just run:
```shell
# Activate your venv
. ~/.virtualenvs/memoorje/bin/activate
# Configure the settings
export DJANGO_SETTINGS_MODULE=memoorje.settings
# Apply database migrations
python3 -m django migrate
```

Start the API development server with:
```shell
python3 -m django runserver
```
