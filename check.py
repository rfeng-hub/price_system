import re

names = []
with open('tickets.txt', 'r', encoding='utf-8') as f:
    lines = f.readlines()
    with open('result.txt', 'w+', encoding='utf-8') as w:
        for line in lines:
            patt0 = re.compile(r"\'city\': \'(\S+)\'")
            city = patt0.search(line)
            patt1 = re.compile(r"\'cinema_name\': '(\S+)'")
            name = patt1.search(line)
            # if name is not None: print(name.group(1))
            patt2 = re.compile(r"\'price\': \'(\d+)\', \'shi_price\': \'(\d+)\', \'nuo_price\': \'(\d+)\'")
            prices = patt2.search(line)
            if city is not None and prices is not None and name is not None:
                if name.group(1) not in names:
                    if prices.group(1) != prices.group(2) or prices.group(1) != prices.group(3) or prices.group(2) != prices.group(3):
                        w.write(city.group(1)+" "+name.group(1)+" "+prices.group()+"\n")
                        names.append(name.group(1))

print(names)