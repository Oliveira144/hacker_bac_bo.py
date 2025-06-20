import streamlit as st
import pandas as pd
import collections
import time # Para simular um atraso na entrada de dados, se necessário

# --- Constantes e Funções Auxiliares ---
NUM_RECENT_RESULTS_FOR_ANALYSIS = 27
MAX_HISTORY_TO_STORE = 1000
NUM_HISTORY_TO_DISPLAY = 100

# Cores e Emojis (mantido o padrão)
def get_color(result):
    if result == 'home': return 'red'
    elif result == 'away': return 'blue'
    else: return 'yellow'

def get_color_emoji(color):
    if color == 'red': return '🔴'
    elif color == 'blue': return '🔵'
    elif color == 'yellow': return '🟡'
    return ''

# --- Funções de Análise (Mantidas, mas adaptadas para as novas features) ---

# As funções analyze_surf, analyze_colors, find_break_patterns, analyze_break_probability, analyze_draw_specifics
# permanecem as mesmas em sua lógica interna, pois elas apenas extraem dados.
# A inteligência de "IA" será aplicada na generate_advanced_suggestion e no gerenciamento de estado.

def analyze_surf(results):
    relevant_results = results[:NUM_RECENT_RESULTS_FOR_ANALYSIS]
    if not relevant_results:
        return {'home_sequence': 0, 'away_sequence': 0, 'draw_sequence': 0,
                'max_home_sequence': 0, 'max_away_sequence': 0, 'max_draw_sequence': 0}
    
    max_home_sequence = 0
    max_away_sequence = 0
    max_draw_sequence = 0
    temp_home_seq = 0
    temp_away_seq = 0
    temp_draw_seq = 0

    for i in range(len(relevant_results)):
        result = relevant_results[i]
        if result == 'home':
            temp_home_seq += 1; temp_away_seq = 0; temp_draw_seq = 0
        elif result == 'away':
            temp_away_seq += 1; temp_home_seq = 0; temp_draw_seq = 0
        else: # draw
            temp_draw_seq += 1; temp_home_seq = 0; temp_away_seq = 0
        max_home_sequence = max(max_home_sequence, temp_home_seq)
        max_away_sequence = max(max_away_sequence, temp_away_seq)
        max_draw_sequence = max(max_draw_sequence, temp_draw_seq)

    actual_current_home_sequence = 0
    actual_current_away_sequence = 0
    actual_current_draw_sequence = 0
    if relevant_results:
        first_result = relevant_results[0]
        for r in relevant_results:
            if r == first_result:
                if first_result == 'home': actual_current_home_sequence += 1
                elif first_result == 'away': actual_current_away_sequence += 1
                else: actual_current_draw_sequence += 1
            else: break
    return {
        'home_sequence': actual_current_home_sequence, 'away_sequence': actual_current_away_sequence,
        'draw_sequence': actual_current_draw_sequence, 'max_home_sequence': max_home_sequence,
        'max_away_sequence': max_away_sequence, 'max_draw_sequence': max_draw_sequence
    }

def analyze_colors(results):
    relevant_results = results[:NUM_RECENT_RESULTS_FOR_ANALYSIS]
    if not relevant_results:
        return {'red': 0, 'blue': 0, 'yellow': 0, 'current_color': '', 'streak': 0, 'color_pattern_27': ''}
    color_counts = {'red': 0, 'blue': 0, 'yellow': 0}
    for result in relevant_results:
        color = get_color(result)
        color_counts[color] += 1
    current_color = get_color(results[0])
    streak = 0
    for result in results: 
        if get_color(result) == current_color: streak += 1
        else: break
    color_pattern_27 = ''.join([get_color(r)[0].upper() for r in relevant_results])
    return {
        'red': color_counts['red'], 'blue': color_counts['blue'], 'yellow': color_counts['yellow'],
        'current_color': current_color, 'streak': streak, 'color_pattern_27': color_pattern_27
    }

def find_break_patterns(results):
    patterns = collections.defaultdict(int)
    relevant_results = results[:NUM_RECENT_RESULTS_FOR_ANALYSIS]
    for i in range(len(relevant_results) - 1):
        color1 = get_color(relevant_results[i])
        color2 = get_color(relevant_results[i+1])
        if color1 != color2: patterns["Quebra Simples"] += 1
        if i < len(relevant_results) - 2:
            color3 = get_color(relevant_results[i+2])
            if color1 == color2 and color1 != color3: patterns[f"2x1 ({color1.capitalize()} {get_color_emoji(color1)} {color3.capitalize()}{get_color_emoji(color3)})"] += 1
        if i < len(relevant_results) - 3:
            color3 = get_color(relevant_results[i+2])
            color4 = get_color(relevant_results[i+3])
            if color1 == color2 and color2 == color3 and color1 != color4: patterns[f"3x1 ({color1.capitalize()} {get_color_emoji(color1)} {color4.capitalize()}{get_color_emoji(color4)})"] += 1
        if i < len(relevant_results) - 3:
            color3 = get_color(relevant_results[i+2])
            color4 = get_color(relevant_results[i+3])
            if color1 == color2 and color3 == color4 and color1 != color3: patterns[f"2x2 ({color1.capitalize()} {get_color_emoji(color1)} {color3.capitalize()}{get_color_emoji(color3)})"] += 1
            if color1 != color2 and color2 != color3 and color3 != color4 and color1 == color3 and color2 == color4: patterns[f"Padrão Alternado ({color1.capitalize()}{get_color_emoji(color1)}-{color2.capitalize()}{get_color_emoji(color2)}-...)"] += 1
        if i < len(relevant_results) - 5:
            color3 = get_color(relevant_results[i+2]); color4 = get_color(relevant_results[i+3])
            color5 = get_color(relevant_results[i+4]); color6 = get_color(relevant_results[i+5])
            if color1 == color2 and color2 == color3 and color4 == color5 and color5 == color6 and color1 != color4: patterns[f"3x3 ({color1.capitalize()} {get_color_emoji(color1)} {color4.capitalize()}{get_color_emoji(color4)})"] += 1
    for i in range(len(relevant_results) - 1):
        color1 = get_color(relevant_results[i]); color2 = get_color(relevant_results[i+1])
        if color2 == 'yellow' and color1 != 'yellow': patterns[f"X Y Draw ({color1.capitalize()}{get_color_emoji(color1)} {color2.capitalize()}{get_color_emoji(color2)})"] += 1
        if i < len(relevant_results) - 2:
            color3 = get_color(relevant_results[i+2])
            if color1 == 'yellow' and color2 != 'yellow' and color3 != 'yellow' and color2 != color3: patterns[f"Draw X Y ({color1.capitalize()}{get_color_emoji(color1)} {color2.capitalize()}{get_color_emoji(color2)} {color3.capitalize()}{get_color_emoji(color3)})"] += 1
    return dict(patterns)

def analyze_break_probability(results):
    relevant_results = results[:NUM_RECENT_RESULTS_FOR_ANALYSIS]
    if not relevant_results or len(relevant_results) < 2: return {'break_chance': 0, 'last_break_type': ''}
    breaks = 0; total_sequences_considered = 0
    for i in range(len(relevant_results) - 1):
        if get_color(relevant_results[i]) != get_color(relevant_results[i+1]): breaks += 1
        total_sequences_considered += 1
    break_chance = (breaks / total_sequences_considered) * 100 if total_sequences_considered > 0 else 0
    last_break_type = ""
    if len(results) >= 2 and get_color(results[0]) != get_color(results[1]):
        last_break_type = f"Quebrou de {get_color(results[1]).capitalize()} {get_color_emoji(get_color(results[1]))} para {get_color(results[0]).capitalize()} {get_color_emoji(get_color(results[0]))}"
    return {'break_chance': round(break_chance, 2), 'last_break_type': last_break_type}

def analyze_draw_specifics(results):
    relevant_results = results[:NUM_RECENT_RESULTS_FOR_ANALYSIS]
    if not relevant_results:
        return {'draw_frequency_27': 0, 'time_since_last_draw': -1, 'draw_patterns': {}}
    draw_count_27 = relevant_results.count('draw')
    draw_frequency_27 = (draw_count_27 / len(relevant_results)) * 100 if len(relevant_results) > 0 else 0
    time_since_last_draw = -1
    for i, result in enumerate(results): 
        if result == 'draw': time_since_last_draw = i; break
    draw_patterns_found = collections.defaultdict(int)
    for i in range(len(relevant_results) - 1):
        color1 = get_color(relevant_results[i]); color2 = get_color(relevant_results[i+1])
        if color2 == 'yellow' and color1 != 'yellow': draw_patterns_found[f"Quebra para Empate ({color1.capitalize()}{get_color_emoji(color1)} para Empate{get_color_emoji('yellow')})"] += 1
        if i < len(relevant_results) - 2:
            color3 = get_color(relevant_results[i+2])
            if color3 == 'yellow':
                if color1 == 'red' and color2 == 'blue': draw_patterns_found["Red-Blue-Draw (🔴🔵🟡)"] += 1
                elif color1 == 'blue' and color2 == 'red': draw_patterns_found["Blue-Red-Draw (🔵🔴🟡)"] += 1
    return {
        'draw_frequency_27': round(draw_frequency_27, 2), 'time_since_last_draw': time_since_last_draw,
        'draw_patterns': dict(draw_patterns_found)
    }

# --- Função de Sugestão com "IA" Simulada ---

def generate_advanced_suggestion(results, surf_analysis, color_analysis, break_probability, break_patterns, draw_specifics, pattern_performance):
    """Gera uma sugestão de aposta baseada em múltiplas análises, com ajuste de confiança por performance de padrão."""
    if not results or len(results) < 5: 
        return {'suggestion': 'Aguardando mais resultados para análise detalhada.', 'confidence': 0, 'reason': '', 'guarantee_pattern': 'N/A'}

    last_result_color = color_analysis['current_color']
    current_streak = color_analysis['streak']
    
    suggestion = "Manter observação"
    confidence = 50
    reason = "Análise preliminar."
    guarantee_pattern = "N/A"

    # Função auxiliar para ajustar a confiança com base no desempenho do padrão
    def adjust_confidence_by_performance(base_confidence, pattern_name):
        if pattern_name in pattern_performance:
            performance = pattern_performance[pattern_name]
            # Uma pontuação de confiabilidade simples: (sucessos + 1) / (sucessos + falhas + 2)
            # Adiciona 1/2 para evitar divisão por zero ou muito baixa em início
            reliability = (performance['successes'] + 1) / (performance['successes'] + performance['failures'] + 2)
            
            # Ajusta a confiança baseada na confiabilidade (ex: max de 100%, min de 20%)
            adjusted_confidence = base_confidence * reliability * 1.2 # Multiplicador para não cair tão rápido
            return min(95, max(20, int(adjusted_confidence))) # Garante que fique entre 20 e 95
        return base_confidence

    # Lógica de Sugestão Aprimorada com Ajuste de Confiança
    
    # 1. Sugestão baseada em Sequência Longa e Máximo Histórico de Surf
    if last_result_color == 'red' and current_streak >= surf_analysis['max_home_sequence'] and surf_analysis['max_home_sequence'] > 0 and current_streak >= 3:
        pattern_name = f"Surf Max Quebra: {last_result_color.capitalize()}"
        confidence = adjust_confidence_by_performance(95, pattern_name)
        suggestion = f"APOSTA FORTE em **VISITANTE** {get_color_emoji('blue')}"
        reason = f"Sequência atual de Vermelho ({current_streak}x) atingiu ou superou o máximo histórico de surf. Grande chance de quebra."
        guarantee_pattern = pattern_name
        return {'suggestion': suggestion, 'confidence': confidence, 'reason': reason, 'guarantee_pattern': guarantee_pattern}
    elif last_result_color == 'blue' and current_streak >= surf_analysis['max_away_sequence'] and surf_analysis['max_away_sequence'] > 0 and current_streak >= 3:
        pattern_name = f"Surf Max Quebra: {last_result_color.capitalize()}"
        confidence = adjust_confidence_by_performance(95, pattern_name)
        suggestion = f"APOSTA FORTE em **CASA** {get_color_emoji('red')}"
        reason = f"Sequência atual de Azul ({current_streak}x) atingiu ou superou o máximo histórico de surf. Grande chance de quebra."
        guarantee_pattern = pattern_name
        return {'suggestion': suggestion, 'confidence': confidence, 'reason': reason, 'guarantee_pattern': guarantee_pattern}
    elif last_result_color == 'yellow' and current_streak >= surf_analysis['max_draw_sequence'] and surf_analysis['max_draw_sequence'] > 0 and current_streak >= 2:
        pattern_name = f"Surf Max Quebra: {last_result_color.capitalize()}"
        confidence = adjust_confidence_by_performance(90, pattern_name)
        suggestion = f"APOSTA FORTE em **CASA** {get_color_emoji('red')} ou **VISITANTE** {get_color_emoji('blue')}"
        reason = f"Sequência atual de Empate ({current_streak}x) atingiu ou superou o máximo histórico de surf. Grande chance de retorno às cores principais."
        guarantee_pattern = pattern_name
        return {'suggestion': suggestion, 'confidence': confidence, 'reason': reason, 'guarantee_pattern': guarantee_pattern}


    # 2. Sugestão baseada em padrões recorrentes de quebra (2x1, 3x1)
    for pattern, count in break_patterns.items():
        if count >= 3: 
            if "2x1 (Red 🔴 Blue 🔵)" in pattern and last_result_color == 'red' and current_streak == 2:
                confidence = adjust_confidence_by_performance(88, pattern)
                suggestion = f"Apostar em **VISITANTE** {get_color_emoji('blue')}"
                reason = f"Padrão 2x1 (🔴🔴🔵) altamente recorrente ({count}x). Espera-se a quebra para azul."
                guarantee_pattern = pattern
                return {'suggestion': suggestion, 'confidence': confidence, 'reason': reason, 'guarantee_pattern': guarantee_pattern}
            elif "2x1 (Blue 🔵 Red 🔴)" in pattern and last_result_color == 'blue' and current_streak == 2:
                confidence = adjust_confidence_by_performance(88, pattern)
                suggestion = f"Apostar em **CASA** {get_color_emoji('red')}"
                reason = f"Padrão 2x1 (🔵🔵🔴) altamente recorrente ({count}x). Espera-se a quebra para vermelho."
                guarantee_pattern = pattern
                return {'suggestion': suggestion, 'confidence': confidence, 'reason': reason, 'guarantee_pattern': guarantee_pattern}
            
            elif "3x1 (Red 🔴 Blue 🔵)" in pattern and last_result_color == 'red' and current_streak == 3:
                confidence = adjust_confidence_by_performance(92, pattern)
                suggestion = f"Apostar em **VISITANTE** {get_color_emoji('blue')}"
                reason = f"Padrão 3x1 (🔴🔴🔴🔵) altamente recorrente ({count}x). Espera-se a quebra para azul."
                guarantee_pattern = pattern
                return {'suggestion': suggestion, 'confidence': confidence, 'reason': reason, 'guarantee_pattern': guarantee_pattern}
            elif "3x1 (Blue 🔵 Red 🔴)" in pattern and last_result_color == 'blue' and current_streak == 3:
                confidence = adjust_confidence_by_performance(92, pattern)
                suggestion = f"Apostar em **CASA** {get_color_emoji('red')}"
                reason = f"Padrão 3x1 (🔵🔵🔵🔴) altamente recorrente ({count}x). Espera-se a quebra para vermelho."
                guarantee_pattern = pattern
                return {'suggestion': suggestion, 'confidence': confidence, 'reason': reason, 'guarantee_pattern': guarantee_pattern}


    # 3. Sugestão de Empate (maior assertividade)
    # Se o tempo desde o último empate for alto E a frequência de empates for baixa OU houver padrão de empate claro
    if draw_specifics['time_since_last_draw'] >= 7 and draw_specifics['draw_frequency_27'] < 12: 
        pattern_name = "Empate Atrasado/Baixa Frequência"
        confidence = adjust_confidence_by_performance(78, pattern_name)
        suggestion = f"Considerar **EMPATE** {get_color_emoji('yellow')}"
        reason = f"Empate não ocorre há {draw_specifics['time_since_last_draw']} rodadas e frequência baixa ({draw_specifics['draw_frequency_27']}% nos últimos 27)."
        guarantee_pattern = pattern_name
        
        # Reforço com padrões de empate
        if "Red-Blue-Draw (🔴🔵🟡)" in draw_specifics['draw_patterns'] and len(results) >= 2 and results[0] == 'away' and results[1] == 'home':
            confidence = adjust_confidence_by_performance(confidence + 10, pattern_name + " + Padrão 🔴🔵🟡") # Aumenta confiança
            suggestion += f" - Reforçado por padrão 🔴🔵🟡."
            guarantee_pattern += " + Padrão 🔴🔵🟡"
        elif "Blue-Red-Draw (🔵🔴🟡)" in draw_specifics['draw_patterns'] and len(results) >= 2 and results[0] == 'home' and results[1] == 'away':
            confidence = adjust_confidence_by_performance(confidence + 10, pattern_name + " + Padrão 🔵🔴🟡")
            suggestion += f" - Reforçado por padrão 🔵🔴🟡."
            guarantee_pattern += " + Padrão 🔵🔴🟡"
        
        return {'suggestion': suggestion, 'confidence': confidence, 'reason': reason, 'guarantee_pattern': guarantee_pattern}
    
    # Se os últimos 2 foram alternados (R-B ou B-R) e não houve empate em X rodadas
    if len(results) >= 2 and ( (get_color(results[0]) == 'red' and get_color(results[1]) == 'blue') or \
                               (get_color(results[0]) == 'blue' and get_color(results[1]) == 'red') ):
        if draw_specifics['time_since_last_draw'] >= 3:
            pattern_name = "Alternância para Empate"
            confidence = adjust_confidence_by_performance(75, pattern_name)
            suggestion = f"Considerar **EMPATE** {get_color_emoji('yellow')}"
            reason = "Resultados alternados (🔴🔵 ou 🔵🔴) podem preceder um empate. Empate atrasado."
            guarantee_pattern = pattern_name
            return {'suggestion': suggestion, 'confidence': confidence, 'reason': reason, 'guarantee_pattern': guarantee_pattern}


    # 4. Outras Sugestões (se as acima não se aplicarem com alta confiança)
    if break_probability['break_chance'] > 65 and current_streak < 3: 
        if len(results) >= 2:
            prev_color = get_color(results[1])
            pattern_name = "Alta Probabilidade de Quebra Geral"
            confidence = adjust_confidence_by_performance(70, pattern_name)
            if prev_color == 'red':
                suggestion = f"Apostar em **VISITANTE** {get_color_emoji('blue')}"
                reason = f"Alta chance de quebra ({break_probability['break_chance']}%). Prever quebra de sequência de {prev_color.capitalize()}."
            elif prev_color == 'blue':
                suggestion = f"Apostar em **CASA** {get_color_emoji('red')}"
                reason = f"Alta chance de quebra ({break_probability['break_chance']}%). Prever quebra de sequência de {prev_color.capitalize()}."
            return {'suggestion': suggestion, 'confidence': confidence, 'reason': reason, 'guarantee_pattern': guarantee_pattern}


    # 5. Default/Manter Observação (se nenhum padrão forte de "garantia" for encontrado)
    suggestion = "Manter observação."
    confidence = 50
    reason = "Nenhum padrão de 'garantia' forte detectado nos últimos 27 resultados para uma aposta segura no momento."
    guarantee_pattern = "Nenhum Padrão Forte"

    return {
        'suggestion': suggestion, 
        'confidence': round(confidence), 
        'reason': reason,
        'guarantee_pattern': guarantee_pattern
    }

def update_analysis(results, pattern_performance):
    """Coordena todas as análises e retorna os resultados consolidados, focando nos últimos N."""
    relevant_results_for_analysis = results[:NUM_RECENT_RESULTS_FOR_ANALYSIS]

    if not relevant_results_for_analysis:
        return {
            'stats': {'home': 0, 'away': 0, 'draw': 0, 'total': 0},
            'surf_analysis': analyze_surf([]),
            'color_analysis': analyze_colors([]),
            'break_patterns': find_break_patterns([]),
            'break_probability': analyze_break_probability([]),
            'draw_specifics': analyze_draw_specifics([]),
            'suggestion': {'suggestion': 'Aguardando resultados para análise.', 'confidence': 0, 'reason': '', 'guarantee_pattern': 'N/A'}
        }

    stats = {'home': relevant_results_for_analysis.count('home'), 
             'away': relevant_results_for_analysis.count('away'), 
             'draw': relevant_results_for_analysis.count('draw'), 
             'total': len(relevant_results_for_analysis)}
    
    surf_analysis = analyze_surf(results) 
    color_analysis = analyze_colors(results)
    break_patterns = find_break_patterns(results)
    break_probability = analyze_break_probability(results)
    draw_specifics = analyze_draw_specifics(results) 

    suggestion_data = generate_advanced_suggestion(results, surf_analysis, color_analysis, break_probability, break_patterns, draw_specifics, pattern_performance)
    
    return {
        'stats': stats,
        'surf_analysis': surf_analysis,
        'color_analysis': color_analysis,
        'break_patterns': break_patterns,
        'break_probability': break_probability,
        'draw_specifics': draw_specifics, 
        'suggestion': suggestion_data
    }

# --- Streamlit UI ---

st.set_page_config(layout="wide", page_title="Football Studio Pro Analyzer (AI Sim.)")

st.title("⚽ Football Studio Pro Analyzer (IA Sim. Adaptativa)")
st.write("Sistema Avançado de Análise e Predição com Adaptação de Padrões")

# --- Gerenciamento de Estado ---
if 'results' not in st.session_state:
    st.session_state.results = []
if 'last_suggested_bet_info' not in st.session_state: # Armazena a sugestão completa da rodada anterior
    st.session_state.last_suggested_bet_info = None
if 'guarantee_failed_streak' not in st.session_state: # Contador de falhas consecutivas de garantia
    st.session_state.guarantee_failed_streak = 0
if 'pattern_performance' not in st.session_state:
    st.session_state.pattern_performance = {} # {'Pattern Name': {'successes': 0, 'failures': 0}}

# A análise é feita sempre com base no estado atual dos resultados e da performance dos padrões
# Inicializa analysis_data com a função update_analysis
if 'analysis_data' not in st.session_state:
    st.session_state.analysis_data = update_analysis(st.session_state.results, st.session_state.pattern_performance)


# --- Função para Adicionar Resultado ---
def add_result(result):
    # Lógica de atualização de desempenho do padrão ANTES de adicionar o novo resultado
    # (Referente à sugestão feita na rodada ANTERIOR)
    if st.session_state.last_suggested_bet_info:
        last_suggestion = st.session_state.last_suggested_bet_info
        suggested_outcome = None # 'home', 'away', or 'draw' based on last_suggestion['suggestion']

        if "CASA" in last_suggestion['suggestion']:
            suggested_outcome = 'home'
        elif "VISITANTE" in last_suggestion['suggestion']:
            suggested_outcome = 'away'
        elif "EMPATE" in last_suggestion['suggestion']:
            suggested_outcome = 'draw'

        # Se houve uma sugestão de alta confiança na rodada anterior
        if suggested_outcome and last_suggestion['confidence'] >= 70 and last_suggestion['guarantee_pattern'] != 'Nenhum Padrão Forte':
            actual_color = get_color(result)
            suggested_color = get_color(suggested_outcome)
            
            pattern_name = last_suggestion['guarantee_pattern']
            if pattern_name not in st.session_state.pattern_performance:
                st.session_state.pattern_performance[pattern_name] = {'successes': 0, 'failures': 0}

            if actual_color == suggested_color:
                st.session_state.pattern_performance[pattern_name]['successes'] += 1
                st.session_state.guarantee_failed_streak = 0 # Resetar streak de falha
            else:
                st.session_state.pattern_performance[pattern_name]['failures'] += 1
                st.session_state.guarantee_failed_streak += 1 # Incrementar streak de falha
                st.warning(f"🚨 **ALERTA: A GARANTIA DO PADRÃO '{pattern_name}' FALHOU!**")
                
        else: # Se a aposta anterior não era de alta confiança ou não tinha padrão de garantia, reseta a streak de falha
            st.session_state.guarantee_failed_streak = 0

    # Adiciona o novo resultado
    st.session_state.results.insert(0, result) 
    st.session_state.results = st.session_state.results[:MAX_HISTORY_TO_STORE] 
    
    # Atualiza todas as análises e a nova sugestão para a PRÓXIMA rodada
    st.session_state.analysis_data = update_analysis(st.session_state.results, st.session_state.pattern_performance)
    
    # Armazena a sugestão gerada AGORA (para ser avaliada na PRÓXIMA adição de resultado)
    st.session_state.last_suggested_bet_info = st.session_state.analysis_data['suggestion']
    
# --- Função para Limpar Histórico ---
def clear_history():
    st.session_state.results = []
    st.session_state.analysis_data = update_analysis([], {}) # Recalcula análise do zero
    st.session_state.last_suggested_bet_info = None
    st.session_state.guarantee_failed_streak = 0
    st.session_state.pattern_performance = {} # Zera o desempenho dos padrões também
    st.experimental_rerun() 

# --- Layout ---
st.header("Registrar Resultado")
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("CASA 🔴", use_container_width=True):
        add_result('home')
with col2:
    if st.button("VISITANTE 🔵", use_container_width=True):
        add_result('away')
with col3:
    if st.button("EMPATE 🟡", use_container_width=True):
        add_result('draw')

st.markdown("---")

# --- Exibir Alerta de Garantia ---
if st.session_state.guarantee_failed_streak > 0:
    st.error(f"🚨 **ALERTA DE FAIXA DE FALHA!** A garantia falhou **{st.session_state.guarantee_failed_streak}** vez(es) consecutiva(s). Considere cautela ou reanalisar. A IA está ajustando a confiança dos padrões.")

st.header("Análise IA e Sugestão")
if st.session_state.results:
    suggestion = st.session_state.analysis_data['suggestion']
    
    st.info(f"**Sugestão:** {suggestion['suggestion']}")
    st.metric(label="Confiança", value=f"{suggestion['confidence']}%")
    st.write(f"**Motivo:** {suggestion['reason']}")
    st.write(f"**Padrão de Garantia da Sugestão:** `{suggestion['guarantee_pattern']}`")
else:
    st.info("Aguardando resultados para gerar análises e sugestões.")

st.markdown("---")

# --- Estatísticas e Padrões (Últimos 27 Resultados) ---
st.header(f"Estatísticas e Padrões (Últimos {NUM_RECENT_RESULTS_FOR_ANALYSIS} Resultados)")

stats_col, color_col = st.columns(2)

with stats_col:
    st.subheader("Estatísticas Gerais")
    stats = st.session_state.analysis_data['stats']
    st.write(f"**Casa {get_color_emoji('red')}:** {stats['home']} vezes")
    st.write(f"**Visitante {get_color_emoji('blue')}:** {stats['away']} vezes")
    st.write(f"**Empate {get_color_emoji('yellow')}:** {stats['draw']} vezes")
    st.write(f"**Total de Resultados Analisados:** {stats['total']}")

with color_col:
    st.subheader("Análise de Cores")
    colors = st.session_state.analysis_data['color_analysis']
    st.write(f"**Vermelho:** {colors['red']}x")
    st.write(f"**Azul:** {colors['blue']}x")
    st.write(f"**Amarelo:** {colors['yellow']}x")
    st.write(f"**Sequência Atual:** {colors['streak']}x {colors['current_color'].capitalize()} {get_color_emoji(colors['current_color'])}")
    st.markdown(f"**Padrão (Últimos {NUM_RECENT_RESULTS_FOR_ANALYSIS}):** `{colors['color_pattern_27']}`")

st.markdown("---")

# --- Análise de Quebra, Surf e Empate ---
col_break, col_surf, col_draw_analysis = st.columns(3)

with col_break:
    st.subheader("Análise de Quebra")
    bp = st.session_state.analysis_data['break_probability']
    st.write(f"**Chance de Quebra:** {bp['break_chance']}%")
    st.write(f"**Último Tipo de Quebra:** {bp['last_break_type'] if bp['last_break_type'] else 'N/A'}")
    
    st.subheader("Padrões de Quebra e Específicos")
    patterns = st.session_state.analysis_data['break_patterns']
    if patterns:
        for pattern, count in patterns.items():
            st.write(f"- {pattern}: {count}x")
    else:
        st.write("Nenhum padrão identificado nos últimos 27 resultados.")

with col_surf:
    st.subheader("Análise de Surf")
    surf = st.session_state.analysis_data['surf_analysis']
    st.write(f"**Seq. Atual Casa {get_color_emoji('red')}:** {surf['home_sequence']}x")
    st.write(f"**Seq. Atual Visitante {get_color_emoji('blue')}:** {surf['away_sequence']}x")
    st.write(f"**Seq. Atual Empate {get_color_emoji('yellow')}:** {surf['draw_sequence']}x")
    st.write(f"---")
    st.write(f"**Máx. Seq. Casa:** {surf['max_home_sequence']}x")
    st.write(f"**Máx. Seq. Visitante:** {surf['max_away_sequence']}x")
    st.write(f"**Máx. Seq. Empate:** {surf['max_draw_sequence']}x")

with col_draw_analysis:
    st.subheader("Análise Detalhada de Empates")
    draw_data = st.session_state.analysis_data['draw_specifics']
    st.write(f"**Frequência Empate ({NUM_RECENT_RESULTS_FOR_ANALYSIS}):** {draw_data['draw_frequency_27']}%")
    st.write(f"**Rodadas sem Empate:** {draw_data['time_since_last_draw']} (Desde o último empate)")
    
    st.subheader("Padrões de Empate Históricos")
    if draw_data['draw_patterns']:
        for pattern, count in draw_data['draw_patterns'].items():
            st.write(f"- {pattern}: {count}x")
    else:
        st.write("Nenhum padrão de empate identificado ainda.")

st.markdown("---")

# --- Desempenho dos Padrões (Nova Seção "IA") ---
st.header("🧠 Desempenho e Adaptação dos Padrões (Simulação de IA)")
if st.session_state.pattern_performance:
    pattern_perf_df = pd.DataFrame.from_dict(st.session_state.pattern_performance, orient='index')
    pattern_perf_df.index.name = 'Padrão'
    pattern_perf_df.reset_index(inplace=True)
    
    # Calcular a taxa de sucesso e exibir
    pattern_perf_df['Taxa de Sucesso'] = (pattern_perf_df['successes'] / (pattern_perf_df['successes'] + pattern_perf_df['failures']) * 100).fillna(0).round(2)
    
    st.dataframe(pattern_perf_df.sort_values(by='Taxa de Sucesso', ascending=False), use_container_width=True)
    st.write("A confiança nas sugestões é ajustada com base neste desempenho.")
else:
    st.write("Comece a registrar resultados para a IA começar a aprender o desempenho dos padrões.")


st.markdown("---")

# --- Histórico dos Últimos 100 Resultados ---
st.header(f"Histórico dos Últimos {NUM_HISTORY_TO_DISPLAY} Resultados")
if st.session_state.results:
    history_to_display = st.session_state.results[:NUM_HISTORY_TO_DISPLAY]
    history_df = pd.DataFrame(history_to_display, columns=["Resultado"])
    history_df['Cor'] = history_df['Resultado'].apply(get_color)
    history_df['Emoji'] = history_df['Cor'].apply(get_color_emoji)
    
    st.dataframe(history_df[['Resultado', 'Cor', 'Emoji']], use_container_width=True)
    if st.button("Limpar Histórico Completo (e Dados da IA)", type="secondary"):
        clear_history()
else:
    st.write("Nenhum resultado registrado ainda. Adicione resultados para começar a análise!")
