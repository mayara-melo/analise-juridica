import com.mongodb.*;
import java.net.UnknownHostException;
import java.io.*;
import java.util.ArrayList;

public class GraphMaker {

    private static Integer currentPercentage = -1;
    private static Integer count = 0;
    private static Long total;

    private static DBCollection links;
    private static DBCollection acordaos;

    public GraphMaker( String dbName, String acordaosCollectionName) throws UnknownHostException{
	    String linksCollectionName = "links" + acordaosCollectionName.toUpperCase(); 
        MongoClient mongoClient = new MongoClient();
        DB db = mongoClient.getDB( dbName );

        links    = db.getCollection( linksCollectionName);
        acordaos = db.getCollection( acordaosCollectionName);
    }

    protected void makeGraph() {
	    links.drop();
        total = acordaos.count();
        for( int i = 1, step = 10000; i <= total; i += step){ 
	        BasicDBObject query = new BasicDBObject(2);
	        query.put("$gte", i);
	        query.put("$lt", i+step);
            DBCursor cursor = acordaos.find( new BasicDBObject("index",query));
	        cursor.addOption(com.mongodb.Bytes.QUERYOPTION_NOTIMEOUT);
            while( cursor.hasNext()) {
    		    printProgress();
                DBObject acordao = cursor.next();
                processAcordao( acordaos, links, acordao);
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
            ArrayList<String> similars = new ArrayList<String>();
            BasicDBList quotes = (BasicDBList) acordao.get("citacoes");
            BasicDBList similarAcordaos = (BasicDBList) acordao.get("acordaosSimilares");
            for( Object quote : quotes) {
                BasicDBObject query = new BasicDBObject("acordaoId", (String)quote);
                BasicDBObject foundQ = (BasicDBObject)acordaos.findOne(query);
                if( foundQ != null) foundQuotes.add( (String)quote);
            }
            for( Object similar : similarAcordaos) {
                DBObject similarAcordao = (DBObject)similar;
                String similarAcordaoId = (String)similarAcordao.get("acordaoId"); 
                BasicDBObject query = new BasicDBObject("acordaoId", similarAcordaoId);
                BasicDBObject found = (BasicDBObject)acordaos.findOne(query);
                similars.add( (String)similarAcordaoId);
                if( found != null) System.out.println("found similar");
                else{
                    BasicDBObject virtualLink = new BasicDBObject();
                    virtualLink.append("id", similarAcordao.get("acordaoId"));
                    virtualLink.append("relator", acordao.get("relator"));
                    virtualLink.append("data", acordao.get("dataJulg"));
                    virtualLink.append("localSigla", acordao.get("localSigla"));
                    virtualLink.append("virtual", true);
                    virtualLink.append("principal",  acordao.get("acordaoId"));
                    links.insert( virtualLink);
                }
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
            link.append("virtual", false);
            link.append("acordaosSimilares", similars);
            links.insert(link);
    }
}
