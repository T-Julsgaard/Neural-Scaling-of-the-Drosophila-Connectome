"""Build the academic PDFs from editable Markdown and vector figure PDFs."""
from pathlib import Path
import re, json, html, datetime
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle, Flowable, KeepTogether, HRFlowable
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from pypdf import PdfReader, PdfWriter, Transformation
import pypdfium2 as pdfium
from PIL import Image, ImageOps, ImageDraw

HERE=Path(__file__).resolve().parent
QA=HERE/'qa'; QA.mkdir(exist_ok=True)
FONT=Path('C:/Windows/Fonts')
for name,file in [('Body','times.ttf'),('BodyBold','timesbd.ttf'),('BodyItalic','timesi.ttf'),('BodyBoldItalic','timesbi.ttf'),('Symbols','cambria.ttc')]:
    pdfmetrics.registerFont(TTFont(name,str(FONT/file)))
pdfmetrics.registerFontFamily('Body',normal='Body',bold='BodyBold',italic='BodyItalic',boldItalic='BodyBoldItalic')
# NIPS 2017 proportions, measured from arXiv:1706.03762v7. The reference
# embeds Nimbus Roman; Windows Times New Roman is our compatible substitute.
WIDTH,HEIGHT=letter; MARGIN=108; CONTENT=WIDTH-2*MARGIN
styles={
 'body':ParagraphStyle('Body',fontName='Body',fontSize=10,leading=11,spaceAfter=5.5,alignment=TA_JUSTIFY,splitLongWords=True),
 'title':ParagraphStyle('Title',fontName='BodyBold',fontSize=17.2,leading=20,spaceBefore=13,spaceAfter=13,alignment=TA_CENTER,keepWithNext=True),
 'subtitle':ParagraphStyle('Subtitle',fontName='BodyItalic',fontSize=11,leading=13,spaceAfter=20,alignment=TA_CENTER,keepWithNext=True),
 'h2':ParagraphStyle('Heading2',fontName='BodyBold',fontSize=12,leading=14,spaceBefore=15,spaceAfter=10,keepWithNext=True),
 'h3':ParagraphStyle('Heading3',fontName='BodyBold',fontSize=10,leading=12,spaceBefore=10,spaceAfter=6,keepWithNext=True),
 'abstract_title':ParagraphStyle('AbstractTitle',fontName='BodyBold',fontSize=12,leading=14,spaceBefore=22,spaceAfter=14,alignment=TA_CENTER,keepWithNext=True),
 'abstract':ParagraphStyle('Abstract',fontName='Body',fontSize=10,leading=11,spaceAfter=5.5,leftIndent=36,rightIndent=36,alignment=TA_JUSTIFY),
 'caption':ParagraphStyle('Caption',fontName='Body',fontSize=9,leading=10,spaceBefore=8,spaceAfter=10,alignment=TA_JUSTIFY),
 'meta':ParagraphStyle('Meta',fontName='Body',fontSize=10,leading=11,spaceAfter=3,alignment=TA_CENTER,keepWithNext=True),
 'ref':ParagraphStyle('Reference',fontName='Body',fontSize=9,leading=10,spaceAfter=6,alignment=TA_JUSTIFY),
 'cell':ParagraphStyle('Cell',fontName='Body',fontSize=9,leading=10,spaceAfter=0),
 'cellhead':ParagraphStyle('Cellhead',fontName='BodyBold',fontSize=9,leading=10,spaceAfter=0),
}
placements=[]
class FigureBlock(KeepTogether):
    """A figure, its descriptive heading, and caption travel together."""

class FlushFigures(Spacer):
    def __init__(self):
        super().__init__(0,0)

class PaperDocTemplate(SimpleDocTemplate):
    """Float a large figure to the next page while prose fills this one."""
    pending_figure=None

    def filterFlowables(self,flowables):
        first=flowables[0]
        if isinstance(first,(FigureBlock,FlushFigures)) and self.pending_figure:
            flowables[:0]=[PageBreak(),self.pending_figure]
            self.pending_figure=None
        elif isinstance(first,FigureBlock) and not self.frame._atTop:
            first.wrapOn(self.canv,self.frame._aW,self.frame._aH)
            if first._H>self.frame._y-self.frame._y1p:
                self.pending_figure=first
                flowables[0]=None

    def handle_pageBegin(self):
        super().handle_pageBegin()
        if self.pending_figure:
            self._hanging.append(self.pending_figure)
            self.pending_figure=None

class VectorFigure(Flowable):
    def __init__(self,path,maxheight=450):
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
    # Preserve mathematical Unicode absent from Times using a serif fallback.
    available=pdfmetrics.getFont('Body').face.charToGlyph
    s=''.join(c if ord(c) in available or ord(c)<128 else f'<font name="Symbols">{c}</font>' for c in s)
    s=re.sub(r'\[([^\]]+)\]\(([^)]+)\)',lambda m:f'<link href="{m.group(2)}" color="black">{m.group(1)}</link>',s)
    s=re.sub(r'\*\*(.+?)\*\*',r'<b>\1</b>',s)
    s=re.sub(r'(?<!\*)\*([^*]+)\*(?!\*)',r'<i>\1</i>',s)
    return s

def title_markup(text):
    """Balance two-line titles instead of leaving a single trailing word."""
    width=lambda s:pdfmetrics.stringWidth(s,'BodyBold',styles['title'].fontSize)
    words=text.split()
    if width(text)>CONTENT:
        choices=[(' '.join(words[:n]),' '.join(words[n:])) for n in range(1,len(words))]
        choices=[(a,b) for a,b in choices if max(width(a),width(b))<=CONTENT]
        if choices:
            a,b=min(choices,key=lambda pair:abs(width(pair[0])-width(pair[1])))
            return markup(a)+'<br/>'+markup(b)
    return markup(text)

def footer(canvas,doc):
    canvas.saveState()
    canvas.setFont('Body',10);canvas.setFillColor(colors.black)
    canvas.drawCentredString(WIDTH/2,40,str(doc.page))
    canvas.restoreState()

def table(lines):
    raw=[[x.strip() for x in line.strip().strip('|').split('|')] for line in lines]
    raw=[r for r in raw if not all(re.fullmatch(r'[:\- ]+',s) for s in r)]
    cols=len(raw[0])
    weights={2:[.33,.67],5:[.35,.13,.14,.18,.20],6:[.29,.1,.12,.15,.17,.17]}.get(cols,[1/cols]*cols)
    if cols==5 and 'C schedule' in raw[0][0]: weights=[.15,.16,.13,.30,.26]
    if cols==5 and 'Study' in raw[0][0]:weights=[.33,.17,.17,.13,.20]
    data=[[Paragraph(markup(v),styles['cellhead' if i==0 else 'cell']) for v in row] for i,row in enumerate(raw)]
    t=Table(data,colWidths=[CONTENT*w for w in weights],repeatRows=1,hAlign='LEFT')
    t.setStyle(TableStyle([('LINEABOVE',(0,0),(-1,0),.8,colors.black),('LINEBELOW',(0,0),(-1,0),.5,colors.black),('LINEBELOW',(0,-1),(-1,-1),.8,colors.black),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),4),('RIGHTPADDING',(0,0),(-1,-1),4),('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5)]))
    return t

def build(name,outname):
    placements.clear();source=(HERE/name).read_text(encoding='utf-8')
    story=[]; lines=source.splitlines();i=0;before_abstract=True;in_abstract=False
    while i<len(lines):
        line=lines[i].strip();i+=1
        if not line:continue
        if line=='<!-- PAGE -->':
            # Retain the dedicated abstract page; let the remaining text reflow.
            if in_abstract: story.append(PageBreak())
            before_abstract=False;in_abstract=False;continue
        if line.startswith('|'):
            group=[line]
            while i<len(lines) and lines[i].strip().startswith('|'):group.append(lines[i].strip());i+=1
            story.extend([Spacer(1,5),table(group),Spacer(1,8)]);continue
        if line.startswith('!['):
            rel=re.search(r'\]\((.+)\)',line).group(1)
            figure=VectorFigure((HERE/rel).with_suffix('.pdf'))
            while i<len(lines) and not lines[i].strip():i+=1
            if i<len(lines) and lines[i].startswith('**Figure'):
                caption=Paragraph(markup(lines[i].strip()),styles['caption']);i+=1
                heading=[]
                if story and isinstance(story[-1],Paragraph) and story[-1].style is styles['h3']:
                    heading=[story.pop()]
                story.append(FigureBlock(heading+[figure,caption]))
            else:story.append(figure)
            continue
        if line.startswith('# '):
            story.extend([HRFlowable(width='100%',thickness=4,color=colors.black),Paragraph(title_markup(line[2:]),styles['title']),HRFlowable(width='100%',thickness=1,color=colors.black,spaceAfter=16)])
            continue
        if line.startswith('## '):
            if line=='## References':story.extend([FlushFigures(),PageBreak()])
            before_abstract=False;in_abstract=line=='## Abstract'
            story.append(Paragraph(markup(line[3:]),styles['abstract_title' if in_abstract else 'h2']));continue
        if line.startswith('### '):story.append(Paragraph(markup(line[4:]),styles['subtitle' if before_abstract else 'h3']));continue
        group=[line]
        while i<len(lines) and lines[i].strip() and not lines[i].startswith(('#','|','![','<!--')):group.append(lines[i].strip());i+=1
        text=' '.join(group)
        sty='meta' if before_abstract else 'abstract' if in_abstract else 'caption' if text.startswith('**Figure') else 'ref' if re.match(r'^\[(?:S)?\d+\]',text) else 'body'
        story.append(Paragraph(markup(text),styles[sty]))
    temp=QA/(outname+'.base.pdf')
    story.append(FlushFigures())
    # SimpleDocTemplate adds six-point frame padding; compensate so the actual
    # text column is precisely 5.5 inches wide, with its top at one inch.
    doc=PaperDocTemplate(str(temp),pagesize=letter,leftMargin=MARGIN-6,rightMargin=MARGIN-6,topMargin=66,bottomMargin=66,title='Bounded participation calibration and memory retention'+(' - Technical supplement' if name.startswith('supplement') else ''),author='Thomas Julsgaard',subject='Computational research report; report date 16 September 2026; production 21 September 2026')
    doc.build(story,onFirstPage=footer,onLaterPages=footer)
    r=PdfReader(temp);w=PdfWriter();w.clone_document_from_reader(r)
    for page,x,y,width,height,path in placements:
        fp=PdfReader(path).pages[0]
        scale=width/float(fp.mediabox.width)
        tr=Transformation().translate(-float(fp.mediabox.left),-float(fp.mediabox.bottom)).scale(scale).translate(x,y)
        w.pages[page].merge_transformed_page(fp,tr)
    w.add_metadata({'/Author':'Thomas Julsgaard','/Title':doc.title,'/Subject':doc.subject,'/Creator':'ReportLab and pypdf; editable Markdown source','/Keywords':'Drosophila, mushroom body, calibration, retention, sequential learning'})
    output=HERE/(outname+'.pdf')
    # Replace atomically: an open preview may permit replacement but deny writes
    # to its current file handle. A failed build must not truncate the old PDF.
    pending=output.with_suffix('.pdf.tmp')
    with pending.open('wb') as f:w.write(f)
    pending.replace(output)
    render=pdfium.PdfDocument(str(output));dest=QA/outname;dest.mkdir(exist_ok=True)
    # Remove only this renderer's old previews when the page count changes.
    for pattern in ('page-*.png','contact-*.png'):
        for old in dest.glob(pattern):old.unlink()
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
