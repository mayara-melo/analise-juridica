import com.mongodb.*;
import java.net.UnknownHostException;
import java.io.*;
import java.util.*;
import java.lang.String;
import javax.xml.stream.XMLStreamException;

public class Main {

    public static final Integer ACORDAOS_PER_PAGE = 10;
    private static Integer currentPercentage = -1;
    private static Integer count = 0;
    private static long total;
    private static final String UPDATE_FILE_NAME= "../update_settings";
 
    public static void main (String[] args) throws UnknownHostException {

        MongoClient mongoClient = new MongoClient();
        DB db = mongoClient.getDB( "DJ" );
        DBCollection collection = db.getCollection("acordaos");
        Integer fIndex, iIndex;
      //  collection.drop();

        System.out.println("\n");

	    try{

            BufferedReader br = new BufferedReader( new FileReader( UPDATE_FILE_NAME));
            fIndex = new Integer( br.readLine());
            String fDate = br.readLine();
            iIndex = new Integer( br.readLine());
            System.out.println("parsing acordaos from index " + iIndex+ " to " + fIndex);
            br.close();
        }
        catch( IOException ex){
            System.out.println( "couldn't read update settings file");
            ex.printStackTrace();
            return;
        }
        
        total = fIndex - iIndex+1;
	
        String fileName = "";
        for (Integer j = iIndex; j <= fIndex; j++ ) {
                fileName = String.format("../files/stj%06d.xml", j);
    	        System.out.println("file: "+ fileName);
                process( fileName, collection, j);
        }
        System.out.println("\n");
    }   

    private static void process (String fileName, DBCollection collection, Integer index) {
        printProgress();

        try {
            Parser parser = new Parser();
            parser.parse( fileName);
            String id = parser.getID();
            String uf = parser.getUF();
            String relator = parser.getRelator();
            String date = parser.getDate();
            String ementa = parser.getEmenta();
            LinkedList<String> citations = parser.getCitations();
            String decision = parser.getDecision();

            BasicDBObject doc = new BasicDBObject();
            doc.append("id", id);
            doc.append("uf", uf);
            doc.append("relator", relator);
            doc.append("date", date);
            doc.append("file", fileName.split("/")[2]);
            doc.append("index", index);
//            doc.append("tags", tags);
//            doc.append("quotesSomething", quotesSomething);
            doc.append("ranked", false);
            doc.append("ementa", ementa);
            doc.append("decisao", decision);
            doc.append("citacoes", citations);
/*            for( Iterator i = citations.listIterator(); i.hasNext(); )
                c = i.next();
                new BasicDBObject(c);
  */              
            collection.insert( doc);

        }
        catch (XMLStreamException ex) {
            System.out.println("Error reading file '" + fileName + "'");
            ex.printStackTrace();
        }
        catch (FileNotFoundException ex) {
            System.out.println("file '" + fileName + " not found'");
            ex.printStackTrace();
   	    }
    }    

    private static void printProgress() {
        count++;

        Integer newPercentage = (int)Math.floor(100 * count / total);
        if (newPercentage != currentPercentage) {
                System.out.print("\r    |");
            for (int i = 1; i <= newPercentage; i++)
                System.out.print("=");
            for (int i = newPercentage + 1; i <= 100; i++)
                System.out.print(" ");
            System.out.print("| " + newPercentage + "%  ");

            currentPercentage = newPercentage;
        }
    }
}
