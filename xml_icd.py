#!/usr/bin/env python
"""
                               xml_icd

a collection of classes and functions for parsing the XML produced by SALT's TCS ICD.

Author                     Version             Date
--------------------------------------------------------
TE Pickering                 0.1             20121012

TODO
--------------------------------------------------------
will need to expand as more of the ICD is made available

Updates
--------------------------------------------------------

"""
import xml
import urllib2
import xml.dom.minidom

class ICD_EW:
    """
    ICD_EW(choices, index)

    Create an ICD_EW object from an array of choices and an index. The choices
    and index come from an <EW> tag in SALT's XML ICD.  An example:
    <EW>
      <Name>tcs mode</Name>
      <Choice>OFF</Choice>
      <Choice>INITIALISE</Choice>
      <Choice>READY</Choice>
      <Choice>SLEW</Choice>
      <Choice>TRACK</Choice>
      <Choice>GUIDE</Choice>
      <Choice>MAINTENANCE</Choice>
      <Choice>CALIBRATION</Choice>
      <Choice>MAJOR FAULT</Choice>
      <Choice>SHUTDOWN</Choice>
      <Val>6</Val>
    </EW>

    Parameters
    ----------
    choices : list
        A list of choices pulled from an <EW> tag in the XML ICD.
    index : int
        The <Val> of the <EW> denoting the index of the current choice

    Provides
    -------
    ICD_EW.choices - list of choices (as input)
    ICD_EW.index - index of current choice (as input)
    ICD_EW.val - choice denoted by provided index
    
    """
    def __init__(self, choices, index):
        self.choices = choices
        self.index = index
        if type(choices) == list:
            if index < len(choices):
                self.val = choices[index]
            else:
                self.val = None
        else:
            self.val = None

def parseElement(e):
    """
    almost every element has a Name and a Val so pull these out and handle null Vals
    """
    k = e.getElementsByTagName("Name")[0].firstChild.data
    if e.getElementsByTagName("Val")[0].firstChild:
        v = e.getElementsByTagName("Val")[0].firstChild.data
    else:
        v = None
    return (k, v)

def parseICD(url="http://sgs.salt/xml/salt-tcs-icd.xml"):
    """
    parser to take the XML ICD and turn it into a dict of clusters.  each cluster in turn is a
    dict of values within the cluster.  the values can be in one of five different data types:
       U32 - mapped to a python int
       DBL - mapped to a python float
       String - left as python unicode
       Boolean - mapped to python bool
       EW - mapped to a ICD_EW object defined here
       Array - mapped to a python list
    """
    doc = xml.dom.minidom.parse(urllib2.urlopen(url, timeout=1))

    # the root element will be a Cluster containing all other clusters
    root = doc.getElementsByTagName("Cluster")[0]

    tcs = {}

    clusters = root.getElementsByTagName("Cluster")

    # loop through each cluster
    for cluster in clusters:
        cls_name = cluster.getElementsByTagName("Name")[0].firstChild.data
        tcs[cls_name] = {}

        # pull out the six datatypes we handle. 
        ints = cluster.getElementsByTagName("U32")
        floats = cluster.getElementsByTagName("DBL")
        strings = cluster.getElementsByTagName("String")
        bools = cluster.getElementsByTagName("Boolean")
        lists = cluster.getElementsByTagName("EW")
        arrays = cluster.getElementsByTagName("Array")

        # loop through the ints
        for i in ints:
            (key, val) = parseElement(i)
            tcs[cls_name][key] = int(val)

        # loop through the floats
        for f in floats:
            (key, val) = parseElement(f)
            tcs[cls_name][key] = float(val)

        # loop through the strings
        for s in strings:
            (key, val) = parseElement(s)
            tcs[cls_name][key] = str(val)

        # loop through the bools
        for b in bools:
            (key, val) = parseElement(b)
            if val:
                tcs[cls_name][key] = bool(int(val))
            else:
                tcs[cls_name][key] = False

        # loop through the EW elements and make them into ICD_EW objects
        for l in lists:
            (key, val) = parseElement(l)
            choices = []
            for c in l.getElementsByTagName("Choice"):
                choices.append(c.firstChild.data)
            tcs[cls_name][key] = ICD_EW(choices, int(val))

        # loop through the arrays
        for a in arrays:
            key = a.getElementsByTagName("Name")[0].firstChild.data
            vals = []
            aints = a.getElementsByTagName("U32")
            afloats = a.getElementsByTagName("DBL")
            astrings = a.getElementsByTagName("String")
            abools = a.getElementsByTagName("Boolean")
            for i in aints:
                (k, v) = parseElement(i)
                vals.append(int(v))
            for f in afloats:
                (k, v) = parseElement(f)
                vals.append(float(v))
            for s in astrings:
                (k, v) = parseElement(s)
                vals.append(str(v))
            for b in abools:
                (k, v) = parseElement(b)
                if v:
                    vals.append(bool(int(v)))
                else:
                    vals.append(False)
            tcs[cls_name][key] = vals
            
    return tcs


