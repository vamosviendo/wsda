import json
import os
import requests
from urllib.parse import urljoin


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

    def _post(self, path, data=None, files=None):
        response = requests.post(
            urljoin(self.base_url, path),
            data=data,
            files=files,
            headers={"X-Test-Token": self.token},
            timeout=(20),
        )
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError:
            print(f"\n[FIXTURE REMOTE 500] {response.url}\n{response.text[:3000]}")
            raise

        return response.json()

    def setup(self, titulo, descripcion):
        data = self._post("/__test__/fixtures/producto/", {
            "titulo": titulo,
            "descripcion": descripcion,
        })
        self.home_pk = data["home"]["pk"]
        return Handle(data["area"]), Handle(data["producto"])

    def crear_elemento(
            self, producto_pk, tipo, titulo, alt_thumbnail="",
            page_data=None, thumbnail_path=None):
        data = {
            "producto_pk": producto_pk,
            "tipo": tipo,
            "titulo": titulo,
            "alt_thumbnail": alt_thumbnail,
        }
        if page_data:
            data["page_data"] = json.dumps(page_data)

        files = None
        fobj = None
        if thumbnail_path:
            # files = {"thumbnail": open(thumbnail_path, "rb")}
            fobj = open(thumbnail_path, "rb")
            files = {"thumbnail": (
                os.path.basename(thumbnail_path),
                fobj,
                "image/png",
            )}

        try:
            return Handle(self._post("/__test__/fixtures/producto/elemento/", data, files))
        finally:
            # if files:
            #     files["thumbnail"].close()
            if fobj:
                fobj.close()

    def cleanup(self):
        if self.home_pk:
            self._post("/__test__/fixtures/producto/cleanup/", {"home_pk": self.home_pk})
            self.home_pk = None
