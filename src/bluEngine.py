#! /usr/bin/python

import inkex
import math, re, cubicsuperpath, bezmisc
#sys.path.append('/usr/share/inkscape/extensions')


def match(string):
    #match = re.search(r"\w+\.\w\w", string)
    match = re.search(r"\w+\.\D", string)
    if match:
        answer = str(match.group())
        answer = answer[0:-2]
    else:
        answer = "null"
    return answer

def boxunion(b1,b2):
    if b1 is None:
        return b2
    elif b2 is None:
        return b1    
    else:
        return((min(b1[0],b2[0]), max(b1[1],b2[1]), min(b1[2],b2[2]), max(b1[3],b2[3])))

def cubicExtrema(y0, y1, y2, y3):
    cmin = min(y0, y3)
    cmax = max(y0, y3)
    d1 = y1 - y0
    d2 = y2 - y1
    d3 = y3 - y2
    if (d1 - 2*d2 + d3):
        if (d2*d2 > d1*d3):
            t = (d1 - d2 + math.sqrt(d2*d2 - d1*d3))/(d1 - 2*d2 + d3)
            if (t > 0) and (t < 1):
                y = y0*(1-t)*(1-t)*(1-t) + 3*y1*t*(1-t)*(1-t) + 3*y2*t*t*(1-t) + y3*t*t*t
                cmin = min(cmin, y)
                cmax = max(cmax, y)
            t = (d1 - d2 - math.sqrt(d2*d2 - d1*d3))/(d1 - 2*d2 + d3)
            if (t > 0) and (t < 1):
                y = y0*(1-t)*(1-t)*(1-t) + 3*y1*t*(1-t)*(1-t) + 3*y2*t*t*(1-t) + y3*t*t*t
                cmin = min(cmin, y)
                cmax = max(cmax, y)
    elif (d3 - d1):
        t = -d1/(d3 - d1)
        if (t > 0) and (t < 1):
            y = y0*(1-t)*(1-t)*(1-t) + 3*y1*t*(1-t)*(1-t) + 3*y2*t*t*(1-t) + y3*t*t*t
            cmin = min(cmin, y)
            cmax = max(cmax, y)
    return cmin, cmax

def refinedBBox(path):
    xmin,xMax,ymin,yMax = path[0][0][1][0],path[0][0][1][0],path[0][0][1][1],path[0][0][1][1]
    for pathcomp in path:
        for i in range(1, len(pathcomp)):
            cmin, cmax = cubicExtrema(pathcomp[i-1][1][0], pathcomp[i-1][2][0], pathcomp[i][0][0], pathcomp[i][1][0])
            xmin = min(xmin, cmin)
            xMax = max(xMax, cmax)
            cmin, cmax = cubicExtrema(pathcomp[i-1][1][1], pathcomp[i-1][2][1], pathcomp[i][0][1], pathcomp[i][1][1])
            ymin = min(ymin, cmin)
            yMax = max(yMax, cmax)
    return xmin,xMax,ymin,yMax


def roughBBox(path):
    xmin,xMax,ymin,yMax = path[0][0][0][0],path[0][0][0][0],path[0][0][0][1],path[0][0][0][1]
    for pathcomp in path:
        for ctl in pathcomp:
            for pt in ctl:
                xmin = min(xmin,pt[0])
                xMax = max(xMax,pt[0])
                ymin = min(ymin,pt[1])
                yMax = max(yMax,pt[1])
    return xmin,xMax,ymin,yMax

def getOrigin(child, layer):
    xoffsetattrib = child.attrib.get("{http://www.inkscape.org/namespaces/inkscape}transform-center-x")
    yoffsetattrib = child.attrib.get("{http://www.inkscape.org/namespaces/inkscape}transform-center-y")
    xoffset = float(layer.get("width"))
    xoffset = float(xoffset/2)
    yoffset = float(layer.get("height"))
    yoffset = float(yoffset/2)
    if xoffsetattrib != None:
        val = float(xoffset) + float(xoffsetattrib)
        layer.set("xorigin", str(val))
    else:
        layer.set("xorigin", str(xoffset))
        
    if yoffsetattrib != None:
        val = float(yoffset) + float(yoffsetattrib)
        layer.set("yorigin", str(val))
    else:
        layer.set("yorigin", str(xoffset))
    
    if xoffsetattrib != None:
        val = float(float(xoffset) + float(xoffsetattrib))
        layer.set("xorigin", str(val))
    else: layer.set("xorigin", str(xoffset))
        
    if yoffsetattrib != None:
        val = float(float(yoffset) + float(yoffsetattrib))
        layer.set("yorigin", str(val))
    else: layer.set("yorigin", str(yoffset))

def updateName(child):
    for at in child.attrib:
        if at == inkex.addNS('export-filename','inkscape'):
            name = child.attrib.get(at)
            name = match(name)
            child.attrib.update({'name':name})
            
def parseRect(child, parent, svg):
    updateName(child)
    layer = inkex.etree.SubElement(parent, str(child.get("id")), attrib=None, nsmap=None)
    y = float(child.get("y"))
    h0 = float(child.get("height"))
    h = inkex.unittouu(svg.get('height'))
    y = y + h0;
    y = h-y
    layer.set("name", str(child.get("name")))
    layer.set("x", str(child.get("x")))
    layer.set("y", str(y))
    layer.set("width", str(child.get("width")))
    layer.set("height", str(child.get("height")))
    getOrigin(child, layer)
    
def parseImage(child, parent, svg):
    updateName(child)
    layer = inkex.etree.SubElement(parent, str(child.get("id")), attrib=None, nsmap=None)
    y = float(child.get("y"))
    h0 = float(child.get("height"))
    h = inkex.unittouu(svg.get('height'))
    y = y + h0;
    y = h-y
    val = child.attrib.get("{http://www.w3.org/1999/xlink}href")
    name = match(val)
    child.attrib.update({'name':name})
    layer.set("name", str(child.get("name")))
    layer.set("x", str(child.get("x")))
    layer.set("y", str(y))
    layer.set("width", str(child.get("width")))
    layer.set("height", str(child.get("height")))
    getOrigin(child, layer)

def parsePath(child, parent, svg):
    updateName(child)
    layer = inkex.etree.SubElement(parent, str(child.get("id")), attrib=None, nsmap=None)
    path = cubicsuperpath.parsePath(child.get("d"))
    pageHeight = inkex.unittouu(svg.attrib['height'])
    rob = roughBBox(path)
    reb = refinedBBox(path)
    box = boxunion(rob, reb)
    x = box[0]
    width = box[1] - box[0]
    y = pageHeight - box[3]
    height = box[3] - box[2]
    layer.set("name", str(child.get("name")))
    layer.set("x", str(x))
    layer.set("y", str(y))
    layer.set("width", str(width))
    layer.set("height", str(height))
    getOrigin(child, layer)
    
def parseText(child, parent, svg):
    return


#===============================================================================
# 
#===============================================================================

class bluEngine (inkex.Effect):
    def __init__(self):
        inkex.Effect.__init__(self)
    
        self.OptionParser.add_option('--mode', action = 'store',
        type = 'string', dest = 'mode', default = "json",
        help = 'choose xml or json based output file')
        
    def output(self):
        print self.data
    
    def effect(self):
        mode = self.options.mode
        
        json = re.match("json", mode)
        xml = re.match("xml", mode)
        
        if json != None:
            print "implement later"
            #sys.stderr.write("mode is json ")
        elif xml != None:
            print "default implementation"
            #sys.stderr.write("mode is xml ")
        else:
            print "shouldn't get here! "
            #sys.stderr.write("no mode selected! ")
            
        
        svg = self.document.getroot();
        self.data = ""
        root = inkex.etree.Element("LEVEL", attrib=None, nsmap=None)
        for element in svg:
            if element.tag == inkex.addNS('g','svg'):
                main = inkex.etree.SubElement(root, str(element.get("id")), attrib=None, nsmap=None)
                for child in element.getchildren():
                    if child.tag == inkex.addNS('rect','svg'):
                        parseRect(child, main, svg)
                    
                    elif child.tag == inkex.addNS('path','svg'):
                        parsePath(child, main, svg)
                    
                    elif child.tag == inkex.addNS('flowRoot','svg'):
                        parseText(child, main, svg)
                        
                    elif child.tag == inkex.addNS('image','svg'):
                        parseImage(child, main, svg)
                    else:
                        break
                        
        self.data = inkex.etree.tostring(root, pretty_print=True)
                    
effect = bluEngine() 
effect.affect() 
