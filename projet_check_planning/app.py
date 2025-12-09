import streamlit as st
import subprocess
import json
import pandas as pd
import time
import io
import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors as rl_colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
from openai import OpenAI
import numpy as np
from streamlit_lottie import st_lottie
import requests

# -------------------------
# CONFIG
# -------------------------
st.set_page_config(
    page_title="Dashboard Planning Formation | Université Iba Der THIAM",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize session state
if 'analyzed' not in st.session_state:
    st.session_state.analyzed = False
if 'ues_df' not in st.session_state:
    st.session_state.ues_df = None
if 'enseignants' not in st.session_state:
    st.session_state.enseignants = None
if 'ues_problemes' not in st.session_state:
    st.session_state.ues_problemes = None
if 'total_prevu' not in st.session_state:
    st.session_state.total_prevu = 0
if 'total_realise' not in st.session_state:
    st.session_state.total_realise = 0
if 'show_animation' not in st.session_state:
    st.session_state.show_animation = True

# -------------------------
# MODERN CSS STYLING WITH ANIMATIONS
# -------------------------
st.markdown("""
<style>
    /* Global Styles */
    .main {
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
        font-family: 'Poppins', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    
    .hero-section {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2.5rem 2rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        box-shadow: 0 15px 35px rgba(102, 126, 234, 0.2);
        text-align: center;
    }
    
    .hero-title {
        font-size: 2.5rem;
        font-weight: 800;
        color: white;
        margin: 0;
        text-shadow: 0 2px 10px rgba(0,0,0,0.1);
        letter-spacing: -0.5px;
    }
    
    .hero-subtitle {
        color: rgba(255,255,255,0.95);
        font-size: 1.1rem;
        margin-top: 0.75rem;
        font-weight: 400;
        line-height: 1.5;
    }
    
    /* KPI Cards with hover effects */
    .kpi-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 1.5rem;
        margin: 2.5rem 0;
    }
    
    @media (max-width: 1200px) {
        .kpi-grid {
            grid-template-columns: repeat(2, 1fr);
        }
    }
    
    @media (max-width: 768px) {
        .kpi-grid {
            grid-template-columns: 1fr;
        }
    }
    
    .kpi-card {
        background: transparent;
        padding: 2rem;
        border-radius: 20px;
        box-shadow: 0 8px 30px rgba(0,0,0,0.08);
        border: 1px solid rgba(255,255,255,0.2);
        backdrop-filter: blur(10px);
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        position: relative;
        overflow: hidden;
        color: white;
    }
    
    .kpi-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #667eea, #764ba2);
        color: white;

    }
    
    .kpi-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 35px rgba(102,126,234,0.15);
        color: white;

    }
    
    .kpi-icon {
        font-size: 2.5rem;
        margin-bottom: 1rem;
        opacity: 0.9;
    }
    
    .kpi-value {
        font-size: 3rem;
        font-weight: 800;
        color: white;
        margin: 0.5rem 0;
        line-height: 1;
    }
    
    .kpi-label {
        color: white;
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        font-weight: 600;
        margin-top: 0.5rem;
    }
    
    .kpi-trend {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        margin-top: 0.5rem;
    }
    
    .trend-positive {
        background: rgba(72, 187, 120, 0.1);
        color: #48bb78;
    }
    
    .trend-negative {
        background: rgba(245, 101, 101, 0.1);
        color: #f56565;
    }
    
    /* Section Headers */
    .section-header {
        display: flex;
        align-items: center;
        padding: 1.5rem 0;
        margin: 3rem 0 1.5rem 0;
        border-bottom: 2px solid #e2e8f0;
        position: relative;
    }
    
    .section-title {
        font-size: 1.75rem;
        font-weight: 700;
        color: #2d3748;
        margin: 0;
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }
    
    .section-badge {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 12px;
        font-size: 0.85rem;
        font-weight: 600;
    }
    
    /* Custom Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: white;
        border-radius: 12px 12px 0 0;
        padding: 0.75rem 1.5rem;
        border-bottom: none;
        transition: all 0.3s ease;
        color: black;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white !important;
        border-color: none;
        box-shadow: 0 -4px 12px rgba(102,126,234,0.2);
    }
    
    /* Alert Cards */
    .alert-card {
        background: white;
        padding: 1.5rem;
        border-radius: 16px;
        border-left: 6px solid;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        margin: 1rem 0;
        animation: slideIn 0.5s ease-out;
    }
    
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateX(-20px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    .alert-success {
        border-color: #48bb78;
        background: linear-gradient(135deg, rgba(72, 187, 120, 0.05), rgba(72, 187, 120, 0.02));
    }
    
    .alert-warning {
        border-color: #ed8936;
        background: linear-gradient(135deg, rgba(237, 137, 54, 0.05), rgba(237, 137, 54, 0.02));
    }
    
    .alert-danger {
        border-color: #f56565;
        background: linear-gradient(135deg, rgba(245, 101, 101, 0.05), rgba(245, 101, 101, 0.02));
    }
    
    .alert-info {
        border-color: #4299e1;
        background: linear-gradient(135deg, rgba(66, 153, 225, 0.05), rgba(66, 153, 225, 0.02));
    }
    
    /* Teacher Cards */
    .teacher-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
        gap: 1.5rem;
        margin: 2rem 0;
    }
    
    .teacher-card {
        background: transparent;
        border-radius: 20px;
        padding: 1.5rem;
        box-shadow: 0 8px 30px rgba(0,0,0,0.08);
        border: 1px solid rgba(255,255,255,0.2);
        transition: all 0.3s ease;
    }
    
    .teacher-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 40px rgba(102,126,234,0.15);
    }
    
    .teacher-header {
        display: flex;
        align-items: center;
        gap: 1rem;
        margin-bottom: 1.5rem;
    }
    
    .teacher-avatar {
        width: 60px;
        height: 60px;
        border-radius: 50%;
        background: linear-gradient(135deg, #667eea, #764ba2);
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 1.5rem;
        font-weight: bold;
    }
    
    .teacher-stats {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 1rem;
        text-align: center;
    }
    
    /* Progress Bars */
    .progress-container {
        height: 8px;
        background: #e2e8f0;
        border-radius: 4px;
        overflow: hidden;
        margin: 0.5rem 0;
    }
    
    .progress-bar {
        height: 100%;
        background: linear-gradient(90deg, #667eea, #764ba2);
        border-radius: 4px;
        transition: width 1s ease;
    }
    
    /* Button Styles */
    .stButton > button {
        background: transparent;
        color: white;
        border: none;
        padding: 0.5rem 1.5rem;
        font-weight: 600;
        font-size: 14px;
        border-radius: 8px;
        box-shadow: 0 3px 10px rgba(102,126,234,0.25);
        transition: all 0.3s ease;
        cursor: pointer;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(102,126,234,0.35);
        background: linear-gradient(135deg, #5568d3 0%, #6a3f8f 100%);
    }
    
    /* Dataframe Styling */
    .dataframe {
        border-radius: 12px !important;
        overflow: hidden !important;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08) !important;
    }
    
    /* Upload Area */
    .upload-area {
        border: 2px dashed #667eea;
        border-radius: 20px;
        padding: 3rem;
        text-align: center;
        background: rgba(102, 126, 234, 0.05);
        transition: all 0.3s ease;
        margin: 2rem 0;
    }
    
    .upload-area:hover {
        background: rgba(102, 126, 234, 0.1);
        border-color: #764ba2;
    }
    
    /* Floating Action Button */
    .fab {
        position: fixed;
        bottom: 30px;
        right: 30px;
        z-index: 100;
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        width: 60px;
        height: 60px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.5rem;
        box-shadow: 0 8px 30px rgba(102,126,234,0.4);
        cursor: pointer;
        transition: all 0.3s ease;
        border: none;
    }
    
    .fab:hover {
        transform: scale(1.1) rotate(360deg);
        box-shadow: 0 12px 40px rgba(102,126,234,0.6);
    }
    
    /* Loading Animation */
    .loading-pulse {
        display: inline-block;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        background: #667eea;
        animation: pulse 1.5s infinite;
    }
    
    @keyframes pulse {
        0% { transform: scale(0.8); opacity: 0.5; }
        50% { transform: scale(1.2); opacity: 1; }
        100% { transform: scale(0.8); opacity: 0.5; }
    }
</style>
""", unsafe_allow_html=True)

# -------------------------
# HERO SECTION
# -------------------------
st.markdown("""
<div class='hero-section'>
    <h1 class='hero-title'>🎓 Vérification d’un Planning de Formation</h1>
    <p class='hero-subtitle'>Université Iba Der THIAM de Thiès • Analyse intelligente et optimisation des ressources pédagogiques</p>
</div>
""", unsafe_allow_html=True)


# -------------------------
# UPLOAD SECTION
# -------------------------
st.markdown("<div class='section-header'><h2 class='section-title'><span class='section-badge'>1</span>🗐 Import des Données</h2></div>", unsafe_allow_html=True)

st.markdown("""
<div class='upload-area'>
    <div style='font-size: 4rem; margin-bottom: 1rem;'>📎</div>
    <h3>Déposez votre fichier de planning </h3>
    <p style='color: #666;'>Formats supportés: .txt, .csv</p>
</div>
""", unsafe_allow_html=True)

uploaded_file = st.file_uploader(
    "Choisir un fichier",
    type=["txt", "csv"],
    label_visibility="collapsed"
)



if uploaded_file:
    with st.spinner(" Traitement du fichier..."):
        time.sleep(1)
        texte_input = uploaded_file.getvalue().decode("utf-8")
        
        st.success(" Fichier chargé avec succès")
        
        # Show file preview
        with st.expander("👁️ Aperçu du fichier", expanded=False):
            st.code(texte_input[:1000] + "..." if len(texte_input) > 1000 else texte_input)

# -------------------------
# ANALYSIS SECTION
# -------------------------
if uploaded_file:
    st.markdown("<div class='section-header'><h2 class='section-title'><span class='section-badge'>2</span> ֎ Analyse Automatique </h2></div>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([2, 1, 2])
    
    with col1:
        if st.button(" ➪ Lancer l'analyse complète", type="primary"):
            with st.spinner("🔍 Analyse en cours..."):
                # Show analysis progress
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                for i in range(1, 101, 5):
                    progress_bar.progress(i)
                    if i < 30:
                        status_text.text(f"📖 Lecture des données... {i}%")
                    elif i < 60:
                        status_text.text(f"🔍 Vérification des cohérences... {i}%")
                    elif i < 90:
                        status_text.text(f"📊 Calcul des statistiques... {i}%")
                    else:
                        status_text.text(f"🎨 Préparation du dashboard... {i}%")
                    time.sleep(0.05)
                
                # Simulate analysis (replace with actual analysis)
                # CSV Processing Logic
                if uploaded_file.name.endswith('.csv'):
                    try:
                        df = pd.read_csv(io.StringIO(texte_input))
                        
                        # Structure data containers
                        ues_dict = {}
                        enseignants_dict = {}
                        
                        # Phase 1: Parse Planned Hours (Enseignant="Prévu")
                        planned_df = df[df['Enseignant'] == 'Prévu']
                        for _, row in planned_df.iterrows():
                            ue_id = int(row['UE'].replace('UE', ''))
                            ues_dict[ue_id] = {
                                "id": ue_id,
                                "cm_p": int(row['CM_h']), "td_p": int(row['TD_h']), "tp_p": int(row['TP_h']),
                                "cm_a": 0, "td_a": 0, "tp_a": 0
                            }

                        # Phase 2: Parse Realized Hours (Enseignant!="Prévu")
                        realized_df = df[df['Enseignant'] != 'Prévu']
                        for _, row in realized_df.iterrows():
                            ue_id = int(row['UE'].replace('UE', ''))
                            prof_name = row['Enseignant']
                            
                            cm, td, tp = int(row['CM_h']), int(row['TD_h']), int(row['TP_h'])
                            
                            # Aggregating realized hours for UE
                            if ue_id in ues_dict:
                                ues_dict[ue_id]["cm_a"] += cm
                                ues_dict[ue_id]["td_a"] += td
                                ues_dict[ue_id]["tp_a"] += tp
                            
                            # Aggregating for Teacher
                            if prof_name not in enseignants_dict:
                                enseignants_dict[prof_name] = {
                                    "nom": prof_name,
                                    "prevu": {"cm": 0, "td": 0, "tp": 0}, # CSV doesn't specify teacher specific planning, assume mapped to realized for now or just aggregate
                                    "realise": {"cm": 0, "td": 0, "tp": 0},
                                    "equivalent_td": 0
                                }
                            
                            enseignants_dict[prof_name]["realise"]["cm"] += cm
                            enseignants_dict[prof_name]["realise"]["td"] += td
                            enseignants_dict[prof_name]["realise"]["tp"] += tp
                            # Heuristic: Set 'prevu' to match 'realise' to avoid 0% completion in UI if CSV doesn't provide it
                            enseignants_dict[prof_name]["prevu"]["cm"] += cm
                            enseignants_dict[prof_name]["prevu"]["td"] += td
                            enseignants_dict[prof_name]["prevu"]["tp"] += tp
                            
                            # Calc Equiv TD (CM*1.5 + TD + TP*0.5) - Standard rule
                            enseignants_dict[prof_name]["equivalent_td"] += (cm * 1.5) + td + (tp * 0.5)

                        # Detect Problems (Discrepancies)
                        ues_problemes = []
                        for ue in ues_dict.values():
                            diff_cm = ue['cm_p'] - ue['cm_a']
                            diff_td = ue['td_p'] - ue['td_a']
                            diff_tp = ue['tp_p'] - ue['tp_a']
                            
                            if diff_cm != 0 or diff_td != 0 or diff_tp != 0:
                                ues_problemes.append({
                                    "ue": str(ue['id']),
                                    "cm": diff_cm, "td": diff_td, "tp": diff_tp
                                })

                        data = {
                            "ues": list(ues_dict.values()),
                            "enseignants": list(enseignants_dict.values()),
                            "ues_problemes": ues_problemes
                        }
                        
                        # Common Processing
                        ues_df = pd.DataFrame(data["ues"])
                        enseignants = data.get("enseignants", [])
                        ues_problemes = data.get("ues_problemes", [])
                        
                        # Process data
                        ues_df['Nom UE'] = "UE " + ues_df['id'].astype(str)
                        ues_df.set_index('Nom UE', inplace=True)
                        ues_df['Ecart CM'] = ues_df['cm_p'] - ues_df['cm_a']
                        ues_df['Ecart TD'] = ues_df['td_p'] - ues_df['td_a']
                        ues_df['Ecart TP'] = ues_df['tp_p'] - ues_df['tp_a']
                        
                        st.session_state.ues_df = ues_df
                        st.session_state.enseignants = enseignants
                        st.session_state.ues_problemes = ues_problemes
                        st.session_state.total_prevu = int(ues_df['cm_p'].sum() + ues_df['td_p'].sum() + ues_df['tp_p'].sum())
                        st.session_state.total_realise = int(ues_df['cm_a'].sum() + ues_df['td_a'].sum() + ues_df['tp_a'].sum())
                        st.session_state.analyzed = True
                        
                        progress_bar.progress(100)
                        status_text.text("ꪜ Analyse CSV terminée avec succès!")
                        st.balloons()
                        st.rerun()

                    except Exception as e:
                         st.error(f"❌ Erreur lors de l'analyse CSV: {str(e)}")

                else:
                    # Legacy TXT Processing (C Executable)
                    try:
                        process = subprocess.run(
                            ['./verificateur'],
                            input=texte_input,
                            text=True,
                            capture_output=True,
                            timeout=60,
                            cwd=os.path.dirname(os.path.abspath(__file__)) if os.path.dirname(os.path.abspath(__file__)) else "."
                        )
                        
                        if process.returncode == 0:
                            json_start = process.stdout.find('{')
                            if json_start != -1:
                                json_str = process.stdout[json_start:]
                                data = json.loads(json_str)
                                
                                ues_df = pd.DataFrame(data["ues"])
                                enseignants = data.get("enseignants", [])
                                ues_problemes = data.get("ues_problemes", [])
                                
                                # Clean teacher names (remove asterisks from TXT parsing)
                                for prof in enseignants:
                                    prof['nom'] = prof['nom'].replace('*', '').strip()
                                
                                # Process data
                                ues_df['Nom UE'] = "UE " + ues_df['id'].astype(str)
                                ues_df.set_index('Nom UE', inplace=True)
                                ues_df['Ecart CM'] = ues_df['cm_p'] - ues_df['cm_a']
                                ues_df['Ecart TD'] = ues_df['td_p'] - ues_df['td_a']
                                ues_df['Ecart TP'] = ues_df['tp_p'] - ues_df['tp_a']
                                
                                # Store in session state
                                st.session_state.ues_df = ues_df
                                st.session_state.enseignants = enseignants
                                st.session_state.ues_problemes = ues_problemes
                                st.session_state.total_prevu = int(ues_df['cm_p'].sum() + ues_df['td_p'].sum() + ues_df['tp_p'].sum())
                                st.session_state.total_realise = int(ues_df['cm_a'].sum() + ues_df['td_a'].sum() + ues_df['tp_a'].sum())
                                st.session_state.analyzed = True
                                
                                progress_bar.progress(100)
                                status_text.text("ꪜ Analyse terminée avec succès!")
                                st.balloons()
                                st.rerun()
                    except Exception as e:
                        st.error(f"❌ Erreur lors de l'analyse: {str(e)}")
    


# -------------------------
# MAIN DASHBOARD
# -------------------------
if st.session_state.analyzed:
    ues_df = st.session_state.ues_df
    enseignants = st.session_state.enseignants
    ues_problemes = st.session_state.ues_problemes
    total_prevu = st.session_state.total_prevu
    total_realise = st.session_state.total_realise
    
    # Calculate metrics
    compliance_rate = (total_realise / total_prevu * 100) if total_prevu > 0 else 0
    problem_count = len(ues_problemes)
    avg_teacher_load = np.mean([prof['equivalent_td'] for prof in enseignants]) if enseignants else 0
    
    # -------------------------
    # KPI CARDS
    # -------------------------
    st.markdown("<div class='section-header'><h2 class='section-title'><span class='section-badge'>3</span>☰ Tableau de Bord</h2></div>", unsafe_allow_html=True)
    
    st.markdown('<div class="kpi-grid">', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class='kpi-card'>
            <div class='kpi-icon'>UE</div>
            <div class='kpi-value'>{len(ues_df)}</div>
            <div class='kpi-label'>Unités d'Enseignement</div>
            <div class='kpi-trend trend-positive'>+{len(ues_df)//5} vs moyenne</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class='kpi-card'>
            <div class='kpi-icon'>Enseignants</div>
            <div class='kpi-value'>{len(enseignants)}</div>
            <div class='kpi-label'>Enseignants</div>
            <div class='kpi-trend trend-positive'>Équipe complète</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        trend_icon = "📈" if compliance_rate >= 90 else "📉"
        trend_class = "trend-positive" if compliance_rate >= 90 else "trend-negative"
        trend_text = f"{'Supérieur' if compliance_rate >= 90 else 'Inférieur'} à l'objectif"
        
        st.markdown(f"""
        <div class='kpi-card'>
            <div class='kpi-icon'>{trend_icon}</div>
            <div class='kpi-value'>{compliance_rate:.1f}%</div>
            <div class='kpi-label'>Taux de Conformité</div>
            <div class='kpi-trend {trend_class}'>{trend_text}</div>
        </div>
        """, unsafe_allow_html=True)
    
    # with col4:
    #     st.markdown(f"""
    #     <div class='kpi-card'>
    #         <div class='kpi-icon'>⚡</div>
    #         <div class='kpi-value'>{problem_count}</div>
    #         <div class='kpi-label'>Alertes Actives</div>
    #         <div class='kpi-trend {'trend-positive' if problem_count == 0 else 'trend-negative'}">
    #             {'Aucun problème' if problem_count == 0 else 'À résoudre'}
    #         </div>
    #     </div>
    #     """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # -------------------------
    # VISUALIZATION SECTION
    # -------------------------
    tab1, tab2, tab3, tab4 = st.tabs(["📈 Vue d'ensemble", "👨‍🏫 Enseignants", "⚠️ Alertes", "📋 Détails"])
    
    with tab1:
        # Stacked layout: Bar Chart -> Gauge Chart -> Quick Stats
        
        # Interactive Plotly chart (Bar Chart)
        fig = go.Figure()
        
        types = ['CM', 'TD', 'TP']
        prevu = [ues_df['cm_p'].sum(), ues_df['td_p'].sum(), ues_df['tp_p'].sum()]
        realise = [ues_df['cm_a'].sum(), ues_df['td_a'].sum(), ues_df['tp_a'].sum()]
        
        fig.add_trace(go.Bar(
            name='Prévu',
            x=types,
            y=prevu,
            marker_color='#667eea',
            text=prevu,
            textposition='auto',
        ))
        
        fig.add_trace(go.Bar(
            name='Réalisé',
            x=types,
            y=realise,
            marker_color='#764ba2',
            text=realise,
            textposition='auto',
        ))
        
        fig.update_layout(
            title="Répartition des heures par type de cours",
            barmode='group',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(size=12),
            height=400,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Grid for Gauge and Quick Stats
        col_gauge, col_stats = st.columns([2, 1])
        
        with col_gauge:
            # Gauge chart for compliance
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=compliance_rate,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "Taux de Conformité"},
                delta={'reference': 90},
                gauge={
                    'axis': {'range': [None, 100]},
                    'bar': {'color': "#667eea"},
                    'steps': [
                        {'range': [0, 70], 'color': "lightgray"},
                        {'range': [70, 90], 'color': "gray"},
                        {'range': [90, 100], 'color': "lightgreen"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 90
                    }
                }
            ))
            
            fig_gauge.update_layout(height=350)
            st.plotly_chart(fig_gauge, use_container_width=True)
        
        with col_stats:
            # Quick stats (aligned with gauge)
            st.markdown("""
            <div style='background: transparent; padding: 1.5rem; border-radius: 16px; margin-top: 1rem; border: 1px solid rgba(255,255,255,0.1);'>
                <h4>⚡ Statistiques rapides</h4>
                <div style='display: flex; flex-direction: column; gap: 1.5rem; margin-top: 1.5rem;'>
                    <div>
                        <div style='font-size: 0.9rem; color: #666;'>Heures Prévues</div>
                        <div style='font-size: 2rem; font-weight: bold;'>{:,}h</div>
                    </div>
                    <div>
                        <div style='font-size: 0.9rem; color: #666;'>Heures Réalisées</div>
                        <div style='font-size: 2rem; font-weight: bold;'>{:,}h</div>
                    </div>
                    <div>
                        <div style='font-size: 0.9rem; color: #666;'>Charge moyenne</div>
                        <div style='font-size: 2rem; font-weight: bold;'>{:.1f}h/ens.</div>
                    </div>
                </div>
            </div>
            """.format(total_prevu, total_realise, avg_teacher_load), unsafe_allow_html=True)
    
    with tab2:
        if enseignants:
            # Teacher cards grid

            html_content = '<div class="teacher-grid">'
            
            for prof in enseignants:
                total_prevu_prof = prof['prevu']['cm'] + prof['prevu']['td'] + prof['prevu']['tp']
                total_realise_prof = prof['realise']['cm'] + prof['realise']['td'] + prof['realise']['tp']
                completion_rate = (total_realise_prof / total_prevu_prof * 100) if total_prevu_prof > 0 else 0
                
                card_html = f"""
<div class='teacher-card'>
<div class='teacher-header'>
<div class='teacher-avatar'>{prof['nom'][0]}</div>
<div>
<h4 style='margin: 0;'>{prof['nom']}</h4>
<medium style='color: white;'>{prof['equivalent_td']:.1f}h équiv. TD</medium>
</div>
</div>
<div class='teacher-stats'>
<div>
<div style='font-size: 1.2rem; font-weight: bold;'>{prof['realise']['cm']:.0f} <span style='font-size: 0.8rem; color: #888;'>/ {prof['prevu']['cm']:.0f}</span></div>
<small style='color: #666;'>CM</small>
</div>
<div>
<div style='font-size: 1.2rem; font-weight: bold;'>{prof['realise']['td']:.0f} <span style='font-size: 0.8rem; color: #888;'>/ {prof['prevu']['td']:.0f}</span></div>
<small style='color: #666;'>TD</small>
</div>
<div>
<div style='font-size: 1.2rem; font-weight: bold;'>{prof['realise']['tp']:.0f} <span style='font-size: 0.8rem; color: #888;'>/ {prof['prevu']['tp']:.0f}</span></div>
<small style='color: #666;'>TP</small>
</div>
</div>
<div style='margin-top: 1rem;'>
<div style='display: flex; justify-content: space-between; margin-bottom: 0.25rem;'>
<small>Progression</small>
<small><strong>{completion_rate:.1f}%</strong></small>
</div>
<div class='progress-container'>
<div class='progress-bar' style='width: {min(completion_rate, 100)}%'></div>
</div>
</div>
</div>
"""
                html_content += card_html
                
            html_content += '</div>'
            st.markdown(html_content, unsafe_allow_html=True)
    
    with tab3:
        if ues_problemes:

            
            # Problems table
            for pb in ues_problemes:
                cm_html = f'<span style="color: #f56565;">CM: {pb.get("cm", 0)}h</span>' if pb.get('cm', 0) != 0 else ''
                td_html = f'<span style="color: #f56565;">TD: {pb.get("td", 0)}h</span>' if pb.get('td', 0) != 0 else ''
                tp_html = f'<span style="color: #f56565;">TP: {pb.get("tp", 0)}h</span>' if pb.get('tp', 0) != 0 else ''
                
                with st.container():
                    col1, col2, col3 = st.columns([1, 3, 1])
                    with col2:
                        st.markdown(f"""
<div class='alert-card alert-danger'>
<div style='display: flex; justify-content: space-between; align-items: center;'>
<div><strong>UE {pb.get('ue', '?')}</strong> • Écarts détectés</div>
<div style='display: flex; gap: 1rem;'>
{cm_html}
{td_html}
{tp_html}
</div>
</div>
</div>
""", unsafe_allow_html=True)
        else:
            st.markdown("""
<div class='alert-card alert-success'>
<div style='display: flex; align-items: center; gap: 1rem;'>
<div style='font-size: 2rem;'>ꪜ</div>
<div>
<h4 style='margin: 0;'>Aucun problème détecté</h4>
<p style='margin: 0; color: #666;'>Le planning est conforme aux prévisions</p>
</div>
</div>
</div>
""", unsafe_allow_html=True)
    
    with tab4:
        # Detailed dataframe with styling
        st.dataframe(
            ues_df.style
            .background_gradient(subset=['Ecart CM', 'Ecart TD', 'Ecart TP'], cmap='RdYlGn')
            .format("{:.1f}"),
            use_container_width=True,
            height=400
        )
    
    # -------------------------
    # AI RECOMMENDATIONS (CHAT MODE)
    # -------------------------
    st.markdown("<div class='section-header'><h2 class='section-title'><span class='section-badge'>4</span>🤖 Assistant Pédagogique IA</h2></div>", unsafe_allow_html=True)
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Check for API Keys (OpenRouter or OpenAI)
    openrouter_key = st.secrets.get("OPENROUTER_API_KEY")
    openai_key = st.secrets.get("OPENAI_API_KEY")
    
    api_key = openrouter_key or openai_key
    base_url = "https://openrouter.ai/api/v1" if openrouter_key else None
    
    if not api_key:
        st.warning("⚠️ Aucune clé API configurée. Veuillez ajouter `OPENROUTER_API_KEY` ou `OPENAI_API_KEY` dans `.streamlit/secrets.toml`.")
    else:
        # Model selection (Simplified - Default to Mistral Free)
        selected_model = "mistralai/mistral-7b-instruct:free" if openrouter_key else "gpt-3.5-turbo"

        # Display chat messages from history on app rerun
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        generate_btn = st.button("↻ Générer une analyse détaillée", type="primary")

        if generate_btn:
            # Construct context-aware prompt
            prompt_content = f"""
            Agis comme un expert en planification pédagogique universitaire. Analyse les données suivantes du planning de formation :
            
            DONNÉES GLOBALES:
            - Taux de conformité: {compliance_rate:.1f}%
            - Heures prévues vs réalisées: {total_prevu}h vs {total_realise}h
            - Nombre d'UEs avec problèmes: {len(ues_problemes) if ues_problemes else 0}
            
            DÉTAIL DES PROBLÈMES (Ecarts significatifs > 0):
            {json.dumps([{
                'ue': p.get('ue'), 
                'ecarts': {'cm': p.get('cm',0), 'td': p.get('td',0), 'tp': p.get('tp',0)}
            } for p in ues_problemes], indent=2)}
            
            CHARGE ENSEIGNANT (Moyenne: {avg_teacher_load:.1f}h):
            {json.dumps([{
                'nom': t['nom'], 
                'charge': t['equivalent_td'], 
                'progression': (t['realise']['cm']+t['realise']['td']+t['realise']['tp'])/(t['prevu']['cm']+t['prevu']['td']+t['prevu']['tp'])*100 if (t['prevu']['cm']+t['prevu']['td']+t['prevu']['tp']) > 0 else 0
            } for t in enseignants[:5]], indent=2)} (Top 5 vacataires/enseignants)
            
            TACHE:
            Fournis 3 recommandations stratégiques, claires et actionnables pour améliorer la planification.
            Utilise un ton professionnel, encourageant mais direct.
            Structure la réponse avec des titres en gras et des points clés.
            Focalise-toi sur l'optimisation des ressources et la résolution des écarts.
            """
            
            # Add user message to history (invisible in UI context but good for logic)
            st.session_state.messages.append({"role": "user", "content": prompt_content})
            
            with st.chat_message("assistant"):
                try:
                    client = OpenAI(api_key=api_key, base_url=base_url)
                    stream = client.chat.completions.create(
                        model=selected_model,
                        messages=[
                            {"role": "system", "content": "Tu es un assistant expert en pédagogie et gestion de planning universitaire."},
                            {"role": "user", "content": prompt_content}
                        ],
                        stream=True,
                    )
                    response = st.write_stream(stream)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                except Exception as e:
                    # Fallback simulation if API fails (e.g., quota exceeded)
                    st.warning(f"Note: Mode simulation activé (Erreur API: {str(e)})")
                    
                    # Simulated streaming response
                    def simulated_stream():
                        response_text = f"""
                        **Analyse IA (Simulation)**
                        
                        Sur la base des données fournies, voici mes recommandations :
                        
                        1. **Optimisation des Travaux Pratiques (Priorité Haute)**
                        - Le taux de conformité global est de {compliance_rate:.1f}%, mais des écarts subsistent.
                        - Je recommande de réaffecter les heures de TP non réalisées vers les enseignants ayant une charge inférieure à la moyenne ({avg_teacher_load:.1f}h).
                        
                        2. **Rééquilibrage de la Charge Enseignant**
                        - Certains vacataires semblent sous-utilisés.
                        - Il serait judicieux de lisser la charge sur l'ensemble de l'équipe pour éviter les surcharges en fin de semestre.
                        
                        3. **Surveillance des UEs Critiques**
                        - {len(ues_problemes) if ues_problemes else 0} UE(s) présentent des écarts.
                        - Mettez en place un point de contrôle hebdomadaire pour ces modules spécifiques.
                        """
                        for word in response_text.split():
                            yield word + " "
                            time.sleep(0.05)
                            
                    response = st.write_stream(simulated_stream)
                    st.session_state.messages.append({"role": "assistant", "content": response})

# -------------------------
# PDF GENERATION
# -------------------------
def generate_pdf_report(ues_df, enseignants, ues_problemes, stats, ai_response=None):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    
    # Styles
    styles = getSampleStyleSheet()
    style_title = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=rl_colors.HexColor('#2c3e50'),
        alignment=TA_CENTER,
        spaceAfter=30
    )
    style_section = ParagraphStyle(
        'SectionHeader',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=rl_colors.HexColor('#2980b9'),
        spaceBefore=20,
        spaceAfter=10,
        borderColor=rl_colors.HexColor('#e0e0e0'),
        borderWidth=0,
        borderBottomWidth=1
    )
    style_body = styles['BodyText']
    
    elements = []
    
    # --- HEADER with Logo ---
    logo_path = "./assets/logo_thies.png"
    header_data = []
    
    if os.path.exists(logo_path):
        logo = RLImage(logo_path, width=1.2*inch, height=1.2*inch) 
        uni_name = Paragraph("<b>UNIVERSITÉ IBA DER THIAM DE THIÈS</b><br/><font size=12>UFR Sciences et Technologies</font>", styles['Title'])
        header_data = [[logo, uni_name]]
    else:
        uni_name = Paragraph("<b>UNIVERSITÉ IBA DER THIAM DE THIÈS</b>", styles['Title'])
        header_data = [[uni_name]]
        
    header_table = Table(header_data, colWidths=[1.5*inch, 5*inch])
    header_table.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 20))
    
    # --- REPORT TITLE ---
    elements.append(Paragraph("Rapport de Vérification de Planning", style_title))
    elements.append(Paragraph(f"Généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}", styles['Normal']))
    elements.append(Spacer(1, 10))
    elements.append(Paragraph("Ce rapport présente une analyse détaillée de la conformité des maquettes pédagogiques par rapport aux enseignements planifiés.", style_body))
    elements.append(Spacer(1, 20))

    # --- 1. GLOBAL STATISTICS ---
    elements.append(Paragraph("1. Synthèse Globale", style_section))
    
    stat_data = [
        ['Métrique', 'Valeur'],
        ['Taux de Conformité Global', f"{stats['compliance']:.1f}%"],
        ['Total Heures Prévues', f"{stats['total_prevu']:,} h"],
        ['Total Heures Réalisées', f"{stats['total_realise']:,} h"],
        ['Nombre d\'UEs Analysées', f"{len(ues_df)}"],
        ['Nombre de Problèmes Détectés', f"{len(ues_problemes)}"]
    ]
    
    t_stats = Table(stat_data, colWidths=[3.5*inch, 2*inch])
    t_stats.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (1,0), rl_colors.HexColor('#34495e')),
        ('TEXTCOLOR', (0,0), (1,0), rl_colors.white),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,0), 12),
        ('BACKGROUND', (0,1), (-1,-1), rl_colors.HexColor('#f7f9fb')),
        ('GRID', (0,0), (-1,-1), 1, rl_colors.white),
    ]))
    elements.append(t_stats)
    elements.append(Spacer(1, 20))

    # --- 2. CHARTS (Matplotlib) ---
    elements.append(Paragraph("2. Visualisation des Données", style_section))
    
    # Chart 1: Distribution Hours
    plt.figure(figsize=(6, 4))
    types = ['CM', 'TD', 'TP']
    prevu_vals = [ues_df['cm_p'].sum(), ues_df['td_p'].sum(), ues_df['tp_p'].sum()]
    realise_vals = [ues_df['cm_a'].sum(), ues_df['td_a'].sum(), ues_df['tp_a'].sum()]
    
    x = np.arange(len(types))
    width = 0.35
    
    plt.bar(x - width/2, prevu_vals, width, label='Prévu', color='#667eea')
    plt.bar(x + width/2, realise_vals, width, label='Réalisé', color='#764ba2')
    
    plt.ylabel('Heures')
    plt.title('Répartition par Type de Cours')
    plt.xticks(x, types)
    plt.legend()
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    
    img_buffer1 = io.BytesIO()
    plt.savefig(img_buffer1, format='png', dpi=100)
    img_buffer1.seek(0)
    plt.close()
    
    elements.append(RLImage(img_buffer1, width=6*inch, height=4*inch))
    elements.append(Spacer(1, 10))
    elements.append(Paragraph("<i>Figure 1: Comparaison des volumes horaires prévus vs réalisés.</i>", styles['Italic']))
    elements.append(Spacer(1, 20))

    # --- 3. PROBLEM DETAIL ---
    if ues_problemes:
        elements.append(Paragraph(f"3. Liste des Anomalies ({len(ues_problemes)})", style_section))
        elements.append(Paragraph("Les Unités d'Enseignement suivantes présentent des écarts significatifs :", style_body))
        elements.append(Spacer(1, 10))
        
        prob_data = [['UE', 'Écart CM', 'Écart TD', 'Écart TP']]
        for prob in ues_problemes:
            prob_data.append([
                prob.get('ue', 'N/A'),
                f"{prob.get('cm', 0):.1f} h" if prob.get('cm', 0) != 0 else "-",
                f"{prob.get('td', 0):.1f} h" if prob.get('td', 0) != 0 else "-",
                f"{prob.get('tp', 0):.1f} h" if prob.get('tp', 0) != 0 else "-"
            ])
            
        t_probs = Table(prob_data, colWidths=[3*inch, 1.5*inch, 1.5*inch, 1.5*inch])
        t_probs.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), rl_colors.HexColor('#e74c3c')),
            ('TEXTCOLOR', (0,0), (-1,0), rl_colors.white),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [rl_colors.white, rl_colors.HexColor('#ffe6e6')]),
            ('GRID', (0,0), (-1,-1), 1, rl_colors.black),
        ]))
        elements.append(t_probs)
    else:
        elements.append(Paragraph("3. Liste des Anomalies", style_section))
        elements.append(Paragraph("Aucune anomalie détectée. Le planning est parfaitement conforme.", style_body))

    # --- 4. DETAILS TEACHERS ---
    elements.append(Paragraph("4. Statistique des Enseignants", style_section))
    elements.append(Spacer(1, 10))
    
    if enseignants:
        teach_data = [['Enseignant', 'CM (Réal./Prév.)', 'TD (Réal./Prév.)', 'TP (Réal./Prév.)', 'Total Équiv.']]
        for prof in enseignants:
            cm_txt = f"{prof['realise']['cm']:.0f}/{prof['prevu']['cm']:.0f}"
            td_txt = f"{prof['realise']['td']:.0f}/{prof['prevu']['td']:.0f}"
            tp_txt = f"{prof['realise']['tp']:.0f}/{prof['prevu']['tp']:.0f}"
            equiv = f"{prof['equivalent_td']:.1f} h"
            teach_data.append([prof['nom'], cm_txt, td_txt, tp_txt, equiv])
            
        t_teach = Table(teach_data, colWidths=[2.5*inch, 1.3*inch, 1.3*inch, 1.3*inch, 1.1*inch])
        t_teach.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), rl_colors.HexColor('#2c3e50')),
            ('TEXTCOLOR', (0,0), (-1,0), rl_colors.white),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [rl_colors.white, rl_colors.HexColor('#f5f6f7')]),
            ('GRID', (0,0), (-1,-1), 1, rl_colors.HexColor('#bdc3c7')),
            ('ALIGN', (0,1), (0,-1), 'LEFT'), # Teacher names left aligned
        ]))
        elements.append(t_teach)
    else:
        elements.append(Paragraph("Aucune donnée enseignant disponible.", style_body))

    # --- 5. AI RECOMMENDATIONS ---
    if ai_response:
        elements.append(Paragraph("5. Recommandations de l'Assistant IA", style_section))
        elements.append(Spacer(1, 10))
        
        # Simple markdown handling
        lines = ai_response.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                elements.append(Spacer(1, 5))
                continue
            
            if line.startswith('###') or line.startswith('**'):
                p = Paragraph(line.replace('**', '').replace('###', '').strip(), styles['Heading3'])
            elif line.startswith('-') or line.startswith('*'):
                p = Paragraph(f"• {line[1:].strip()}", style_body)
            else:
                p = Paragraph(line, style_body)
            elements.append(p)
            elements.append(Spacer(1, 3))
        
    # Build
    doc.build(elements)
    buffer.seek(0)
    return buffer

# -------------------------
# EXPORT SECTION
# -------------------------
st.markdown("<div class='section-header'><h2 class='section-title'><span class='section-badge'>5</span>⎙ Export & Rapports</h2></div>", unsafe_allow_html=True)

# Generate PDF button
if st.button("↻ Générer le rapport PDF"):
    with st.spinner("Génération du rapport professionnel en cours..."):
        # Calculate stats for the report
        stats = {
            'compliance': compliance_rate,
            'total_prevu': total_prevu,
            'total_realise': total_realise
        }
        
        # Get AI response if available
        ai_content = None
        if "messages" in st.session_state and st.session_state.messages:
            last_msg = st.session_state.messages[-1]
            if last_msg["role"] == "assistant":
                ai_content = last_msg["content"]
        
        pdf_buffer = generate_pdf_report(ues_df, enseignants, ues_problemes, stats, ai_content)
        
        time.sleep(1.5) # Fake loading time for UX
        st.success("ꪜ Rapport généré avec succès!")
        
        st.download_button(
            label="⎙ Télécharger le Rapport Officiel (PDF)",
            data=pdf_buffer,
            file_name=f"Rapport_Verification_Planning_{datetime.now().strftime('%Y%m%d')}.pdf",
            mime="application/pdf",
            type="primary"
        )

# -------------------------
# FOOTER
# -------------------------
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 2rem 0;'>
    <p>🎓 <strong>Dashboard Planning Formation</strong> • Université Iba Der THIAM de Thiès</p>
    <small>Version 2.0 • Dernière mise à jour: {}</small>
</div>
""".format(datetime.now().strftime("%d/%m/%Y")), unsafe_allow_html=True)




