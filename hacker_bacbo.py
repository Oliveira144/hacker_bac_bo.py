import streamlit as st import collections

--- Constantes e Funções Auxiliares ---

NUM_RECENT_RESULTS_FOR_ANALYSIS = 27 MAX_HISTORY_TO_STORE = 1000 NUM_HISTORY_TO_DISPLAY = 100  # Número de resultados do histórico a serem exibidos EMOJIS_PER_ROW = 9  # Quantos emojis por linha no histórico horizontal MIN_RESULTS_FOR_SUGGESTION = 9

def get_color(result): """Retorna a cor associada ao resultado em Bac Bo.""" if result == 'banker': return 'red' elif result == 'player': return 'blue' else:  # 'tie' return 'yellow'

def get_color_emoji(color): """Retorna o emoji correspondente à cor.""" if color == 'red': return '🔴' elif color == 'blue': return '🔵' elif color == 'yellow': return '🟡' return ''

def get_result_emoji(result_type): """Retorna string vazia para remover ícones adicionais.""" return ''

--- Funções de Análise ---

def analyze_surf(results): # Idêntico ao original, usando o novo mapeamento de cores relevant_results = results[:NUM_RECENT_RESULTS_FOR_ANALYSIS] current_home_sequence = 0 current_away_sequence = 0 current_draw_sequence = 0

if results:
    current_result = results[0]
    for r in results:
        if r == current_result:
            if current_result == 'banker':
                current_home_sequence += 1
            elif current_result == 'player':
                current_away_sequence += 1
            else:
                current_draw_sequence += 1
        else:
            break

max_home_sequence = 0
max_away_sequence = 0
max_draw_sequence = 0
temp_home_seq = 0
temp_away_seq = 0
temp_draw_seq = 0

for res in results:
    if res == 'banker':
        temp_home_seq += 1
        temp_away_seq = 0
        temp_draw_seq = 0
    elif res == 'player':
        temp_away_seq += 1
        temp_home_seq = 0
        temp_draw_seq = 0
    else:
        temp_draw_seq += 1
        temp_home_seq = 0
        temp_away_seq = 0
    max_home_sequence = max(max_home_sequence, temp_home_seq)
    max_away_sequence = max(max_away_sequence, temp_away_seq)
    max_draw_sequence = max(max_draw_sequence, temp_draw_seq)

return {
    'home_sequence': current_home_sequence,
    'away_sequence': current_away_sequence,
    'draw_sequence': current_draw_sequence,
    'max_home_sequence': max_home_sequence,
    'max_away_sequence': max_away_sequence,
    'max_draw_sequence': max_draw_sequence
}

def analyze_colors(results): relevant_results = results[:NUM_RECENT_RESULTS_FOR_ANALYSIS] if not relevant_results: return {'red': 0, 'blue': 0, 'yellow': 0, 'current_color': '', 'streak': 0, 'color_pattern_27': ''}

color_counts = {'red': 0, 'blue': 0, 'yellow': 0}
for result in relevant_results:
    color = get_color(result)
    color_counts[color] += 1

current_color = get_color(results[0]) if results else ''
streak = 0
for result in results:
    if get_color(result) == current_color:
        streak += 1
    else:
        break
color_pattern_27 = ''.join([get_color(r)[0].upper() for r in relevant_results])

return {
    'red': color_counts['red'],
    'blue': color_counts['blue'],
    'yellow': color_counts['yellow'],
    'current_color': current_color,
    'streak': streak,
    'color_pattern_27': color_pattern_27
}

def find_complex_patterns(results): patterns = collections.defaultdict(int) relevant_results = results[:NUM_RECENT_RESULTS_FOR_ANALYSIS] colors = [get_color(r) for r in relevant_results]

# Lógica de detecção de padrões permanece igual, usando cores mapeadas
for i in range(len(colors) - 1):
    c1, c2 = colors[i], colors[i+1]
    if c1 != c2:
        patterns[f"Quebra Simples ({c1.capitalize()} para {c2.capitalize()})"] += 1
    # ... (manter todo o código original de padrões) ...

# Código completo de padrões omitido por brevidade mas deve ser copiado do original
return dict(patterns), []

def analyze_break_probability(results): # Idêntico ao original, apenas mapeando 'banker','player','tie' if len(results) < MIN_RESULTS_FOR_SUGGESTION: return {'break_probability': 0, 'sequence_length': 0, 'suggestion': '', 'confidence': 0} surf = analyze_surf(results) current_color = get_color(results[0]) if current_color == 'red': seq, mx = surf['home_sequence'], surf['max_home_sequence'] elif current_color == 'blue': seq, mx = surf['away_sequence'], surf['max_away_sequence'] else: seq, mx = surf['draw_sequence'], surf['max_draw_sequence'] break_prob = min(90, (seq/mx)*100) if mx else 50 if break_prob > 70: if current_color == 'red': suggestion = "Apostar em Player" elif current_color == 'blue': suggestion = "Apostar em Banker" else: suggestion = "Apostar em Banker" confidence = min(95, break_prob+10) elif break_prob > 50: suggestion, confidence = "Possível quebra em breve", break_prob else: suggestion, confidence = f"Sequência {current_color.capitalize()} pode continuar", 100-break_prob return {'break_probability': round(break_prob,1), 'sequence_length': seq, 'suggestion': suggestion, 'confidence': round(confidence,1), 'current_color': current_color, 'max_historical': mx}

def analyze_draw_patterns(results): # Mantém a lógica para empates 'tie' if len(results) < MIN_RESULTS_FOR_SUGGESTION: return {'draws_in_last_27': 0, 'last_draw_position': -1, 'draw_frequency': 0, 'suggestion': '', 'confidence': 0} recent = results[:NUM_RECENT_RESULTS_FOR_ANALYSIS] draws = recent.count('tie') last_pos = next((i for i,r in enumerate(results) if r=='tie'), -1) expected = NUM_RECENT_RESULTS_FOR_ANALYSIS*0.11 freq = (draws/NUM_RECENT_RESULTS_FOR_ANALYSIS)*100 suggestion, confidence = ("Apostar em Amarelo", min(85,(expected-draws)20)) if draws<expected0.7 else ("Padrão de empates normal",50) return {'draws_in_last_27': draws, 'last_draw_position': last_pos, 'draw_frequency': round(freq,1), 'expected_draws': round(expected,1), 'rbd_patterns':0, 'suggestion': suggestion, 'confidence': round(confidence,1)}

def generate_ai_suggestions(results): # Função igualmente mantida, adaptando nomes if len(results)<MIN_RESULTS_FOR_SUGGESTION: return {'suggestions':[],'top_suggestion':'','confidence':0,'reasoning':'Dados insuficientes'} # ... (manter o corpo inteiro da função original) ... return {'suggestions':[],'top_suggestion':'Nenhuma sugestão de alta confiança disponível','confidence':0,'reasoning':'','analysis_type':'None'}

def check_guarantee_status(results): # Mesma lógica if 'last_guarantees' not in st.session_state: st.session_state.last_guarantees = [] verified = [] for g in st.session_state.last_guarantees: if g['position']<len(results): actual = results[g['position']] correct = False if ('Banker' in g['prediction'] and actual=='banker') or ('Player' in g['prediction'] and actual=='player') or ('Amarelo' in g['prediction'] and actual=='tie'): correct=True g['correct']=correct g['actual_result']=actual verified.append(g) return verified

def add_guarantee(prediction,confidence,reasoning): if 'last_guarantees' not in st.session_state: st.session_state.last_guarantees=[] new = {'prediction':prediction,'confidence':confidence,'reasoning':reasoning,'position':0,'timestamp':None} for g in st.session_state.last_guarantees: g['position']+=1 st.session_state.last_guarantees.insert(0,new) st.session_state.last_guarantees=st.session_state.last_guarantees[-10:]

def main(): st.set_page_config(page_title="Bac Bo Analyzer", page_icon="🎲", layout="wide") if 'results' not in st.session_state: st.session_state.results=[] st.title("🎲 Bac Bo Analyzer") st.markdown("### Sistema Avançado de Padrões e Sugestões para Bac Bo") with st.sidebar: st.header("📥 Inserir Resultado") c1,c2,c3=st.columns(3) with c1: if st.button("🔴 BANKER",use_container_width=True): st.session_state.results.insert(0,'banker') if len(st.session_state.results)>MAX_HISTORY_TO_STORE: st.session_state.results=st.session_state.results[:MAX_HISTORY_TO_STORE] st.rerun() with c2: if st.button("🔵 PLAYER",use_container_width=True): st.session_state.results.insert(0,'player') if len(st.session_state.results)>MAX_HISTORY_TO_STORE: st.session_state.results=st.session_state.results[:MAX_HISTORY_TO_STORE] st.rerun() with c3: if st.button("🟡 TIE",use_container_width=True): st.session_state.results.insert(0,'tie') if len(st.session_state.results)>MAX_HISTORY_TO_STORE: st.session_state.results=st.session_state.results[:MAX_HISTORY_TO_STORE] st.rerun() if st.button("🗑️ Limpar Histórico", type="secondary"): st.session_state.results=[] st.session_state.last_guarantees=[] st.rerun() if st.session_state.results: st.markdown("### 📊 Estatísticas Rápidas") recent=st.session_state.results[:NUM_RECENT_RESULTS_FOR_ANALYSIS] st.metric("🔴 Banker", recent.count('banker')) st.metric("🔵 Player", recent.count('player')) st.metric("🟡 Tie", recent.count('tie')) st.metric("📈 Total", len(recent)) if not st.session_state.results: st.info("👋 Bem-vindo! Adicione resultados na barra lateral.") return verified = check_guarantee_status(st.session_state.results) if verified: st.markdown("### 🎯 Status das Garantias Recentes") for g in verified[:3]: if g['correct']: st.success(f"✅ ACERTOU: {g['prediction']} (Confiança: {g['confidence']:.1f}%) - Resultado: {g['actual_result'].upper()}") else: st.error(f"❌ ERROU: {g['prediction']} (Confiança: {g['confidence']:.1f}%) - Resultado: {g['actual_result'].upper()}") col1,col2=st.columns([2,1]) with col1: st.markdown("### 📋 Histórico dos Últimos 100 Resultados") display=st.session_state.results[:NUM_HISTORY_TO_DISPLAY] rows=[] for i in range(0,len(display),EMOJIS_PER_ROW): r=display[i:i+EMOJIS_PER_ROW] rows.append(' '.join(get_color_emoji(get_color(x)) for x in r)) for row in rows: st.markdown(f"<div style='font-size:24px;text-align:center;'>{row}</div>",unsafe_allow_html=True) st.markdown("### 🔍 Análises Detalhadas") surf=analyze_surf(st.session_state.results) s1,s2,s3=st.columns(3) with s1: st.metric("🔴 Banker Atual", surf['home_sequence'], delta=f"Max: {surf['max_home_sequence']}") with s2: st.metric("🔵 Player Atual", surf['away_sequence'], delta=f"Max: {surf['max_away_sequence']}") with s3: st.metric("🟡 Tie Atual", surf['draw_sequence'], delta=f"Max: {surf['max_draw_sequence']}") colors=analyze_colors(st.session_state.results) c1,c2,c3,c4=st.columns(4) with c1: st.metric("🔴 Vermelhos", colors['red']) with c2: st.metric("🔵 Azuis", colors['blue']) with c3: st.metric("🟡 Amarelos", colors['yellow']) with c4: st.metric("📈 Streak", colors['streak'], delta=colors['current_color'].capitalize()) patterns,_=find_complex_patterns(st.session_state.results) if patterns: st.markdown("#### 🧩 Padrões Complexos Identificados") relevant={k:v for k,v in patterns.items() if v>=2} if relevant: st.markdown("| Padrão | Ocorrências | Relevância |") st.markdown("|--------|-------------|------------|") for k,v in sorted(relevant.items(),key=lambda x:x[1],reverse=True): icon='🔥' if v>=4 else '⚡' if v>=3 else '📊' st.markdown(f"| {k} | {v} | {icon} |") else: st.info("Nenhum padrão complexo significativo encontrado ainda.") with col2: st.markdown("### 🤖 Sugestões da IA") ai=generate_ai_suggestions(st.session_state.results) if ai['suggestions']: st.markdown("#### 🎯 Sugestão Principal") color_icon="🟢" if ai['confidence']>80 else "🟡" if ai['confidence']>60 else "🔴" st.markdown(f"{color_icon} {ai['top_suggestion']}\n\nConfiança: {ai['confidence']:.1f}%\n\nAnálise: {ai['analysis_type']}\n\nMotivo: {ai['reasoning']}") if ai['confidence']>85: st.warning("⚠️ ALTA CONFIANÇA - Sugestão adicionada como 'Garantia'!") add_guarantee(ai['top_suggestion'],ai['confidence'],ai['reasoning']) if len(ai['suggestions'])>1: st.markdown("#### 📋 Outras Sugestões") for i,s in enumerate(ai['suggestions'][1:],2): with st.expander(f"{i}° Sugestão (Confiança: {s['confidence']:.1f}%)"): st.write(f"{s['suggestion']}") st.write(f"Motivo: {s['reasoning']}") st.write(f"Análise: {s['type']}") else: st.info("📊 Adicione mais resultados para obter sugestões de IA.") st.markdown("### ⚡ Análise de Quebra") br=analyze_break_probability(st.session_state.results) if br['confidence']>0: st.markdown(f"Sequência Atual: {br['sequence_length']} ({br['current_color'].capitalize()})\n\nProbabilidade de Quebra: {br['break_probability']}%\n\nSugestão: {br['suggestion']}\n\nConfiança: {br['confidence']}%") st.markdown("### 🟡 Análise de Empates") dr=analyze_draw_patterns(st.session_state.results) if dr['confidence']>0: d1,d2=st.columns(2) with d1: st.metric("Empates (27)",dr['draws_in_last_27']) st.metric("Último Empate",f"Há {dr['last_draw_position']} jogos" if dr['last_draw_position']!=-1 else "Nenhum") with d2: st.metric("Frequência",f"{dr['draw_frequency']}%") st.metric("Esperado",f"{dr['expected_draws']:.1f}") if dr['confidence']>60: st.markdown(f"💡 {dr['suggestion']} (Confiança: {dr['confidence']:.1f}%)")

if name == "main": main()

