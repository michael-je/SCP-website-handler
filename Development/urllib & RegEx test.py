import urllib.request
import re

# url = 'http://pythonprogramming.net/parse-website-using-regular-expressions-urllib/'
# url = 'http://google.com'
url = 'http://www.scp-wiki.net/'

req = urllib.request.Request(url)
resp = urllib.request.urlopen(req)
respData = resp.read()

paragraphs = re.findall(r'<p>(.*?)</p>', str(respData))
for eachP in paragraphs:
    print(eachP)

# print(respData)