%{
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "data.h"
#include "y.tab.h"

/* yylval members used by the lexer */
extern union YYSTYPE yylval;
%}

%option noyywrap

/* Expressions régulières */
CHIFFRE     [0-9]+(\.[0-9]+)?
HEURE       {CHIFFRE}h?
ESPACE      [ \t\r]+
NOM_ENS     \*[^*]+\*

%%

"UE"        { return TOK_UE; }
"CM"        { return TOK_CM; }
"TD"        { return TOK_TD; }
"TP"        { return TOK_TP; }

{NOM_ENS}   {
                /* On duplique la chaîne pour la passer à Yacc */
                yylval.strVal = strdup(yytext);
                return TOK_NOM_ENS;
            }

{HEURE}     {
                /* Gérer 'h' optionnel */
                char tmp[64];
                strncpy(tmp, yytext, sizeof(tmp)-1);
                tmp[sizeof(tmp)-1] = '\0';
                char *h = strchr(tmp, 'h');
                if (h) *h = '\0';
                yylval.floatVal = atof(tmp);
                return TOK_VAL;
            }

":"         { return TOK_DEUX_POINTS; }
","         { return TOK_VIRGULE; }
";"         { return TOK_POINT_VIRGULE; }
\n          { /* Ignorer sauts de ligne */ }
{ESPACE}    { /* Ignorer espaces */ }

.           { /* Ignorer caractères inconnus */ }

%%
