# AGENTS.md - Development Guidelines for wlili

This file provides guidance for AI agents working on this codebase.

## Project Overview

- **Type**: Django + Wagtail CMS website
- **Python**: 3.x
- **Database**: SQLite (dev), PostgreSQL (prod)
- **Testing**: pytest + Selenium (functional tests)

---

## Build / Lint / Test Commands

### Django Management

```bash
# Run development server
python manage.py runserver

# Apply migrations
python manage.py migrate

# Create migrations
python manage.py makemigrations

# Collect static files
python manage.py collectstatic --noinput
```

### Running Tests

```bash
# Run all tests
pytest

# Run a single test file
pytest base/tests.py

# Run a single test class
pytest base/tests.py::FooterFunctionalTests

# Run a single test method
pytest base/tests.py::FooterFunctionalTests::test_footer_renders_without_error

# Run unit/integration tests only (excludes functional tests)
pytest -k "not FunctionalTest"

# Run functional tests only (Selenium)
pytest functional_tests/

# Run tests with verbose output
pytest -v

# Run tests without reusing DB
pytest --reuse-db --no-migrateci
```

### Running the Development Server

```bash
python manage.py runserver
```

---

## General behavior
- Atenerse al modo Plan a menos que esté seleccionado explicitamente el modo build
- No aplicar directamente cambios al código, sino presentarlos en pantalla para su revisión. Indicar con un comentario los lugares específicos del código en los que se han hecho cambios.

---

## Code Style Guidelines

### General Principles

- **Minuciosidad controlada**: Balance between quality and progress
- **ATDD**: Write functional tests first, then unit tests
- **Clean code**: Clear names, comments only when essential

### Imports

- **Standard library** first, then **third-party**, then **local**
- Always use absolute imports (no relative imports like `from ..models`)
- Group imports: stdlib, third-party, local
- Imports at the beginning of the file, not local to function, method or class, unless necessary

```python
# Correct
from django.db import models
from wagtail.admin.panels import FieldPanel
from base.models import FooterText
```

### Formatting

- **Line length**: Max 120 characters (follow Django's style)
- **Indentation**: 4 spaces
- **Blank lines**: Two between top-level definitions, one between methods
- **No trailing whitespace**

### Naming Conventions

- **Classes**: `PascalCase` (e.g., `FooterText`, `NavigationSettings`)
- **Functions/methods**: `snake_case` (e.g., `crear_sitio_con_homepage`)
- **Variables**: `snake_case` (e.g., `root_page`, `homepage`)
- **Constants**: `UPPER_SNAKE_CASE`
- **Private members**: Prefix with `_` (e.g., `_get_hostname`)
- **Templates**: Lowercase with underscores (e.g., `footer.html`)
- **URL names**: Lowercase with hyphens (e.g., `wagtailadmin`)

### Django/Wagtail Patterns

- **Models**: Define in `models.py` per app
- **Views**: Use Wagtail's page models (inherit from `Page`)
- **Templates**: Store in `<app>/templates/<app>/`
- **Static files**: Store in `static/<app>/`
- **Settings**: Modular (`settings/base.py`, `settings/dev.py`, `settings/production.py`)
- **Test files**: `tests.py` per app, or `test_*.py`

### Model Definition

```python
@register_setting
class MySettings(BaseGenericSetting):
    field = models.CharField(max_length=255, blank=True)

    panels = [FieldPanel("field")]

    class Meta:
        verbose_name = "my settings"


@register_snippet
class MySnippet(models.Model):
    body = RichTextField()

    panels = [FieldPanel("body")]

    def __str__(self):
        return "My Snippet"
```

### Error Handling

- Use try/except with specific exceptions
- Always chain exceptions: `from exc`
- Raise descriptive `ImportError` messages
- Avoid bare `except:` clauses

### Test Organization

Follow this structure in tests:

1. **Functional tests**: Test from user perspective using templates
2. **Unit tests**: Test models, template tags, views

```python
class MyFunctionalTests(WagtailPageTestCase):
    """Tests from user's perspective."""

    def setUp(self):
        # Create minimal site structure
        ...

    def test_user_sees_expected_content(self):
        response = self.client.get(self.homepage.url)
        self.assertContains(response, "expected")


class MyModelTests(WagtailPageTestCase):
    """Unit tests for models."""

    def test_model_creation(self):
        obj = MyModel(field="value")
        obj.save()
        self.assertEqual(MyModel.objects.count(), 1)
```

### Functional Tests (Selenium)

- Inherit from `FunctionalTestBase`
- Use explicit waits (`wait_for`, `wait_for_text`)
- Take screenshots on failure
- Clean up in `tearDownClass`

### Unit tests:
- Principalmente testean funciones o métodos.
- Los test para un método deben cumplir: 
  - qué valor debe devolver 
  - qué efectos colaterales debe tener
  - en qué casos debe lanzar una excepción
- Deben organizarse en clases o archivos según el método que estén testeando.

Ejemplo trivial:
```python
estado = {"valor": 0}

def funcion(arg):
    estado["valor"] = 2
    if arg < 0:
        raise ValueError("No se acepta valor negativo")
    return arg * estado["valor"]

class TestFuncion(TestCase):
    def test_devuelve_arg_por_2(self):
        self.assertEqual(funcion(2), 4)
    
    def test_asigna_2_a_estado(self):
        estado["valor"] = 1
        funcion(3)
        self.assertEqual(estado["valor"], 2)
    
    def test_no_acepta_valor_negativo(self):
        with self.assertRaises(ValueError):
            funcion(-2)

```

---

## Key Files

| Path | Description |
|------|-------------|
| `wlili/settings/base.py` | Main Django settings |
| `wlili/settings/dev.py` | Development settings |
| `base/models.py` | Core settings snippets |
| `functional_tests/base.py` | Selenium test base class |
| `pytest.ini` | pytest configuration |

---

## Environment Variables

Create `wlili/settings/local.py` for local overrides:

```python
from .dev import *

DEBUG = True
SECRET_KEY = "your-secret-key"
ALLOWED_HOSTS = ["localhost", "127.0.0.1"]
```
