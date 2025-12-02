%{
#include <stdio.h>
#include <stdlib.h>
#include "data.h"

int yylex();
void yyerror(char *s);

UE tab_ues[100];
int max_ue_id = 0;
%}

%union {
    float floatVal;
    int intVal;
    char *strVal;
}

%token TOK_UE TOK_CM TOK_TD TOK_TP TOK_DEUX_POINTS TOK_VIRGULE TOK_POINT_VIRGULE TOK_NOM_ENS
%token <floatVal> TOK_VAL

%%

programme:
    liste_ue liste_enseignants
    {
        check_resultats(); /* Génération du JSON à la fin */
    }
    ;

liste_ue: definition_ue | liste_ue definition_ue ;

definition_ue:
    TOK_UE TOK_VAL opt_deux_points 
    TOK_CM opt_deux_points TOK_VAL opt_virgule 
    TOK_TD opt_deux_points TOK_VAL opt_virgule 
    TOK_TP opt_deux_points TOK_VAL
    {
        init_ue((int)$2, $6, $10, $14);
    }
    ;

liste_enseignants: bloc_enseignant | liste_enseignants bloc_enseignant ;

bloc_enseignant:
    TOK_NOM_ENS liste_assignations TOK_POINT_VIRGULE
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

void init_ue(int id, float cm, float td, float tp) {
    if(id < 100) {
        tab_ues[id].id = id;
        tab_ues[id].cm_prevu = cm; tab_ues[id].td_prevu = td; tab_ues[id].tp_prevu = tp;
        tab_ues[id].defined = 1;
        if(id > max_ue_id) max_ue_id = id;
    }
}

void add_heures(int id, float cm, float td, float tp) {
    if(id < 100 && tab_ues[id].defined) {
        tab_ues[id].cm_assure += cm; tab_ues[id].td_assure += td; tab_ues[id].tp_assure += tp;
    }
}

// C'EST ICI QUE L'ON GENERE LE JSON POUR PYTHON
void check_resultats() {
    printf("[\n"); // Début du tableau JSON
    int first = 1;
    for(int i = 1; i <= max_ue_id; i++) {
        if(tab_ues[i].defined) {
            if(!first) printf(",\n");
            first = 0;
            printf("  {\"id\": %d, \"cm_p\": %.2f, \"cm_a\": %.2f, \"td_p\": %.2f, \"td_a\": %.2f, \"tp_p\": %.2f, \"tp_a\": %.2f}",
                   i, tab_ues[i].cm_prevu, tab_ues[i].cm_assure,
                   tab_ues[i].td_prevu, tab_ues[i].td_assure,
                   tab_ues[i].tp_prevu, tab_ues[i].tp_assure);
        }
    }
    printf("\n]\n"); // Fin du tableau JSON
}

void yyerror(char *s) { fprintf(stderr, "Erreur: %s\n", s); }

int main() {
    for(int i=0; i<100; i++) tab_ues[i].defined = 0;
    yyparse();
    return 0;
}