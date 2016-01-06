#-*- coding: utf-8 -*-
from django.shortcuts import render, render_to_response, RequestContext
from .models import Hrac
from hracTimu.models import HracTimu
from kategoriaTurnaju.models import KategoriaTurnaju
from tim.models import Tim
from turnaj.models import Turnaj
from zapas.models import Zapas
import django_tables2 as tables
from django_tables2 import RequestConfig
from django.utils.safestring import mark_safe
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from django.utils.encoding import smart_unicode



class BaseSimpleTable(tables.Table): 
    krstne_meno = tables.Column(verbose_name= 'Krstné meno',orderable=True)
    priezvisko = tables.Column(verbose_name= 'Priezvisko',orderable=True)
    poznamka = tables.Column(verbose_name= 'Poznámka',orderable=True)
    spirit = tables.Column(verbose_name= 'Počet Spiritov',orderable=False,empty_values=())
    pohlavie = tables.Column(verbose_name= 'Pohlavie',orderable=True,empty_values=())
    
    def render_foto(self,record):
        if record.foto == "" or record.foto is None:
            return mark_safe("<div class='round2'><img src='" +'https://secure.gravatar.com/avatar/ad516503a11cd5ca435acc9bb6523536?s=320'+ "'></div>")
        else:
            return mark_safe("<div class='round2'><img src='" +smart_unicode(record.foto)+ "'></div>")
     
    def render_klub(self,record):
        return mark_safe("<a href='klub_hrac=" +str(record.klub.id)+ "'>"+ smart_unicode(record.klub.nazov) +"</a>")   
    
    def render_spirit(self,record):
        hracitimu = HracTimu.objects.filter(hrac = record.id).values('tim')
        timy = Tim.objects.filter(id__in=hracitimu).values('zapas_tim')
        zapasy = Zapas.objects.filter(id__in=timy)
        spirity = zapasy.filter(spirit=True)
        return str(len(spirity))
         
    class Meta:
        model = Hrac
        fields = ('foto','priezvisko', 'pohlavie','krstne_meno','poznamka')
        attrs = {"class": "paleblue"}
        orderable = True



class SimpleTable(BaseSimpleTable):
    foto = tables.Column(verbose_name= 'Foto',orderable=True,empty_values=())
    prezivka = tables.LinkColumn('turnaj_hraca', args=[tables.A('id')], orderable=True, empty_values=(), verbose_name= 'Prezívka')
    klub = tables.Column(verbose_name= 'Klub',orderable=True)
    
    
    class Meta:
        model = Hrac
        fields = ('foto','prezivka','priezvisko', 'pohlavie', 'krstne_meno','klub','poznamka')
        attrs = {"class": "paleblue"}
        orderable = True
    
# Create your views here.
class SimpleTableKlikolNaKlub(BaseSimpleTable):
    foto = tables.Column(verbose_name= 'Foto',orderable=True,empty_values=())
    prezivka = tables.LinkColumn('turnaj_hraca', args=[tables.A('id')], orderable=True, empty_values=(), verbose_name= 'Prezívka')
    
    class Meta:
        model = Hrac
        fields = ('foto','prezivka','priezvisko', 'pohlavie', 'krstne_meno','poznamka')
        attrs = {"class": "paleblue"}
        orderable = True

def hrac(request):
    queryset = Hrac.objects.all()
    nazov = 'Hráči'
    obsah = mark_safe("<h1>" + nazov + "</h1><section>Zobrazenie všetkých hráčov </section>")
    table = SimpleTable(queryset)
    RequestConfig(request).configure(table)
    return render_to_response("table.html", {"table": table,"nazov": nazov,"obsah":obsah },context_instance=RequestContext(request))

from turnaj.views import SimpleTable as SimpleTableTurnaj

def turnaj_hraca (request, id):
    button = mark_safe('''<form action="#" method="get">Od: <script type="text/javascript"src="http://www.snaphost.com/jquery/Calendar.aspx"></script> &nbsp;Do: <script type="text/javascript">$(function () {$("#SnapHost_Calendar2").datepicker({ showOn: 'both', buttonImage: 'http://www.snaphost.com/jquery/calendar.gif',
    buttonImageOnly: true, changeMonth: true, showOtherMonths: true, selectOtherMonths: true
    });});</script>
    <input name="SnapHost_Calendar2" id="SnapHost_Calendar2" type="text" />
     <input type="submit" class="btn" value="Click" name="mybtn">
    </form>''')
    nazov = smart_unicode("Turnaje Hráča")
    hracitimu = HracTimu.objects.filter(hrac = id).values('tim')
    timy = Tim.objects.filter(id__in=hracitimu).values('kategoria_turnaju')
    kategorieTurnajov = KategoriaTurnaju.objects.filter(id__in=timy).values('turnaj')
    hrac = Hrac.objects.filter(id=id)
    queryset = Turnaj.objects.filter(id__in=kategorieTurnajov)
    
    if request.GET.get('mybtn') and request.GET.get("SnapHost_Calendar") != "" and request.GET.get("SnapHost_Calendar2") != "":
        od = request.GET.get("SnapHost_Calendar")
        od = od.split("/")
        od = [od[2], od[0], od[1]]
        od = "-".join(od)
        do = request.GET.get("SnapHost_Calendar2")
        do = do.split("/")
        do = [do[2], do[0], do[1]]
        do = "-".join(do)
        queryset= queryset.filter(datum_od__range=[od,do])
    
    table = SimpleTableTurnaj(queryset)
    RequestConfig(request).configure(table)
    obsah = None
    if hrac[0].foto != "":
        hracitimu = HracTimu.objects.filter(hrac = id).values('tim')
        timy = Tim.objects.filter(id__in=hracitimu).values('zapas_tim')
        zapasy = Zapas.objects.filter(id__in=timy)
        spirity = zapasy.filter(spirit=True)
        pocetSpiritov = len(spirity)
        meno = 'Meno: ' + smart_unicode(hrac[0].krstne_meno) + ' ' + smart_unicode(hrac[0].priezvisko) + '<br>'
        klub = 'Klub: ' + smart_unicode(hrac[0].klub) + '<br>'
        spirit = 'Spirit: ' + str(pocetSpiritov) + '<br>'
        pohlavie = 'Pohlavie: ' + smart_unicode(hrac[0].pohlavie) + '<br>'
        profil = "<div class='profil'>" + '<h3>Profil</h3>'+ meno + klub + pohlavie + spirit + '</div>'
        obsah = mark_safe("<h1>" + nazov + " " +smart_unicode(hrac[0].prezivka) + "</h1><section><div class='round'><img src='" + smart_unicode(hrac[0].foto) + "'></div> " + profil + " </section>")
    else:
        hracitimu = HracTimu.objects.filter(hrac = id).values('tim')
        timy = Tim.objects.filter(id__in=hracitimu).values('zapas_tim')
        zapasy = Zapas.objects.filter(id__in=timy)
        spirity = zapasy.filter(spirit=True)
        pocetSpiritov = len(spirity)
        meno = 'Meno: ' + smart_unicode(hrac[0].krstne_meno) + ' ' + smart_unicode(hrac[0].priezvisko) + '<br>'
        klub = 'Klub: ' + smart_unicode(hrac[0].klub) + '<br>'
        spirit = 'Spirit: ' + str(pocetSpiritov) + '<br>'
        pohlavie = 'Pohlavie: ' + smart_unicode(hrac[0].pohlavie) + '<br>'
        profil = "<div class='profil'>" + '<h3>Profil</h3>'+ meno + klub + pohlavie + spirit + '</div>'
        obsah = mark_safe("<h1>" + nazov + " " +smart_unicode(hrac[0].prezivka) + "</h1><section><div class='round'><img src='" + 'https://secure.gravatar.com/avatar/ad516503a11cd5ca435acc9bb6523536?s=320' + "'></div> " + profil + " </section>")
    return render_to_response("table.html", {"table": table,"nazov": nazov,"obsah":obsah, "button":button},context_instance=RequestContext(request))
   

def hraci_klubu(request,id):
    nazov = smart_unicode('Hráči Klubu')
    queryset = Hrac.objects.filter(klub = id)
    table = SimpleTableKlikolNaKlub(queryset)
    obsah = None
    if len(queryset) != 0:
        nazov_klubu = None
        if queryset[0].klub is not None:
            nazov_klubu = smart_unicode(queryset[0].klub)
            obsah = mark_safe("<h1>" + nazov + " "+ nazov_klubu +"</h1><section>"+ smart_unicode('Zobrazenie všetkých Klubov') +"</section>")
        else:
           obsah = mark_safe("<h1>NEEXISTUJÚ HRÁČI PRE DANÝ KLUB</h1>") 
    else:
        obsah = mark_safe("<h1>NEEXISTUJÚ HRÁČI PRE DANÝ KLUB</h1>")
    RequestConfig(request).configure(table)
    return render_to_response("table.html", {"table": table,"nazov": nazov,"obsah":obsah},context_instance=RequestContext(request))
    