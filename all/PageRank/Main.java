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
	PageRanker calculator = new PageRanker( inDBName, inCollection);
        calculator.calculatePageRanks1();
        calculator.calculatePageRanks2();
    }
}
