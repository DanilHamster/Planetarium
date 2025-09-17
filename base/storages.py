import os

from django.core.cache import cache
from storages.backends.dropbox import DropboxStorage
from storages.utils import safe_join


class WindowsCompatibleDropboxStorage(DropboxStorage):
    def _full_path(self, name):
        if name == "/":
            name = ""

        name = name.lstrip("/")

        if self.root_path and name.startswith(self.root_path + "/"):
            name = name[len(self.root_path) + 1 :]

        root = self.root_path.strip("/\\") if self.root_path else ""

        full_path = (
            os.path.join("/", root, name)
            if os.name == "nt"
            else f"/{root}/{name}"
        )
        return full_path.replace("\\", "/").replace("//", "/")

    @staticmethod
    def _get_cache_key(name):
        return f"dropbox:media:{name}"

    def url(self, name):
        name = self._full_path(name)
        if not name.startswith("/"):
            name = "/" + name

        cache_key = self._get_cache_key(name)
        link = cache.get(cache_key)
        if link:
            return link
        link = super().url(name)
        cache.set(cache_key, link, timeout=4 * 60 * 60)
        return link
