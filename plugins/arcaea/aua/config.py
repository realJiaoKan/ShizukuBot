from typing import Optional, Any
from pathlib import Path
from ruamel import yaml

Config_path = Path(__file__).parent.absolute() / "config.yml"

New_map = {
    "aua_url": "https://server.awbugl.top/botarcapi",
    "aua_ua": "shizukuBot6H3E2C5M8S",
    "src_url": "https://api.ritsuki.top/api",
}


class ConfigsManager:
    def __init__(self, file: Path):
        self._data: dict = {}
        self._path: str = file
        if not self._path:
            self._path = Config_path
        self._file: str = Path(self._path)
        if self._file.is_file():
            with open(self._path, "r", encoding="utf8") as f:
                self._data = yaml.load(f, Loader=yaml.Loader)
        else:
            self._file.parent.mkdir(exist_ok=True, parents=True)
            with open(self._path, "w", encoding="utf-8") as f:
                yaml.dump(New_map, f, Dumper=yaml.RoundTripDumper)

            with open(self._path, "r", encoding="utf8") as f:
                self._data = yaml.load(f, Loader=yaml.Loader)

    def get_config(self, key: str, default: Optional[Any] = None) -> Optional[Any]:

        if key in self._data.keys() and self._data[key] is not None:
            return self._data[key]
        if default is not None:
            self._data[key] = default
        self._data[key] = New_map[key]
        with open(self._path, "w", encoding="utf-8") as f:
            yaml.dump(self._data, f, Dumper=yaml.RoundTripDumper)
        if self._data[key] is not None:
            return self._data[key]
        return None


config = ConfigsManager(Config_path)
