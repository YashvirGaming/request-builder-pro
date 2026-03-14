import xml.etree.ElementTree as ET

def parse_http_debugger_xml(file_path):

    requests = []

    context = ET.iterparse(file_path, events=("start", "end"))

    method = None
    url = None
    headers = {}
    body = ""

    for event, elem in context:

        if event == "end":

            if elem.tag == "Method":
                method = elem.text

            elif elem.tag == "Url":
                url = elem.text

            elif elem.tag == "Header":
                headers[elem.attrib.get("name")] = elem.text

            elif elem.tag == "Body":
                body = elem.text

            elif elem.tag == "Request":

                requests.append({
                    "method": method,
                    "url": url,
                    "headers": headers.copy(),
                    "payload": body
                })

                headers.clear()
                body = ""

                elem.clear()

    return requests