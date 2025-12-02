%{
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "y.tab.h"
%}

%option noyywrap

CHIFFRE     [0-9]+(\.[0-9]+)?
HEURE       {CHIFFRE}h?
ESPACE      [ \t\r]+
NOM_ENS     \*[^*]+\*

%%

"UE"        { return TOK_UE; }
"CM"        { return TOK_CM; }
"TD"        { return TOK_TD; }
"TP"        { return TOK_TP; }

{NOM_ENS}   { return TOK_NOM_ENS; }

{HEURE}     {
    char *h = strchr(yytext, 'h');
    if (h) *h = '\0'; 
    yylval.floatVal = atof(yytext);
    return TOK_VAL;
}

":"         { return TOK_DEUX_POINTS; }
","         { return TOK_VIRGULE; }
";"         { return TOK_POINT_VIRGULE; }
\n          { /* Ignorer */ }
{ESPACE}    { /* Ignorer */ }
.           { /* Ignorer caractères inconnus */ }

%%