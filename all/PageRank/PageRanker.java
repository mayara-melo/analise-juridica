import com.mongodb.*;
import java.net.UnknownHostException;
import java.util.ArrayList;
import java.util.LinkedList;
import java.util.HashMap;
import java.util.Map;
import java.util.Scanner;

public class PageRanker{

    private HashMap<String, Acordao> acordaos = new HashMap<String, Acordao>();
    private DB db;
    private DBCollection links;
    private Double epsilon = 1.0E-18;
    private Double d = 0.85;
    private Double n;
    private String linksName;

    public PageRanker( String dbName, String linksName) throws UnknownHostException {
	this.linksName = linksName;
        MongoClient mongoClient = new MongoClient();
        this.db = mongoClient.getDB( dbName );
        this.links = db.getCollection(linksName);
	buildMap();
	n = (double)acordaos.size();
    }

    private void buildMap() throws UnknownHostException {
        Long numAcordaos = links.count();
        Double n = numAcordaos.doubleValue();
        DBCursor cursor = links.find();
        cursor.addOption(com.mongodb.Bytes.QUERYOPTION_NOTIMEOUT);
        while(cursor.hasNext()) {
            DBObject acordaoObject = cursor.next();
            try {
                String id          = acordaoObject.get("acordaoId").toString();
		String relator     = acordaoObject.get("relator").toString();
		String data        = acordaoObject.get("data").toString();
		String tribunal    = acordaoObject.get("tribunal").toString();
                BasicDBList quotes = (BasicDBList) acordaoObject.get("citacoes");
                ArrayList<String> quotesIDs = dbListToArrayListOfIDs( quotes);

                Acordao acordao = new Acordao( id, relator, data, tribunal, quotesIDs, numAcordaos);
                acordaos.put(id, acordao);

            } catch(NullPointerException ex) {
                System.out.println("NULL POINTER EXCEPTION");
                ex.printStackTrace();
            }
        }
        for (Acordao acordao : acordaos.values()) {
            ArrayList<String> quotes = acordao.getQuotes();
            for (String q : quotes) {
                Acordao quotedAcordao = acordaos.get( q);
                if( quotedAcordao != null) {
		    acordao.quotes.add( quotedAcordao);
                    quotedAcordao.isQuotedBy.add( acordao);
		}
		else
	            System.out.println("not found quotes: "+ q);
            }
        }
    }

    private ArrayList<String> dbListToArrayListOfIDs(BasicDBList list) {
        ArrayList<String> arrayList = new ArrayList<String>();
        for (Object object : list) {
            String id = object.toString();
            arrayList.add(id);
        }
        return arrayList;
    }

    private Double euclidianDistance(HashMap<String, Double> pMap, HashMap<String, Double> qMap) {
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

    private HashMap<String, Double> initPageRanks(){
	HashMap<String, Double> pageRanks = new HashMap<String, Double>();
        for (Acordao acordao : acordaos.values()) {
            pageRanks.put( acordao.getID(), acordao.pageRank);
        }
	return pageRanks;
    }

    private HashMap<String, Double> updatePageRanks(){
        HashMap<String, Double> newPageRanks = new HashMap<String, Double>();
        for (Acordao acordao : acordaos.values()) {
            acordao.pageRank = acordao.tempPageRank;
            newPageRanks.put(acordao.getID(), acordao.pageRank);
        }
	return newPageRanks;
    }

    private HashMap<String, Double> updateNormalizePageRanks( Double sum){
        HashMap<String, Double> newPageRanks = new HashMap<String, Double>();
        for (Acordao acordao : acordaos.values()) {
            acordao.pageRank = acordao.tempPageRank / sum;
            newPageRanks.put( acordao.getID(), acordao.pageRank);
        }
	return newPageRanks;
    }

    private void insertPageRanksInCollection( DBCollection pageRanked){
        pageRanked.drop();
        for (Acordao acordao : acordaos.values()) {
            BasicDBObject doc = new BasicDBObject();
            doc.append("id", acordao.getID());
	    doc.append("relator", acordao.getRelator());
            doc.append("pageRank", acordao.pageRank);
            ArrayList<String> quotingAcordaos = new ArrayList<String>();
            for (Acordao quoting : acordao.isQuotedBy) {
                quotingAcordaos.add(quoting.getID());
            }
            doc.append("isQuotedBy", quotingAcordaos);
            ArrayList<String> quotedAcordaos = new ArrayList<String>();
            for (Acordao quoted : acordao.quotes) {
                quotedAcordaos.add(quoted.getID());
            }
            doc.append("quotes", quotedAcordaos);
            pageRanked.insert(doc);
        }
    }

    protected void calculatePageRanks1() throws UnknownHostException {

	HashMap<String, Double> pageRanks = initPageRanks();
	Integer rounds = 0;
        while(true) {
	    Double prSum = 0.0;
            for (Acordao acordao : acordaos.values()) {
                Double sum = 0.0;
                for(Acordao quotingAcordao : acordao.isQuotedBy) {
                    Double pr = quotingAcordao.pageRank;
                    Integer l = quotingAcordao.quotes.size();
                    Double term = pr/l;
                    sum += term;
                }
                acordao.tempPageRank = ((1 - d) / n) + (d * sum);
		prSum += acordao.tempPageRank;
            }
//	    HashMap<String, Double> newPageRanks = updateNormalizePageRanks( prSum);
	    HashMap<String, Double> newPageRanks = updatePageRanks();
	    rounds += 1;
            if (euclidianDistance(pageRanks, newPageRanks) < epsilon) break;

            pageRanks.clear();
            pageRanks = (HashMap<String, Double>) newPageRanks.clone();
        }
	System.out.println("rounds: "+rounds.toString());
	DBCollection pageRanked = db.getCollection( linksName+"pageRanked1");
        insertPageRanksInCollection( pageRanked);
    }

    protected void calculatePageRanks2() throws UnknownHostException {

	HashMap<String, Double> pageRanks = initPageRanks();
	Integer rounds = 0;
        while(true) {
	    Double prSum = 0.0;
            for (Acordao acordao : acordaos.values()) {
                Double sum = 0.0;
                for(Acordao quotingAcordao : acordao.isQuotedBy) {
                    sum = quotingAcordao.pageRank;
                }
                acordao.tempPageRank = ((1 - d) / n) + (d * sum);
		prSum += acordao.tempPageRank;
            }
//	    HashMap<String, Double> newPageRanks = updateNormalizePageRanks( prSum);
	    HashMap<String, Double> newPageRanks = updatePageRanks();
	    rounds += 1;
            if (euclidianDistance(pageRanks, newPageRanks) < epsilon) break;

            pageRanks.clear();
            pageRanks = (HashMap<String, Double>) newPageRanks.clone();
        }
	System.out.println("rounds: "+rounds.toString());
	DBCollection pageRanked = db.getCollection( linksName+"pageRanked2");
        insertPageRanksInCollection( pageRanked);
    }
}
