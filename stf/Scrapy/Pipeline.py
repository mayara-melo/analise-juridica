import subprocess
import re
from datetime import datetime, timedelta

FILE_NDOCS = 'temp'
FILE_UPDATER_SETTINGS = '../updater_settings'

def nextDay( cur_date):
    print cur_date
    y = int(cur_date[0:4])
    m = int(cur_date[4:6])
    d = int(cur_date[6:8])
    date = datetime( y,m,d)
    date = date + timedelta( days=1)
    d = str(date.day).zfill(2)
    m = str(date.month).zfill(2)
    y = str(date.year)
    return y+m+d

fupdater = open(FILE_UPDATER_SETTINGS, 'r+')
if (fupdater):
    prevIndex = fupdater.readline()
    prevFinalDate = fupdater.readline()
    if prevIndex and prevFinalDate:
        fIndex = iIndex = int( prevIndex) +1
        iDate = nextDay( str( prevFinalDate))
        choice = raw_input("buscar acordaos desde de "+ iDate+ "? s/n:")
    if ( choice == 'n'):
        iDate = raw_input("insira a data inicial de busca: yyyymmdd:\n")
        iIndex = fIndex = 1
    fDate = raw_input("insira a data final: yyyymmdd\n>")
else:
    print "cannot open file\n"

idateArg = "iDate="+iDate
fdateArg = "fDate="+fDate

# Extrai o numero de acordaos encontrados 
subprocess.call(["scrapy", "crawl", "stf_get_nacordaos",
                 "-a", idateArg,"-a", fdateArg])

with open(FILE_NDOCS, 'r+') as f:
    nacordaos = int( f.readline())
    f.seek(0)
    f.truncate()
    f.close()

print("iIndex: "+str(iIndex))
print("fIndex: "+str(fIndex))

totPages = nacordaos/10+1
# Parse paginas
for i in range (1, totPages+1):
    pageArg = "page="+str(i)
    indexArg = "index="+str(fIndex)
    subprocess.call(["scrapy", "crawl", "stfSpider",
                    "-a", idateArg, 
                    "-a", fdateArg,
                    "-a", pageArg,
                    "-a", indexArg]
#                    "--nolog"]
                   )
    fIndex += 10

fIndex -= (11 - nacordaos %10)
# Atualiza os valores da ultima extracao
wdata = raw_input("Atualizar dados? s/n: ")
if (wdata == 's'):
    fupdater.seek(0)
    fupdater.truncate()
    fupdater.write(
        str(fIndex-1) + '\n'+
        fDate + '\n'+
        str(iIndex)
    )
fupdater.close()

