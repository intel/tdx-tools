"""
Manage the artifacts.

A artifact is listed in artifact.yaml file in below format:

    latest-guest-image:
      source: http://xyz.qcow2.tar.xz
      sha256sum: 92d82663d1a3ad7b2c2b2f50b2145e388a48eb6b4e0b767cd94a5cf05394c98f

    latest-guest-image:
      source: https://<a SSL website>/test.qcow2
      sha256sum: https://<a SSL website>/test.sha256sum.txt

    latest-guest-image:
      source: file:///home/sample_user/test.qcow2

- The field of source URI could be starts with 'http', 'https' for remote file,
  or 'file' for local file
- The field of sha256sum could:
  + a SHA256 string
  + remote file by starting with 'http'/'https'
  + local file by starting with 'file'

"""
import os
import logging
import ssl
import hashlib
import shutil
import tarfile
from urllib.parse import urlparse
from tempfile import mkstemp
import requests
import yaml
from yaml.constructor import ConstructorError

__author__ = 'cpio'

LOG = logging.getLogger(__name__)
MB = 1024 * 1024
BLOCKSIZE = 1024 * 4  # pagesize


class DownloadExecutor:
    """
    Download executor to download the given URL to given filepath
    """

    def __init__(self, url, filepath):
        self._url = url
        self._filepath = filepath

    def run(self):
        """
        Run executor
        """
        LOG.info("Download: %s => %s ...", self._url, self._filepath)

        response = requests.get(self._url, stream=True,
                                verify=ssl.get_default_verify_paths().openssl_cafile,
                                timeout=10)
        response.raise_for_status()
        try:
            with open(self._filepath, "wb") as fobj:
                file_size = int(response.headers.get('Content-Length', 0))
                chunk_size = 1 * MB
                chunks = file_size / chunk_size
                curr_chunk = 1
                prev_perc = -1
                for content in response.iter_content(chunk_size=chunk_size):
                    fobj.write(content)
                    downloaded = int((curr_chunk * chunk_size) / MB)
                    perc = int((curr_chunk * 100) / chunks)
                    if perc != prev_perc and perc % 10 == 0:
                        prev_perc = perc
                        LOG.debug("downloaded: %4dM/%4dM (%02d%%)",
                                  downloaded, int(file_size / MB), perc)

                    curr_chunk += 1
        except (IOError, OSError):
            LOG.error("Fail download to file %s",
                      self._filepath, exc_info=True)
            return

        LOG.debug("... download completed => %s!", self._filepath)

    @staticmethod
    def download(url, filepath):
        """
        Static method to create DownloadExector instance to perform download.
        """
        executor = DownloadExecutor(url, filepath)
        executor.run()


class Artifact:
    """
    Artifact classs
    """

    def __init__(self, source, sha256sum):
        assert source is not None, "Must provide 'source' field"
        self._source = source
        self._sha256sum = sha256sum
        result = urlparse(source)
        self.schema = result.scheme
        self.path = result.path
        self.filename = os.path.basename(self.path)

    def _get_sha256sum_from_file(self, sha256sum_filename):
        with open(sha256sum_filename, "r", encoding='utf-8') as sha256_fobj:
            for line in sha256_fobj.readlines():
                hash_data, filename = line.split()
                if filename.strip() == self.filename:
                    return hash_data.strip()
        return None

    @property
    def sha256sum(self):
        """
        The input of sha256 could be one of below type:
        - http://remote_address/remote_sha256file.txt
        - https://remote_address/remote_sha256file.txt
        - file:///opt/local_sha256file.txt
        - fdb926cfec108ed291a2493459a08a8864635ae1eada428862d0a5fc27ee4ea3
        """
        result = urlparse(self._sha256sum)
        if result.scheme in ['http', 'https']:
            # Download remote sha256sum and search based on filename
            _, path = mkstemp()
            DownloadExecutor.download(self._sha256sum, path)
            return self._get_sha256sum_from_file(path)

        if result.scheme in ['file']:
            # Search sha256sum from local file based on filename
            return self._get_sha256sum_from_file(result.path)

        # The field of sha256sum is just that string
        return self._sha256sum

    def get(self, dest_dir, cache_dir):
        """
        Get artifact.

        If artifact is remote uri with prefix 'http' or 'https', then download
        it and verify its sha256sum

        If artifact is local source, then just return its path
        """
        if self.schema in ['http', 'https']:
            assert self._sha256sum is not None, \
                "Must provide sha256sum file or string for remote source to " \
                "verify downloading"
            return self.download(dest_dir, cache_dir)

        if self.schema == 'file':
            assert os.path.exists(self.path), \
                f"File {self.path} does not exist"
            assert not self.path.endswith('tar.xz'), \
                "Not support tar.xz for local file"
            return self.path

        assert False, "Source field must starts with 'http/https/file'"
        return None

    def download(self, dest_dir, cache_dir):
        """
        Download artifact from given URL to dest_dir.

        It will save to cache_dir to avoid duplicate download a same file.
        """
        assert os.path.exists(dest_dir)
        assert os.path.exists(cache_dir)

        cache_file = os.path.join(cache_dir, self.filename)
        dest_file = os.path.join(dest_dir, self.filename)

        retries = 0
        is_download_new = False

        while retries < 5:
            if os.path.exists(cache_file):
                # check checksum for cache_file
                if self._validate_sha256sum(cache_file):
                    break
                os.remove(cache_file)

            DownloadExecutor.download(self._source, cache_file)
            is_download_new = True
            retries += 1

        # if download new file, then need decompress it to overwrite existing one
        if cache_file.endswith("tar.xz"):
            if is_download_new or not os.path.exists(cache_file[:-7]):
                LOG.debug("Decompress file %s...", cache_file)
                with tarfile.open(cache_file) as tarfd:
                    tarfd.extractall(cache_dir)

            cache_file = cache_file[:-7]
            dest_file = dest_file[:-7]

        # check whether need copy the cache file to destination according to timestamp
        need_copy = False
        if not os.path.exists(dest_file):
            need_copy = True
        else:
            cache_file_created = os.path.getctime(cache_file)
            dest_file_created = os.path.getctime(dest_file)
            need_copy = cache_file_created > dest_file_created

        if need_copy:
            LOG.info("copying file: %s -> %s", cache_file, dest_file)
            shutil.copyfile(cache_file, dest_file)

        return dest_file

    def _validate_sha256sum(self, filepath):
        sha256 = hashlib.sha256()
        with open(filepath, 'rb') as fobj:
            buf = fobj.read(BLOCKSIZE)
            while len(buf) > 0:
                sha256.update(buf)
                buf = fobj.read(BLOCKSIZE)
        provider = self.sha256sum
        LOG.debug("file hash: %s, expected hash: %s", sha256.hexdigest(),
                  provider)
        return sha256.hexdigest() == provider


class ArtifactFactory(dict):
    """
    Manage all artifacts from manifest file.
    """

    _INSTANCE = None

    def __init__(self, manifest):
        super().__init__()
        self._manifest = manifest
        self._artifacts = {}
        self._parse_manifest()

    def _parse_manifest(self):
        for key in self._manifest.keys():
            self._artifacts[key] = Artifact(
                self._manifest[key].get("source"),
                self._manifest[key].get("sha256sum"))

    def keys(self):
        return self._artifacts.keys()

    def values(self):
        return self._artifacts.values()

    def __getitem__(self, key):
        # pylint: disable=consider-iterating-dictionary
        if key not in self._artifacts.keys():
            return None
        return self._artifacts[key]


class ArtifactManifest(dict):

    """
    Artifact manifest file in following format:

    - name: tdx-latest-kernel
      url: .... (if in tar or xz, then decompress automatically)
      checksum: in sha256
      checksum_url: the checksum file in same format as the output of "sha256sum"

    """

    _INSTANCE = None       # for singleton

    def __init__(self, filepath):
        super().__init__()
        assert os.path.exists(filepath), "Manifest file does not exists"
        self._filepath = filepath
        self._dict = None
        yaml.add_constructor(
            yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
            self._no_duplicates_constructor)

    def load(self):
        """
        Load manifest file explicitly.
        """
        try:
            with open(self._filepath, encoding="utf-8") as fobj:
                self._dict = yaml.load(fobj, Loader=yaml.FullLoader)
                if not isinstance(self._dict, dict):
                    LOG.error(
                        "The format of %s is invalid, not a dict.",
                        self._filepath)
                    return None
                return self._dict
        except (IOError, OSError):
            LOG.error("Fail to open the file %s",
                      self._filepath, exc_info=True)
            return None
        except yaml.constructor.ConstructorError:
            LOG.error(
                "Found the duplicate key in yaml file %s", self._filepath,
                exc_info=True)
            return None

    def keys(self):
        return self._dict.keys()

    def values(self):
        return self._dict.values()

    def __getitem__(self, key):
        if key not in self.keys():
            return None
        return self._dict[key]

    @staticmethod
    def _no_duplicates_constructor(loader, node, deep=False):
        """
        Overwrite the yaml constructor to check for duplicate keys.
        """
        mapping = {}
        for key_node, value_node in node.value:
            key = loader.construct_object(key_node, deep=deep)
            value = loader.construct_object(value_node, deep=deep)
            if key in mapping:
                raise ConstructorError(
                    "while constructing a mapping",
                    node.start_mark,
                    f"found duplicate key ({key})", key_node.start_mark)
            mapping[key] = value

        return loader.construct_mapping(node, deep)
