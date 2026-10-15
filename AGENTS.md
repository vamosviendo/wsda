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
pytest tests/test.py

# Run a single test class
pytest tests/test.py::FooterFunctionalTests

# Run a single test method
pytest tests/test.py::FooterFunctionalTests::test_footer_renders_without_error

# Run a single test method outside of a class
pytest tests/test.py::test_footer_renders_without_error

# Run unit/integration tests only (excludes functional tests)
pytest tests/unit

# Run functional tests only (Selenium)
pytest tests/functional

# Run tests with verbose output
pytest -v

# Run tests without reusing DB
pytest --reuse-db --no-migrateci
```

### Running Functional Tests Against Staging (Remote Fixtures)

Los functional tests pueden ejecutarse contra el staging server. Cuando `TEST_SERVER`
está definido, los fixtures **no crean datos vía ORM local**; en su lugar, llaman a
**endpoints HTTP** del server remoto que crean datos reales en staging. El navegador
(Selenium) apunta a staging, no al `live_server` local.

```bash
DJANGO_TEST_TOKEN="<token>" \
TEST_SERVER=staging.lilianamedela.com.ar \
DJANGO_TEST_ADMIN_USERNAME=admin \
DJANGO_TEST_ADMIN_PASSWORD="<password>" \
.vwlili/bin/pytest tests/functional/<archivo>.py
```
Variables de entorno:

    TEST_SERVER — URL del server remoto. Si está presente, activa el modo remoto.
    DJANGO_TEST_TOKEN — token que autentica los endpoints de test (X-Test-Token). Sin él, los endpoints no se registran.
    DJANGO_TEST_ADMIN_USERNAME / DJANGO_TEST_ADMIN_PASSWORD — credenciales para crear el admin remoto (usado por algunos tests).

Arquitectura (3 capas):

    Server — src/utils/remote_test_fixtures.py: vistas @_safe_json (aplican @csrf_exempt + @require_POST + _check_test_token). Registradas en src/utils/urls.py, incluidas en src/wlili/urls.py solo bajo if os.environ.get("DJANGO_TEST_TOKEN"). Retornan JSON; ante error devuelven el traceback en {"error", "traceback"}.
    Cliente — tests/remote_fixtures.py: clase RemoteProductoFixtures con métodos por fixture (crean páginas vía HTTP) y Handle (objeto liviano con .url, .pk, .title, .titulo, .descripcion, .block_id). Usa requests.Session con Retry(connect=5) para tolerar conectividad intermitente.
    Fixtures — en tests/conftest.py, cada fixture hace:

```python
    if os.environ.get("TEST_SERVER"):
        return remote_fixtures.<metodo_remoto>()
# ... lógica ORM local
```
Endpoints disponibles (ruta → función → propósito):

Ruta 	Función 	Propósito

- /\_\_test__/fixtures/area/ 	fixtures_area 	Crea test-home + area; cuelga del site root_page
- /\_\_test__/fixtures/producto/ 	fixtures_producto 	Crea producto bajo un area_pk
- /\_\_test__/fixtures/producto/elemento/ 	fixtures_producto_elemento 	Agrega un elemento al producto
- /\_\_test__/fixtures/area/productos/ 	fixtures_area_productos 	Rellena el StreamField productos del área (imagen + link)
- /\_\_test__/fixtures/pagina/ 	fixtures_pagina_simple 	Crea AcercaDePage/ContactPage bajo site.root_page (slug con uuid)
- /\_\_test__/fixtures/curriculum/ 	fixtures_curriculum 	Crea CurriculumPage con entradas (StreamField)
- /\_\_test__/fixtures/homepage/ 	fixtures_homepage 	Configura la homepage real con una franja; captura el body original
- /\_\_test__/fixtures/homepage/cleanup/ 	fixtures_homepage_cleanup 	Restaura el body original de la homepage
- /\_\_test__/fixtures/pagina/cleanup/ 	fixtures_pagina_cleanup 	Borra una página por pk
- /\_\_test__/fixtures/producto/cleanup/ 	fixtures_producto_cleanup 	Borra el test-home (y su subtree) por home_pk

Navegación vs URL directa:

    Páginas accedidas desde el menú (AcercaDePage, ContactPage, CurriculumPage, HomePage) cuelgan del site.root_page real de staging (show_in_menus=True, slug con uuid).
    Páginas accedidas por URL directa (AreaPage, ProductoPage, ElementoPage) cuelgan de un test-home-<uuid> aislado.

Cleanup: El fixture remote_fixtures (teardown) llama client.cleanup(), que:

    Borra páginas de contenido por pk (cleanup_pks).
    Borra el test-home por home_pk.
    Restaura el body original de la homepage (homepage_original_body).

Reglas de diseño (importante):

    test_page (factory de tests/conftest.py) NO debe volverse remoto-consciente. Es un factory de ORM local usado por tests unitarios. Los functional tests que crean datos deben usar fixtures remotos específicos.
    Los endpoints aceptan una lista blanca de modelos (e.g. SIMPLE_PAGE_TYPES) y validan issubclass(model, Page); no aceptan nombres de modelo arbitrarios.
    Los tests que dependen del ORM (consultas a modelos, mutación de objetos) no funcionan en remoto y deben refactorizarse a asserts puramente de template.


### Running the Development Server

```bash
python manage.py runserver
```

---

## General behavior
- Atenerse al modo Plan a menos que esté seleccionado explicitamente el modo build
- No aplicar directamente cambios al código, sino presentarlos en pantalla para su revisión. Indicar con un comentario los lugares específicos del código en los que se han hecho cambios.
- Cuando falte información, solicitarla. Comprobar en vez de inferir o suponer. Empiria.
- No vamos a salir del modo Plan nunca, o lo haremos en muy raras ocasiones. Los cambios siempre serán presentados, y yo, el humano, me encargaré de aplicalos luego de haberlos revisado.
- Al presentar un código modificado, deben señalarse los cambios que se han hecho mediante comentarios. Los comentarios no deben estar al principio del módulo, clase o función cambiado sino siguiendo estos lineamientos:
  - En caso de que se modifique una línea, el comentario que marca el cambio debe estar al costado de esa línea.
  - En caso de que se modifique un bloque de líneas, el comentario que marca el cambio debe estar inmediatamente antes del bloque modificado.

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
3. Los tests deben basarse en pytest.
4. La ubicación canónica para los test es tests/, Los tests alojados en directorios dentro de las aplicaciones, así como los alojados en functional_tests/ (basados en unittest) son obsoletos y no deben ser tenidos en cuenta.
5. Presentar primero functional tests, luego unit tests.

### Functional Tests (Selenium)

- Heredan de `tests.functional.base.MiFirefox` (con `base_url`).
- Usan `browser.wait_for`, `browser.wait_fors`, `browser.wait_for_not` (waits explícitos).
- `browser.get_page()` reintenta ante `about:neterror` (conectividad intermitente a staging).
- Para ejecutarlos contra staging, ver "Running Functional Tests Against Staging (Remote Fixtures)".

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

| Path                       | Description                                                                                                                   |
|----------------------------|-------------------------------------------------------------------------------------------------------------------------------|
| `wlili/settings/base.py`   | Main Django settings                                                                                                          |
| `wlili/settings/dev.py`    | Development settings                                                                                                          |
| `base/models.py`           | Core settings snippets                                                                                                        |
| `functional_tests/base.py` | Selenium test base class                                                                                                      |
| `pytest.ini`               | pytest configuration                                                                                                          |
| `src/media`                | directorio canónico de media (alineado con MEDIA_ROOT y con el bind mount de production ```~/sites/wlili/media:/src/media```) |
| `src/db.sqlite3`           | SQLite database file (alineado con DATABASE_URL). Es la DB que usa el runserver.                                              |

- El sync local <-> server usa src/, no la raíz.

---

## Environment Variables

Create `wlili/settings/local.py` for local overrides:

```python
from .dev import *

DEBUG = True
SECRET_KEY = "your-secret-key"
ALLOWED_HOSTS = ["localhost", "127.0.0.1"]
```

## Deployment

- El sitio se encuentra alojado en un droplet de Digital Ocean con Ubuntu 20.04 LTS
- El dominio (y la url de producción del sitio) es lilianamedela.com.ar. La url de staging es staging.lilianamedela.com.ar
- Datos del sitio en server remoto (base de datos, archivos de media, etc.) en /home/vv/sites/wlili
- Datos del sitio staging en server remoto en /home/vv/sites/wlili-staging

