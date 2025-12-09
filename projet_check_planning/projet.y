%{
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "data.h"

int yylex();
void yyerror(char *s);

/* Variables globales (définies dans ce fichier) */
UE tab_ues[100];
Enseignant tab_profs[50];
int max_ue_id = 0;
int nb_profs = 0;
%}

/* Union pour yylval */
%union {
    float floatVal;
    int intVal;
    char *strVal;
}

%token TOK_UE TOK_CM TOK_TD TOK_TP TOK_DEUX_POINTS TOK_VIRGULE TOK_POINT_VIRGULE
%token <floatVal> TOK_VAL
%token <strVal> TOK_NOM_ENS

%%

programme:
    liste_ue liste_enseignants
    { check_resultats(); }
    ;

liste_ue: definition_ue | liste_ue definition_ue ;

definition_ue:
    TOK_UE TOK_VAL opt_deux_points
    TOK_CM opt_deux_points TOK_VAL opt_virgule
    TOK_TD opt_deux_points TOK_VAL opt_virgule
    TOK_TP opt_deux_points TOK_VAL
    { 
        /* TOK_VAL est un float, mais l'id est entier */
        init_ue((int)$2, $6, $10, $14); 
    }
    ;

liste_enseignants: bloc_enseignant | liste_enseignants bloc_enseignant ;

bloc_enseignant:
    TOK_NOM_ENS 
    { 
        nouveau_prof($1); 
        free($1); /* on a strdup dans le lexer */
    }
    liste_assignations 
    TOK_POINT_VIRGULE
    ;

liste_assignations: assignation | liste_assignations assignation ;

assignation:
    TOK_UE TOK_VAL opt_deux_points
    TOK_CM opt_deux_points TOK_VAL opt_virgule
    TOK_TD opt_deux_points TOK_VAL opt_virgule
    TOK_TP opt_deux_points TOK_VAL
    { 
        add_heures((int)$2, $6, $10, $14); 
    }
    ;

opt_deux_points: TOK_DEUX_POINTS | ;
opt_virgule: TOK_VIRGULE | ;

%%

/* --- CODE C --- */

void init_ue(int id, float cm, float td, float tp) {
    if (id < 0 || id >= 100) return;
    tab_ues[id].id = id;
    tab_ues[id].cm_prevu = cm;
    tab_ues[id].td_prevu = td;
    tab_ues[id].tp_prevu = tp;

    /* initialiser les heures assurées à 0 */
    tab_ues[id].cm_assure = 0.0f;
    tab_ues[id].td_assure = 0.0f;
    tab_ues[id].tp_assure = 0.0f;

    tab_ues[id].defined = 1;
    if (id > max_ue_id) max_ue_id = id;
}

void nouveau_prof(char *nom) {
    if (nb_profs < 50) {
        /* On copie le nom */
        strncpy(tab_profs[nb_profs].nom, nom, sizeof(tab_profs[nb_profs].nom)-1);
        tab_profs[nb_profs].nom[sizeof(tab_profs[nb_profs].nom)-1] = '\0';

        /* Initialiser totaux réalisés et prévus */
        tab_profs[nb_profs].cm_total = 0.0f;
        tab_profs[nb_profs].td_total = 0.0f;
        tab_profs[nb_profs].tp_total = 0.0f;

        tab_profs[nb_profs].cm_prevu = 0.0f;
        tab_profs[nb_profs].td_prevu = 0.0f;
        tab_profs[nb_profs].tp_prevu = 0.0f;

        tab_profs[nb_profs].eq_td_total = 0.0f;

        nb_profs++;
    }
}

void add_heures(int id, float cm, float td, float tp) {
    /* 1) Ajouter à l'UE (heures assurées) */
    if (id >= 0 && id < 100 && tab_ues[id].defined) {
        tab_ues[id].cm_assure += cm;
        tab_ues[id].td_assure += td;
        tab_ues[id].tp_assure += tp;
    } else {
        /* UE non définie : on peut l'ignorer ou afficher un warning */
        fprintf(stderr, "Warning: assignation pour UE %d non définie (ignorée)\n", id);
    }

    /* 2) Ajouter au Prof en cours (heures réalisées) */
    if (nb_profs > 0) {
        int p = nb_profs - 1;
        tab_profs[p].cm_total += cm;
        tab_profs[p].td_total += td;
        tab_profs[p].tp_total += tp;

        /* Ajouter les heures prévues de cette UE au prof */
        if (id >= 0 && id < 100 && tab_ues[id].defined) {
            tab_profs[p].cm_prevu += tab_ues[id].cm_prevu;
            tab_profs[p].td_prevu += tab_ues[id].td_prevu;
            tab_profs[p].tp_prevu += tab_ues[id].tp_prevu;
        }

        /* Calcul EQ TD : CM*1.5 + TD*1 + TP*0.5 */
        tab_profs[p].eq_td_total += (cm * 1.5f) + (td * 1.0f) + (tp * 0.5f);
    }
}

void check_resultats() {
    /* --- Affichage lisible par professeur --- */
    printf("=== Statistiques par enseignant ===\n");
    for (int i = 0; i < nb_profs; i++) {
        printf("Enseignant %s\n", tab_profs[i].nom);
        printf("  CM prevu : %.2f  | CM realise : %.2f\n", tab_profs[i].cm_prevu, tab_profs[i].cm_total);
        printf("  TD prevu : %.2f  | TD realise : %.2f\n", tab_profs[i].td_prevu, tab_profs[i].td_total);
        printf("  TP prevu : %.2f  | TP realise : %.2f\n", tab_profs[i].tp_prevu, tab_profs[i].tp_total);
        printf("  => Equiv. TD total (calcule a partir des stats realise) : %.2f h\n", tab_profs[i].eq_td_total);
        printf("\n");
    }

    /* --- Sortie JSON détaillée --- */
    printf("{\n");

    /* JSON Partie UEs */
    printf("  \"ues\": [\n");
    int first = 1;
    for (int i = 1; i <= max_ue_id; i++) {
        if (tab_ues[i].defined) {
            if (!first) printf(",\n");
            first = 0;
            printf("    {\"id\": %d, \"cm_p\": %.2f, \"cm_a\": %.2f, \"td_p\": %.2f, \"td_a\": %.2f, \"tp_p\": %.2f, \"tp_a\": %.2f}",
                   i, tab_ues[i].cm_prevu, tab_ues[i].cm_assure,
                   tab_ues[i].td_prevu, tab_ues[i].td_assure,
                   tab_ues[i].tp_prevu, tab_ues[i].tp_assure);
        }
    }
    printf("\n  ],\n");

    /* JSON Partie Enseignants (enrichie) */
    printf("  \"enseignants\": [\n");
    first = 1;
    for (int i = 0; i < nb_profs; i++) {
        if (!first) printf(",\n");
        first = 0;
        printf("    {\n");
        printf("      \"nom\": \"%s\",\n", tab_profs[i].nom);
        printf("      \"prevu\": {\"cm\": %.2f, \"td\": %.2f, \"tp\": %.2f},\n",
               tab_profs[i].cm_prevu, tab_profs[i].td_prevu, tab_profs[i].tp_prevu);
        printf("      \"realise\": {\"cm\": %.2f, \"td\": %.2f, \"tp\": %.2f},\n",
               tab_profs[i].cm_total, tab_profs[i].td_total, tab_profs[i].tp_total);
        printf("      \"equivalent_td\": %.2f\n", tab_profs[i].eq_td_total);
        printf("    }");
    }
    printf("\n  ],\n");

    /* Analyse des problèmes par UE (manquantes / en trop) */
    printf("  \"ues_problemes\": [\n");
    first = 1;
    for (int i = 1; i <= max_ue_id; i++) {
        if (tab_ues[i].defined) {
            float diff_cm = tab_ues[i].cm_assure - tab_ues[i].cm_prevu;
            float diff_td = tab_ues[i].td_assure - tab_ues[i].td_prevu;
            float diff_tp = tab_ues[i].tp_assure - tab_ues[i].tp_prevu;
            if (diff_cm != 0.0f || diff_td != 0.0f || diff_tp != 0.0f) {
                if (!first) printf(",\n");
                first = 0;
                printf("    {\"ue\": %d, \"cm\": %.2f, \"td\": %.2f, \"tp\": %.2f}",
                       i, diff_cm, diff_td, diff_tp);
            }
        }
    }
    printf("\n  ]\n");

    printf("}\n");
}

void yyerror(char *s) {
    fprintf(stderr, "Erreur: %s\n", s);
}

/* --- main --- */
int main() {
    /* Initialiser les UEs par défaut */
    for (int i = 0; i < 100; i++) {
        tab_ues[i].defined = 0;
        tab_ues[i].cm_prevu = tab_ues[i].td_prevu = tab_ues[i].tp_prevu = 0.0f;
        tab_ues[i].cm_assure = tab_ues[i].td_assure = tab_ues[i].tp_assure = 0.0f;
        tab_ues[i].id = i;
    }

    /* initialisation nb_profs = 0 (déjà en global) */
    yyparse();
    return 0;
}
