
package test;

import java.net.*;

import org.xml.sax.InputSource;
import org.w3c.dom.*;

import javax.xml.transform.OutputKeys;
import javax.xml.transform.Transformer;
import javax.xml.transform.TransformerConfigurationException;
import javax.xml.transform.TransformerException;
import javax.xml.transform.TransformerFactory;
import javax.xml.transform.TransformerFactoryConfigurationError;
import javax.xml.transform.dom.DOMSource;
import javax.xml.transform.stream.StreamResult;
import javax.xml.parsers.DocumentBuilderFactory;

import java.io.FileWriter;
import java.io.IOException;
import java.io.PrintWriter;
import java.io.StringWriter;
import javax.xml.parsers.ParserConfigurationException;
import org.xml.sax.SAXException;

/** 
 * Scrape Google Geocode and Places API to populate 5-digit zip codes
 *
 * https://developers.google.com/places/documentation/#PlaceSearchRequests * 
 * 
 * @author Anonymous
 * 
 * Note: This method may break Google API usage policies but I cannot tell for sure.
 *
 */

public class GeocodeProcessor {

	private static final String GEOCODE_REQUEST = "https://maps.googleapis.com/maps/api/geocode/xml";
	private static final String TEXT_REQUEST = "https://maps.googleapis.com/maps/api/place/textsearch/xml";
	private static final String PLACES_REQUEST = "https://maps.googleapis.com/maps/api/place/search/xml";
	private static final String PLACES_DETAIL = "https://maps.googleapis.com/maps/api/place/details/xml";
	private static final String GOOGLE_KEY = "AIzaSyB5H8frwYEom9rgEzqjJ169nC5yZKVX1fQ";

	public GeocodeProcessor( int test, String testname, String sta, String county, String cit, String zip ) {

		System.out.println("Processing test " + test);
		
		/** String search to find latitude and longitude of nearest hotels to state+city+zip */
		String smartQuery = "hotel+near+" + cit + "+" + sta;
		smartQuery = smartQuery.replace( ' ', '+' );
		if ( zip.length() == 5 ) smartQuery = smartQuery + "+" + zip;

		Document geocodeResult = queryByText( GOOGLE_KEY, smartQuery );
		//printXML( geocodeResult );		
		XPathReader georesult = new XPathReader( geocodeResult );
		
	    int resPos = 1;
		while ( zip.length() != 5 ) { // search until 5 digit zip is found within result starting with first result in the response
			String ref = georesult.readString( "/PlaceSearchResponse/result[" + resPos + "]/reference/text()" );		
			Document detailResult = null; // create a non-null doc with doc builder?
			try {
				detailResult = queryPlaceByDetail( GOOGLE_KEY, ref );
			} catch (IOException e) {
				e.printStackTrace();
			} catch (SAXException e) {
				e.printStackTrace();
			} catch (ParserConfigurationException e) {
				e.printStackTrace();
			}
			//printXML( detailResult );
			XPathReader detail = new XPathReader( detailResult );
			NodeList nodeList = detail.readNodeList( "/PlaceDetailsResponse/result[" + resPos + "]/address_component" );
			for ( int i=0; i<nodeList.getLength(); i++ ) {  // loop through address components within each result
				String t = detail.readString( "/PlaceDetailsResponse/result[" + resPos + "]/address_component[" + (i+1) + "]/type[1]/text()" );
				if ( t.equalsIgnoreCase( "postal_code") ) {
					String res = detail.readString( "/PlaceDetailsResponse/result[" + resPos + "]/address_component[" + (i+1) + "]/long_name/text()" );
					if ( res.length() == 5 ) {
						zip = res; // if zip code is detected in response, within a result, stop searching and go to next test
					} else {
						System.out.println("zip length: " + res.length() );
					}
				}
			}
			resPos++;
		}

	    String address = georesult.readString( "/PlaceSearchResponse/result[" + resPos + "]/formatted_address" ).replace( ",", "" );
	    String lat = georesult.readString( "/PlaceSearchResponse/result[" + resPos + "]/geometry/location/lat/text()" );
	    String lng = georesult.readString( "/PlaceSearchResponse/result[" + resPos + "]/geometry/location/lng/text()" );

		archiveResult( test, testname, sta, county, cit, address, zip, lat, lng );

	}

	public void archiveResult( int test, String tname, String sta, String county, String cit, String add, String zip, String lat, String lng ) {
		System.out.println( "Result: " + test + "," + sta + "," + cit + "," + zip + "," + add + "," + lat + "," + lng + "," + tname );
		PrintWriter out = null;
		try {
			out = new PrintWriter( new FileWriter( "out.csv", true ) );
		} catch ( IOException e ) {
			e.printStackTrace();
		} 
		out.println( test + "," + sta + "," + county + "," + cit + "," + add + "," + zip + "," + lat + "," + lng + "," + tname ); 
		out.close(); 
	}

	public static Document queryGeocodeByCity( String key, String sta, String cit, String zip ) {

		//if ( sta.equals("null") ) sta = "OR";
		//if ( cit.equals("null") ) cit = "Portland";
		if ( zip.equals("null") ) zip = "";

		String urlString = GEOCODE_REQUEST
				+ "?address=" + cit + ",+" + sta + "+" + zip
				+ "&sensor=false"
				//+ "&region=us"
				+ "&key=" + key;
		System.out.println( urlString );
		Document result = sendQuery( urlString );
		return result;    	
	}

	public static Document queryByText( String key, String text ) {		
		String urlString = TEXT_REQUEST
				+ "?query=" + text
				+ "&sensor=false"
				+ "&key=" + key;
		System.out.println( urlString );
		Document result = sendQuery( urlString );
		return result;    	
	}

	public static Document queryPlaceByKeyword( String loc, String key, String keyword ) 
			throws IOException, SAXException, ParserConfigurationException {
		String urlString = PLACES_REQUEST
				+ "?location=" + loc 
				+ "&sensor=false"
				+ "&key=" + key
				+ "&rankby=distance"
				+ "&keyword=" + keyword;
		//System.out.println( urlString );
		Document result = sendQuery( urlString );
		return result;    	
	}

	public static Document queryPlaceByDetail( String key, String ref ) 
			throws IOException, SAXException, ParserConfigurationException {
		String urlString = PLACES_DETAIL
				+ "?reference=" + ref 
				+ "&sensor=false"
				+ "&key=" + key;
		//System.out.println( urlString );
		Document result = sendQuery( urlString );
		return result;    	
	}

	@SuppressWarnings("unused")
	private static Document queryPlaceByRadius( String loc, String key, String radius ) {
		String urlString = PLACES_REQUEST
				+ "?location=" + loc 
				+ "&sensor=false"
				+ "&key=" + key
				+ "&radius=" + radius;
		//System.out.println( urlString );
		Document result = sendQuery( urlString );
		return result;    	
	}

	private static Document sendQuery( String urlstring ) {
		URL url = null;
		try {
			url = new URL( urlstring );
		} catch (MalformedURLException e1) {
			e1.printStackTrace();
		}
		HttpURLConnection conn = null;
		try {
			conn = (HttpURLConnection)url.openConnection();
		} catch (IOException e1) {
			e1.printStackTrace();
		}
		Document result = null;
		try {
			conn.connect();
			InputSource geocoderResultInputSource 
			= new InputSource( conn.getInputStream() );
			result = DocumentBuilderFactory.newInstance()
					.newDocumentBuilder().parse( geocoderResultInputSource );
		} catch (IOException e) {
			e.printStackTrace();
		} catch (SAXException e) {
			e.printStackTrace();
		} catch (ParserConfigurationException e) {
			e.printStackTrace();
		} finally {
			conn.disconnect();
		}
		return result;		
	}

	public static void printXML( Document xmlDoc )  {
		System.out.print("\nGoogle Places Result\n------------------\n");
		Transformer transformer = null;
		try {
			transformer = TransformerFactory.newInstance().newTransformer();
		} catch (TransformerConfigurationException e) {
			e.printStackTrace();
		} catch (TransformerFactoryConfigurationError e) {
			e.printStackTrace();
		}
		transformer.setOutputProperty(OutputKeys.INDENT, "yes");
		StreamResult result = new StreamResult( new StringWriter() );
		DOMSource source = new DOMSource( xmlDoc );
		try {
			transformer.transform(source, result);
		} catch (TransformerException e) {
			e.printStackTrace();
		}
		String xmlString = result.getWriter().toString();
		System.out.println(xmlString);        
	}

}
