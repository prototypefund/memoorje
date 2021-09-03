# Quick Development Setup

* Enable your local `venv` with project dependencies.
* Set the environment variable `DJANGO_SETTINGS_MODULE` to `memoorje.settings`.
* Create a development database (e.g. `python3 -m django migrate`).

Then you may run the development server:

```shell
python3 -m django runserver
```