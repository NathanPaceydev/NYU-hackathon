"""Create a private five-slide view of the supplied template without changing it."""
from pathlib import Path
import zipfile
from xml.etree import ElementTree as ET
ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT.parent / 'Slides Templates  and Judging/NYUAD Hackathon Presentation Template.pptx'
TARGET = ROOT / '.build/ideation-template.pptx'
TARGET.parent.mkdir(exist_ok=True)
ns = {'p': 'http://schemas.openxmlformats.org/presentationml/2006/main',
      'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}
with zipfile.ZipFile(SOURCE) as source, zipfile.ZipFile(TARGET, 'w', zipfile.ZIP_DEFLATED) as target:
    presentation = ET.fromstring(source.read('ppt/presentation.xml'))
    slides = presentation.find('p:sldIdLst', ns)
    removed = []
    for slide in list(slides)[5:]:
        removed.append(slide.get('{' + ns['r'] + '}id'))
        slides.remove(slide)
    relationships = ET.fromstring(source.read('ppt/_rels/presentation.xml.rels'))
    for rel in list(relationships):
        if rel.get('Id') in removed:
            relationships.remove(rel)
    for name in source.namelist():
        data = source.read(name)
        if name == 'ppt/presentation.xml':
            data = ET.tostring(presentation, encoding='utf-8', xml_declaration=True)
        elif name == 'ppt/_rels/presentation.xml.rels':
            data = ET.tostring(relationships, encoding='utf-8', xml_declaration=True)
        target.writestr(name, data)
print(TARGET)
