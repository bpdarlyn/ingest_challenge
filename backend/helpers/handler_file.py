import os
import errno
import time
import shutil


class HandlerFile(object):
    def __init__(self, base_dir):
        self.base_dir = base_dir
        self._mkdir_p(base_dir)

    @staticmethod
    def _mkdir_p(path):
        folder_structure = os.path.dirname(path)
        try:
            os.makedirs(folder_structure, exist_ok=True)
        except OSError as exc:  # Python > 2.5
            if ((exc.errno == errno.EEXIST and os.path.isdir(path))
                    or exc.errno == errno.EISDIR):
                pass
            else:
                raise

    def wait_until_file_exists(self, file_path):
        while True:
            print("checking", file_path)
            if self.isfile(file_path):
                print("file exists")
                break
            else:
                print("file does not exists.")
                print("waiting 2 seconds")
                time.sleep(2)

    def append_to(self, a, b):
        gg = self.open(b, "a")
        gg.write(self.open(a, "r").read())
        gg.close()

    def listdir(self, path):
        aaa = os.path.join(self.base_dir, path.lstrip("/"))
        # print "LISTING DIR: %s"%aaa
        bbb = os.listdir(aaa)
        bbb.sort()
        # print "RETURNING: %s elements"%len(bbb)
        return bbb

    def size_for_fd(self, my_file):
        return os.fstat(my_file.fileno()).st_size

    def move(self, a, b):
        shutil.move(os.path.join(self.base_dir, a.lstrip("/")),
                    os.path.join(self.base_dir, b.lstrip("/")))

    def remove(self, path_to_file):
        return os.remove(os.path.join(self.base_dir, path_to_file.lstrip("/")))

    def open(self, path_to_file, mode="r", buffering=-1, errors='ignore', encoding=None):
        if 'b' in mode:
            return open(os.path.join(self.base_dir, path_to_file.lstrip("/")),
                        mode=mode, buffering=buffering, encoding=encoding)
        return open(os.path.join(self.base_dir, path_to_file.lstrip("/")),
                    mode=mode, buffering=buffering, errors=errors, encoding=encoding)

    def copy(self, orig, dest):
        return shutil.copy(os.path.join(self.base_dir, orig.lstrip("/")),
                           os.path.join(self.base_dir, dest.lstrip("/")))

    def copyFromLocal(self, orig, dest, handler_file_absolute):
        return shutil.copy(handler_file_absolute.pathToLocal(orig),
                           os.path.join(self.base_dir, dest.lstrip("/")))

    def pathToLocal(self, dest):
        return os.path.join(self.base_dir, dest.lstrip("/"))

    def mkdir_p(self, path):
        return self._mkdir_p(os.path.join(self.base_dir, path.lstrip("/")))

    def touch(self, path):
        return self._touch(os.path.join(self.base_dir, path.lstrip("/")))

    @staticmethod
    def _touch(fname, times=None):
        fhandle = open(fname, 'a')
        try:
            os.utime(fname, times)
        finally:
            fhandle.close()

    def rmtree(self, path):
        if path.strip() == "/":
            raise Exception("not allowed")
        if path.strip() == "":
            raise Exception("not allowed")
        return shutil.rmtree(os.path.join(self.base_dir, path.lstrip("/")))

    def file_size(self, path):
        f = open(os.path.join(self.base_dir, path.lstrip("/")))
        f.seek(0, os.SEEK_END)
        size = f.tell()
        f.close()
        return size

    def isfile(self, path):
        return os.path.isfile(os.path.join(self.base_dir, path.lstrip("/")))

    def isdir(self, path):
        return os.path.isdir(os.path.join(self.base_dir, path.lstrip("/")))

    def ls(self, path):
        aux = []
        prefix = os.path.join(self.base_dir, path.lstrip("/"))
        if not os.path.isdir(prefix): return []
        for f in os.listdir(prefix):
            ff = os.path.join(prefix, f)
            if os.path.isfile(ff) or os.path.isdir(ff): aux.append(f)
        return aux
