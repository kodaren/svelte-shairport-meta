import sys
import base64
import json
import xml.etree.ElementTree as ET

def from_hex(hex_string):
    bytes_object = bytes.fromhex(hex_string)
    return bytes_object.decode("ascii")

def read_data(line):
    data = ""
    try:
        data = base64.b64decode(line).decode('utf-8')
    except TypeError:
        pass
    return data

def guessImageMime(magic):

    if magic.startswith(b'\xff\xd8'):
        return 'image/jpeg'
    elif magic.startswith(b'\x89PNG\r\n\x1a\r'):
        return 'image/png'
    else:
        return "image/jpg"

if __name__ == "__main__":

    metadata = {}
    fi = sys.stdin
    while True:
        line = sys.stdin.readline()
        if not line:    #EOF
            break
        
        sys.stdout.flush()

        if not line.startswith("<item>"):
            continue
        lines = line

        while line.find("</item>") < 0:
            line = sys.stdin.readline()
            lines = lines + line
        #print ("Lines: " + lines)

        root = ET.fromstring(lines)
        typ = from_hex(root.find("type").text)
        code = from_hex(root.find("code").text)
        length = int(root.find("length").text)
        dataEl = root.find("data")

        if (dataEl == None ):
            continue

        #data = dataEl.text
        
        pict = None
        data = ""
        if (typ =="ssnc" and code == "PICT"):
            pict = dataEl.text.lstrip()
            pictData = base64.b64decode(pict)
            mime = guessImageMime(pictData)
            print ( json.dumps({"CoverArt":{ "Base64Encoded": pict, "Mime": mime } }) )
            sys.stdout.flush()
            continue

        data = read_data(dataEl.text.strip())
        
        # Everything read
        if (typ == "core"):
            if (code == "asal"):
                metadata['Album Name'] = data
            elif (code == "asar"):
                metadata['Artist'] = data
            #elif (code == "ascm"):
            #    metadata['Comment'] = data
            elif (code == "asgn"):
                metadata['Genre'] = data
            elif (code == "minm"):
                metadata['Title'] = data
            elif (code == "ascp"):
                metadata['Composer'] = data
            #elif (code == "asdt"):
            #    metadata['File Kind'] = data
            #elif (code == "assn"):
            #    metadata['Sort as'] = data
            #elif (code == "clip"):
            #    metadata['IP'] = data
        if (typ == "ssnc" and code == "snam"):
            metadata['snam'] = data
        if (typ == "ssnc" and code == "prgr"):
            #metadata['prgr'] = data
            prgr = data.split("/")
            if (len(prgr) == 3):
                pData ={} 
                pData['Start'] = prgr[0]
                pData['Current'] = prgr[1]
                pData['End'] = prgr[2]
                metadata['Progress']= pData

        if (typ == "ssnc" and code == "pfls"):
            metadata = {}
            print ( json.dumps({}) )
            sys.stdout.flush()
        if (typ == "ssnc" and code == "pend"):
            metadata = {}
            print ( json.dumps({}) )
            sys.stdout.flush()
        if (typ == "ssnc" and code == "prsm"):
            metadata['pause'] = False
        if (typ == "ssnc" and code == "pbeg"):
            metadata['pause'] = False
        if (typ == "ssnc" and code == "mden"):
            print ( json.dumps(metadata) )
            sys.stdout.flush()
            metadata = {}
