# 🎓 Dashboard de Vérification de Planning - Université Iba Der THIAM de Thiès

**Version 2.0**

## 📝 Présentation du Projet
Ce projet est une solution complète d'analyse et de vérification des plannings de formation, développée dans le cadre du **Master 2 UIDT** (Module Compilation). 

L'application combine la puissance de l'analyse lexicale et syntaxique (via un moteur **Flex/Bison** en C) avec une interface Web moderne et interactive en **Python/Streamlit**. Elle a pour but d'aider les responsables pédagogiques à s'assurer de la conformité des enseignements planifiés par rapport aux maquettes pédagogiques officielles (LMD).

## ✨ Fonctionnalités Principales

### 📊 Analyse et Visualisation
- **Traitement Automatisé** : Import et parsing de fichiers de planning textuels.
- **Tableau de Bord KPI** : Vue synthétique des taux de conformité, volumes horaires globaux et charges d'enseignement.
- **Graphiques Interactifs** : Visualisation dynamique (Plotly) de la répartition CM/TD/TP et de la progression.
- **Support Multi-Onglets** : Navigation fluide entre la vue d'ensemble, le détail par enseignant, les alertes et les données brutes.

### 🤖 Intelligence Artificielle (Assistant Pédagogique)
- **Analyse Stratégique** : Intégration de modèles LLM (par défaut **Mistral 7B via OpenRouter**) pour analyser les données.
- **Recommandations Contextuelles** : L'IA identifie les déséquilibres et propose des plans d'action concrets (optimisation des TP, lissage des charges).
- **Mode Chat Interactif** : Interface de discussion pour interroger l'assistant sur les données du planning.

### 📄 Reporting Professionnel
- **Génération PDF** : Export de rapports officiels soignés via `ReportLab`.
- **Contenu Riche** : Intégration automatique du logo de l'université, des statistiques clés, des graphiques (Matplotlib) et de l'analyse IA.
- **Archivage** : Documents prêts pour l'impression et l'administratif.

## 🛠️ Stack Technique

| Composant | Technologie | Usage |
|-----------|-------------|-------|
| **Frontend** | Streamlit | Interface utilisateur interactive |
| **Logique Mètier** | Python (Pandas) | Manipulation et analyse des données |
| **Parsing** | C / Flex / Bison | Analyse syntaxique du fichier source (`verificateur.exe`) |
| **Graphismes** | Plotly / Matplotlib | Graphiques interactifs et statiques pour PDF |
| **IA** | OpenAI SDK / OpenRouter | Génération de texte et analyse intelligente |
| **Export** | ReportLab | Création de documents PDF |

## 🚀 Guide d'Installation

### Prérequis
- Python 3.8 ou supérieur
- Système d'exploitation Windows (pour la compatibilité avec `verificateur.exe` fourni) ou recompilation des sources C nécessaire.

### 1. Installation des dépendances Python
Assurez-vous d'avoir les bibliothèques suivantes installées :
```bash
pip install streamlit pandas plotly matplotlib reportlab openai streamlit-lottie numpy requests
```

### 2. Configuration des Clés API (Optionnel mais recommandé)
Pour activer l'analyse IA, créez un fichier `.streamlit/secrets.toml` à la racine du projet :

```toml
# Configuration pour OpenRouter (Recommandé - Mistral 7B Free)
OPENROUTER_API_KEY = "sk-or-votre-cle-ici..."

# Configuration pour OpenAI (Alternative)
OPENAI_API_KEY = "sk-votre-cle-openai..."
```
*Note : Si aucune clé n'est détectée, l'application passera automatiquement en mode "Simulation" pour l'IA.*

### 3. Lancement de l'application
Exécutez la commande suivante depuis la racine du projet :
```bash
streamlit run app.py
```

## 📂 Structure des Fichiers Clés

- `app.py` : Cœur de l'application Streamlit. Contient toute la logique UI, l'intégration IA et la génération de PDF.
- `verificateur.exe` : Exécutable compilé chargé de lire et valider le format du fichier de planning en entrée.
- `logo_thies.png` : Ressource graphique utilisée pour l'en-tête des rapports PDF.
- `projet.l` / `projet.y` : Sources Lex et Yacc définissant la grammaire du langage de planning accepté.
- `.streamlit/secrets.toml` : Fichier de configuration des secrets (à ne pas partager).

## 👥 Auteurs
`**Cheikh Mbacké COLY**`
`**Bassirou KANE**`
`**Mouhamet DIAGNE**`
`**Promotion Master 2 UIDT - Université Iba Der THIAM de Thiès**`
`*Projet de Compilation*`
