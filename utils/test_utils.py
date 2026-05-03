from wagtail.models import Page, Site

from home.models import HomePage
from produccion.models import ElementoPage


# ============================================================
# Fixture compartida entre test classes
# ============================================================

def crear_estructura_basica(test_case):
    """
    Crea la estructura mínima necesaria:
      root → site (testsite)
           → homepage
    Devuelve (root_page, homepage).
    Llama a esto en setUp() de cada clase.
    """
    root_page = Page.get_first_root_node()
    homepage = HomePage(title="Home")
    root_page.add_child(instance=homepage)
    Site.objects.update_or_create(
        hostname="testsite",
        defaults={
            "root_page": homepage,
            "is_default_site": True,
            "site_name": "Liliana Medela",
        },
    )
    return root_page, homepage


def get_elemento_por_block_id(producto_page, block_id):
    return next(
        e for e in producto_page.get_children().specific() if str(e.block_id) == str(block_id)
    )
