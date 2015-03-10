package stf.Parser;

import java.util.ArrayList;
import java.util.Calendar;
import java.util.GregorianCalendar;
import java.util.Date;

public class Secao {

    private String name;
    private String fileName;
    private ArrayList<String> lines = new ArrayList<String>();

    public Secao (String name, String fileName) {
        this.name = name;
        this.fileName = fileName;
    }

    public String getName() {
        return this.name;
    }

    public void addLine (String line) {
        this.lines.add(line);
    }

    public String getID() {
        return lines.get(0).split("/")[0].trim();
    }

    public String getUF() {
        try {
            String uf = lines.get(0).split("/")[1].split("-")[0].trim();
            if (uf.length() > 2)
                return null;
            return uf;
        }
        catch(ArrayIndexOutOfBoundsException e) {
            return null;
        }
    }

    public String getRelator() {
        for (String s : this.lines) {
            if (s.startsWith("Relator")) {
                return s.split(":")[1].replace("Min.", "").trim();
            }
        }
        return "NULL";
    }

    public Date getDate() {
        String dateString = "0/0/0";
        for (String s : this.lines) {
            if (s.startsWith("Julgamento")) {
                dateString = s.split(":")[1].trim();
            }
        }
        int date = Integer.valueOf(dateString.split("/")[0]);
        int month = Integer.valueOf(dateString.split("/")[1].trim());
        int year = Integer.valueOf(dateString.split("/")[2].trim());
        Calendar calendar = new GregorianCalendar();
        calendar.set(year, month -1, date);
        return calendar.getTime();
    }

    public Boolean getAcordaosCitados() {
        for (String s : this.lines)
            if (s.matches(".*[Aa]c[oó]rd[aã]o *(s|\\( *s *\\))? *citado *(s|\\( *s *\\))? *:?.*")) return true;
        return false;
    }

    public ArrayList<String> getTags() {
        ArrayList<String> ret = new ArrayList<String>();

        String tagsLine = "";
        for (String line : lines) {
            if (! line.contains("VIDE EMENTA")) {
                tagsLine += line;
            }
        }
        tagsLine = tagsLine.replaceAll("- ", "");
        tagsLine = tagsLine.replaceAll("(, )*MIN\\..*?:",",");
        tagsLine = tagsLine.replaceAll("QUESTÃO DE ORDEM[ ]*:[:, ]*", "");
        tagsLine = tagsLine.replaceAll("[ ]*\\(.*?\\)[ ]*", "");
        tagsLine = tagsLine.replaceAll("(\\.+,,+)|(,+\\.+)", ",");
        tagsLine = tagsLine.replaceAll("(,,)|(;)", ",");
        tagsLine = tagsLine.replaceAll(",[ ]+,", ",");
        tagsLine = tagsLine.trim();
        String[] tags = tagsLine.split(",|\\.");
        for (String tag : tags) {
            if (! tag.isEmpty())
                ret.add(tag.trim());
        }
        return ret;
    }

}
