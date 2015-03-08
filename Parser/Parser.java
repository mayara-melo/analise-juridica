import java.util.*;
import java.io.*;

import java.util.ArrayList;
import java.util.List;
import javax.xml.stream.XMLInputFactory;
import javax.xml.stream.XMLStreamConstants;
import javax.xml.stream.XMLStreamException;
import javax.xml.stream.XMLStreamReader;
import javax.xml.stream.events.*;

public class Parser {

	private HashMap<String, String> secoes = new HashMap<String, String>();
	private LinkedList<String> citations = new LinkedList<String>();
	public void parse( String fileName) throws XMLStreamException, FileNotFoundException {

        XMLInputFactory factory = XMLInputFactory.newInstance();
        XMLStreamReader reader = factory.createXMLStreamReader( new FileInputStream( fileName));
		String tagContent = "";
        while(reader.hasNext()){
			int event = reader.next();
            String currSec = ""; 
          	switch(event){
              	case XMLStreamConstants.START_ELEMENT: 
                    tagContent = "";
                   // System.out.println( reader.getLocalName());
              		switch(reader.getLocalName()){
               		 	case "acordaoId":
                            secoes.put( "id", reader.getElementText().trim());
                  			break;
                		case "ementa":
                  			secoes.put( "ementa", reader.getElementText().trim());
                 			break;
                		case "dataJulg":
                  			secoes.put( "dataJulg", reader.getElementText().trim());
                 			break;
                		case "citacoes":
                            event = reader.nextTag();
                            while (event == XMLStreamConstants.START_ELEMENT) {
                                citations.add( reader.getElementText().trim());
                                event = reader.nextTag();
                            }
                            event = reader.nextTag();
                 			break;
                		case "dataPublic":
                  			secoes.put( "dataPublic", reader.getElementText().trim());
                 			break;
                		case "relator":
                  			secoes.put( "relator", reader.getElementText().trim());
                 			break;
                		case "uf":
                  			secoes.put( "uf", reader.getElementText().trim());
                 			break;
                		case "decisao":
                  			secoes.put( "decisao", reader.getElementText().trim());
                 			break;
                    }
                  	break; 
    		}	
		}	
    }
   
    String getID() {
        return secoes.get("id");
    }

    String getUF() {
        return secoes.get("uf");
    }

    String getRelator() {
        return secoes.get("relator");
    }

    String getDate() {
        return secoes.get("dataJulg");
    }
    String getDecision() {
        return secoes.get("decisao");
    }
    String getEmenta() {
        return secoes.get("ementa");
    }
    LinkedList<String> getCitations() {
        return citations;
    }

 /*   String getCitations() {
        return secoes.get("ementa");
    }*/
/*    Boolean getQuotesSomething() {
        if (secoes.get("Acórdãos no mesmo sentido") == null) {
            if (secoes.get("Observação") == null)
                return false;
            return secoes.get("Observação").getAcordaosCitados();
        }
        return true;
    }
*/
}
