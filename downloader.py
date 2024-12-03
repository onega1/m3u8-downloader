import os
import time
import aiohttp
import asyncio

class Downloader():

    def __init__(self, url = None, directory = None, name = None, parse_handler = None, timeout = 10, retry = 3, *args, **kwargs):
        print('初始化')
        self.url = url
        self.timeout = timeout
        self.retry = retry
        self.local_directory = directory
        self.name = name
        self.parse_handler = parse_handler
        self.final_path = os.path.join(directory, name)

    def parse_m3u8_text(self, text):
        """
        实现该方法，用于解析你指定的m3u8文件内容
        params:
            text: m3u8文件url
        return:
            list: ts文件数组
        """
        pass

    def merge_ts_files(self, order_list):
        with open(self.final_path, 'wb') as outfile:
            for line in order_list:
                filename = line.split("/")[-1]
                filepath = os.path.join(self.local_directory, filename)
                if os.path.exists(filepath):
                    with open(filepath, 'rb') as infile:
                        outfile.write(infile.read())
                    os.remove(filepath)

    # 文件下载
    async def download_f(self, url):
        async with self.session.get(url) as response:
            text = await response.text()
            return text
    
    # 下载并处理 ts 文件集合
    async def handle_ts(self, url):
        retries = self.retry
        backoff_factor=1
        for attempt in range(retries):
            try:
                async with self.session.get(url) as response:
                    response.raise_for_status()
                    filename = url.split("/")[-1]
                    with open(self.local_directory + filename, 'wb') as f:
                        while True:
                            chunk = await response.content.read(8192)
                            if not chunk:
                                break
                            f.write(chunk)
                self.success_count = self.success_count + 1
                break
                    # print(f"下载 {filename} 完成")
            except Exception as e:
                print(f"重试 {attempt + 1} failed => {url}")
                print(e)
                if attempt < retries - 1:
                    await asyncio.sleep(backoff_factor * (2 ** attempt))  # 指数退避策略
                else:
                    self.fail_count = self.fail_count + 1
                    print(f"下载 {url} 失败")

    def re_count(self):
        # 重新计数
        self.success_count = 0
        self.fail_count = 0
        
    # 加载 m3u8 主流程
    async def main(self):
        self.re_count()
        self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout))
        start_time = time.time()
        m3u8_url = self.url
        print('开始处理: {}'.format(m3u8_url))
        try:
            # 下载 m3u8 文件
            m3u8_file = await self.download_f(m3u8_url)
            # 解析 m3u8 文件
            ts_order_list = self.parse_handler(m3u8_file)
            print(f'ts文件总数: {len(ts_order_list)}')
        except Exception as e:
            print(e)
            return

        # 下载 ts 文件
        tasks = [self.handle_ts(url) for url in ts_order_list]
        await asyncio.gather(*tasks)
        await self.session.close()

        print(f'成功数量: {self.success_count}')
        print(f'失败数量: {self.fail_count}')

        # 合并 ts 文件
        self.merge_ts_files(ts_order_list)

        print('处理结束, 消耗时间: {}s'.format(time.time() - start_time))
        self.re_count()

    def start(self):
        asyncio.run(self.main())

        
        