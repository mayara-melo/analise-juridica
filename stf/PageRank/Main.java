import com.mongodb.*;
import java.net.UnknownHostException;
import java.util.*;

public class Main {

    private static HashMap<String, Acordao> acordaos = new HashMap<String, Acordao>();
    private static LinkedList<String> docTypesList = new LinkedList(Arrays.asList(
		"AI","RE","HC","ARE","ADI","RCL","RHC","MS","AC","RMS","INQ","EXT","PET","SS","AO","AR",
		"ACO","MI","AP","STA","IF","CC","ADPF","SEC","SL","CR","ADC","PSV","AS","HD", "AOE","PPE","RC","SE"));

    public static void main(String[] args) throws UnknownHostException {
        MongoClient mongoClient = new MongoClient();
        DB db = mongoClient.getDB( "DJs" );
        DBCollection links = db.getCollection("linksSTF");

	Iterator<String> iterator = docTypesList.iterator();
	while (iterator.hasNext()) {
	    acordaos = new HashMap<String,Acordao>();
	    String type = iterator.next();
	    BasicDBObject query = new BasicDBObject("acordaoId",new BasicDBObject("$regex", "^"+type+" .*")); 
	    System.out.println(query);
            buildMap( links.find(query));
	    DBCollection pageRank = db.getCollection("pgRk1STF"+type);
	    pageRank.drop();
            calculatePageRanksNcitations( pageRank);
	}

    }

    private static void buildMap( DBCursor cursor) throws UnknownHostException {
        Long numAcordaos = new Long( cursor.count());
        Double n = numAcordaos.doubleValue();

        while(cursor.hasNext()) {
            DBObject acordaoObject = cursor.next();
            try {
                String id          = acordaoObject.get("acordaoId").toString();
                BasicDBList quotes = (BasicDBList) acordaoObject.get("citacoes");
                ArrayList<String> quotesIDs = dbListToArrayListOfIDs( quotes);

                Acordao acordao = new Acordao( id, quotesIDs, numAcordaos);
                acordaos.put(id, acordao);

            } catch(NullPointerException ex) {
                System.out.println("NULL POINTER EXCEPTION, BITCH");
                ex.printStackTrace();
            }
        }
        for (Acordao acordao : acordaos.values()) {
            ArrayList<String> quotes = acordao.getQuotes();
            for (String q : quotes) {
//	    	System.out.println("quotes: "+ q);
                Acordao quotedAcordao = acordaos.get( q);
		if(quotedAcordao !=null){
                    acordao.quotes.add( quotedAcordao);
                    quotedAcordao.isQuotedBy.add( acordao);
		}
		else{
		    acordao.quotes.remove(quotedAcordao);
		}
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



    private static void calculatePageRanksNcitations( DBCollection pageRanked) throws UnknownHostException {

	Double epsilon = 1.0E-18;
	Double d = 0.85;

	HashMap<String, Double> pageRanks = new HashMap<String, Double>();
        for (Acordao acordao : acordaos.values()) {
            pageRanks.put( acordao.getID(), acordao.pageRank);
        }
	Double n = (double)acordaos.size();
        while(true) {
            for (Acordao acordao : acordaos.values()) {
                Double sum = 0.0;
                for(Acordao quotingAcordao : acordao.isQuotedBy) {
                    Double pr = quotingAcordao.pageRank;
                    Integer l = quotingAcordao.quotes.size();
                    Double term = pr/l;
                    sum += term;
                }
                acordao.tempPageRank = ((1 - d) / n) + (d * sum);
            }

            HashMap<String, Double> newPageRanks = new HashMap<String, Double>();

            for (Acordao acordao : acordaos.values()) {
                acordao.pageRank = acordao.tempPageRank;
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
