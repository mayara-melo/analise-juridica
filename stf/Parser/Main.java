package stf.Parser;

import com.mongodb.*;
import java.net.UnknownHostException;
import java.io.*;
import java.util.Set;
import java.util.Date;
import java.util.ArrayList;
import java.lang.String;
import stf.Updater.STFUpdaterInfo;

public class Main {

    public static final Integer ACORDAOS_PER_PAGE = 10;
    private static final String UPDATE_SETTINGS_FILE = "../updater_settings"; 
    private static Integer currentPercentage = -1;
    private static Integer count = 0;
    private static long total;

    public static void main (String[] args) throws UnknownHostException {
        MongoClient mongoClient = new MongoClient();
        DB db = mongoClient.getDB( "DJ" );
        DBCollection collection = db.getCollection("acordaosSTF");
        Integer fIndex, iIndex;

	    try{

            BufferedReader br = new BufferedReader( new FileReader( UPDATE_SETTINGS_FILE));
            fIndex = new Integer( br.readLine());
            String fDate = br.readLine();
            iIndex = new Integer( br.readLine());
            System.out.println("parsing acordaos from index " + iIndex+ " to " + fIndex);
            System.out.println("iIndex: " + iIndex);
            System.out.println("fIndex: " + fIndex);
            br.close();
        }
        catch( IOException ex){
            System.out.println( "couldn't read update settings file");
            ex.printStackTrace();
            return;
        }
        
        total = fIndex - iIndex + 1;
	
        String fileName = "";
        for (Integer j = iIndex; j <= fIndex; j++ ) {
                fileName = String.format("../files/stf%06d.xml", j);
    	        System.out.println("file: "+ fileName);
                process( fileName, collection, j);
        }
        System.out.println("\n");
    }   

    private static void process (String fileName, DBCollection collection, Integer index) {
        printProgress();

        try {
            FileReader fileReader = new FileReader(fileName);
            BufferedReader bufferedReader = new BufferedReader(fileReader);

            Parser parser = new Parser();
            parser.parse(bufferedReader, fileName);
            String id = parser.getID();
            String uf = parser.getUF();
            String relator = parser.getRelator();
            Date date = parser.getDate();
            ArrayList<String> tags = parser.getTags();
            Boolean quotesSomething = parser.getQuotesSomething();

            BasicDBObject doc = new BasicDBObject();
            doc.append("id", id);
            doc.append("uf", uf);
            doc.append("relator", relator);
            doc.append("date", date);
            doc.append("file", fileName.split("/")[2]);
            doc.append("index", index);
            doc.append("tags", tags);
            doc.append("quotesSomething", quotesSomething);
            doc.append("ranked", false);
            collection.insert(doc);

            bufferedReader.close();
        }
        catch (FileNotFoundException ex) {
            System.out.println("Unable to open file '" + fileName + "'");
        }
        catch (IOException ex) {
            System.out.println("Error reading file '" + fileName + "'");
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
