# AGENTS.md - Development Guidelines for wlili

Este archivo complementa el `AGENTS.md` global
(`~/.config/opencode/AGENTS.md`). Aquí vive sólo lo específico del
proyecto. Ante conflicto, este archivo tiene prioridad sobre el global.

## Project Overview

- **Type**: Django + Wagtail CMS website
- **Python**: 3.x
- **Database**: SQLite (dev), PostgreSQL (prod)
- **Testing**: pytest + Selenium (functional tests)

## Modo de trabajo — nota local

- En este proyecto el modo build es excepcional. Rara vez se seleccionará,
  y los cambios siempre serán presentados para revisión antes de aplicarse.

## Build / Lint / Test Commands

### Django Management

```bash
python manage.py runserver
python manage.py migrate
python manage.py makemigrations
python manage.py collectstatic --noinput
```

### Running Tests

```bash
pytest                                                        # all
pytest tests/test.py                                          # single file
pytest tests/test.py::FooterFunctionalTests                   # single class
pytest tests/test.py::FooterFunctionalTests::test_footer_renders_without_error
pytest tests/test.py::test_footer_renders_without_error
pytest tests/unit                                             # unit/integration only
pytest tests/functional                                       # functional only
pytest -v
pytest --reuse-db --no-migrateci
```

### Running Functional Tests Against Staging (Remote Fixtures)

Los functional tests pueden ejecutarse contra el staging server. Cuando
`TEST_SERVER` está definido, los fixtures **no crean datos vía ORM
local**; en su lugar, llaman a **endpoints HTTP** del server remoto que
crean datos reales en staging. El navegador (Selenium) apunta a staging,
no al `live_server` local.

```bash
DJANGO_TEST_TOKEN="<token>" \
TEST_SERVER=staging.lilianamedela.com.ar \
DJANGO_TEST_ADMIN_USERNAME=admin \
DJANGO_TEST_ADMIN_PASSWORD="<password>" \
.vwlili/bin/pytest tests/functional/<archivo>.py
```

Variables de entorno:

- `TEST_SERVER` — URL del server remoto. Si está presente, activa el modo remoto.
- `DJANGO_TEST_TOKEN` — token que autentica los endpoints de test (`X-Test-Token`). Sin él, los endpoints no se registran.
- `DJANGO_TEST_ADMIN_USERNAME` / `DJANGO_TEST_ADMIN_PASSWORD` — credenciales para crear el admin remoto (usado por algunos tests).

Arquitectura (3 capas):

- **Server** — `src/utils/remote_test_fixtures.py`: vistas `@_safe_json` (aplican `@csrf_exempt` + `@require_POST` + `_check_test_token`). Registradas en `src/utils/urls.py`, incluidas en `src/wlili/urls.py` solo bajo `if os.environ.get("DJANGO_TEST_TOKEN")`. Retornan JSON; ante error devuelven el traceback en `{"error", "traceback"}`.
- **Cliente** — `tests/remote_fixtures.py`: clase `RemoteProductoFixtures` con métodos por fixture (crean páginas vía HTTP) y `Handle` (objeto liviano con `.url`, `.pk`, `.title`, `.titulo`, `.descripcion`, `.block_id`). Usa `requests.Session` con `Retry(connect=5)` para tolerar conectividad intermitente.
- **Fixtures** — en `tests/conftest.py`, cada fixture hace:

```python
if os.environ.get("TEST_SERVER"):
    return remote_fixtures.<metodo_remoto>()
# ... lógica ORM local
```

Endpoints disponibles (ruta → función → propósito):

| Ruta | Función | Propósito |
|---|---|---|
| `__test__/fixtures/area/` | `fixtures_area` | Crea test-home + area; cuelga del site `root_page` |
| `__test__/fixtures/producto/` | `fixtures_producto` | Crea producto bajo un `area_pk` |
| `__test__/fixtures/producto/elemento/` | `fixtures_producto_elemento` | Agrega un elemento al producto |
| `__test__/fixtures/area/productos/` | `fixtures_area_productos` | Rellena el StreamField `productos` del área (imagen + link) |
| `__test__/fixtures/pagina/` | `fixtures_pagina_simple` | Crea `AcercaDePage`/`ContactPage` bajo `site.root_page` (slug con uuid) |
| `__test__/fixtures/curriculum/` | `fixtures_curriculum` | Crea `CurriculumPage` con entradas (StreamField) |
| `__test__/fixtures/homepage/` | `fixtures_homepage` | Configura la homepage real con una franja; captura el body original |
| `__test__/fixtures/homepage/cleanup/` | `fixtures_homepage_cleanup` | Restaura el body original de la homepage |
| `__test__/fixtures/pagina/cleanup/` | `fixtures_pagina_cleanup` | Borra una página por pk |
| `__test__/fixtures/producto/cleanup/` | `fixtures_producto_cleanup` | Borra el test-home (y su subtree) por `home_pk` |

Navegación vs URL directa:

- Páginas accedidas desde el menú (`AcercaDePage`, `ContactPage`, `CurriculumPage`, `HomePage`) cuelgan del `site.root_page` real de staging (`show_in_menus=True`, slug con uuid).
- Páginas accedidas por URL directa (`AreaPage`, `ProductoPage`, `ElementoPage`) cuelgan de un `test-home-<uuid>` aislado.

Cleanup: El fixture `remote_fixtures` (teardown) llama `client.cleanup()`, que:

- Borra páginas de contenido por pk (`cleanup_pks`).
- Borra el test-home por `home_pk`.
- Restaura el body original de la homepage (`homepage_original_body`).

Reglas de diseño (importante):

- `test_page` (factory de `tests/conftest.py`) **NO** debe volverse remoto-consciente. Es un factory de ORM local usado por tests unitarios. Los functional tests que crean datos deben usar fixtures remotos específicos.
- Los endpoints aceptan una lista blanca de modelos (e.g. `SIMPLE_PAGE_TYPES`) y validan `issubclass(model, Page)`; no aceptan nombres de modelo arbitrarios.
- Los tests que dependen del ORM (consultas a modelos, mutación de objetos) no funcionan en remoto y deben refactorizarse a asserts puramente de template.

### Running the Development Server

```bash
python manage.py runserver
```

*Nota:* Buscar estos y otros comandos en Makefile

## Convenciones locales del proyecto

### Tests

- La ubicación canónica para los tests es `tests/`. Los tests alojados en
  directorios dentro de las aplicaciones, así como los alojados en
  `functional_tests/` (basados en unittest) son obsoletos y no deben ser
  tenidos en cuenta.
- Los functional tests heredan de `tests.functional.base.MiFirefox` (con
  `base_url`).
- Usan `browser.wait_for`, `browser.wait_fors`, `browser.wait_for_not`
  (waits explícitos).
- `browser.get_page()` reintenta ante `about:neterror` (conectividad
  intermitente a staging).
- Para ejecutarlos contra staging, ver "Running Functional Tests Against
  Staging (Remote Fixtures)".

### Model Definition — ejemplos del proyecto

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

### CSS y estáticos

- Estilos globales: `src/wlili/static/css/{base,header,footer}.css`,
  enlazados en `src/wlili/templates/base.html`.
- Estilos por página: `src/<app>/static/css/*.css`, cargados con
  `{% block extra_css %}`.
- Tokens de diseño: CSS custom properties definidas en `base.css`.
- `src/static/` es `STATIC_ROOT`: se genera con `collectstatic` y está
  ignorado. No editar a mano.
- No hay build de Sass. No agregar SCSS sin un plan de migración explícito.

## Key Files

| Path | Description |
|---|---|
| `wlili/settings/base.py` | Main Django settings |
| `wlili/settings/dev.py` | Development settings |
| `base/models.py` | Core settings snippets |
| `functional_tests/base.py` | Selenium test base class |
| `pytest.ini` | pytest configuration |
| `src/media` | directorio canónico de media (alineado con `MEDIA_ROOT` y con el bind mount de producción `~/sites/wlili/media:/src/media`) |
| `src/db.sqlite3` | SQLite database file (alineado con `DATABASE_URL`). Es la DB que usa el runserver. |

- El sync local <-> server usa `src/`, no la raíz.

## Environment Variables

Create `wlili/settings/local.py` for local overrides:

```python
from .dev import *

DEBUG = True
SECRET_KEY = "your-secret-key"
ALLOWED_HOSTS = ["localhost", "127.0.0.1"]
```

## Deployment

- El sitio se encuentra alojado en un droplet de Digital Ocean con Ubuntu 20.04 LTS.
- El dominio (y la url de producción del sitio) es `lilianamedela.com.ar`. La url de staging es `staging.lilianamedela.com.ar`.
- Datos del sitio en server remoto (base de datos, archivos de media, etc.) en `/home/vv/sites/wlili`.
- Datos del sitio staging en server remoto en `/home/vv/sites/wlili-staging`.