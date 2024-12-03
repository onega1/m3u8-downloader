from downloader import Downloader

url = 'https://vip1.lz-cdn6.com/20220819/23119_06404026/1000k/hls/mixed.m3u8'

def parse_handler(text):
    path = str(url)[0:-10]
    part_list = list(map(lambda e: path + e, filter(lambda f: f.startswith('#') == False, text.splitlines())))
    return part_list

dl = Downloader(url=url, directory='videos\\', name='demo.mp4', parse_handler=parse_handler)
dl.start()