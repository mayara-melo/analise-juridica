import java.util.ArrayList;

public class Acordao {

    public ArrayList<Acordao> quotes = new ArrayList<Acordao>();
    public ArrayList<Acordao> isQuotedBy = new ArrayList<Acordao>();

    private String id;
    private ArrayList<String> quotesIDs;

    public Double pageRank;
    public Double tempPageRank;

    public Acordao(String id, ArrayList<String> quotesIDs, Long numAcordaos ) {
        this.id        = id;
        this.quotesIDs = quotesIDs;
        this.pageRank  = 1/numAcordaos.doubleValue();
    }

    public ArrayList<String> getQuotes() {
        return this.quotesIDs;
    }

    public String getID() {
        return this.id;
    }
}
