all:
	javac *.java -classpath ./mongo-java-driver-2.12.4.jar:"../../../Codigo/";
	java -cp mongo-java-driver-2.12.4.jar:"../../../Codigo":. stf.Parser.Main

init:
	mongod
