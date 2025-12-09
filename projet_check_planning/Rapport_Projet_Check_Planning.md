# Rapport Détaillé du Projet : Check Planning

**Université Iba Der THIAM de Thiès**  
**Master 2 UIDT - Module de Compilation**  
**Date du rapport** : 09 Décembre 2025

---

## 1. Introduction et Objectifs

### 1.1 Contexte
Dans le cadre de la gestion des enseignements universitaires, la vérification de la conformité entre les maquettes pédagogiques (le prévu) et les enseignements effectivement dispensés (le réalisé) est cruciale. Ce projet, intitulé **Check Planning**, propose une solution automatisée pour auditer ces données.

### 1.2 Objectif
L'objectif principal est de fournir un outil capable de :
1.  **Analyser** des fichiers de planning structurés (format texte propriétaire).
2.  **Vérifier** la conformité des volumes horaires (CM, TD, TP).
3.  **Calculer** les charges d'enseignement avec les pondérations officielles.
4.  **Visualiser** les écarts via un tableau de bord interactif.
5.  **Produire** des rapports administratifs formels (PDF).

---

## 2. Architecture Technique

Le projet adopte une architecture hybride **C / Python**, tirant parti de la robustesse du C pour l'analyse syntaxique et de la flexibilité de Python pour l'interface utilisateur.

### 2.1 Schéma de Flux de Données

```mermaid
graph LR
    A[Fichier Planning (.txt)] -->|Analyse Lexicale & Syntaxique| B(Moteur C)
    B -->|Sortie JSON Structurée| C[Interface Streamlit (Python)]
    C -->|Visualisation| D[Tableau de Bord Web]
    C -->|Génération| E[Rapport PDF ReportLab]
    C -->|Prompt Contextuel| F[API IA (LLM Mistral)]
    F -->|Recommandations| C
```

---

## 3. Composants Détaillés

### 3.1 Le Moteur de Compilation (Backend C)
Ce module est le cœur logique de l'application. Il utilise **Flex** et **Bison** pour interpréter le langage de description du planning.

*   **Analyse Lexicale (`projet.l`)** :
    *   Identifie les *tokens* : `UE`, `CM`, `TD`, `TP`, noms d'enseignants (entre `*`), valeurs numériques.
    *   Gère les séparateurs (`:`, `,`, `;`).

*   **Analyse Syntaxique (`projet.y`)** :
    *   Définit la grammaire : Un programme est une liste d'UEs suivie d'une liste d'Enseignants.
    *   **Structures de Données (`data.h`)** :
        *   `UE` : Contient les heures prévues et réalisées par type.
        *   `Enseignant` : Contient les heures effectuées et le calcul de charge.
    *   **Logique d'Agrégation** :
        *   À chaque parsing, les heures sont accumulées dans les structures en mémoire.
        *   La sortie est générée au format **JSON** pour faciliter la communication avec Python.

### 3.2 L'Interface Utilisateur (Frontend Streamlit)
Développée en Python (`app.py`), elle assure l'interaction avec l'utilisateur.

*   **Ingestion des Données** :
    *   Exécute le binaire `verificateur.exe` avec le fichier texte en entrée.
    *   Récupère et parse le flux JSON standard (`stdout`).
    *   Alternativement, supporte l'import direct de fichiers CSV (logique Python pure).
*   **Gestion d'État** : Utilise `st.session_state` pour persister les données entre les ré-exécutions (rechargement de page).

---

## 4. Logique Métier et Formules de Calcul

Le système implémente des règles de gestion précises conformes aux standards universitaires.

### 4.1 Taux de Conformité Global
C'est un indicateur de performance macroscopique. Il représente le volume global réalisé par rapport au volume prévu.

$$ \text{Taux de Conformité} = \left( \frac{\sum \text{Heures Réalisées (CM+TD+TP)}}{\sum \text{Heures Prévues (CM+TD+TP)}} \right) \times 100 $$

*Note : Ce calcul est basé sur le volume horaire brut, sans pondération.*

### 4.2 Charge Enseignant (Équivalent TD)
Pour rémunérer ou comptabiliser la charge de travail, les heures sont pondérées selon leur nature.

$$ \text{Charge Équiv. TD} = (\text{Heures CM} \times 1.5) + (\text{Heures TD} \times 1.0) + (\text{Heures TP} \times 0.5) $$

*Cette formule a été validée et corrigée (coefficient TP passé de 1.0 à 0.5) pour respecter strictement le cahier des charges.*

### 4.3 Progression Enseignant
Sert à visualiser l'avancement individuel d'un professeur sur ses modules.

$$ \text{Progression} = \left( \frac{\text{Heures Réalisées Brut}}{\text{Heures Prévues Brut}} \right) \times 100 $$

---

## 5. Fonctionnalités Clés du Tableau de Bord

### 5.1 Indicateurs de Performance (KPI)
Le dashboard présente immédiatement :
*   **Nombre d'UEs et d'Enseignants**.
*   **Taux de Conformité** avec indicateur visuel (Vert/Rouge selon seuil 90%).
*   **Statistiques Rapides** : Total Heures Prévues, Total Heures Réalisées, Charge Moyenne.

### 5.2 Visualisations Interactives
*   **Graphique à Barres (Plotly)** : Comparaison Prévu vs Réalisé groupée par type (CM/TD/TP).
*   **Jauge de Performance** : Indicateur semi-circulaire du taux de conformité global.
*   **Cartes Enseignants** : Fiches individuelles affichant la photo (avatar), la charge équivalente, et le détail précis "Réalisé / Prévu" pour chaque type d'heure.

### 5.3 Détection des Anomalies
Un onglet dédié liste toutes les UEs présentant un écart (positif ou négatif) entre le prévu et le réalisé, permettant une intervention rapide.

### 5.4 Intelligence Artificielle (Assistant Pédagogique)
Intégration d'un LLM (Mistral-7B via OpenRouter ou GPT via OpenAI) pour :
*   Analyser les données JSON brutes.
*   Identifier les déséquilibres subtils (ex: surcharge d'un vacataire).
*   Générer des recommandations stratégiques textuelles.

### 5.5 Rapport Légal (PDF)
Génération à la volée d'un document PDF professionnel incluant :
*   En-tête institutionnel (Logo UIDT).
*   Tableaux récapitulatifs (statistiques, anomalies).
*   Graphiques (générés via Matplotlib pour l'intégration statique).
*   Analyse textuelle de l'IA (si disponible).

---

## 6. Stack Technologique

| Couche | Technologie | Rôle |
| :--- | :--- | :--- |
| **Langage Principal** | Python 3.9+ | Orchestration, UI, Logique |
| **Parsing** | C (Flex/Bison) | Moteur de vérification rapide |
| **Framework Web** | Streamlit | Interface utilisateur réactive |
| **Visualisation** | Plotly & Matplotlib | Graphiques web et statiques |
| **Documents** | ReportLab | Moteur PDF bas niveau |
| **IA** | OpenAI Client | Connecteur LLM |

---

## 7. Conclusion

Le projet **Check Planning** est un outil complet qui dépasse la simple vérification de fichiers. En combinant compilation, visualisation de données et intelligence artificielle, il offre aux responsables pédagogiques une vision claire et actionnable de l'activité académique. Sa structure modulaire permet d'envisager facilement des extensions futures, comme la connexion directe à une base de données MySQL ou l'intégration de la gestion des salles.
