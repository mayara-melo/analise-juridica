import com.mongodb.*;
import java.net.UnknownHostException;
import java.io.*;
import java.util.ArrayList;

public class Main {

    private static Integer currentPercentage = -1;
    private static Integer count = 0;
    private static Long total;


    public static void main(String[] args) throws UnknownHostException {

        MongoClient mongoClient = new MongoClient();
        DB db = mongoClient.getDB( "DJs" );

        DBCollection acordaosSTJ = db.getCollection("stj");
        DBCollection acordaosSTF = db.getCollection("stf");
        DBCollection links       = db.getCollection("linksAll");
        DBCollection acordaosAll = db.getCollection("acordaosAll");
	links.drop();

        total = acordaosSTJ.count() + acordaosSTF.count();
 
	for( int i = 1; i <= 290000; i += 10000){ 
	    BasicDBObject query = new BasicDBObject(2);
	    query.put("$gte", i);
	    query.put("$lt", i+10000);
            DBCursor cursorAll = acordaosAll.find( new BasicDBObject("index",query));
	    cursorAll.addOption(com.mongodb.Bytes.QUERYOPTION_NOTIMEOUT);
            while( cursorAll.hasNext()) {
                printProgress();
                DBObject acordao = cursorAll.next();
	        processAcordao( acordaosAll, links, acordao);
	    }
        }
        System.out.println("\n");
    }

    private static void printProgress() {
        count++;
        Integer newPercentage = (int)Math.floor(100 * count / total);
        if (newPercentage != currentPercentage) {
                System.out.print("\r |");
            for (int i = 1; i <= newPercentage; i++)
                System.out.print("=");
            for (int i = newPercentage + 1; i <= 100; i++)
                System.out.print(" ");
            System.out.print("| " + newPercentage + "%  ");

            currentPercentage = newPercentage;
        }
    }


    private static void processAcordao( DBCollection acordaos, DBCollection links, DBObject acordao) {
            ArrayList<String> foundQuotes = new ArrayList<String>();
            BasicDBList quotes = (BasicDBList) acordao.get("citacoes");
            for( Object quote : quotes) {
                BasicDBObject query = new BasicDBObject("acordaoId", (String)quote);
                BasicDBObject foundQ = (BasicDBObject)acordaos.findOne(query);
                if( foundQ != null) foundQuotes.add( (String)quote);
            }

            BasicDBObject link = new BasicDBObject("_id", acordao.get("_id"));
            link.append("acordaoId", acordao.get("acordaoId"));
            link.append("localSigla", acordao.get("localSigla"));
            link.append("ementa", acordao.get("ementa"));
            link.append("decisao", acordao.get("decisao"));
            link.append("relator", acordao.get("relator"));
            link.append("data", acordao.get("dataJulg"));
            link.append("tribunal", acordao.get("tribunal"));
            link.append("index", acordao.get("index"));
            link.append("citacoes", foundQuotes);
            links.insert(link);

    }

}
