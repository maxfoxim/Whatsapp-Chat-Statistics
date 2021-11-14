# -*- coding: utf-8 -*-
import re
from re import *
from string import *
import matplotlib.pyplot as plt
import time
import numpy

import datetime
import matplotlib.dates as mdates
import matplotlib.cbook as cbook
from PIL import Image
from fpdf import FPDF

#Verbesserungen: Hilfen, Wer-Wem-geschrieben, Anzahl in Plot,

#Anleitung: Den Whatsapp verlauf an sich selbst (per Mail oder Cloud) schicken und in den gleichen Ordner wie das Programm legen. 
# Mein_Name in seinen Vornamen ändern, so wie es in der Datei steht. Das gleiche noch für den anderen Namen.
#Ausführen. Fertig.

# hier der volle Vorname und der erste Buchstaben vom nachname +.. Wenn unklar ist, einfach in die .txt Datei schauen.
Mein_Name="Stephan"
name_fremd="Elisabeth"


datei_zum_offnen="WhatsApp Chat mit "+name_fremd+".txt"
infile=open(datei_zum_offnen)
#infile=open(datei_zum_offnen)
#name=datei_zum_offnen[:-4]
####### Konstanten ######
balken=40 # Anzahl Balken bei 2x2 Plots
MINIMUMZEIT_HISTO=1   #10    #h
MINIMUMZEIT_Initative=12   #12   #h
Fotos_ausschliessen=True
save_as_pdf=False
############

figsize_ratio=(15,10)
dpi_angabe=150

#alles im Text ist klein geschrieben
name_klein      =Mein_Name.lower()
name_fremd_klein=name_fremd.lower()


#einlesen
dateifile=infile.read()

#schliessen
infile.close()

#nach Zeilen trenne
lines=dateifile.split(chr(10))
print("Anzahl Nachrichten",len(lines))


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def num_extr(a,b):
    #print "a,b",a, b
    if is_number(b) and is_number(a):
        return int(a)*10+int(b)
    #if is_number(a)!=True:
    #    return 0
    if is_number(a)==True:
        return int(a)

def monats_tage(monat):
	if (monat==1) or (monat==3) or (monat==5) or (monat==7) or (monat==8) or (monat==10) or (monat==12):
		return 31
	else:
		return 30


def alles_in_sekunden(Jahr,monat,tag,stunde,minute):
		return time.mktime((Jahr,monat,tag,stunde,minute,0,0,0,0))		


def zeit_ext(s):
	# extrahiere die Zeit
	anfang=2
	stunde=s[2:4]
	minute=s[5:7]
	minuten=float(minute)
	stunden=float(stunde)
	#print s
	#print "stunden,(stunden+minuten/60.)/24.",stunden,(stunden+minuten/60.)/24.
	return (stunden+minuten/60.)/24.,int(stunden),int(minuten)

def datum_ext(s):
	#extrahiere das Datum
	#print "S----",s
	Splitter=s.split(".")
	tag=int(Splitter[0])
	monat=int(Splitter[1])
	jahr=int(Splitter[2]) # vierstellig oder zweistellig!!!

	#print "tag,monat,jahr,jahr+((monat)*monats_tage(monat)+tag)/365.      ",tag,monat,jahr,jahr+((monat-1)*monats_tage(monat)+tag)/365.
	
	return 2000+jahr+((monat-1)*monats_tage(monat)+(tag))/365.,int(jahr),int(monat),int(tag)

def anzahl_woerter(zeile):
	#print re.findall("\w+", zeile)
	return len(re.findall("\w+", zeile))-7 #7 ist eine Konstante


def anzahl_emoji(zeile):
	zeile=zeile.replace("\"","")
	#print re.findall(u"[^\u0000-\u007e]", zeile)
	return len(re.findall(u"[^\u0000-\u007e]", zeile))/4 #6 ist eine Konstante


def zeit_differenzen(zeiten,personen,MINIMUMZEIT):
	zeit_ich_zu_ich=[]
	zeit_ich_zu_fremd=[]
	zeit_fremd_zu_ich=[]
	zeit_fremd_zu_fremd=[]
	zeit_konstante=60*60. # 60 sekunden mal 60 minuten = 1h
	for i in range(len(zeiten)-1):
		if (zeiten[i+1]-zeiten[i])/zeit_konstante>MINIMUMZEIT:
			if personen[i]=="ich" and personen[i+1]=="fremd":
				zeit_ich_zu_fremd. append((zeiten[i+1]-zeiten[i])/zeit_konstante)
			if personen[i]=="fremd" and personen[i+1]=="ich":
				zeit_fremd_zu_ich. append((zeiten[i+1]-zeiten[i])/zeit_konstante)
			if personen[i]=="fremd" and personen[i+1]=="fremd":
				zeit_fremd_zu_fremd.append((zeiten[i+1]-zeiten[i])/zeit_konstante)
			if personen[i]=="ich" and personen[i+1]=="ich":		
				zeit_ich_zu_ich.    append((zeiten[i+1]-zeiten[i])/zeit_konstante)
	return zeit_ich_zu_ich,zeit_ich_zu_fremd,zeit_fremd_zu_ich,zeit_fremd_zu_fremd

def zeit_differenzen_MAXI(zeiten,personen,MAXIMUMZEIT):
	zeit_ich_zu_ich=[]
	zeit_ich_zu_fremd=[]
	zeit_fremd_zu_ich=[]
	zeit_fremd_zu_fremd=[]
	zeit_konstante=60.*60. # 60 sekunden mal 60 minuten = 1h
	for i in range(len(zeiten)-1):
		if 0<(zeiten[i+1]-zeiten[i])/zeit_konstante<MAXIMUMZEIT :
			#print (zeiten[i+1]-zeiten[i])/zeit_konstante
			if personen[i]=="ich" and personen[i+1]=="fremd":
				zeit_ich_zu_fremd.append((zeiten[i+1]-zeiten[i])/zeit_konstante)
			if personen[i]=="fremd" and personen[i+1]=="ich":
				zeit_fremd_zu_ich.append((zeiten[i+1]-zeiten[i])/zeit_konstante)
			if personen[i]=="fremd" and personen[i+1]=="fremd":
				zeit_fremd_zu_fremd.append((zeiten[i+1]-zeiten[i])/zeit_konstante)
			if personen[i]=="ich" and personen[i+1]=="ich":		
				zeit_ich_zu_ich.append((zeiten[i+1]-zeiten[i])/zeit_konstante)
				
	return zeit_ich_zu_ich,zeit_ich_zu_fremd,zeit_fremd_zu_ich,zeit_fremd_zu_fremd

#nicht mhr nötig
def voranalyse(zeile):
	
	# finde extra zeile "\n"
	EXTRA_ZEILE=False
	datum= re.findall("[0-9][0-9].[0-9][0-9].[0-9][0-9]",lines[i]) 	
	if len(datum)==0:
		EXTRA_ZEILE=True				
			
	zeile=zeile.lower()
	
	#zeile=zeile.replace("ü","ue")
	zeile=zeile.replace("ö","oe")
	zeile=zeile.replace("ä","ae")
	zeile=zeile.replace("ß","ss")
		
	return zeile,EXTRA_ZEILE

def pronomen(liste_worter):
	du_worter=[]
	ich_worter=[]
	wir_worter=[]
	liste_ich=["ich","mir","mich","mein"]
	liste_du= ["du","dir","dich","dein"]
	liste_wir=["wir","uns","unseren"]
	
	for ich_wort in liste_ich:
		zwischen_ich=re.findall(ich_wort,liste_worter)
		if len(zwischen_ich) > 0:
			ich_worter.append(len(zwischen_ich))
	for du_wort in liste_du:
		zwischen_du=re.findall(du_wort,liste_worter)
		if len(zwischen_du) > 0:
			du_worter.append(len(zwischen_du))
	for wir_wort in liste_wir:
		zwischen_wir=re.findall(wir_wort,liste_worter)
		if len(zwischen_wir) > 0:
			wir_worter.append(len(zwischen_wir))		
	
	return sum(du_worter),sum(ich_worter),sum(wir_worter)


datum_array=[]

array11=[]
array21=[]
array12=[]
array22=[]

fremdzaehler=0
ichzaehler=0

anzahl_emoji_ich=[]
anzahl_emoji_fremd=[]

anzahl_worte_ich=[]
anzahl_worte_fremd=[]

anzahl_ich_worte_fremd=0
anzahl_ich_worte_ich=0
anzahl_du_worte_fremd=0
anzahl_du_worte_ich=0
anzahl_wir_worte_fremd=0
anzahl_wir_worte_ich=0

tageszeit=[]
zeit_array_person=[]
zeit_array_zeit=[]
datum_anzahl=[]
datum_liste=[]
zwischenspeicher=0
zeit_array_jahr_tage=[]
wochentag=[0,0,0,0,0,0,0]
matplotlib_zeitformat=[]



################ GRUPPEN CHATS ##################


mitglieder_gruppe_raw=[]
mitglieder_gruppe=[]
#Mitglieder finden
for i in lines[:]:
	
	mitglieder_gruppe_raw.append(re.findall(" -.*?:",i))		
	if  (    len(mitglieder_gruppe_raw[-1])>0 and (  len(re.findall('\d+', mitglieder_gruppe_raw[-1][0][:] )) < 1 )    ):
		mitglieder_gruppe.append(mitglieder_gruppe_raw[-1][0][:])

#print(mitglieder_gruppe)

mitglieder_gruppe=set(mitglieder_gruppe)
Info_Array=[]
for i in mitglieder_gruppe:
	worter=anzahl_woerter(i)
	Info_Array.append([i,0,0,i[2:-1]])




#print (Info_Array)

#Info_Teilnehmer=["Name","Anzahlnachrichten","Anzahl Worte"]
gesamtzahl_worte=0
worter_anzahl=0
for nachricht in lines[:]:
	#try:
	if True:	
		
		index=0
		while index<len(Info_Array):
			#print(index,Info_Array[index][0])
			if len(re.findall(Info_Array[index][0],nachricht))>0:
				worter_anzahl=anzahl_woerter(nachricht)
				Info_Array[index][1]=Info_Array[index][1]+1	
				Info_Array[index][2]=Info_Array[index][2]+worter_anzahl
				#if worter_anzahl>50:
				#print(worter_anzahl,gesamtzahl_worte)
				gesamtzahl_worte=gesamtzahl_worte+worter_anzahl

			index=index+1
	#except:
		#print("FEHLER Auffüllen",nachricht)	
		
		
print(Info_Array)	
print("Gesamtzahl",gesamtzahl_worte)
#print(Info_Array[0][:])
namen=[]
werte=[]
anzahl_worte=[]
prozent_anzahl_worte=[]
prozent_anzahl_nachrichten=[]
anzahl_worte_pro_nachricht=[]
anzahl_nachrichten_gesamt=len(lines)


for a in Info_Array:
	werte.append(a[1]) #anzahl_nachrichten
	anzahl_worte.append(a[2])
	namen.append(a[3])
	prozent_anzahl_worte.append(       round(a[2]/gesamtzahl_worte*100,1) )
	prozent_anzahl_nachrichten.append( round(a[1]/anzahl_nachrichten_gesamt*100,1) )

i=0
while i < len(Info_Array):
	if Info_Array[i][1]>0:
		anzahl_worte_pro_nachricht.append(round(Info_Array[i][2]/Info_Array[i][1],1))
	else:
		anzahl_worte_pro_nachricht.append(0)
	i=i+1
# Data to plot
print(prozent_anzahl_worte)
labels = namen
sizes = werte
anzahl_teilnehmer=len(sizes)
pseudo_werte=range(anzahl_teilnehmer)

# KuchenPlot
grosse_plot=12
plt.figure(figsize=(grosse_plot, grosse_plot))  # Don't create a humongous figure
plt.title(datei_zum_offnen[:-4]+"\nProzent Nachrichten")
plt.pie(sizes, labels=labels, #colors=colors,
	autopct='%1.1f%%', shadow=False, startangle=0)
plt.axis('equal')
plt.savefig(name_fremd+"_Pie_Chart.png",dpi=150)

#Barchart Anzahl Nachrichten
plt.figure(figsize=figsize_ratio, dpi=dpi_angabe)  

plt.subplots_adjust(bottom=0.15, top=0.95)
plt.title(datei_zum_offnen[:-4]+"\nAnzahl Nachrichten")
plt.xlim((-0.5,anzahl_teilnehmer))
plt.ylabel("Anzahl Nachrichten")
plt.gca().xaxis.grid(True)
plt.xticks(pseudo_werte,labels,rotation='vertical')
plt.bar(pseudo_werte,sizes,0.9)
i=0
for x_werte in pseudo_werte:
	plt.text(x_werte, sizes[i]+15,str(prozent_anzahl_nachrichten[i])+" %",horizontalalignment="center",fontsize=16)#,alignment="centering")
	i=i+1
plt.grid()
plt.savefig(name_fremd+"_Bargramm_Nachrichten.png")


#Barchart Anzahl Worte
plt.figure(figsize=figsize_ratio, dpi=dpi_angabe)  
plt.subplots_adjust(bottom=0.15, top=0.95)
plt.title(datei_zum_offnen[:-4]+"\nAnzahl Wörter")
plt.xlim((-0.5,anzahl_teilnehmer))
plt.ylabel("Anzahl Wörter")
plt.gca().xaxis.grid(True)
pseudo_werte=range(anzahl_teilnehmer)
plt.xticks(pseudo_werte,labels,rotation='vertical')
plt.bar(pseudo_werte,anzahl_worte,0.9)
i=0
for x_werte in pseudo_werte:
	plt.text(x_werte, anzahl_worte[i]+15,str(prozent_anzahl_worte[i])+" %",horizontalalignment="center",fontsize=16)#,alignment="centering")
	i=i+1
#plt.yscale('log')
plt.grid()
plt.savefig(name_fremd+"_Bargramm_Wörter.png")
	


#Barchart Anzahl Worte pro Nachricht
plt.figure(figsize=figsize_ratio, dpi=dpi_angabe)  
plt.subplots_adjust(bottom=0.15, top=0.95)
plt.title(datei_zum_offnen[:-4]+"\nAnzahl Wörter/Nachricht")
plt.xlim((-0.5,anzahl_teilnehmer))
plt.ylabel("Anzahl Wörter/Nachricht")
plt.gca().xaxis.grid(True)
pseudo_werte=range(anzahl_teilnehmer)
plt.xticks(pseudo_werte,labels,rotation='vertical')
plt.bar(pseudo_werte,anzahl_worte_pro_nachricht,0.9)
i=0
for x_werte in pseudo_werte:
	plt.text(x_werte, anzahl_worte_pro_nachricht[i],str(anzahl_worte_pro_nachricht[i]),horizontalalignment="center",fontsize=16)#,alignment="centering")
	i=i+1
#plt.yscale('log')
plt.grid()
plt.savefig(name_fremd+"_Bargramm_Worte_pro_Nachricht.png")
	
	


if anzahl_teilnehmer>0:
	#name_klein="stephan"

	############# MEDIEN Rausschneiden
	i=0
	if Fotos_ausschliessen:
		while i < len(lines)-1:
			if re.findall("<Medien ausgeschlossen>",lines[i]):
				lines[i]="FOTO"		
			i=i+1


	### Voranalyse
	i=0
	while i < len(lines)-1:
		lines[i],Extrazeile=voranalyse(lines[i])		
		if Extrazeile: # fuege zeilen mit Absatz zusammen
			lines[i-1]=lines[i-1]+" "+lines[i]
			del lines[i] 
			#print i,"Absatz"
			i=i-1
		i=i+1	


	print(Mein_Name)
	print("Name Klein:",name_klein,"ENDE")
	print( "----------------")
	i=0
	while i < len(lines)-1:
		SPEICHERE_ZEIT=False
	# zaehle fremde Beitrage
		if re.findall("- "+name_fremd_klein,lines[i]):
			fremdzaehler=fremdzaehler+1
			anzahl_worte_fremd.append(anzahl_woerter(lines[i])-1)
			anzahl_emoji_fremd.append(anzahl_emoji(lines[i]))
			#print (name,i,anzahl_worte_fremd[-1],"----------", len(zeit_array_person),len(zeit_array_zeit))#lines[i]    
			zeit_array_person.append("fremd")
			#print("fremd",lines[i])
			du_worter,ich_worter,wir_worter=pronomen(lines[i])
			anzahl_ich_worte_fremd=anzahl_ich_worte_fremd+ich_worter
			anzahl_du_worte_fremd =anzahl_du_worte_fremd+du_worter
			anzahl_wir_worte_fremd=anzahl_wir_worte_fremd+wir_worter
			
			SPEICHERE_ZEIT=True
	    
	# zaehle eigene Beitrage
		if re.findall("- "+name_klein,lines[i]):
			ichzaehler=ichzaehler+1
			anzahl_worte_ich .append(anzahl_woerter(lines[i]))
			anzahl_emoji_ich .append(anzahl_emoji(lines[i]))
			zeit_array_person.append("ich")
			#print("ich",lines[i])
			#print name,i,anzahl_worte_ich[-1],"----------", len(zeit_array_person),len(zeit_array_zeit)#lines[i]    
			#print ""
			du_worter,ich_worter,wir_worter=pronomen(lines[i])
			anzahl_ich_worte_ich=anzahl_ich_worte_ich+ich_worter
			anzahl_du_worte_ich =anzahl_du_worte_ich +du_worter
			anzahl_wir_worte_ich=anzahl_wir_worte_ich+wir_worter
			
			SPEICHERE_ZEIT=True

		#try:
		if SPEICHERE_ZEIT:
		#if 1==1:
		
			datum= re.findall("[0-9][0-9].[0-9][0-9].[0-9][0-9]",lines[i]) 
			zeiten=re.findall(", [0-9][0-9]:[0-9][0-9] - ",        lines[i])
			#print(datum,zeiten)
			if (len(datum)>0 and len(zeiten)>0):
				stunde,stunde_h,minute=zeit_ext(zeiten[0])
				datum,jahr,monat,tag=datum_ext(datum[0])             
				tageszeit.append(stunde)
				if datum!=None:
					datum_array.append(  datum+stunde*1/(60*24*365) )
					zeit_array_zeit.append(alles_in_sekunden(2000+jahr, monat, tag, stunde_h, minute))
					zeit=time.localtime(zeit_array_zeit[-1])
					zeit_array_jahr_tage.append(zeit[0]+zeit[-2]/365.) # Jahr+ Tag/365
					wochentag[zeit[-3]]=wochentag[zeit[-3]]+1
					#print zeit,zeit_array_jahr_tage[-1]
					if zeit_array_jahr_tage[-1]>zwischenspeicher:
						datum_anzahl.append(1)
						matplotlib_zeitformat.append(datetime.datetime(zeit[0], zeit[1], zeit[2]))
						datum_liste.append(zeit_array_jahr_tage[-1])
						zwischenspeicher=zeit_array_jahr_tage[-1]
						print (zeit)
					else:
						datum_anzahl[-1]=datum_anzahl[-1]+1
			else:
				print ("TEST",lines[i]	)			
					
					#print i,2000+jahr, monat, tag, stunde_h, minute 

		#except:
			#print "Zeile Fehler",i,lines[i]
		#print i,"--",len(zeit_array_person),len(zeit_array_zeit)
		i=i+1


	print ("anzahl_ich_worte_ich",anzahl_ich_worte_ich)

	######## Zur berechnung der Anzahl der initativ anschriften
	#MINIMUMZEIT_Initative=24 # in h
	zeit_ich_zu_ich,zeit_ich_zu_fremd,zeit_fremd_zu_ich,zeit_fremd_zu_fremd= zeit_differenzen(zeit_array_zeit,zeit_array_person,MINIMUMZEIT_Initative)
	Initative_Fremd=len(zeit_fremd_zu_fremd)+len(zeit_fremd_zu_ich)
	Initative_Ich=len(zeit_ich_zu_ich)+len(zeit_ich_zu_fremd)

	##### zur Berechnung der Durchschnittszeit der nachrichten
	MINIMUMZEIT=0 # in h
	zeit_ich_zu_ich,zeit_ich_zu_fremd,zeit_fremd_zu_ich,zeit_fremd_zu_fremd= zeit_differenzen(zeit_array_zeit,zeit_array_person,MINIMUMZEIT)
	Zeitabstand_Fremd=numpy.average(zeit_fremd_zu_fremd+zeit_fremd_zu_ich)
	Zeitabstand_Ich  =numpy.average(zeit_ich_zu_ich+zeit_ich_zu_fremd)


	##### zur Berechnung der Durchschnittsantwortzeit der nachrichten
	MAXIMUMZEIT=2 # in h
	zeit_ich_zu_ich,zeit_ich_zu_fremd,zeit_fremd_zu_ich,zeit_fremd_zu_fremd= zeit_differenzen_MAXI(zeit_array_zeit,zeit_array_person,MAXIMUMZEIT)
	Antwortzeit_Fremd=numpy.mean(zeit_fremd_zu_ich)*60
	Antwortzeit_ICH  =numpy.mean(zeit_ich_zu_fremd)*60


	########### für die Darstellung als Histogramm
	#MINIMUMZEIT_HISTO=0 # in h
	zeit_ich_zu_ich,zeit_ich_zu_fremd,zeit_fremd_zu_ich,zeit_fremd_zu_fremd= zeit_differenzen(zeit_array_zeit,zeit_array_person,MINIMUMZEIT_HISTO)
	#print("zeit_ich_zu_ich",zeit_ich_zu_ich,zeit_array_zeit,zeit_array_person)


	print ("Langen Zeitarry",len(zeit_array_person),len(zeit_array_zeit))

	print ("\n\nAnzahl der Nachrichten insgesamt")
	print (name_fremd, fremdzaehler)
	print ("Selbst", ichzaehler)
	Anzahl_Tage=int((max(datum_array)-min(datum_array))*365)
	print ("Anzahl Tage",Anzahl_Tage)



	######## Jahresverlauf

	years = mdates.YearLocator()   # every year
	months = mdates.MonthLocator()  # every month
	days = mdates.DayLocator()  # every month

	yearsFmt = mdates.DateFormatter('%d-%m-%y')

	plt.clf()
	fig, ax = plt.subplots(figsize=(14, 6))
	plt.subplots_adjust(left=0.05, bottom=None, right=0.99, top=None, wspace=0.35, hspace=0.4)
	#ax.plot(matplotlib_zeitformat,datum_anzahl,"o")#,1/365.,1,"b")
	ax.vlines(matplotlib_zeitformat,datum_anzahl,0)#,1/365.,1,"b")  #Daten

	# format the ticks
	ax.xaxis.set_major_locator(months)
	ax.xaxis.set_minor_locator(days)
	ax.xaxis.set_major_formatter(yearsFmt)

	#ax.ticklabel_format(style='plain', axis='x',useOffset=False)#, scilimits=(0,0))
	#ax.bar(datum_liste,datum_anzahl,1/365.,1,"b")

	ax.grid()
	ax.set_xlabel("Zeit")
	ax.set_ylabel("Anzahl Nachrichten")
	ax.set_title("Nachrichten im Jahresüberblick "+name_fremd)

	try: ## Datum an den Grenzen erweitern für bessere Sicht
		if (matplotlib_zeitformat[0].month-1)>0:
			datemin = datetime.date(matplotlib_zeitformat[0].year, matplotlib_zeitformat[0].month-1, 1)
		else:
			datemin = datetime.date(matplotlib_zeitformat[0].year-1, 12, 1)		
		if (matplotlib_zeitformat[-1].month+1)<13:
			datemax = datetime.date(matplotlib_zeitformat[-1].year, matplotlib_zeitformat[-1].month+1, 1)
		else:
			datemax = datetime.date(matplotlib_zeitformat[-1].year+1, 2, 1)		
		ax.set_xlim(datemin, datemax)
	except:
		print ("Problem mit Grenzen Datum")
	#ax.xaxis_date()
	ax.autoscale_view() # Dreht das x_label automatisch
	fig.autofmt_xdate()
	locator = mdates.HourLocator(interval=10)
	locator.MAXTICKS = 10000
	ax.xaxis.set_minor_locator(locator)
	#plt.ylim(0,40)
	plt.savefig(name_fremd+"_Jahresüberblick.png")

	################################### 2x2 Plot
	if len(zeit_fremd_zu_fremd)<2:    #um Fehler zu vermeiden
		zeit_fremd_zu_fremd.append(-1)
		

	plt.clf()
	plt.figure(figsize=figsize_ratio, dpi=dpi_angabe)  
	plt.subplot(223)
	plt.title("Ich auf mich")
	plt.xlabel("Stunden")
	plt.hist(zeit_ich_zu_ich,bins=balken)
	plt.subplot(222)
	plt.title("Ich zu "+name_fremd)
	plt.hist(zeit_ich_zu_fremd,bins=balken)
	plt.subplot(221)
	plt.title(name_fremd+" zu mir")
	plt.hist(zeit_fremd_zu_ich,bins=balken)
	plt.subplot(224)
	plt.title(name_fremd+" auf "+name_fremd)
	plt.hist(zeit_fremd_zu_fremd,bins=balken)
	plt.xlabel("Stunden")
	plt.savefig(name_fremd+"_Antwortzeiten.png")


	#####################################################################
	### plot wieviel nachrichten zu welcher Stunde verschickt wurden
	plt.clf()
	plt.figure(figsize=figsize_ratio, dpi=dpi_angabe)  
	tageszeit_stunden=[a*24 for a in tageszeit]
	plt.xlabel("Stunde")
	plt.ylabel("Anzahl Whatsapp Nachrichten")
	plt.xlim((0,24))
	plt.xticks([0,2,4,6,8,10,12,14,16,18,20,22])
	plt.grid()
	plt.title(name_fremd+" Anzahl Nachrichten pro Tageszeit")
	n, bins, patches=plt.hist(tageszeit_stunden,96) #  
	max_uhrzeit=bins[numpy.argmax(n)]
	plt.savefig(name_fremd+"_Tageszeit.png")
	  

	#####################################################################
	### plot wieviel nachrichten an welchem Tag verschickt wurden
	plt.clf()
	plt.figure(figsize=figsize_ratio, dpi=dpi_angabe)  
	tageszeit_stunden=[a*24 for a in tageszeit]
	plt.xlabel("Wochentag")
	plt.ylabel("Anzahl Whatsapp Nachrichten")
	plt.xlim((0,7))
	#plt.xticks([0,2,4,6,8,10,12,14,16,18,20,22])
	plt.grid()
	plt.title(name_fremd+" Anzahl Nachrichten pro Wochentag")
	#n, bins, patches=plt.hist(tageszeit_stunden,96) #  
	#max_uhrzeit=bins[numpy.argmax(n)]
	woche=[1,2,3,4,5,6,7]
	plt.xlim((0,8))
	plt.xticks(woche,("Mo","Di","Mi","Do","Fr","Sa","So"))
	plt.bar(woche,wochentag,0.9)
	plt.savefig(name_fremd+"_Wochentag.png")

	######################### Auswertung worter Count
	"""

	"""
	######################
	datei=open("Auswertungen von "+name_fremd+".txt","w+")
	datei.write(
		"Anzahl der Nachrichten Ich\t"+str(ichzaehler)+"\n"+
		"Anzahl der Nachrichten "+name_fremd+"\t"+str(fremdzaehler)+"\n"+
		"Emojis ICH\t"+str(sum(anzahl_emoji_ich))+"\n"+
		"Emojis "+name_fremd+"\t"+str(sum(anzahl_emoji_fremd))+"\n"+
		"Worte ICH\t"+str(sum(anzahl_worte_ich))+"\n"+
		"Worte "+name_fremd+"\t"+str(sum(anzahl_worte_fremd))+"\n"+
	    "Emoji/Worte Verhältnis ICH\t"+str(sum(anzahl_emoji_ich)/float(sum(anzahl_worte_ich)))+"\n"+
		"Emoji/Worte Verhältnis "+name_fremd+"\t"+str(sum(anzahl_emoji_fremd)/float(sum(anzahl_worte_fremd)))+"\n"
		"Worte/Nachrict ICH\t"      +str(sum(anzahl_worte_ich)/float(ichzaehler))+"\n"+
		"Worte/Nachricht "+name_fremd+" \t"+str(sum(anzahl_worte_fremd)/float(fremdzaehler))+"\n"+
		"Initative Ich \t"+str(Initative_Ich)+"\n"+
		"Initative Fremd \t"+str(Initative_Fremd)+"\n"+
		"Zeitabstand Ich Durchschnitt (h) \t"+str(Zeitabstand_Ich)+"\n"+
		"Zeitabstand Fremd Durchschnitt(h) \t"+str(Zeitabstand_Fremd)+"\n"+
		"Durchschnitt Antwortzeit ICH (min) \t"     +str(Antwortzeit_ICH)+"\n"+
		"Durchschnitt Antwortzeit Fremd (min) \t"+str(Antwortzeit_Fremd)+"\n"+
		"Durchschnitt Uhrzeit  \t"     +str(numpy.mean(tageszeit_stunden))+"\n"
		"Max Uhrzeit  \t"     +str((max_uhrzeit))+"\n"
		"Anzahl an den Worten -Ich,Mir,Mich,Mein- von Fremd "+str(anzahl_ich_worte_fremd)+"\n"
		"Anzahl an den Worten -Ich,Mir,Mich,Mein- von Mir "+  str(anzahl_ich_worte_ich)+"\n"
		"Anzahl an den Worten -Du,Dir,Dich,Dein- von Fremd "+ str(anzahl_du_worte_fremd)+"\n"
		"Anzahl an den Worten -Du,Dir,Dich,Dein- von Mir "+str(anzahl_du_worte_ich)+"\n"
		"Anzahl an den Worten -Wir,Uns,Unseren- von Fremd "+str(anzahl_wir_worte_fremd)+"\n"
		#"Anzahl an den Worten -Wir,Uns,Unseren- von Mir "+str(anzahl_wir_worte_ich)+"\n"
		)
	datei.close()

	datei_console=open("Auswertungen von "+name_fremd+".txt","r+")
	dateifile=datei_console.read()
	datei_console.close()
	lines=dateifile.split(chr(10))
	for a in lines:
		print (a)
	   

if save_as_pdf:
	imagelist=[name_fremd+"_Wochentag.png",name_fremd+"_Tageszeit.png",name_fremd+"_Antwortzeiten.png",name_fremd+"_Jahresüberblick.png",name_fremd+"_Bargramm_Wörter.png",name_fremd+"_Bargramm_Worte_pro_Nachricht.png",name_fremd+"_Bargramm_Nachrichten.png"]
	pdf = FPDF('L', 'mm', 'A4')
	# imagelist is the list with all image filenames
	for image in imagelist:
		pdf.add_page()
		pdf.image(image,w=250)
	pdf.output("Zusammenfassung_"+name_fremd+".pdf", "F")