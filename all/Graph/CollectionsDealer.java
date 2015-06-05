import com.mongodb.*;
import java.net.UnknownHostException;
import java.io.*;
import java.util.ArrayList;

public class CollectionsDealer {

    private static DBCollection collection1;
    private static DBCollection collection2;
    private static DBCollection jointCollection;

    public CollectionsDealer( String dbName, String collection1Name, String collection2Name) throws UnknownHostException{
	String jointCollectionName = collection1Name + collection2Name; 
	System.out.println("Collections will be joined to "+jointCollectionName);
        MongoClient mongoClient = new MongoClient();
        DB db = mongoClient.getDB( dbName );

        jointCollection = db.getCollection( jointCollectionName);
        collection1     = db.getCollection( collection1Name);
        collection2     = db.getCollection( collection2Name);
    }

    private static void copyCollectionItems( DBCollection collectionSource){
        DBCursor cursor = collectionSource.find();
	cursor.addOption(com.mongodb.Bytes.QUERYOPTION_NOTIMEOUT);
	while( cursor.hasNext()) {
            BasicDBObject acordao = (BasicDBObject) cursor.next();
	    jointCollection.save( acordao);
        }
    }

    protected static void joinCollections() {
	jointCollection.drop();
//	copyCollectionItems( collection1);
//	copyCollectionItems( collection2);
        DBCursor cursor = collection1.find();
	cursor.addOption(com.mongodb.Bytes.QUERYOPTION_NOTIMEOUT);
	while( cursor.hasNext()) {
            DBObject acordao = (BasicDBObject) cursor.next();
	    jointCollection.insert( acordao);
        }
        cursor = collection2.find();
	cursor.addOption(com.mongodb.Bytes.QUERYOPTION_NOTIMEOUT);
	while( cursor.hasNext()) {
            DBObject acordao = cursor.next();
	    jointCollection.insert( acordao);
        }
	System.out.println("Collections joined");
    }
}

