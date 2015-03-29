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
        DB db = mongoClient.getDB( "test" );

        DBCollection acordaosSTF = db.getCollection("stf");
        DBCollection acordaosSTJ = db.getCollection("stj");

//        total = acordaosSTF.count();
        total = acordaosSTJ.count();

        DBCursor cursorSTF = acordaosSTF.find();
        DBCursor cursorSTJ = acordaosSTJ.find();

        DBCollection links = db.getCollection("linksSTJ");
        links.drop();
 
/*        BasicDBObject queryNotRanked = new BasicDBObject("linked", false);
        cursorSTF = acordaosSTF.find( queryNotRanked);
        cursorSTF.sort(new BasicDBObject("index", -1));
        Integer minIndex = (int) (acordaos.findOne( queryNotRanked).get("index"));
        
        cursorSTF = acordaosSTF.find(new BasicDBObject("index", new BasicDBObject("$gte", minIndex)));
        total = new Long(cursorSTF.count());
        
        acordaosSTF.update( new BasicDBObject( "linked", false),
                         new BasicDBObject( "$unset", new BasicDBObject("linked", "")),
                         false, true);
  */      //System.out.println("\n");
        while( cursorSTJ.hasNext()) {
            printProgress();

            DBObject acordao = cursorSTJ.next();
            
            //System.out.println( "index: "+acordao.get("index"));
	        processAcordao( acordaosSTJ, links, acordao);

        }

       /* cursor = acordaos.find(new BasicDBObject("index", new BasicDBObject("$gt", 25000)).append("ranked", false));
        System.out.println("\n");
        while(cursor.hasNext()) {

            printProgress();

            DBObject acordao = cursor.next();

            processFile(tree, acordaos, links, acordao);

        }
*/
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
            ArrayList<BasicDBObject> foundQuotes = new ArrayList<BasicDBObject>();
            BasicDBList quotes = (BasicDBList) acordao.get("citacoes");
            for( Object quote : quotes) {
                BasicDBObject query = new BasicDBObject("acordaoId", (String)quote);
                BasicDBObject foundQ = (BasicDBObject)acordaos.findOne(query);
                if( foundQ != null) foundQuotes.add( foundQ);
            }

            BasicDBObject link = new BasicDBObject("_id", acordao.get("_id"));
            link.append("acordaoId", acordao.get("acordaoId"));
            link.append("localSigla", acordao.get("localSigla"));
            link.append("local", acordao.get("local"));
            link.append("relator", acordao.get("relator"));
            link.append("data", acordao.get("dataJulg"));
            link.append("quotesSomething", acordao.get("quotesSomething"));
            link.append("tribunal", acordao.get("tribunal"));
            link.append("citacoes", foundQuotes);
            links.insert(link);

    }

}
