import requests
from bs4 import BeautifulSoup

r  = requests.get("http://www.gw2shinies.com/alchemy.php?display=All&saviewcolumn=Buy&sellchoice=Sell&viewtype=All&includegifts=Yes")
data = BeautifulSoup(r.text, "html.parser")

target = "Rugged Leather"

#grab itemtable
table = data.find('table', {'class': 'itemsTable'})
rows = table.findChildren('tr')

for row in rows:
    for cell in row:
        if target in row.text:
            print(cell)