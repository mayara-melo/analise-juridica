package stf.Parser;

import java.util.*;
import java.io.*;

public class Parser {

    private String[] excludeStrings = {
        "[![Salvar]",
        "[![Imprimir]",
        "**fim do documento"
    };

    private HashMap<String, Secao> secoes = new HashMap<String, Secao>();
    private Secao secaoAtual;

    public void parse(BufferedReader reader, String fileName) throws IOException {

        String line;
        Boolean firstTime = true;
        Secao titulo = new Secao("Titulo", fileName);
        secoes.put("Titulo", titulo);
        secaoAtual = titulo;

        while((line = reader.readLine()) != null) {
            line = line.replace("&nbsp", "");
            while(line.startsWith(" ") || line.startsWith("\t")) {
                line = line.replaceFirst("^\t", "");
                line = line.replaceFirst("^ ", "");
            }

            Boolean ok = true;
            for (int i = 0; i < excludeStrings.length; i++) {
                if (line.startsWith(excludeStrings[i]))
                    ok = false;
            }

            if (line.startsWith("**") && firstTime) {
                line = line.replace("**", "");
                firstTime = false;
            }

            if ( ok && line.length() > 3) {
                if (line.startsWith("**")) {
                    String title = line.replace("**", "");
                    Secao secao = new Secao(title, fileName);
                    secoes.put(title, secao);
                    secaoAtual = secao;
                }
                else {
                    secaoAtual.addLine(line.trim());
                }
            }
        }
    }

    String getID() {
        return secoes.get("Titulo").getID();
    }

    String getUF() {
        return secoes.get("Titulo").getUF();
    }

    String getRelator() {
        return secoes.get("Titulo").getRelator();
    }

    Date getDate() {
        return secoes.get("Titulo").getDate();
    }

    ArrayList<String> getTags() {
        return secoes.get("Indexação").getTags();
    }

    Boolean getQuotesSomething() {
        if (secoes.get("Acórdãos no mesmo sentido") == null) {
            if (secoes.get("Observação") == null)
                return false;
            return secoes.get("Observação").getAcordaosCitados();
        }
        return true;
    }

}
