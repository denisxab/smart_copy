from hashlib import sha256

from pydantic import BaseModel


class CopyConf_cp(BaseModel):
    exclude: list[str]
    infloder: str
    outfolder: str


class CopyConf(BaseModel):
    cp: CopyConf_cp




def sha256sum(path_file):
    """
    Получить хеш сумму файла
    @param path_file: Путь к файлу
    """
    h = sha256()
    b = bytearray(128 * 1024)
    mv = memoryview(b)
    with open(path_file, 'rb', buffering=0) as f:
        for n in iter(lambda: f.readinto(mv), 0):
            h.update(mv[:n])
    return h.hexdigest()
