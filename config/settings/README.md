# Settings

Settings for the project are split into different files based on the specific aspect being configured.
There is a trade-off here, losing the ability to see all the environment specific settings that have been
applied in one place. This is traded in favor of having a more easily discoverable settings hierachy.
If new dependencies are added which also need to be configured via the settings, it is preferable to have it have
its own settings file.

## Convention

### 1. The `__init__.py` file

All settings are imported as wildcard imports in the `__init__.py` file e.g.:

```python
from .authentication import *
from .database import *
...
```

If a new settings file is added, it should also be imported here in a similar manner.

No environment specific overrides should happen in this file. Instead, those should happen inside each specific settings
file.

### 2. The settings file(s)

**1. Description**

Each settings file starts with a block comment section that describes the settings in the file, adds any necessary
documentation links, and lists out the environment variables that affect that setting.

Example:

```python
# ------------------------------------------------------------------------------------------------
# DATABASE SETTINGS
#
# Environment variables used:
#   DB_NAME           - Name of the database
#   DB_USER           - Database username
#   DB_PASSWORD       - Database user password
#   DB_HOST           - Database host address
#   DB_PORT           - Database port
#   DB_SSL_MODE       - (Optional) SSL mode for database connection (e.g., 'require', 'disable')
#   DB_SSL_ROOT_CERT  - (Optional) Path to the SSL root certificate file
# ------------------------------------------------------------------------------------------------
```

**2. Imports**

Try to minimize the imports you need to make in settings files. Most of the django framework components (like models)
need settings to be initialized and won't work well if imported here.

**3. Setting options**

Unless the library specifically requires otherwise, settings are typically defined in all capital letters.
The setting can also include any setting specific documentation links for easy reference. This is preferred over adding
a comment with all possible options that the setting can take, unless it's a project specific custom setting.

Example:

```python
# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
```

**4. `__all__` object**

At the bottom of the file, you should add an __all__ object that defined all the settings that should be made available.
While this is not mandatory, it is preferred since there will be a wildcard import of the file, and it is preferable not
to import anything that wasn't intended to be used as a setting.
