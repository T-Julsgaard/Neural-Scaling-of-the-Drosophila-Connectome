"""Build the academic PDFs from editable Markdown and vector figure PDFs."""
from pathlib import Path
import re, json, html, datetime
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle, Flowable
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from pypdf import PdfReader, PdfWriter, Transformation
import pypdfium2 as pdfium
from PIL import Image, ImageOps, ImageDraw

HERE=Path(__file__).resolve().parent
QA=HERE/'qa'; QA.mkdir(exist_ok=True)
FONT=Path('C:/Windows/Fonts')
for name,file in [('Body','cambria.ttc'),('BodyBold','cambriab.ttf'),('BodyItalic','cambriai.ttf'),('BodyBoldItalic','cambriaz.ttf'),('Sans','calibri.ttf'),('SansBold','calibrib.ttf'),('SansItalic','calibrii.ttf')]:
    pdfmetrics.registerFont(TTFont(name,str(FONT/file)))
pdfmetrics.registerFontFamily('Body',normal='Body',bold='BodyBold',italic='BodyItalic',boldItalic='BodyBoldItalic')
pdfmetrics.registerFontFamily('Sans',normal='Sans',bold='SansBold',italic='SansItalic',boldItalic='SansBold')
INK=colors.HexColor('#173C51'); GRAY=colors.HexColor('#59666D'); TEAL=colors.HexColor('#00877D')
WIDTH,HEIGHT=A4; MARGIN=52; CONTENT=WIDTH-2*MARGIN
styles={
 'body':ParagraphStyle('Body',fontName='Body',fontSize=11,leading=15.1,spaceAfter=9,textColor=colors.HexColor('#22282C'),splitLongWords=True),
 'title':ParagraphStyle('Title',fontName='SansBold',fontSize=28,leading=31.5,spaceBefore=10,spaceAfter=12,textColor=colors.black,keepWithNext=True),
 'h2':ParagraphStyle('Heading2',fontName='SansBold',fontSize=17,leading=21,spaceBefore=7,spaceAfter=12,textColor=colors.black,keepWithNext=True),
 'h3':ParagraphStyle('Heading3',fontName='SansBold',fontSize=12.6,leading=16,spaceBefore=7,spaceAfter=9,textColor=colors.black,keepWithNext=True),
 'caption':ParagraphStyle('Caption',fontName='Sans',fontSize=9.1,leading=12.1,spaceBefore=9,spaceAfter=6,textColor=GRAY),
 'meta':ParagraphStyle('Meta',fontName='Sans',fontSize=11,leading=15,spaceAfter=4,textColor=colors.black),
 'ref':ParagraphStyle('Reference',fontName='Body',fontSize=10.1,leading=13.7,spaceAfter=10,textColor=colors.HexColor('#22282C')),
 'cell':ParagraphStyle('Cell',fontName='Sans',fontSize=9,leading=11.6,spaceAfter=0,textColor=colors.HexColor('#22282C')),
 'cellhead':ParagraphStyle('Cellhead',fontName='SansBold',fontSize=9,leading=11.6,spaceAfter=0,textColor=colors.white),
}
placements=[]
class VectorFigure(Flowable):
    def __init__(self,path,maxheight=530):
        super().__init__(); self.path=path
        p=PdfReader(path).pages[0]; self.sw=float(p.mediabox.width);self.sh=float(p.mediabox.height)
        scale=min(CONTENT/self.sw,maxheight/self.sh)
        self.width=self.sw*scale; self.height=self.sh*scale
        self.hAlign='CENTER'
    def draw(self):
        x,y=self.canv.absolutePosition(0,0)
        placements.append((self.canv.getPageNumber()-1,x,y,self.width,self.height,self.path))

def markup(s):
    s=s.replace('–','-').replace('—','-').replace('‑','-')
    s=html.escape(s)
    s=re.sub(r'\[([^\]]+)\]\(([^)]+)\)',lambda m:f'<link href="{m.group(2)}" color="#006F69">{m.group(1)}</link>',s)
    s=re.sub(r'\*\*(.+?)\*\*',r'<b>\1</b>',s)
    s=re.sub(r'(?<!\*)\*([^*]+)\*(?!\*)',r'<i>\1</i>',s)
    return s

def footer(canvas,doc):
    canvas.saveState()
    if doc.page>1:
        canvas.setFont('Sans',8);canvas.setFillColor(GRAY)
        canvas.drawString(MARGIN,HEIGHT-32,'PARTICIPATION CALIBRATION AND MEMORY RETENTION')
        canvas.setStrokeColor(colors.HexColor('#D9E1E4'));canvas.setLineWidth(.5)
        canvas.line(MARGIN,HEIGHT-40,WIDTH-MARGIN,HEIGHT-40)
    canvas.setFont('Sans',8);canvas.setFillColor(GRAY)
    canvas.drawString(MARGIN,27,'Thomas Julsgaard  |  Research report  |  16 September 2026')
    canvas.drawRightString(WIDTH-MARGIN,27,str(doc.page))
    canvas.restoreState()

def table(lines):
    raw=[[x.strip() for x in line.strip().strip('|').split('|')] for line in lines]
    raw=[r for r in raw if not all(re.fullmatch(r'[:\- ]+',s) for s in r)]
    cols=len(raw[0])
    weights={2:[.33,.67],5:[.35,.13,.14,.18,.20],6:[.29,.1,.12,.15,.17,.17]}.get(cols,[1/cols]*cols)
    if cols==5 and 'C schedule' in raw[0][0]: weights=[.15,.16,.13,.30,.26]
    if cols==5 and 'Study' in raw[0][0]:weights=[.34,.14,.17,.15,.20]
    data=[[Paragraph(markup(v),styles['cellhead' if i==0 else 'cell']) for v in row] for i,row in enumerate(raw)]
    t=Table(data,colWidths=[CONTENT*w for w in weights],repeatRows=1,hAlign='LEFT')
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),INK),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#F2F6F7')]),('GRID',(0,0),(-1,-1),.4,colors.HexColor('#D9D9D9')),('VALIGN',(0,0),(-1,-1),'MIDDLE'),('LEFTPADDING',(0,0),(-1,-1),8),('RIGHTPADDING',(0,0),(-1,-1),8),('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7)]))
    return t

def build(name,outname):
    placements.clear();source=(HERE/name).read_text(encoding='utf-8')
    story=[]; lines=source.splitlines();i=0;before_abstract=True
    while i<len(lines):
        line=lines[i].strip();i+=1
        if not line:continue
        if line=='<!-- PAGE -->': story.append(PageBreak());before_abstract=False;continue
        if line.startswith('|'):
            group=[line]
            while i<len(lines) and lines[i].strip().startswith('|'):group.append(lines[i].strip());i+=1
            story.extend([Spacer(1,5),table(group),Spacer(1,13)]);continue
        if line.startswith('!['):
            rel=re.search(r'\]\((.+)\)',line).group(1)
            story.append(VectorFigure((HERE/rel).with_suffix('.pdf')));continue
        if line.startswith('# '):story.append(Paragraph(markup(line[2:]),styles['title']));continue
        if line.startswith('## '):
            before_abstract=False;story.append(Paragraph(markup(line[3:]),styles['h2']));continue
        if line.startswith('### '):story.append(Paragraph(markup(line[4:]),styles['h3']));continue
        group=[line]
        while i<len(lines) and lines[i].strip() and not lines[i].startswith(('#','|','![','<!--')):group.append(lines[i].strip());i+=1
        text=' '.join(group)
        sty='meta' if before_abstract else 'caption' if text.startswith('**Figure') else 'ref' if re.match(r'^\[(?:S)?\d+\]',text) else 'body'
        story.append(Paragraph(markup(text),styles[sty]))
    temp=QA/(outname+'.base.pdf')
    doc=SimpleDocTemplate(str(temp),pagesize=A4,leftMargin=MARGIN,rightMargin=MARGIN,topMargin=57,bottomMargin=49,title='Bounded participation calibration and memory retention'+(' - Technical supplement' if name.startswith('supplement') else ''),author='Thomas Julsgaard',subject='Computational research report; report date 16 September 2026; production 21 September 2026')
    doc.build(story,onFirstPage=footer,onLaterPages=footer)
    r=PdfReader(temp);w=PdfWriter();w.clone_document_from_reader(r)
    for page,x,y,width,height,path in placements:
        fp=PdfReader(path).pages[0]
        scale=width/float(fp.mediabox.width)
        tr=Transformation().translate(-float(fp.mediabox.left),-float(fp.mediabox.bottom)).scale(scale).translate(x,y)
        w.pages[page].merge_transformed_page(fp,tr)
    w.add_metadata({'/Author':'Thomas Julsgaard','/Title':doc.title,'/Subject':doc.subject,'/Creator':'ReportLab and pypdf; editable Markdown source','/Keywords':'Drosophila, mushroom body, calibration, retention, sequential learning'})
    output=HERE/(outname+'.pdf')
    with output.open('wb') as f:w.write(f)
    render=pdfium.PdfDocument(str(output));dest=QA/outname;dest.mkdir(exist_ok=True)
    stats=[];thumbs=[]
    for j,p in enumerate(render):
        pil=p.render(scale=1.6).to_pil().convert('RGB');pil.save(dest/f'page-{j+1:02}.png')
        small=pil.copy();small.thumbnail((298,421));tile=Image.new('RGB',(322,451),'#DEE5E8');tile.paste(small,((322-small.width)//2,9));ImageDraw.Draw(tile).text((12,432),f'Page {j+1}',fill='black');thumbs.append(tile)
        txt=p.get_textpage().get_text_range()
        stats.append({'page':j+1,'characters':len(txt),'text_start':txt[:100]})
    for start in range(0,len(thumbs),6):
        ts=thumbs[start:start+6];contact=Image.new('RGB',(966,451*((len(ts)+2)//3)),'white')
        for j,t in enumerate(ts):contact.paste(t,((j%3)*322,(j//3)*451))
        contact.save(dest/f'contact-{start//6+1}.png')
    (dest/'page_inventory.json').write_text(json.dumps(stats,indent=2))
    print(outname, 'pages',len(render),'words',len(source.split()))

if __name__=='__main__':
    build('report.md','academic_report')
    build('supplement.md','technical_supplement')
