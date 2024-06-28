import ioc_extract
import re

gazetteer = {
    'Encoding/Encryption Algorithms': ['aes', 'xor', 'ror', 'base64', 'rc4', 'des', 'lznt1', 'cast', '3des', 'lzo'],
    'Communication Protocols': ['http', 'https', 'ftp', 'smtp', 'pop3', 'dns'],
    'Data Objects': ['desktop', 'clipboard', 'directory', 'exchange', 'gmail', 'outlook', 'mailbox', 'keystroke',
                     'keylogger', 'password']
}


def extract_terms(text, gazetteer):  # text will be in lower cose
    extracted_terms = {}

    for category, terms in gazetteer.items():
        extracted_terms[category] = []
        for term in terms:
            pattern = re.compile(r'\b{}\b'.format(re.escape(term)), re.IGNORECASE)
            matches = re.findall(pattern, text)

            extracted_terms[category].extend(matches)

    return extracted_terms


def GetTTPelements(Text):
    res, res_origin = ioc_extract.extract_observables(Text)

    Gazett_res = extract_terms(Text, gazetteer)

    Conversion = {
        "ipv4": res["ipv4addr"],
        "ipv6": res["ipv6addr"],
        "asn": res["asn"],
        "domain": res["fqdn"],
        "email": res["email"],
        "filename": res["filename"],
        "url": res["url"],
        "hash": res["md5"] + res["sha1"] + res["sha256"] + res["ssdeep"],
        "filepath": res["filepath"],
        "cve": res["cve"],
        "regkey": res["regkey"],
        "encodeencryptalgorithms": Gazett_res["Encoding/Encryption Algorithms"],
        "communicationprotocol": Gazett_res["Communication Protocols"],
        "dataobject": Gazett_res["Data Objects"]
    }

    countVector = []

    for i in Conversion:
        countVector.append(len(Conversion[i]))

    text2 = Text

    for i in Conversion:

        for j in Conversion[i]:
            text2 = text2.replace(j, i)

    return Conversion, countVector, text2.lower()
