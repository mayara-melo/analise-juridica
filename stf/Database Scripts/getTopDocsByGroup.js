db.AIPageRanked.drop()
db.pageRankedSTF.find(  {"id":{$regex:"AI .*"}},
                        {"id":1}
                     ).sort({"pageRank":-1}).forEach( function(current) {
        var acordao = {
            "_id" : current._id,
            "acordaoId" : current.acordaoId,
            "pageRank"  : current.pageRank,
            "isQuotedBy": current.isQuotedBy
        };
        db.AIPageRanked.insert( acordao);
    ));
