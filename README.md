# PyJSONQuery
A library for implementing a JSON Querying language in Python

## Why not just 'JSONQuery'

Implementations might (hopefully) be called for for other languages.

## Inspiration

The inspiration for this comes from [XPath](https://www.w3.org/TR/xpath-31/) and [XQuery](https://www.w3.org/TR/xquery-31/). 
A simple guide for both may be found at the [W3Schools XPath Tutorial](https://www.w3schools.com/xml/xpath_intro.asp) and the [W3Schools XQuery Tutorial](https://www.w3schools.com/xml/xquery_intro.asp).

## Focus

The primary focus for this will be fairly basic querying (specify a path, get zero or more elements) and very basic operations (such as aggregations, transformations, mutation, and looping)

## Example

Take the following document:

```json
{"name" : "ns1:timeSeriesResponseType",
"declaredType" : "org.cuahsi.waterml.TimeSeriesResponseType",
"scope" : "javax.xml.bind.JAXBElement$GlobalScope",
"value" : {
  "queryInfo" : {
    "queryURL" : "http://waterservices.usgs.gov/nwis/iv/format=json&indent=on&sites=01646500&period=PT1H&parameterCd=00060&siteStatus=all",
    "criteria" : {
      "locationParam" : "[ALL:01646500]",
      "variableParam" : "[00060]",
      "parameter" : [ ]
    },
    "note" : [ {
      "value" : "[ALL:01646500]",
      "title" : "filter:sites"
    }, {
      "value" : "[mode=PERIOD, period=PT1H, modifiedSince=null]",
      "title" : "filter:timeRange"
    }, {
      "value" : "methodIds=[ALL]",
      "title" : "filter:methodId"
    }, {
      "value" : "2022-03-15T12:37:07.500Z",
      "title" : "requestDT"
    }, {
      "value" : "a04cffb0-a45c-11ec-b279-005056beda50",
      "title" : "requestId"
    }, {
      "value" : "Provisional data are subject to revision. Go to http://waterdata.usgs.gov/nwis/help/?provisional for more information.",
      "title" : "disclaimer"
    }, {
      "value" : "caas01",
      "title" : "server"
    } ]
  },
  "timeSeries" : [ {
    "sourceInfo" : {
      "siteName" : "POTOMAC RIVER NEAR WASH, DC LITTLE FALLS PUMP STA",
      "siteCode" : [ {
        "value" : "01646500",
        "network" : "NWIS",
        "agencyCode" : "USGS"
      } ],
      "timeZoneInfo" : {
        "defaultTimeZone" : {
          "zoneOffset" : "-05:00",
          "zoneAbbreviation" : "EST"
        },
        "daylightSavingsTimeZone" : {
          "zoneOffset" : "-04:00",
          "zoneAbbreviation" : "EDT"
        },
        "siteUsesDaylightSavingsTime" : true
      },
      "geoLocation" : {
        "geogLocation" : {
          "srs" : "EPSG:4326",
          "latitude" : 38.94977778,
          "longitude" : -77.12763889
        },
        "localSiteXY" : [ ]
      },
      "note" : [ ],
      "siteType" : [ ],
      "siteProperty" : [ {
        "value" : "ST",
        "name" : "siteTypeCd"
      }, {
        "value" : "02070008",
        "name" : "hucCd"
      }, {
        "value" : "24",
        "name" : "stateCd"
      }, {
        "value" : "24031",
        "name" : "countyCd"
      } ]
    },
    "variable" : {
      "variableCode" : [ {
        "value" : "00060",
        "network" : "NWIS",
        "vocabulary" : "NWIS:UnitValues",
        "variableID" : 45807197,
        "default" : true
      } ],
      "variableName" : "Streamflow, ft&#179;/s",
      "variableDescription" : "Discharge, cubic feet per second",
      "valueType" : "Derived Value",
      "unit" : {
        "unitCode" : "ft3/s"
      },
      "options" : {
        "option" : [ {
          "name" : "Statistic",
          "optionCode" : "00000"
        } ]
      },
      "note" : [ ],
      "noDataValue" : -999999.0,
      "variableProperty" : [ ],
      "oid" : "45807197"
    },
    "values" : [ {
      "value" : [
      {      
        "value" : "9000",
        "qualifiers" : [ "P" ],
        "dateTime" : "2022-03-15T07:30:00.000-04:00"
      },
      {      
        "value" : "9250",
        "qualifiers" : [ "P" ],
        "dateTime" : "2022-03-15T07:30:00.000-04:00"
      },
      {
        "value" : "9570",
        "qualifiers" : [ "P" ],
        "dateTime" : "2022-03-15T07:45:00.000-04:00"
      } ],
      "qualifier" : [ {
        "qualifierCode" : "P",
        "qualifierDescription" : "Provisional data subject to revision.",
        "qualifierID" : 0,
        "network" : "NWIS",
        "vocabulary" : "uv_rmk_cd"
      } ],
      "qualityControlLevel" : [ ],
      "method" : [ {
        "methodDescription" : "",
        "methodID" : 69928
      } ],
      "source" : [ ],
      "offset" : [ ],
      "sample" : [ ],
      "censorCode" : [ ]
    } ],
    "name" : "USGS:01646500:00060:00000"
  } ]
},
"nil" : false,
"globalScope" : true,
"typeSubstituted" : false
}
```

The query `/` will yield the entirety of the above document. The query `/value/queryInfo/queryURL` will yield `http://waterservices.usgs.gov/nwis/iv/format=json&indent=on&sites=01646500&period=PT1H&parameterCd=00060&siteStatus=all`, and `/value/timeSeries/0/values/0/value` will yield:

```json
{      
    "value" : "9000",
    "qualifiers" : [ "P" ],
    "dateTime" : "2022-03-15T07:30:00.000-04:00"
},
{      
    "value" : "9250",
    "qualifiers" : [ "P" ],
    "dateTime" : "2022-03-15T07:30:00.000-04:00"
},
{
    "value" : "9570",
    "qualifiers" : [ "P" ],
    "dateTime" : "2022-03-15T07:45:00.000-04:00"
}
```

Something like:

```python
summation = query("/value/timeSeries/0/values/0/value/*/value").sum()
```

would yield `27820`.
