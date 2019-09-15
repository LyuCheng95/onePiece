import scrapy
import os
import urllib
import zlib

class onePieceSpider(scrapy.Spider):

    name = "onePiece"
    start_urls = [
        "https://manhua.fzdm.com/2/900/"
    ]
    
    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url, self.parse)

    def parse(self, response):
        imgTag = response.css('#mhimg0 a #mhpic').get()
        print(">>>>imgTag", imgTag)
        if imgTag:
            imgUrl = self.extractAttr(imgTag, 'src')
            filename = '900-1'
            self.saveImg(filename, imgUrl)
        nextPage = response.css('.navigation a.pure-button-primary').get()
        nextPageContent = self.extractContent(nextPage)
        if nextPageContent == '下一页':
            nextPageUrl = self.extractAttr(nextPage, 'href')
            nextPageUrl = self.constructPageUrl(response.request.url, nextPageUrl)
            print(">>>>nextPageUrl", nextPageUrl)
            # yield scrapy.Request(nextPageUrl, callback=self.parse)

    def extractAttr(self, tag, attr):
        fragments = tag.split(' ')
        src = ""
        recordFlag = False
        for frag in fragments:
            if (frag[:len(attr)] == attr):
                for char in frag:
                    if (char == '''"''' or char == "'"):
                        recordFlag = not recordFlag
                        continue
                    if (recordFlag):
                        src += char
                break
        return src

    def extractContent(self, tag):
        content = ""
        recordFlag = False
        for char in tag:
            if char == ">":
                recordFlag = True
                continue
            if char == "<":
                if recordFlag:
                    return content
            if recordFlag:
                content += char
        return content

    def constructPageUrl(self, prevUrl, indexUrl):
        print(prevUrl)
        fragments = prevUrl.split('/')
        fragments[-1] = indexUrl
        nextUrl = '/'.join(fragments)
        return nextUrl

    def saveImg(self, name, img_url):
        print('saving pic: ', name, img_url)
        pic_name = './' + name + '.jpg'
        exists = os.path.exists(pic_name)
        if exists:
            self.log('pic exists: ' + pic_name)
            return

        try:
            user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
            headers = { 'User-Agent' : user_agent }

            req = urllib.request.Request(img_url, headers=headers)
            response = urllib.request.urlopen(req, timeout=30)

            data = response.read()

            if response.info().get('Content-Encoding') == 'gzip':
                data = zlib.decompress(data, 16 + zlib.MAX_WBITS)

            fp = open(pic_name, "wb")
            fp.write(data)
            fp.close

            # self.log('save image finished:' + pic_name)

        except Exception as e:
            self.log('save image error.')
            self.log(e)