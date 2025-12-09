#ifndef DATA_H
#define DATA_H

/* Structure d'une UE */
typedef struct {
    int id;
    float cm_prevu;
    float td_prevu;
    float tp_prevu;
    float cm_assure;
    float td_assure;
    float tp_assure;
    int defined;
} UE;

/* Structure d'un enseignant */
typedef struct {
    char nom[100];

    /* heures réalisées */
    float cm_total;
    float td_total;
    float tp_total;

    /* heures prévues (somme des UE pour lesquelles il intervient) */
    float cm_prevu;
    float td_prevu;
    float tp_prevu;

    /* total en équivalent TD */
    float eq_td_total;
} Enseignant;

/* Variables globales partagées */
extern UE tab_ues[100];
extern Enseignant tab_profs[50];
extern int max_ue_id;
extern int nb_profs;

/* Fonctions */
void init_ue(int id, float cm, float td, float tp);
void add_heures(int id, float cm, float td, float tp);
void nouveau_prof(char *nom);
void check_resultats();

#endif /* DATA_H */
