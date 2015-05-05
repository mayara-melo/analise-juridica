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

        total = acordaosSTJ.count();

        DBCollection links = db.getCollection("linksSTJ");
	links.drop();
 
	for( int i = 1; i <= 290000; i += 5000){ 
	    BasicDBObject query = new BasicDBObject(2);
	    query.put("$gte", i);
	    query.put("$lt", i+5000);
            DBCursor cursorSTJ = acordaosSTJ.find( new BasicDBObject("index",query));
	    cursorSTJ.addOption(com.mongodb.Bytes.QUERYOPTION_NOTIMEOUT);
	    System.out.println( cursorSTJ);
            while( cursorSTJ.hasNext()) {
                printProgress();
                DBObject acordao = cursorSTJ.next();
                System.out.println( "index: "+acordao.get("index"));
	        processAcordao( acordaosSTJ, links, acordao);
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
            link.append("legislacao", acordao.get("legislacao"));
            link.append("relator", acordao.get("relator"));
            link.append("data", acordao.get("dataJulg"));
            link.append("tribunal", acordao.get("tribunal"));
            link.append("index", acordao.get("index"));
            link.append("dataJulg", acordao.get("dataPublic"));
            link.append("citacoes", foundQuotes);
            links.insert(link);

    }

}
