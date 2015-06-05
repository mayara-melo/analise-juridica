import java.net.UnknownHostException;
import java.util.ArrayList;
import java.util.LinkedList;
import java.util.HashMap;
import java.util.Map;
import java.util.Scanner;

public class Main {

    public static void main(String[] args) throws UnknownHostException {
	String inDBName = args[0];
	String inCollection = args[1];
	GraphMaker graphMaker = new GraphMaker( inDBName, inCollection);
//	CollectionsDealer cd = new CollectionsDealer("DJs", "stf", "stj");
//	cd.joinCollections();
        graphMaker.makeGraph();
    }
}
