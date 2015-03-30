import com.mongodb.*;
import java.net.UnknownHostException;
import java.util.ArrayList;
import java.util.LinkedList;
import java.util.HashMap;
import java.util.Map;
import java.util.Scanner;

public class Main {

    private static HashMap<String, Acordao> acordaos = new HashMap<String, Acordao>();
//    private static List<String> names = new LinkedList(Arrays.asList("ADI","RE", "HC","Agr","AI","Ext"));
    public static void main(String[] args) throws UnknownHostException {
        MongoClient mongoClient = new MongoClient();
        DB db = mongoClient.getDB( "test" );
        DBCollection links = db.getCollection("linksSTF");
        buildMap( links);
        calculatePageRanks( db.getCollection("pageRankedSTF"));
    }

    private static void buildMap( DBCollection links) throws UnknownHostException {
        Long numAcordaos = links.count();

        DBCursor cursor = links.find();
        while(cursor.hasNext()) {
            DBObject acordaoObject = cursor.next();
            try {
                String id          = acordaoObject.get("acordaoId").toString();
                String relator     = acordaoObject.get("relator").toString();
                String date        = acordaoObject.get("data").toString();
                String tribunal    = acordaoObject.get("tribunal").toString();
                BasicDBList quotes = (BasicDBList) acordaoObject.get("citacoes");
                ArrayList<String> quotesIDs = dbListToArrayListOfIDs( quotes);

                Acordao acordao = new Acordao( id, relator, date, tribunal, quotesIDs, numAcordaos);
                acordaos.put(id, acordao);


            } catch(NullPointerException ex) {
                System.out.println("NULL POINTER EXCEPTION, BITCH");
                ex.printStackTrace();
            }
        }
        for (Acordao acordao : acordaos.values()) {
            ArrayList<String> quotes = acordao.getQuotes();
            for (String q : quotes) {
                Acordao quotedAcordao = acordaos.get( q);
                acordao.quotes.add( quotedAcordao);
                quotedAcordao.isQuotedBy.add( acordao);
            }
        }

    }

    private static ArrayList<String> dbListToArrayListOfIDs(BasicDBList list) {
        ArrayList<String> arrayList = new ArrayList<String>();
        for (Object object : list) {
            DBObject dbObject = (DBObject) object;
            String id = dbObject.get("acordaoId").toString();
            arrayList.add(id);
        }
        return arrayList;
    }

    private static Double euclidianDistance(HashMap<String, Double> pMap, HashMap<String, Double> qMap) {
        Double sum = 0.0;
        for (Map.Entry<String, Double> entry : pMap.entrySet()) {
            String id = entry.getKey();
            Double p = entry.getValue();
            Double q = qMap.get(id);
            Double term = Math.pow(p - q, 2);
            sum += term;
        }
        System.out.println(Math.sqrt(sum));
        return Math.sqrt(sum);
    }

    private static void calculatePageRanks( DBCollection pageRanked) throws UnknownHostException {

        System.out.println("calculating pageranks now");

        //Double n = count.doubleValue();


       // DBObject query = new BasicDBObject("id", new BasicDBObject("$regex","^"+idBegin+".*$"));
//        Long count = new Long( acordaos.length());
    //	System.out.println("found "+ n+ " of id beginning with "+ idBegin);
	//    System.out.println("cursor: "+ cursor+ " n: "+ n);


        Double n = (double)acordaos.size();
        Double d = 0.85;

        HashMap<String, Double> pageRanks = new HashMap<String, Double>();
        for (Acordao acordao : acordaos.values()) {
            pageRanks.put( acordao.getID(), acordao.pageRank);
        }

        Double epsilon = 1.0E-18;
        while(true) {
            Double prSum = 0.0;
            for (Acordao acordao : acordaos.values()) {
                Double sum = 0.0;
                for(Acordao quotingAcordao : acordao.isQuotedBy) {
                    sum += quotingAcordao.pageRank;
                }
                acordao.tempPageRank = ((1 - d) / n) + (d * sum);
                prSum += acordao.tempPageRank;
            }

            HashMap<String, Double> newPageRanks = new HashMap<String, Double>();
            for (Acordao acordao : acordaos.values()) {
                acordao.pageRank = acordao.tempPageRank/ prSum;
                newPageRanks.put(acordao.getID(), acordao.pageRank);
            }

            if (euclidianDistance(pageRanks, newPageRanks) < epsilon) break;

            pageRanks.clear();
            pageRanks = (HashMap<String, Double>) newPageRanks.clone();

        }

        pageRanked.drop();

        for (Acordao acordao : acordaos.values()) {
            BasicDBObject doc = new BasicDBObject();
            doc.append("id", acordao.getID());
            doc.append("tribunal", acordao.getTribunal());
            doc.append("pageRank", acordao.pageRank);
            ArrayList<String> quotingAcordaos = new ArrayList<String>();
            for (Acordao quoting : acordao.isQuotedBy) {
                quotingAcordaos.add(quoting.getID());
            }
            doc.append("isQuotedBy", quotingAcordaos);
            pageRanked.insert(doc);
        }

    }

}
