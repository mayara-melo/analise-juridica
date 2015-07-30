scrapy crawl -a "iDate=20030101" -a "fDate=20040101" -a "update"=0 stj --logfile 'logstj29Jul' 

#for i in {2002..2012}
#do
#	echo "processing stj year $i"
#	J=$((i+1))
#	firstDay="0101"
#	anoI=$i$firstDay
#	anoF=$J$firstDay
#	scrapy crawl -a "iDate=$anoI" -a "fDate=$anoF" -a "update"=0 stj --logfile "logstj-$i" --loglevel 'ERROR' 
#done
