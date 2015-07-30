#scrapy crawl -a "iDate=20010101" -a "fDate=20020101" -a "page"=1 -a "index"=1 stf --logfile='logstf28Jul01' --loglevel='INFO'
#scrapy crawl -a "iDate=20020101" -a "fDate=20030101" -a "page"=1 -a "index"=1 stf --logfile='logstf28Jul02' --loglevel='INFO'
#scrapy crawl -a "iDate=20030101" -a "fDate=20040101" -a "page"=1 -a "index"=1 stf --logfile='logstf28Jul03' --loglevel='INFO'

for i in {2001..2012}
do
    echo "processing stf year $i"
    J=$((i+1))
    firstDay="0101"
    anoI=$i$firstDay
    anoF=$J$firstDay
    echo $anoI
    echo "oooooooooooooooooooooo $anoF"
    scrapy crawl -a "iDate=$anoI" -a "fDate=$anoF" -a "page"=1 -a "index"=1 stf --logfile='logstf$i' --loglevel='INFO'
    wait
done
