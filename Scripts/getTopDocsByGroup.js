conn = new Mongo()
db = conn.getDB("DJs")
var group;
db.pageRankedNcitationsSTF.find(  {"id":{$regex:"^"+group+" "}},
                        {"id":1, "_id":-1}
    ).sort({"pageRank":-1}
    ).limit(10).forEach( function(current) {
	var doc = db.pageRankedSTF.findOne({ "_id": current._id});
	print( doc.id);
    });
