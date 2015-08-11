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
        DBCursor cursor = acordaos.find();
	    cursor.addOption(com.mongodb.Bytes.QUERYOPTION_NOTIMEOUT);
        while( cursor.hasNext()) {
    	    printProgress();
            DBObject acordao = cursor.next();
            processAcordao( acordaos, links, acordao);
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
            String acordaoId = (String)acordao.get("acordaoId");
            BasicDBList quotes = (BasicDBList) acordao.get("citacoes");
            BasicDBList similarAcordaos = (BasicDBList) acordao.get("similares");
            for( Object quote : quotes) {
                BasicDBObject query = new BasicDBObject("acordaoId", (String)quote);
                BasicDBObject foundQ = (BasicDBObject)acordaos.findOne(query);
                if( foundQ != null) foundQuotes.add( (String)quote);
            }
            for( Object similar : similarAcordaos) {
                BasicDBObject similarAcordao = (BasicDBObject)similar;
                String similarAcordaoId = (String)similarAcordao.get("acordaoId"); 
                similars.add( (String)similarAcordaoId);
                //Verify if similar acordao is already in collection, if it's not insert it, otherwise update it
                BasicDBObject query = new BasicDBObject("acordaoId", similarAcordaoId);
                BasicDBObject isSimilarInCollection = (BasicDBObject)acordaos.findOne(query);
                
                BasicDBList similarToAcordaos = new BasicDBList();
                similarToAcordaos.add( acordaoId);

                if( isSimilarInCollection == null) { //not in collection
                    BasicDBObject alreadyInGraph = (BasicDBObject)links.findOne( new BasicDBObject("id", similarAcordaoId));
                    if( alreadyInGraph != null){ //if already inserted add previous similarities 
                        similarToAcordaos.addAll( (BasicDBList)alreadyInGraph.get("acordaosSimilares"));
                    }
                    similarAcordao.append("virtual", true);
                    similarAcordao.append("acordaoId", similarAcordaoId);
                    similarAcordao.append("localSigla", similarAcordao.get("localSigla"));
                    similarAcordao.append("tribunal", acordao.get("tribunal"));
                    similarAcordao.append("relator", similarAcordao.get("relator"));
                    similarAcordao.append("data", similarAcordao.get("dataJulg"));
                    similarAcordao.append("citacoes",  new BasicDBList());
                }
                similarAcordao.append("acordaosSimilares", similarToAcordaos);
                links.save( similarAcordao);
            }
/*            BasicDBObject link = (BasicDBObject) acordao;
            link.append("acordaosSimilares", similars);
            link.append("virtual", false);
            links.insert( link);*/
            BasicDBObject link = new BasicDBObject("_id", acordao.get("_id"));
            link.append("acordaoId", acordao.get("acordaoId"));
            link.append("localSigla", acordao.get("localSigla"));
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
