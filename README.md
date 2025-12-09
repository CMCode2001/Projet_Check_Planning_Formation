# Projet_Check_Planning_Formation

Un outil de vérification automatique de conformité des plannings de formation utilisant **Lex & Yacc (Flex & Bison)** et une interface web **Streamlit**.

## 📋 Vue d'ensemble

Ce projet analyse des fichiers de planning de formation pour vérifier que :

- ✅ Toutes les heures prévues (CM, TD, TP) pour chaque UE (Unité d'Enseignement) sont assurées
- ✅ Les écarts entre les heures prévues et assurées sont identifiés
- ✅ Les données sont visualisées sous forme de graphiques et tableaux interactifs

---

## 📁 Structure des fichiers

### Fichiers socles du projet

#### `projet.l` (Lexer - Flex)

- **Utilité** : Analyse lexicale (tokenization) du fichier d'entrée
- **Rôle** : Lit le fichier caractère par caractère et reconnaît les éléments textuels :
  - Les mots-clés : `UE`, `CM`, `TD`, `TP`
  - Les nombres avec unité (ex: `9h`, `15.5h`)
  - Les noms d'enseignants entre astérisques (ex: `*Enseignant AB*`)
  - Les séparateurs : `:`, `,`, `;`
- **Sortie** : Envoie des tokens (jetons) au parser (Bison)

#### `projet.y` (Parser - Bison)

- **Utilité** : Analyse syntaxique et sémantique du fichier
- **Rôle** :
  - Vérifie que la structure du fichier est correcte
  - Stocke les heures **prévues** pour chaque UE
  - Traite les blocs enseignants et calcule les heures **assurées**
  - Applique la formule d'équivalence : `1h CM = 1.5h EqTD`
  - Génère un rapport JSON avec les résultats
- **Sortie** : JSON contenant les données structurées des UEs et leurs écarts

#### `data.h` (Header C)

- **Utilité** : Définition des structures de données partagées
- **Contenu** :
  - Structure `UE` : stocke les heures prévues et assurées pour chaque UE
  - Variables globales : tableau des UEs (`tab_ues[100]`)
  - Déclarations des fonctions principales :
    - `init_ue()` : initialise une UE avec ses heures prévues
    - `add_heures()` : ajoute les heures assurées
    - `check_resultats()` : génère le rapport JSON

#### `app.py` (Interface utilisateur - Streamlit)

- **Utilité** : Interface web interactive pour l'utilisateur
- **Fonctionnalités** :
  - 📤 Upload de fichier texte (.txt)
  - 📊 Affichage des graphiques comparatifs (Prévu vs Assuré) :
    - Graphiques pour CM, TD, TP séparément
    - Codes couleur : Bleu (Prévu) | Rouge (Assuré)
  - ⚠️ Tableau des écarts avec code couleur :
    - 🔴 Rouge : manque d'heures
    - 🟢 Vert : excès d'heures
    - ⚪ Gris : conformité parfaite
  - 📈 Barre de progression visuelle
  - ℹ️ Affichage du fichier source en expandeur

#### `input.txt` (Fichier d'exemple)

- **Utilité** : Exemple de format d'entrée attendu
- **Structure** :

  ```
  UE 1 CM: 9h, TD 15h, TP 30h
  UE 2: CM: 9h, TD 15h, TP: 30h

  *Enseignant AB*
  UE 1: CM: 9h, TD 15h, TP: 0h
  UE 2: CM 9h, TD 0h, TP: 0h
  ;

  *Enseignant CD*
  UE 4 CM 12h, TD 15h, TP: 30h
  ;
  ```

#### `fonctionnement.txt` (Documentation interne)

- **Utilité** : Explication détaillée du fonctionnement du parser
- **Contenu** : Description de l'algorithme et des formules utilisées

---

## 🚀 Comment lancer l'application

### Prérequis

- **Flex & Bison** installés (générateurs de parsers)
- **GCC** (compilateur C)
- **Python 3.8+** avec Streamlit

### Étape 1 : Compiler le programme C

Depuis le dossier `projet_check_planning/`, exécutez :

```bash
# Générer les fichiers C à partir des fichiers Flex et Bison
bison -d -y projet.y
flex projet.l

# Compiler l'exécutable
gcc lex.yy.c y.tab.c -o verificateur
```

**Résultat** : Un exécutable `verificateur.exe` est créé.

### Étape 2 : Installer les dépendances Python

```bash
# Depuis la racine du projet
pip install streamlit pandas
```

### Étape 3 : Lancer l'application Streamlit

```bash
# Depuis le dossier projet_check_planning/
streamlit run app.py
```

L'application s'ouvrira dans votre navigateur à l'adresse `http://localhost:8501`

---

## 📝 Processus de vérification

1. **Lexical** → Le fichier est tokenisé par Flex
2. **Syntaxique** → Bison vérifie la structure grammaticale
3. **Sémantique** → Les heures sont calculées et comparées
4. **Rapport** → Un JSON est généré avec les écarts
5. **Visualisation** → Streamlit affiche les graphiques et tableaux

---

## 📊 Format attendu du fichier d'entrée

```
UE <id> CM: <heures>h, TD: <heures>h, TP: <heures>h
...

*Enseignant <Nom>*
UE <id>: CM: <heures>h, TD: <heures>h, TP: <heures>h
...
;
```

---

## 🔧 Dépannage

- **Erreur de compilation C** : Vérifiez que Flex et Bison sont installés
- **Erreur JSON** : Vérifiez le format du fichier d'entrée
- **Port 8501 occupé** : Utilisez `streamlit run app.py --server.port 8502`
