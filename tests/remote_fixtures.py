import json
import os
import requests
from requests.adapters import HTTPAdapter
from urllib.parse import urljoin
from urllib3.util.retry import Retry


class Handle:
    def __init__(self, data):
        self.url = data["url"]
        self.pk = data["pk"]
        self.title = data.get("title")
        self.titulo = data.get("titulo")
        self.descripcion = data.get("descripcion")
        self.block_id = data.get("block_id")


class RemoteProductoFixtures:
    def __init__(self, base_url, token):
        self.base_url = base_url
        self.token = token
        self.home_pk = None

        # Varios intentos de conexión para evitar errores de conectividad
        retry = Retry(
            connect=5,
            read=0,
            status=0,
            redirect=0,
            backoff_factor=1.0,
            allowed_methods=None,
        )
        self.session = requests.Session()
        adapter = HTTPAdapter(max_retries=retry)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

    def _post(self, path, data=None, files=None):
        response = self.session.post(
            urljoin(self.base_url, path),
            data=data,
            files=files,
            headers={"X-Test-Token": self.token},
            timeout=20,
        )
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError:
            print(f"\n[FIXTURE REMOTE 500] {response.url}\n{response.text[:3000]}")
            raise

        return response.json()

    def setup_area(self):
        data = self._post("/__test__/fixtures/area/", {})
        self.home_pk = data["home"]["pk"]
        return Handle(data["area"])

    def setup_producto(self, area_pk, titulo, descripcion):
        data = self._post("/__test__/fixtures/producto/", {
            "area_pk": area_pk,
            "titulo": titulo,
            "descripcion": descripcion,
        })
        return Handle(data["producto"])

    def crear_elemento(
            self, producto_pk, tipo, titulo, alt_thumbnail="",
            page_data=None, thumbnail=None):
        data = {
            "producto_pk": producto_pk,
            "tipo": tipo,
            "titulo": titulo,
            "alt_thumbnail": alt_thumbnail,
        }

        files = {}

        if thumbnail is not None:
            path = getattr(thumbnail, "path", None)
            if path:
                fobj = open(path, "rb")
                files["thumbnail"] = (
                    os.path.basename(path),
                    fobj,
                    "image/png"
                )

        if page_data:
            clean_page_data = {}
            for key, value in page_data.items():
                path = getattr(value, "path", None)
                if path:
                    fobj = open(path, "rb")
                    ct = "image/png" if key == "thumbnail" else "application/octet-stream"
                    files[key] = (os.path.basename(path), fobj, ct)
                else:
                    clean_page_data[key] = value
            page_data = clean_page_data

        if page_data:
            data["page_data"] = json.dumps(page_data)

        try:
            data = self._post("/__test__/fixtures/producto/elemento/", data, files)
            return Handle(data)
        finally:
            for f in files.values():
                f[1].close()

    def area_con_productos(
            self, area_pk, producto_pk, nombre, descripcion, imagen_path):
        fobj = open(imagen_path, "rb")
        files = {"imagen": (os.path.basename(imagen_path), fobj, "image/png")}
        data = {
            "area_pk": area_pk,
            "producto_pk": producto_pk,
            "nombre": nombre,
            "descripcion": descripcion or "",
        }

        try:
            return Handle(self._post("/__test__/fixtures/area/productos/", data, files))
        finally:
            fobj.close()

    def cleanup(self):
        if self.home_pk:
            self._post("/__test__/fixtures/producto/cleanup/", {"home_pk": self.home_pk})
            self.home_pk = None
