#ifndef DATA_H
#define DATA_H

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

extern UE tab_ues[100]; 
extern int max_ue_id;

void init_ue(int id, float cm, float td, float tp);
void add_heures(int id, float cm, float td, float tp);
void check_resultats(); // Cette fonction générera le JSON

#endif