import locale
import platform
import subprocess

default_encoding = locale.getpreferredencoding()


def ping_site(site_name):
    """
    Pings a site and prints out a result at system encoding
    :param site_name: site url
    :return:
    """
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    args = ['ping', param, '2', site_name]
    process = subprocess.Popen(args, stdout=subprocess.PIPE)
    for line in process.stdout:
        print(line.decode(default_encoding))


# ping_site('ya.ru')
ping_site('youtube.com')
