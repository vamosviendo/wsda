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
        self.compuesto = data.get("compuesto")


class RemoteProductoFixtures:
    def __init__(self, base_url, token):
        self.base_url = base_url
        self.token = token
        self.homepage_original_body = None
        self.cleanup_pks = []
        self.imagen_pks = []
        self.documento_pks = []

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
            print(f"\n[FIXTURE REMOTE ERROR] {response.url}\n{response.text[:3000]}")
            raise

        return response.json()

    def set_homepage_franja(self, area_url, imagen_path):
        fobj = open(imagen_path, 'rb')
        files = {"imagen": (os.path.basename(imagen_path), fobj, "image/png")}
        data = {"area_url": area_url}
        try:
            response = self._post("/__test__/fixtures/homepage/", data, files)
        finally:
            fobj.close()

        self.homepage_original_body = response.get("original_body")
        if response.get("imagen_pk"):
            self.imagen_pks.append(response["imagen_pk"])
        return Handle(response)

    def setup_area(self):
        data = self._post("/__test__/fixtures/area/", {})
        self.cleanup_pks.append(data["home"]["pk"])
        return Handle(data["area"])

    def setup_elemento_compuesto(self, padre_pk, titulo, descripcion):
        data = self._post("/__test__/fixtures/elemento/compuesto/", {
            "padre_pk": padre_pk,
            "titulo": titulo,
            "descripcion": descripcion,
        })
        return Handle(data["elemento"])

    def crear_elemento(
            self, padre_pk, tipo, titulo, alt_thumbnail="",
            compuesto=False, page_data=None, thumbnail=None):
        data = {
            "padre_pk": padre_pk,
            "tipo": tipo,
            "titulo": titulo,
            "alt_thumbnail": alt_thumbnail,
            "compuesto": str(compuesto).lower(),
        }

        files = {}

        if thumbnail is not None:
            path = getattr(thumbnail, "path", None)
            if path:
                fobj = open(path, "rb")
                files["thumbnail"] = (
                    os.path.basename(path), fobj, "image/png"
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
            data = self._post("/__test__/fixtures/elemento/", data, files)
            self.imagen_pks.extend(data.get("imagenes") or [])
            self.documento_pks.extend(data.get("documentos") or [])
            return Handle(data)
        finally:
            for f in files.values():
                f[1].close()

    def crear_pagina_simple(
            self, tipo, title, page_data=None, show_in_menus=False):
        data = {"tipo": tipo, "title": title}
        if page_data:
            data["page_data"] = json.dumps(page_data)
        if show_in_menus:
            data["show_in_menus"] = "true"
        handle = Handle(self._post("/__test__/fixtures/pagina/", data))
        self.cleanup_pks.append(handle.pk)
        return handle

    def crear_curriculum(self,
            title="Curriculum",
            entradas=None,
            show_in_menus=False):
        data = {"title": title}
        if show_in_menus:
            data["show_in_menus"] = "true"
        if entradas:
            data["entradas"] = json.dumps(entradas)
        handle = Handle(self._post("/__test__/fixtures/curriculum/", data))
        self.cleanup_pks.append(handle.pk)
        return handle

    def cleanup(self):
        for pk in reversed(self.cleanup_pks):
            self._cleanup_pk(pk)
        self.cleanup_pks = []
        if self.homepage_original_body is not None:
            self._post(
                "/__test__/fixtures/homepage/cleanup/",
                {"original_body": json.dumps(self.homepage_original_body)}
            )
            self.homepage_original_body = None
        if self.imagen_pks or self.documento_pks:
            self._post("/__test__/fixtures/media/cleanup/", {
                "imagen_pks": json.dumps(self.imagen_pks),
                "documento_pks": json.dumps(self.documento_pks),
            })
            self.imagen_pks = []
            self.documento_pks = []

    def _cleanup_pk(self, pk):
        self._post("/__test__/fixtures/pagina/cleanup/", {"pk": pk})
