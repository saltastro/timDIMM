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
    and index come from an <EW> Enum tag in SALT's XML ICD.  An example:
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

def safeType(x, typ):
    """
    need some way to take a type as an argument and safely transform first argument into it
    """
    try:
        return typ(x)
    except:
        return None

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
    dict of values within the cluster.  the values can be in one of six different data types:
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

    # main dict we'll populate and return
    tcs = {}

    # easy types where we just turn a string into the type we want, safely
    types = ["U32", "DBL", "String", "Boolean"]
    lambdas = [lambda x: safeType(x, int),
               lambda x: safeType(x, float),
               lambda x: safeType(x, str),
               lambda x: safeType(safeType(x, int), bool),
               ]
    simples = zip(types, lambdas)

    # get clusters
    clusters = root.getElementsByTagName("Cluster")

    # loop through each cluster
    for cluster in clusters:
        cls_name = cluster.getElementsByTagName("Name")[0].firstChild.data
        tcs[cls_name] = {}

        # pull out the complex datatypes we handle differently. 
        lists = cluster.getElementsByTagName("EW")
        arrays = cluster.getElementsByTagName("Array")

        # go through the simple data types
        for s in simples:
            typ = s[0]
            func = s[1]
            tags = cluster.getElementsByTagName(typ)
            for t in tags:
                (key, val) = parseElement(t)
                tcs[cls_name][key] = func(val)

        # loop through the EW elements and make them into ICD_EW objects
        for l in lists:
            (key, val) = parseElement(l)
            choices = []
            for c in l.getElementsByTagName("Choice"):
                choices.append(c.firstChild.data)
            tcs[cls_name][key] = ICD_EW(choices, safeType(val, int))

        # loop through the arrays
        for a in arrays:
            key = a.getElementsByTagName("Name")[0].firstChild.data
            # pull this out since we need it for clean-up
            tag = a.getElementsByTagName("Name")[1].firstChild.data
            vals = []
            for s in simples:
                typ = s[0]
                func = s[1]
                tags = a.getElementsByTagName(typ)
                for t in tags:
                    (k, v) = parseElement(t)
                    vals.append(func(v))

            tcs[cls_name][key] = vals
            
            # getElementsByTagName is fully recursive so Arrays generate spurious entries to the
            # dict of the cluster. e.g., 'lamp power' Array creates an entry called 'Boolean' and
            # 'Temperatures' one called 'Numeric'. use the tag we pulled out to remove it if it's there.
            try:
                del tcs[cls_name][tag]
            except:
                pass
            
    return tcs
