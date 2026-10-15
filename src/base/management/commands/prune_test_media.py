from django.core.management.base import BaseCommand

from utils.remote_test_fixtures import (
    _prune_test_media, _prune_test_pages_remnant,
    _test_media_candidatos, _test_pages_candidatos,
)


class Command(BaseCommand):
    help = "Elimina páginas e imágenes/documentos creados por tests remotos (red de seguridad)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run", action="store_true",
            help="Lista de lo que se borrará, sin borrar nada."
        )

    def handle(self, *args, **options):
        paginas = _test_pages_candidatos()
        imagenes, documentos = _test_media_candidatos()
        if options["dry_run"]:
            self.stdout.write(f"Páginas: {paginas.count()}  Imágenes: {len(imagenes)}  Documentos: {len(documentos)}")
            for p in paginas:
                self.stdout.write(f"  [page] {p.pk}  {p.slug}")
            for img in imagenes:
                self.stdout.write(f"  [img] {img.pk}  {img.title}  ({img.file.name})")
            for doc in documentos:
                self.stdout.write(f"  [doc] {doc.pk}  {doc.title}  ({doc.file.name})")
            self.stdout.write(self.style.WARNING("dry-run: no se eliminó nada"))
            return

        n_pag = _prune_test_pages_remnant()
        n_img, n_doc = _prune_test_media()
        self.stdout.write(self.style.SUCCESS(
            f"Eliminados: {n_pag} páginas, {n_img} imágenes, {n_doc} documentos"
        ))