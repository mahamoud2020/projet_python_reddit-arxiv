# -*- coding: utf-8 -*-
"""
Created on Tue Jan 10 02:09:55 2023

@author: Abdoulrazack Mahamoud Isman
"""

# Importation des librairies necessaires 

import pandas
import praw
import re
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize  
from nltk.tokenize import RegexpTokenizer
import datetime as dt
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_extraction.text import CountVectorizer
import pickle
import urllib.request
import xmltodict
import tkinter as tk
from tkinter import ttk
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt

# création classe " Corpus "

class Corpus():
    
    #Initialisation de la classe
    def __init__(self,name): 
        self.name = name
        self.collection = {}
        self.authors = {}
        self.id2doc = {}
        self.id2aut = {}
        self.ndoc = 0
        self.naut = 0
        self.chainereunie = ""
        self.dico = []
        self.type = ""
            
    def add_doc(self, doc):
        #  ajout d'un document au corpus à l'aide d' dictionnaire collection
        self.collection[self.ndoc] = doc
        # utilisation d'une liste indexée (plus simple à explorer)
        self.id2doc[self.ndoc] = doc.get_title()
        self.ndoc += 1
        aut_name = doc.get_author()
        aut = self.get_aut2id(aut_name)
        # ajouter à la liste d'auteurs : Nouvel auteur 
        if aut is not None:
            self.authors[aut].add(doc)
        else:
            self.add_aut(aut_name,doc)
            
    def add_aut(self, aut_name,doc):
        # Lien avec la classe Author
        aut_temp = Author(aut_name)
        aut_temp.add(doc)
        self.authors[self.naut] = aut_temp
        self.id2aut[self.naut] = aut_name
        
        self.naut += 1

    def get_aut2id(self, author_name):
        #  récupérer l'auteur par son id
        aut2id = {v: k for k, v in self.id2aut.items()}
        aut = aut2id.get(author_name)
        return aut

    def get_doc(self, i):
        # récupérer un document du corpus
        return self.collection[i]
    
    def get_coll(self):
        #  récupérer tous les documents du corpus
        return self.collection
    
    def traitementdico(self):
        if len(self.dico) == 0:
            
            self.dico = self.chainereunie.split(" ")
            self.dico = self.tokenize()
           
            
    def decoupagetemporel(self, mot, periode, iter):
        # générer un tableau avec un nombre de x jours
        tableauperiodes = []
        d = dt.datetime.today()
        tableauperiodes.append(d)
        for i in range(1,int(iter)):
            d = d - dt.timedelta(days=int(periode))
            tableauperiodes.append(d)
            
        test = {}
        
        # on compte le mot dans chaque document et on compare la date du document aux périodes pour créer un tableau associatif
        # ou la clé est la période supérieure, et la valeur est le count du mot
        for j in tableauperiodes:
            test[j]=0
            for i in self.collection:
            
                if self.collection[i].date<j and self.collection[i].date>(j - dt.timedelta(days=int(periode))):
                    test[j] = test[j] + self.collection[i].title.count(mot) + self.collection[i].text.count(mot)
        
        # et on inverse le tableau et on récupère les données des axes X et Y
        new_dict = {dt.datetime.strftime(key, "%Y-%m-%d"): val for key, val in test.items()}
        keys = list(new_dict.keys())
        values = list(new_dict.values())
        
        keys.reverse()
        values.reverse()
        
        # tracer  la courbe avec matplotlib
        plt.plot(keys,values)
        
        #plt.figure(1, figsize=(5, 3))
        
        plt.xlabel("Date", fontsize=8)
        plt.ylabel("Nombre d'occurrences du terme " + str(mot), fontsize=8)
        
        plt.title("Évolution temporelle du terme " + str(mot), fontsize=8)
        
        plt.show()
    
    def getType(self):
        return self.type    
    
    def setType(self, chainetype):
        self.type = chainetype
        

    def __str__(self):
        # Il peut y avoir une version simplifiée de l'affichage du corpus
        return "Corpus: " + self.name + ", type : " + self.type + ", nb doc: "+ str(self.ndoc)+ ", nb auteurs: "+ str(self.naut)
    
    def __repr__(self):
        return self.name

    def sort_title(self,nreturn=None):
        # on trie le corpus en fonction du titre
        if nreturn is None:
            nreturn = self.ndoc
        return [self.collection[k] for k, v in sorted(self.collection.items(), key=lambda item: item[1].get_title())][:(nreturn)]

    def sort_date(self,nreturn):
        # on trie le corpus selon la date
        if nreturn is None:
            nreturn = self.ndoc
        return [self.collection[k] for k, v in sorted(self.collection.items(), key=lambda item: item[1].get_date(), reverse=True)][:(nreturn)]
    
    def save(self,file):
        # on Sauvegarde le fichier au format .crp
            pickle.dump(self, open(file, "wb" ))
     
  # fonction permettant de réunir les documents en une chaine de caractère          
    def chainereuniefonc(self):
        
        if (self.chainereunie == ""):
            for doc in self.collection:
                chaine = self.collection[doc].get_text()
                self.chainereunie += (chaine)
    
  # fonction petmettant de chercher un mot-clé          
    def search(self, keyword):   
            sample = ""
            if keyword in self.chainereunie:
               for m in re.finditer(keyword, self.chainereunie):
                   for i in range(m.start(0) - 50, m.end(0) + 50):
                       sample += self.chainereunie[i]
            print(sample)
                               
  # fonction permettant de chercher un mot-clé selon la taille donnée par l'utilisateur  
    
    def concorde(self, keyword, taille):
            sample = ""
            if keyword in self.chainereunie:
               for m in re.finditer(keyword, self.chainereunie):
                   for i in range(m.start(0) - taille, m.end(0) + taille):
                       sample += self.chainereunie[i]
            print(sample)
    
  
    # on retir les mots qui ne sont pas porteurs de sens
    
    def tokenize(self):
        
        stop_words = set(stopwords.words('english'))  
        tokenizer = RegexpTokenizer(r'\w+')
        
        chaineinter = ""
        
        
        for word in tokenizer.tokenize(self.chainereunie):
            chaineinter = chaineinter + word + " "
        
    
        word_tokens = word_tokenize(chaineinter)
  
        filtered_sentence = [w for w in word_tokens if not w in stop_words]  
  
        filtered_sentence = []  
  
        for w in word_tokens:  
            if w not in stop_words:  
                filtered_sentence.append(w)
        
        return filtered_sentence
       
    
   
    # cette fonction va générer un dataframe Pandas contenant les termes les plus utilisés
    def stats(self):
        
        data = pandas.DataFrame.from_dict(self.dico)
            
        freq = data[0].value_counts()
        print()
        print("Les dix termes les plus utilisés sont :")
        print()
        print(freq.head(10))
            
                 
  # fonction permettant d'effectuer un traitement de la chaîne  créée dans " chainereuniefonc "      
    def nettoyer_texte(self):    
        self.chainereunie = self.chainereunie.lower()
        self.chainereunie.replace("\n"," ")
    
   
 # création classe " Author " 
   
    
class Author():
    #Initialisation de la classe
    def __init__(self,name):
        self.name = name
        self.production = {}
        self.ndoc = 0
    
   # ajout d' un auteur
    def add(self, doc): 
        self.production[self.ndoc] = doc
        self.ndoc += 1

    def __str__(self):
        return "Auteur: " + self.name + ", Number of docs: "+ str(self.ndoc)
    def __repr__(self):
        return self.name
    

# création classe " Document " 

class Document(): 
   #Initialisation de la classe
    def __init__(self, date, title, author, text, url, type):
        self.date = date
        self.title = title
        self.author = author
        self.text = text
        self.url = url
        self.type = type
    
    # les getters
    
    def get_author(self):
        return self.author

   # get_title
    def get_title(self):
        return self.title
    
    # get_date
    def get_date(self):
        return self.date
    
    # get_source
    def get_source(self):
        return self.source
     
    # get_text
    def get_text(self):
        return self.text

    def __str__(self):
        return "Document " + self.getType() + " : " + self.title
    
    def __repr__(self):
        return self.title
    
    # get_type
    def getType(self):
        return self.type
    
    #get_url
    def getUrl(self):
        return self.url

# création classe " Document "
    
class RedditDocument(Document):
   #Initialisation de la classe 
    def __init__(self, date, title, author, text, url, type, nbcomm):
        super().__init__(date, title, author, text, url, type)
        self.nbcomm = nbcomm
        
    def getnbcomm(self):
        return self.nbcomm
    
    def setnbcomm(self, nbcomm):
        self.nbcomm = nbcomm
    
    def __str__(self):
        return (super().__str__() + " Nbcomm : " + str(self.nbcomm))

    
# création classe " Document "

class ArxivDocument(Document):
   #Initialisation de la classe 
    def __init__(self, date, title, author, text, url, type, coauthor):
        super().__init__(date, title, author, text, url, type)
        self.coauthor = coauthor
    
    def getcoauthor(self):
        return self.coauthor
    
    def setcoauthor(self, coauthor):
        self.coauthor = coauthor

    
    def __str__(self):
        return (super().__str__() + " Co-auteurs : " + self.coauthor)
           


# Création du Corpus 
corpuslist = []

# initialisation de la fenêtre tkinter
def menuprincipal():
   # creation de la fenetre  
    fenetreprincipale = tk.Tk() 
    # ajout d'un titre à la fenetre
    fenetreprincipale.title("Corpus Reddit & Arxiv")
    
    print("Nombre de corpus : "+str(len(corpuslist)))
    
    label = tk.Label(fenetreprincipale, text="Projet programmation python")
    label.pack(pady=0)

    
    # Création d'un widget Frame dans la fenêtre principale
    Frame1 = tk.Frame(fenetreprincipale,borderwidth=2,relief="groove")
    Frame1.pack(padx=10,pady=10)
    
    # Boutons de création de corpus
    bouton1 = tk.Button(Frame1, text="Création d'un corpus Reddit", bg="#00FFFF", fg="Black", command=lambda : corpusRedditForm(fenetreprincipale))
    bouton1.pack(pady=20)
    
    bouton2 = tk.Button(Frame1, text="Création d'un corpus Arxiv", bg="Purple", fg="Black", command=lambda : corpusArxivForm(fenetreprincipale))
    bouton2.pack(pady=10)
    
    # sélection d' un corpus parmi les corpus déjà créés, 
    # pour créer des méthodes necessaires.
    
    if len(corpuslist) >= 1:
        Frame2 = tk.Frame(fenetreprincipale,borderwidth=2,relief="groove")
        Frame2.pack(padx=10,pady=10)
        
        # Liste à deroulée
        comboExample = ttk.Combobox(Frame2, values=corpuslist, width=100)
            
        comboExample.current(0)
        comboExample.pack()
        
        # Ajout d'un document Reddit ou Arxiv selon le corpus qui est sélectionné
        
        if corpuslist[comboExample.current()].getType() == "Reddit":
            color = "#00FFFF"
            bouton3 = tk.Button(Frame2, text="Ajouter document Reddit", bg="#00FFFF", fg="Black", command=lambda : doc(corpuslist[comboExample.current()], fenetreprincipale))
            bouton3.pack(pady=20)
        else:
            color = "Purple"
            bouton3 = tk.Button(Frame2, text="Ajouter document Arxiv", bg="Purple", fg="Black", command=lambda: doc(corpuslist[comboExample.current()], fenetreprincipale))
            bouton3.pack(pady=10)
         
        bouton4 = tk.Button(Frame2, text="Afficher stats corpus", bg=color, fg="Black", command=lambda : corpuslist[comboExample.current()].stats())
        bouton4.pack(pady=20)
        
        bouton5 = tk.Button(Frame2, text="Rechercher dans le corpus", bg=color, fg="Black", command=lambda : recherche(corpuslist[comboExample.current()], fenetreprincipale))
        bouton5.pack(pady=20)
        
        bouton6 = tk.Button(Frame2, text="Sauvegarder le corpus", bg=color, fg="Black", command=lambda : sauvegarde(corpuslist[comboExample.current()], fenetreprincipale))
        bouton6.pack(pady=20)
        
        bouton7 = tk.Button(Frame2, text="Afficher résultats TF/IDF", bg=color, fg="Black", command=lambda : TFIDF(corpuslist[comboExample.current()]))
        bouton7.pack(pady=20)
        
        bouton8 = tk.Button(Frame2, text="Évolution temporelle d'un terme", bg=color, fg="Black", command=lambda : decoupagetemporel(corpuslist[comboExample.current()], fenetreprincipale))
        bouton8.pack(pady=20)
    
    # on compare deux corpus et on sélectionne deux corpus avec deux listes déroulantes
    
    if len(corpuslist) >= 2:
        Frame3 = tk.Frame(fenetreprincipale,borderwidth=2,relief="groove")
        Frame3.pack(padx=10,pady=10)
        
        labelidf = tk.Label(Frame3, text="Sélectionner deux corpus")
        labelidf.pack()
        
        comboExample1 = ttk.Combobox(Frame3, values=corpuslist, width=100)
            
        comboExample1.current(0)
        comboExample1.pack()
        
        comboExample2 = ttk.Combobox(Frame3, values=corpuslist, width=100)
            
        comboExample2.current(1)
        comboExample2.pack()
        
        bouton4 = tk.Button(Frame3, text="Comparaison statistique entre deux corpus", bg="#00FFFF", fg="Black", command=lambda : comparestats(corpuslist[comboExample1.current()],corpuslist[comboExample2.current()]))
        bouton4.pack(pady=10)
        
        bouton5 = tk.Button(Frame3, text="Comparaison TF/IDF entre deux corpus", bg="#00FFFF", fg="Black", command=lambda : compareTFIDF(corpuslist[comboExample1.current()],corpuslist[comboExample2.current()]))
        bouton5.pack(pady=10)

        
    # Fermeture de l'appli
    boutonquit = tk.Button(fenetreprincipale, text="Quitter", fg="black", command=fenetreprincipale.destroy)
    boutonquit.pack(pady=20)
    
    
    # lancement de la fenêtre créée
    
    fenetreprincipale.geometry("800x800")
    fenetreprincipale.mainloop()


 # fonction permettant de revenir au menu principal 
def retourmenu(fenetre):
    fenetre.destroy()
    #print("retourmenu")
    menuprincipal()
    
def corpusRedditForm(fenetre):
    
    fenetre.destroy()
    
    # création d'un formulaire de type Reddit
    # deux champs sont crées : nom du corpus et subreddit
    
    fenetrecorpus = tk.Tk()
    fenetrecorpus.title("Création de formulaire Reddit")
    fenetrecorpus.geometry("400x300")
    
    
    label = tk.Label(fenetrecorpus, text="Entrez le nom de votre corpus")
    label.pack()
    
    nomcorpus = tk.Entry(fenetrecorpus)
    nomcorpus.pack()
    
    label = tk.Label(fenetrecorpus, text="Entrez le Subreddit souhaitée (ex: football)")
    label.pack()
    
    subreddit = tk.Entry(fenetrecorpus)
    subreddit.pack()
    
    bouton4 = tk.Button(fenetrecorpus, text="Créer le corpus", bg="#00FFFF", fg="Black", command= lambda : corpusReddit(nomcorpus.get(), subreddit.get(), fenetrecorpus))
    bouton4.pack(pady=10)
    
    bouton4 = tk.Button(fenetrecorpus, text="Retour au menu", bg="Teal", fg="Black", command= lambda : retourmenu(fenetrecorpus))
    bouton4.pack(pady=10)
     
  
  # création d'un corpus de type Reddit   
def corpusReddit(nomcorpus, subreddit, fenetre):
    corpus = Corpus(nomcorpus)
    corpus.setType("Reddit")
    corpuslist.append(corpus)

    # utilisation  de l'API  Reddit pour récupérer les 300 documents en tendance sur reddit
    reddit = praw.Reddit(client_id='bUSpPjr1zI02Nw', client_secret='KkUgCs09VU03a32wbiP3tTW0IW0', user_agent='Reddit WebScraping')
    hot_posts = reddit.subreddit(subreddit).hot(limit=500) # limite 500 
    for post in hot_posts:
        #On crée un document avec les informations données
        datet = dt.datetime.fromtimestamp(post.created)
        txt = post.title + ". "+ post.selftext
        txt = txt.replace('\n', ' ')
        txt = txt.replace('\r', ' ')
        #Auteur est un champ facultatif
        if hasattr(post, 'author_fullname'):
            doc = Document(datet,
                               post.title,
                               post.author_fullname,
                               txt,
                               post.url, "Reddit")
        else:
             doc = Document(datet,
                               post.title,
                               "",
                               txt,
                               post.url, "Reddit")
            
        corpus.add_doc(doc)
    
    # appels des méthodes de traitement des données
    
    corpus.chainereuniefonc()
    corpus.nettoyer_texte()
    corpus.traitementdico()
    
    print("Création du corpus, %d documents et %d auteurs" % (corpus.ndoc,corpus.naut))
    
    retourmenu(fenetre)

# creation d'un formulaire de type ArXiv 
#deux champs sont crées :  nom du corpus et champ de recherche 

def corpusArxivForm(fenetre): 
    fenetre.destroy()
    
    fenetrecorpus = tk.Tk()
    fenetrecorpus.title("Création de formulaire Arxiv")
    fenetrecorpus.geometry("400x300")
    
    label = tk.Label(fenetrecorpus, text="Entrez le nom de votre corpus")
    label.pack()
    
    nomcorpus = tk.Entry(fenetrecorpus)
    nomcorpus.pack()
    
    label = tk.Label(fenetrecorpus, text="Entrez un champ de recherche (ex: footall)")
    label.pack()
    
    urlarxiv = tk.Entry(fenetrecorpus)
    urlarxiv.pack()
    
    bouton4 = tk.Button(fenetrecorpus, text="Créer le corpus", bg="Purple", fg="Black", command= lambda : corpusArxiv(nomcorpus, urlarxiv.get(), fenetrecorpus))
    bouton4.pack(pady=10)
    
    bouton4 = tk.Button(fenetrecorpus, text="Retour au menu", bg="Teal", fg="Black", command= lambda : retourmenu(fenetrecorpus))
    bouton4.pack(pady=10)
    
 
 # création d' un corpus de type ArXiv   
def corpusArxiv(nomcorpus, urlarxiv, fenetre):
    corpus = Corpus(nomcorpus)
    corpus.setType("Arxiv")
    corpuslist.append(corpus)
    
    url = 'http://export.arxiv.org/api/query?search_query=all:' + urlarxiv + '&start=0&max_results=5'
    data =  urllib.request.urlopen(url).read().decode()
    docs = []
    docs += xmltodict.parse(data)['feed']['entry']
     
    for i in docs:
        datet = dt.datetime.strptime(i['published'], '%Y-%m-%dT%H:%M:%SZ')
   
        try:
            author = [aut['name'] for aut in i['author']][0]
        except:
            author = i['author']['name']
        txt = i['title']+ ". " + i['summary']
        txt = txt.replace('\n', ' ')
        txt = txt.replace('\r', ' ')
        doc = Document(datet,
                       i['title'],
                       author,
                       txt,
                       i['id'],
                       "Arxiv"
                       )
        corpus.add_doc(doc)   
        
    # appels des méthodes de traitement des données
            
    corpus.chainereuniefonc()
    corpus.nettoyer_texte()
    corpus.traitementdico()
        
    print("Création du corpus, %d documents et %d auteurs" % (corpus.ndoc,corpus.naut))
    
    retourmenu(fenetre)

# Comparaison de deux corpus

def compareTFIDF(corpus1, corpus2):
    print("CORPUS 1 : ")
    TFIDF(corpus1)
    print("CORPUS 2 : ")
    TFIDF(corpus2)
    
def TFIDF(corpus):

    # instanciation de CountVectorizer() 
    cv=CountVectorizer() 
 
    word_count_vector=cv.fit_transform(corpus.dico)
    
    tfidf_transformer=TfidfTransformer(smooth_idf=True,use_idf=True) 
    tfidf_transformer.fit(word_count_vector)
    
    # affichage des valeurs IDF 
    df_idf = pandas.DataFrame(tfidf_transformer.idf_, index=cv.get_feature_names(),columns=["idf_weights"]) 
 
    print(df_idf.sort_values(by=['idf_weights']))
    
    

# formulaire de sauvegarde du corpus
def sauvegarde(corpus, fenetre):
    fenetre.destroy()
    
    fenetresave = tk.Tk()

    labelsave = tk.Label(fenetresave, text="Entrer un nom de fichier .crp")
    labelsave.pack(pady=20)
    
    entry = tk.Entry(fenetresave)
    entry.pack()
    
    bouton1 = tk.Button(fenetresave, text="Sauvegarder", bg="#00FFFF", fg="Black", command= lambda: sauvegarder(corpus, entry.get(), fenetresave))
    bouton1.pack(pady=20)
    
    bouton4 = tk.Button(fenetresave, text="Retour au menu", bg="Teal", fg="Black", command= lambda : retourmenu(fenetresave))
    bouton4.pack(pady=10)
    
    fenetresave.mainloop()

def sauvegarder(corpus, nomfichier, fenetre):
    
    print("Enregistrement du corpus sur le disque...")
    
    pickle.dump(corpus, open(nomfichier, "wb" ))
    
    retourmenu(fenetre)
  
 # ajout d' un document au corpus   
def sauvegarderDocReddit(corpus, date, titre, auteur, texte, url, type, nbcomm, fenetre):
    docreddit = RedditDocument(date, titre, auteur, texte, url, type, nbcomm)
    corpus.add_doc(docreddit)
    retourmenu(fenetre)
    
 
 # ajout d'un document au corpus   
def sauvegarderDocArxiv(corpus, date, titre, auteur, texte, url, type, coauteur, fenetre):
    docarxiv = ArxivDocument(date, titre, auteur, texte, url, type, coauteur)
    corpus.add_doc(docarxiv)
    retourmenu(fenetre)

# analyse comparative des termes le plus utilisés de deux corpus
def comparestats(corpus1, corpus2):
    corpus1.stats()
    corpus2.stats()


# formulaire de création d'un document
def doc(corpus, fenetre):
    fenetre.destroy()
    
    fenetreformdoc = tk.Tk()
    fenetreformdoc.geometry = ("1000x300")
    
    labeldate = tk.Label(fenetreformdoc, text="Date : ")
    labeldate.pack(pady=10)
    
    entrydate = tk.Entry(fenetreformdoc)
    entrydate.pack()
    
    
    labeltitre = tk.Label(fenetreformdoc, text="Titre : ")
    labeltitre.pack(pady=10)
    
    entrytitre = tk.Entry(fenetreformdoc)
    entrytitre.pack()
    
    
    labelauteur = tk.Label(fenetreformdoc, text="Auteur : ")
    labelauteur.pack(pady=10)
    
    entryauteur = tk.Entry(fenetreformdoc)
    entryauteur.pack()
    
    
    labeltexte = tk.Label(fenetreformdoc, text="Texte : ")
    labeltexte.pack(pady=10)
    
    entrytexte = tk.Entry(fenetreformdoc)
    entrytexte.pack()
    
    
    labelurl = tk.Label(fenetreformdoc, text="URL : ")
    labelurl.pack(pady=10)
    
    entryurl = tk.Entry(fenetreformdoc)
    entryurl.pack()
    
    if corpus.getType() == "Reddit":
        
        labelnbcomm = tk.Label(fenetreformdoc, text="Nombre de commentaires : ")
        labelnbcomm.pack(pady=10)
        
        entrynbcomm = tk.Entry(fenetreformdoc)
        entrynbcomm.pack()
        
        bouton1 = tk.Button(fenetreformdoc, text="Enregistrer", bg="#00FFFF", fg="white", command= lambda: sauvegarderDocReddit(corpus, entrydate.get(), entrytitre.get(), entryauteur.get(), entrytexte.get(), entryurl.get(), "Reddit", entrynbcomm.get(), fenetreformdoc))
        bouton1.pack(pady=10)
    
    else:
    
        labelcoauteur = tk.Label(fenetreformdoc, text="Co-auteur : ")
        labelcoauteur.pack(pady=10)
        
        entrycoauteur = tk.Entry(fenetreformdoc)
        entrycoauteur.pack()
    
        bouton1 = tk.Button(fenetreformdoc, text="Enregistrer", bg="#00FFFF", fg="Black", command= lambda: sauvegarderDocArxiv(corpus, entrydate.get(), entrytitre.get(), entryauteur.get(), entrytexte.get(), entryurl.get(), "Arxiv", entrycoauteur.get(), fenetreformdoc))
        bouton1.pack(pady=10)
    
    bouton2 = tk.Button(fenetreformdoc, text="Retour au menu", bg="Teal", fg="Black", command= lambda: retourmenu(fenetreformdoc))
    bouton2.pack(pady=10)
    
    fenetreformdoc.mainloop()

# Formulaire de recherche d'un mot-clé
def recherche(corpus, fenetre):
    fenetre.destroy()
    
    fenetrerecherche = tk.Tk()
    
    labelrecherche = tk.Label(fenetrerecherche, text="Mot-clé de recherche : ")
    labelrecherche.pack(pady=10)
        
    entryrecherche = tk.Entry(fenetrerecherche)
    entryrecherche.pack()
    
    bouton1 = tk.Button(fenetrerecherche, text="Recherche", bg="#00FFFF", fg="Black", command= lambda: rechercher(corpus, entryrecherche.get(), fenetrerecherche))
    bouton1.pack(pady=10)
    
    bouton4 = tk.Button(fenetrerecherche, text="Retour au menu", bg="Teal", fg="Black", command= lambda : retourmenu(fenetrerecherche))
    bouton4.pack(pady=10)

def rechercher(corpus, motcle, fenetre):
    corpus.search(motcle)
    
    retourmenu(fenetre)

def decoupagetemporel(corpus, fenetre):
    
    fenetre.destroy()
    
    fenetredecoupage = tk.Tk()
    
    labeldecoupage = tk.Label(fenetredecoupage, text="Mot-clé à observer : ")
    labeldecoupage.pack(pady=10)
        
    entrydecoupage = tk.Entry(fenetredecoupage)
    entrydecoupage.pack()
    
    labelperiode = tk.Label(fenetredecoupage, text="Période (nombre de jours) : ")
    labelperiode.pack(pady=10)
        
    entryperiode = tk.Entry(fenetredecoupage)
    entryperiode.pack()
    
    labeliter = tk.Label(fenetredecoupage, text="Nombre d'itérations : ")
    labeliter.pack(pady=10)
        
    entryiter = tk.Entry(fenetredecoupage)
    entryiter.pack()
    
    bouton1 = tk.Button(fenetredecoupage, text="OK", bg="#00FFFF", fg="Black", command= lambda: decouper(corpus, entrydecoupage.get(), entryperiode.get(), entryiter.get(), fenetredecoupage))
    bouton1.pack(pady=10)
    
    bouton4 = tk.Button(fenetredecoupage, text="Retour au menu", bg="Teal", fg="Black", command= lambda : retourmenu(fenetredecoupage))
    bouton4.pack(pady=10)

def decouper(corpus, mot, periode, iter, fenetre):
    corpus.decoupagetemporel(mot, periode, iter)
    retourmenu(fenetre)



fenetreintro = tk.Tk()

# Fenêtre d'accueil de l'appli

labelintro = tk.Label(fenetreintro, text="Pour commencer, veuillez d'abord créer un corpus")
labelintro.pack()

bouton1 = tk.Button(fenetreintro, text="Créer un corpus Reddit", bg="#00FFFF", fg="Black", command= lambda: corpusRedditForm(fenetreintro))
bouton1.pack(pady=10)

bouton2 = tk.Button(fenetreintro, text="Créer un corpus Arxiv", bg="Purple", fg="Black", command= lambda: corpusArxivForm(fenetreintro))
bouton2.pack(pady=10)

fenetreintro.mainloop()



