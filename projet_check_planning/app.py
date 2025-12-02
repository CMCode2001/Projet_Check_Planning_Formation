import streamlit as st
import subprocess
import json
import pandas as pd
import time # Nécessaire pour simuler le temps de chargement visuel

# Configuration de la page
st.set_page_config(page_title="Vérificateur Planning", page_icon="🎓")

# Titre
st.title("🎓 Vérificateur de Planning")
st.markdown("---")

# 1. Zone pour déposer le fichier
uploaded_file = st.file_uploader("Choisissez votre fichier texte (.txt)", type="txt")

if uploaded_file is not None:
    # Lire le texte
    texte_input = uploaded_file.getvalue().decode("utf-8")
    
    # --- NOUVEAUTÉ 1 : Affichage du fichier source ---
    st.info("Fichier chargé avec succès.")
    with st.expander("📄 Voir le contenu du fichier source", expanded=True):
        st.code(texte_input, language='text')

    # Bouton pour lancer l'action
    if st.button("🚀 Lancer l'audit de conformité"):
        
        # --- NOUVEAUTÉ 2 : Barre de progression ---
        progress_text = "Démarrage de l'analyse..."
        my_bar = st.progress(0, text=progress_text)
        
        # Étape 1 : Préparation
        time.sleep(0.3) # Petite pause pour l'effet visuel
        my_bar.progress(25, text="📂 Lecture et préparation des données...")
        
        # Étape 2 : Exécution du moteur C
        my_bar.progress(50, text="⚙️ Exécution du moteur Lex & Yacc...")
        
        # On envoie le texte au programme C via l'entrée standard (stdin)
        process = subprocess.run(
            ['./verificateur'],     # Le nom de l'exécutable C
            input=texte_input,      # Le contenu du fichier texte
            text=True,              # Mode texte
            capture_output=True     # Récupérer ce que le C affiche
        )

        # Étape 3 : Traitement de la réponse
        my_bar.progress(80, text="📊 Traitement des données JSON...")
        time.sleep(0.3) # Petite pause pour l'effet visuel

        if process.returncode != 0:
            my_bar.empty() # On enlève la barre en cas d'erreur
            st.error("❌ Erreur critique lors de l'analyse !")
            with st.expander("Détails techniques de l'erreur"):
                st.text(process.stderr) 
        else:
            # 3. Récupération du JSON généré par le C
            try:
                raw_json = process.stdout
                data = json.loads(raw_json) # Conversion JSON -> Python
                
                # Étape 4 : Finalisation
                my_bar.progress(100, text="✅ Analyse terminée !")
                time.sleep(0.5)
                my_bar.empty() # On cache la barre de progression à la fin

                st.success(f"Analyse réussie ! {len(data)} UEs identifiées et traitées.")

                # Création d'un tableau de données (DataFrame)
                df = pd.DataFrame(data)
                df['Nom UE'] = "UE " + df['id'].astype(str)
                df.set_index('Nom UE', inplace=True)

                # 4. Affichage des Graphiques
                st.subheader("📈 Comparaison : Heures Prévues vs Assurées")
                
                tab1, tab2, tab3 = st.tabs(["Cours Magistral (CM)", "Travaux Dirigés (TD)", "Travaux Pratiques (TP)"])
                
                with tab1:
                    st.bar_chart(df[['cm_p', 'cm_a']], color=["#4A90E2", "#E24A4A"]) # Bleu et Rouge personnalisé
                    st.caption("🔵 Bleu: Prévu | 🔴 Rouge: Assuré")
                
                with tab2:
                    st.bar_chart(df[['td_p', 'td_a']], color=["#4A90E2", "#E24A4A"])
                
                with tab3:
                    st.bar_chart(df[['tp_p', 'tp_a']], color=["#4A90E2", "#E24A4A"])

                # 5. Tableau des écarts
                st.subheader("⚠️ Rapport détaillé des écarts")
                df['Ecart CM'] = df['cm_p'] - df['cm_a']
                df['Ecart TD'] = df['td_p'] - df['td_a']
                df['Ecart TP'] = df['tp_p'] - df['tp_a']
                
                # Fonction de style pour les couleurs
                def highlight_ecarts(val):
                    if val > 0: # Manque d'heures
                        return 'background-color: #ffcccc; color: black' 
                    elif val < 0: # Trop d'heures
                        return 'background-color: #ccffcc; color: black'
                    else: # Pile poil (0)
                        return 'color: gray'

                # Affichage du tableau stylisé
                st.dataframe(df[['Ecart CM', 'Ecart TD', 'Ecart TP']].style.map(highlight_ecarts))
                
                with st.expander("ℹ️ Légende du tableau"):
                    st.markdown("""
                    - **Fond Rouge** : Il manque des heures (Prévu > Assuré).
                    - **Fond Vert** : Excès d'heures (Prévu < Assuré).
                    - **Gris** : Le quota est parfaitement respecté.
                    """)

            except json.JSONDecodeError:
                my_bar.empty()
                st.error("Erreur : Le programme C n'a pas renvoyé de JSON valide.")
                st.text("Sortie brute reçue :")
                st.code(process.stdout)