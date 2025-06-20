import streamlit as st
import pandas as pd
import collections
import time

# --- Constantes e Funções Auxiliares ---
NUM_RECENT_RESULTS_FOR_ANALYSIS = 27
MAX_HISTORY_TO_STORE = 1000

# Resultados do Bac Bo: 'player', 'banker', 'tie'
# Mapeamento de cores para visualização conforme sua solicitação
def get_color(result):
    if result == 'player': return 'blue'    # Jogador (azul)
    elif result == 'banker': return 'red'   # Banca (vermelho)
    else: return 'yellow' # Empate (amarelo)

def get_color_emoji(color):
    if color == 'blue': return '🔵'  # Emoji para Jogador (azul)
    elif color == 'red': return '🔴'    # Emoji para Banca (vermelho)
    elif color == 'yellow': return '🟡' # Emoji para Empate (amarelo)
    return ''

# --- Funções de Análise Adaptadas para Bac Bo (Jogador/Banca) ---

def analyze_surf(results):
    relevant_results = results[:NUM_RECENT_RESULTS_FOR_ANALYSIS]
    if not relevant_results:
        return {'player_sequence': 0, 'banker_sequence': 0, 'tie_sequence': 0,
                'max_player_sequence': 0, 'max_banker_sequence': 0, 'max_tie_sequence': 0}
    
    max_player_sequence = 0
    max_banker_sequence = 0
    max_tie_sequence = 0
    temp_player_seq = 0
    temp_banker_seq = 0
    temp_tie_seq = 0

    for i in range(len(relevant_results)):
        result = relevant_results[i]
        if result == 'player':
            temp_player_seq += 1; temp_banker_seq = 0; temp_tie_seq = 0
        elif result == 'banker':
            temp_banker_seq += 1; temp_player_seq = 0; temp_tie_seq = 0
        else: # tie
            temp_tie_seq += 1; temp_player_seq = 0; temp_banker_seq = 0
        max_player_sequence = max(max_player_sequence, temp_player_seq)
        max_banker_sequence = max(max_banker_sequence, temp_banker_seq)
        max_tie_sequence = max(max_tie_sequence, temp_tie_seq)

    actual_current_player_sequence = 0
    actual_current_banker_sequence = 0
    actual_current_tie_sequence = 0
    if relevant_results:
        first_result = relevant_results[0]
        for r in relevant_results:
            if r == first_result:
                if first_result == 'player': actual_current_player_sequence += 1
                elif first_result == 'banker': actual_current_banker_sequence += 1
                else: actual_current_tie_sequence += 1
            else: break
    return {
        'player_sequence': actual_current_player_sequence, 'banker_sequence': actual_current_banker_sequence,
        'tie_sequence': actual_current_tie_sequence, 'max_player_sequence': max_player_sequence,
        'max_banker_sequence': max_banker_sequence, 'max_tie_sequence': max_tie_sequence
    }

def analyze_colors(results):
    relevant_results = results[:NUM_RECENT_RESULTS_FOR_ANALYSIS]
    if not relevant_results:
        return {'blue': 0, 'red': 0, 'yellow': 0, 'current_color': '', 'streak': 0, 'color_pattern_27': ''}
    color_counts = {'blue': 0, 'red': 0, 'yellow': 0}
    for result in relevant_results:
        color = get_color(result)
        color_counts[color] += 1
    current_color = get_color(results[0]) if results else '' # Handle empty results
    streak = 0
    for result in results:  
        if get_color(result) == current_color: streak += 1
        else: break
    color_pattern_27 = ''.join([get_color(r)[0].upper() for r in relevant_results]) # B for blue, R for red, Y for yellow
    return {
        'blue': color_counts['blue'], 'red': color_counts['red'], 'yellow': color_counts['yellow'],
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
        if color2 == 'yellow' and color1 != 'yellow': patterns[f"X Y Empate ({color1.capitalize()}{get_color_emoji(color1)} {color2.capitalize()}{get_color_emoji(color2)})"] += 1 # Adaptação: X Y Tie -> X Y Empate
        if i < len(relevant_results) - 2:
            color3 = get_color(relevant_results[i+2])
            if color1 == 'yellow' and color2 != 'yellow' and color3 != 'yellow' and color2 != color3: patterns[f"Empate X Y ({color1.capitalize()}{get_color_emoji(color1)} {color2.capitalize()}{get_color_emoji(color2)} {color3.capitalize()}{get_color_emoji(color3)})"] += 1 # Adaptação: Tie X Y -> Empate X Y
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

def analyze_tie_specifics(results):
    relevant_results = results[:NUM_RECENT_RESULTS_FOR_ANALYSIS]
    if not relevant_results:
        return {'tie_frequency_27': 0, 'time_since_last_tie': -1, 'tie_patterns': {}}
    tie_count_27 = relevant_results.count('tie')
    tie_frequency_27 = (tie_count_27 / len(relevant_results)) * 100 if len(relevant_results) > 0 else 0
    time_since_last_tie = -1
    for i, result in enumerate(results):  
        if result == 'tie': time_since_last_tie = i; break
    tie_patterns_found = collections.defaultdict(int)
    for i in range(len(relevant_results) - 1):
        color1 = get_color(relevant_results[i]); color2 = get_color(relevant_results[i+1])
        if color2 == 'yellow' and color1 != 'yellow': tie_patterns_found[f"Quebra para Empate ({color1.capitalize()}{get_color_emoji(color1)} para Empate{get_color_emoji('yellow')})"] += 1
        if i < len(relevant_results) - 2:
            color3 = get_color(relevant_results[i+2])
            if color3 == 'yellow':
                if color1 == 'blue' and color2 == 'red': tie_patterns_found["Jogador-Banca-Empate (🔵🔴🟡)"] += 1 # Adaptação
                elif color1 == 'red' and color2 == 'blue': tie_patterns_found["Banca-Jogador-Empate (🔴🔵🟡)"] += 1 # Adaptação
    return {
        'tie_frequency_27': round(tie_frequency_27, 2), 'time_since_last_tie': time_since_last_tie,
        'tie_patterns': dict(tie_patterns_found)
    }

# --- Função de Sugestão com "IA" Simulada Adaptada (Jogador/Banca) ---
def generate_advanced_suggestion(results, surf_analysis, color_analysis, break_probability, break_patterns, tie_specifics, pattern_performance):
    """Gera uma sugestão de aposta baseada em múltiplas análises, com ajuste de confiança por performance de padrão."""
    if not results or len(results) < 5:  
        return {'suggestion': 'Aguardando mais resultados para análise detalhada.', 'confidence': 0, 'reason': '', 'guarantee_pattern': 'N/A'}

    last_result_color = color_analysis['current_color']
    current_streak = color_analysis['streak']
    
    suggestion = "Manter observação"
    confidence = 50
    reason = "Análise preliminar."
    guarantee_pattern = "N/A"

    def adjust_confidence_by_performance(base_confidence, pattern_name):
        if pattern_name in pattern_performance:
            performance = pattern_performance[pattern_name]
            reliability = (performance['successes'] + 1) / (performance['successes'] + performance['failures'] + 2)
            adjusted_confidence = base_confidence * reliability * 1.2
            return min(95, max(20, int(adjusted_confidence)))
        return base_confidence

    # 1. Sugestão baseada em Sequência Longa e Máximo Histórico de Surf
    if last_result_color == 'blue' and current_streak >= surf_analysis['max_player_sequence'] and surf_analysis['max_player_sequence'] > 0 and current_streak >= 3: # Adaptado para 'blue'/'player'
        pattern_name = f"Surf Max Quebra: {last_result_color.capitalize()}"
        confidence = adjust_confidence_by_performance(95, pattern_name)
        suggestion = f"APOSTA FORTE em **BANCA** {get_color_emoji('red')}" # Sugere Banca
        reason = f"Sequência atual de Jogador ({current_streak}x) atingiu ou superou o máximo histórico de surf. Grande chance de quebra."
        guarantee_pattern = pattern_name
        return {'suggestion': suggestion, 'confidence': confidence, 'reason': reason, 'guarantee_pattern': guarantee_pattern}
    elif last_result_color == 'red' and current_streak >= surf_analysis['max_banker_sequence'] and surf_analysis['max_banker_sequence'] > 0 and current_streak >= 3: # Adaptado para 'red'/'banker'
        pattern_name = f"Surf Max Quebra: {last_result_color.capitalize()}"
        confidence = adjust_confidence_by_performance(95, pattern_name)
        suggestion = f"APOSTA FORTE em **JOGADOR** {get_color_emoji('blue')}" # Sugere Jogador
        reason = f"Sequência atual de Banca ({current_streak}x) atingiu ou superou o máximo histórico de surf. Grande chance de quebra."
        guarantee_pattern = pattern_name
        return {'suggestion': suggestion, 'confidence': confidence, 'reason': reason, 'guarantee_pattern': guarantee_pattern}
    elif last_result_color == 'yellow' and current_streak >= surf_analysis['max_tie_sequence'] and surf_analysis['max_tie_sequence'] > 0 and current_streak >= 2:
        pattern_name = f"Surf Max Quebra: {last_result_color.capitalize()}"
        confidence = adjust_confidence_by_performance(90, pattern_name)
        suggestion = f"APOSTA FORTE em **JOGADOR** {get_color_emoji('blue')} ou **BANCA** {get_color_emoji('red')}" # Sugere Jogador ou Banca
        reason = f"Sequência atual de Empate ({current_streak}x) atingiu ou superou o máximo histórico de surf. Grande chance de retorno às cores principais."
        guarantee_pattern = pattern_name
        return {'suggestion': suggestion, 'confidence': confidence, 'reason': reason, 'guarantee_pattern': guarantee_pattern}

    # 2. Sugestão baseada em padrões recorrentes de quebra (2x1, 3x1)
    for pattern, count in break_patterns.items():
        if count >= 3:  
            if "2x1 (Blue 🔵 Red 🔴)" in pattern and last_result_color == 'blue' and current_streak == 2: # Adaptação de cores
                confidence = adjust_confidence_by_performance(88, pattern)
                suggestion = f"Apostar em **BANCA** {get_color_emoji('red')}"
                reason = f"Padrão 2x1 (🔵🔵🔴) altamente recorrente ({count}x). Espera-se a quebra para Banca."
                guarantee_pattern = pattern
                return {'suggestion': suggestion, 'confidence': confidence, 'reason': reason, 'guarantee_pattern': guarantee_pattern}
            elif "2x1 (Red 🔴 Blue 🔵)" in pattern and last_result_color == 'red' and current_streak == 2: # Adaptação de cores
                confidence = adjust_confidence_by_performance(88, pattern)
                suggestion = f"Apostar em **JOGADOR** {get_color_emoji('blue')}"
                reason = f"Padrão 2x1 (🔴🔴🔵) altamente recorrente ({count}x). Espera-se a quebra para Jogador."
                guarantee_pattern = pattern
                return {'suggestion': suggestion, 'confidence': confidence, 'reason': reason, 'guarantee_pattern': guarantee_pattern}
            
            elif "3x1 (Blue 🔵 Red 🔴)" in pattern and last_result_color == 'blue' and current_streak == 3: # Adaptação de cores
                confidence = adjust_confidence_by_performance(92, pattern)
                suggestion = f"Apostar em **BANCA** {get_color_emoji('red')}"
                reason = f"Padrão 3x1 (🔵🔵🔵🔴) altamente recorrente ({count}x). Espera-se a quebra para Banca."
                guarantee_pattern = pattern
                return {'suggestion': suggestion, 'confidence': confidence, 'reason': reason, 'guarantee_pattern': guarantee_pattern}
            elif "3x1 (Red 🔴 Blue 🔵)" in pattern and last_result_color == 'red' and current_streak == 3: # Adaptação de cores
                confidence = adjust_confidence_by_performance(92, pattern)
                suggestion = f"Apostar em **JOGADOR** {get_color_emoji('blue')}"
                reason = f"Padrão 3x1 (🔴🔴🔴🔵) altamente recorrente ({count}x). Espera-se a quebra para Jogador."
                guarantee_pattern = pattern
                return {'suggestion': suggestion, 'confidence': confidence, 'reason': reason, 'guarantee_pattern': guarantee_pattern}

    # 3. Sugestão de Empate (maior assertividade)
    if tie_specifics['time_since_last_tie'] >= 7 and tie_specifics['tie_frequency_27'] < 12:  
        pattern_name = "Empate Atrasado/Baixa Frequência"
        confidence = adjust_confidence_by_performance(78, pattern_name)
        suggestion = f"Considerar **EMPATE** {get_color_emoji('yellow')}"
        reason = f"Empate não ocorre há {tie_specifics['time_since_last_tie']} rodadas e frequência baixa ({tie_specifics['tie_frequency_27']}% nos últimos 27)."
        guarantee_pattern = pattern_name
        
        # Reforço com padrões de empate
        if "Jogador-Banca-Empate (🔵🔴🟡)" in tie_specifics['tie_patterns'] and len(results) >= 2 and results[0] == 'banker' and results[1] == 'player': # Adaptação
            confidence = adjust_confidence_by_performance(confidence + 10, pattern_name + " + Padrão 🔵🔴🟡")
            suggestion += f" - Reforçado por padrão 🔵🔴🟡."
            guarantee_pattern += " + Padrão 🔵🔴🟡"
        elif "Banca-Jogador-Empate (🔴🔵🟡)" in tie_specifics['tie_patterns'] and len(results) >= 2 and results[0] == 'player' and results[1] == 'banker': # Adaptação
            confidence = adjust_confidence_by_performance(confidence + 10, pattern_name + " + Padrão 🔴🔵🟡")
            suggestion += f" - Reforçado por padrão 🔴🔵🟡."
            guarantee_pattern += " + Padrão 🔴🔵🟡"
        
        return {'suggestion': suggestion, 'confidence': confidence, 'reason': reason, 'guarantee_pattern': guarantee_pattern}
    
    # Se os últimos 2 foram alternados (B-R ou R-B) e não houve empate em X rodadas
    if len(results) >= 2 and ( (get_color(results[0]) == 'blue' and get_color(results[1]) == 'red') or \
                               (get_color(results[0]) == 'red' and get_color(results[1]) == 'blue') ):
        if tie_specifics['time_since_last_tie'] >= 3:
            pattern_name = "Alternância para Empate"
            confidence = adjust_confidence_by_performance(75, pattern_name)
            suggestion = f"Considerar **EMPATE** {get_color_emoji('yellow')}"
            reason = "Resultados alternados (🔵🔴 ou 🔴🔵) podem preceder um empate. Empate atrasado."
            guarantee_pattern = pattern_name
            return {'suggestion': suggestion, 'confidence': confidence, 'reason': reason, 'guarantee_pattern': guarantee_pattern}

    # 4. Outras Sugestões (se as acima não se aplicarem com alta confiança)
    if break_probability['break_chance'] > 65 and current_streak < 3:  
        if len(results) >= 2:
            prev_color = get_color(results[1])
            pattern_name = "Alta Probabilidade de Quebra Geral"
            confidence = adjust_confidence_by_performance(70, pattern_name)
            if prev_color == 'blue':
                suggestion = f"Apostar em **BANCA** {get_color_emoji('red')}"
                reason = f"Alta chance de quebra ({break_probability['break_chance']}%). Prever quebra de sequência de {prev_color.capitalize()}."
            elif prev_color == 'red':
                suggestion = f"Apostar em **JOGADOR** {get_color_emoji('blue')}"
                reason = f"Alta chance de quebra ({break_probability['break_chance']}%). Prever quebra de sequência de {prev_color.capitalize()}."
            return {'suggestion': suggestion, 'confidence': confidence, 'reason': reason, 'guarantee_pattern': guarantee_pattern}

    suggestion = "Manter observação."
    confidence = 50
    reason = "Nenhum padrão de 'garantía' forte detectado nos últimos 27 resultados para uma aposta segura no momento."
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
            'stats': {'player': 0, 'banker': 0, 'tie': 0, 'total': 0}, # Adaptado para 'player', 'banker', 'tie'
            'surf_analysis': analyze_surf([]),
            'color_analysis': analyze_colors([]),
            'break_patterns': find_break_patterns([]),
            'break_probability': analyze_break_probability([]),
            'tie_specifics': analyze_tie_specifics([]),
            'suggestion': {'suggestion': 'Aguardando resultados para análise.', 'confidence': 0, 'reason': '', 'guarantee_pattern': 'N/A'}
        }

    stats = {'player': relevant_results_for_analysis.count('player'),  
             'banker': relevant_results_for_analysis.count('banker'),  
             'tie': relevant_results_for_analysis.count('tie'),  
             'total': len(relevant_results_for_analysis)}
    
    surf_analysis = analyze_surf(results)  
    color_analysis = analyze_colors(results)
    break_patterns = find_break_patterns(results)
    break_probability = analyze_break_probability(results)
    tie_specifics = analyze_tie_specifics(results)

    suggestion_data = generate_advanced_suggestion(results, surf_analysis, color_analysis, break_probability, break_patterns, tie_specifics, pattern_performance)
    
    return {
        'stats': stats,
        'surf_analysis': surf_analysis,
        'color_analysis': color_analysis,
        'break_patterns': break_patterns,
        'break_probability': break_probability,
        'tie_specifics': tie_specifics,
        'suggestion': suggestion_data
    }

# --- Função para Renderizar o Histórico (Roadmap) ---
def render_roadmap_history(results_list_latest_first, max_cols=30, max_rows_per_col=6):
    """
    Renderiza o histórico em formato de roadmap (torre e linha) usando emojis e st.columns.
    max_cols limita o número de colunas exibidas.
    max_rows_per_col limita a altura de cada coluna para evitar rolagem excessiva e manter a visualização padrão do roadmap.
    """
    if not results_list_latest_first:
        st.write("Nenhum resultado para exibir o roadmap.")
        return

    results_oldest_first = results_list_latest_first[::-1] # Inverter para analisar do mais antigo para o mais novo

    roadmap_columns_data = []
    current_column = []

    for i, result in enumerate(results_oldest_first):
        emoji = get_color_emoji(get_color(result))

        if not current_column:
            current_column.append(emoji)
        else:
            last_result_in_current_col_color = get_color(results_oldest_first[i-1])
            current_result_color = get_color(result)

            if current_result_color == last_result_in_current_col_color:
                current_column.append(emoji)
            else:
                roadmap_columns_data.append(current_column)
                current_column = [emoji]
    
    if current_column: # Adicionar a última coluna se houver
        roadmap_columns_data.append(current_column)

    # Limitar o número de colunas a serem exibidas
    roadmap_columns_data = roadmap_columns_data[-max_cols:]

    # Encontrar a altura máxima para alinhar as linhas
    max_height = max(len(col) for col in roadmap_columns_data) if roadmap_columns_data else 0

    # Ajustar a altura máxima para a altura padrão de roadmap (geralmente 6)
    display_height = min(max_height, max_rows_per_col)

    # Criar uma lista de colunas Streamlit que se estenderá por toda a largura
    # Cada coluna do roadmap_columns_data será uma coluna Streamlit
    cols_streamlit = st.columns(len(roadmap_columns_data))

    # Preencher as colunas do Streamlit linha por linha (de baixo para cima para simular o roadmap)
    for r_idx in range(display_height): # Iterar pelas linhas do roadmap (de 0 até display_height-1)
        for c_idx, col_data in enumerate(roadmap_columns_data): # Iterar por cada coluna de dados do roadmap
            
            emoji_to_display = " "
            if r_idx >= (display_height - len(col_data)):
                # Calcula o índice real na lista col_data
                actual_idx_in_col_data = r_idx - (display_height - len(col_data))
                emoji_to_display = col_data[actual_idx_in_col_data]
            
            with cols_streamlit[c_idx]:
                st.markdown(emoji_to_display)
            else: # Add empty column if no data
                with cols_streamlit[c_idx]:
                    st.markdown(" ") # Espaço vazio para alinhar as colunas

# --- Streamlit UI ---

st.set_page_config(layout="wide", page_title="Bac Bo Pro Analyzer (Roadmap e IA Sim.)")

st.title("🎲 Bac Bo Pro Analyzer (Roadmap e IA Sim. Adaptativa)")
st.write("Sistema Avançado de Análise e Predição com Adaptação de Padrões para Bac Bo")

# --- Gerenciamento de Estado ---
if 'results' not in st.session_state:
    st.session_state.results = []
if 'last_suggested_bet_info' not in st.session_state:  
    st.session_state.last_suggested_bet_info = None
if 'guarantee_failed_streak' not in st.session_state:  
    st.session_state.guarantee_failed_streak = 0
if 'pattern_performance' not in st.session_state:
    st.session_state.pattern_performance = {}  

if 'analysis_data' not in st.session_state:
    st.session_state.analysis_data = update_analysis(st.session_state.results, st.session_state.pattern_performance)


# --- Função para Adicionar Resultado ---
def add_result(result):
    if st.session_state.last_suggested_bet_info:
        last_suggestion = st.session_state.last_suggested_bet_info
        suggested_outcome = None  

        if "JOGADOR" in last_suggestion['suggestion']: # Adaptado
            suggested_outcome = 'player'
        elif "BANCA" in last_suggestion['suggestion']: # Adaptado
            suggested_outcome = 'banker'
        elif "EMPATE" in last_suggestion['suggestion']:
            suggested_outcome = 'tie'

        if suggested_outcome and last_suggestion['confidence'] >= 70 and last_suggestion['guarantee_pattern'] != 'Nenhum Padrão Forte':
            actual_color = get_color(result)
            suggested_color = get_color(suggested_outcome)
            
            pattern_name = last_suggestion['guarantee_pattern']
            if pattern_name not in st.session_state.pattern_performance:
                st.session_state.pattern_performance[pattern_name] = {'successes': 0, 'failures': 0}

            if actual_color == suggested_color:
                st.session_state.pattern_performance[pattern_name]['successes'] += 1
                st.session_state.guarantee_failed_streak = 0  
            else:
                st.session_state.pattern_performance[pattern_name]['failures'] += 1
                st.session_state.guarantee_failed_streak += 1  
                st.warning(f"🚨 **ALERTA: A GARANTIA DO PADRÃO '{pattern_name}' FALHOU!**")
                
        else:  
            st.session_state.guarantee_failed_streak = 0

    st.session_state.results.insert(0, result)  
    st.session_state.results = st.session_state.results[:MAX_HISTORY_TO_STORE]  
    
    st.session_state.analysis_data = update_analysis(st.session_state.results, st.session_state.pattern_performance)
    
    st.session_state.last_suggested_bet_info = st.session_state.analysis_data['suggestion']
    
# --- Função para Limpar Histórico ---
def clear_history():
    st.session_state.results = []
    st.session_state.analysis_data = update_analysis([], {})  
    st.session_state.last_suggested_bet_info = None
    st.session_state.guarantee_failed_streak = 0
    st.session_state.pattern_performance = {}  
    st.experimental_rerun()  

# --- Layout ---
st.header("Registrar Resultado")
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("JOGADOR 🔵", use_container_width=True): # Botão Jogador (Azul)
        add_result('player')
with col2:
    if st.button("BANCA 🔴", use_container_width=True): # Botão Banca (Vermelho)
        add_result('banker')
with col3:
    if st.button("EMPATE 🟡", use_container_width=True): # Botão Empate (Amarelo)
        add_result('tie')

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

# --- Histórico dos Últimos Resultados (Roadmap) ---
st.header("📜 Histórico de Resultados (Roadmap Bac Bo)")
# Envolver a renderização do roadmap em uma div com estilo para centralizar, se necessário
st.markdown("<div style='display: flex; justify-content: center;'>", unsafe_allow_html=True)
render_roadmap_history(st.session_state.results)  
st.markdown("</div>", unsafe_allow_html=True)

st.markdown("---")

# --- Estatísticas e Padrões (Últimos 27 Resultados) ---
st.header(f"Estatísticas e Padrões (Últimos {NUM_RECENT_RESULTS_FOR_ANALYSIS} Resultados)")

stats_col, color_col = st.columns(2)

with stats_col:
    st.subheader("Estatísticas Gerais")
    stats = st.session_state.analysis_data['stats']
    st.write(f"**Jogador {get_color_emoji('blue')}:** {stats['player']} vezes")
    st.write(f"**Banca {get_color_emoji('red')}:** {stats['banker']} vezes")
    st.write(f"**Empate {get_color_emoji('yellow')}:** {stats['tie']} vezes")
    st.write(f"**Total de Resultados Analisados:** {stats['total']}")

with color_col:
    st.subheader("Análise de Cores")
    colors = st.session_state.analysis_data['color_analysis']
    st.write(f"**Azul (Jogador):** {colors['blue']}x")
    st.write(f"**Vermelho (Banca):** {colors['red']}x")
    st.write(f"**Amarelo (Empate):** {colors['yellow']}x")
    st.write(f"**Sequência Atual:** {colors['streak']}x {colors['current_color'].capitalize()} {get_color_emoji(colors['current_color'])}")
    st.markdown(f"**Padrão (Últimos {NUM_RECENT_RESULTS_FOR_ANALYSIS}):** `{colors['color_pattern_27']}`")

st.markdown("---")

# --- Análise de Quebra, Surf e Empate ---
col_break, col_surf, col_tie_analysis = st.columns(3)

with col_break:
    st.subheader("Análise de Quebra")
    bp = st.session_state.analysis_data['break_probability']
    st.write(f"**Chance de Quebra:** {bp['break_chance']}%")
    st.write(f"**Último Tipo de Quebra:** {bp['last_break_type'] if bp['last_break_type'] else 'N/A'}")
    
    st.subheader("Padrões de Quebra e Específicos")
    patterns = st.session_state.analysis_data['break_patterns'] # Completed this line
    if patterns:
        for pattern, count in patterns.items():
            st.write(f"- {pattern}: {count}x")
    else:
        st.write("Nenhum padrão de quebra significativo detectado.")

with col_surf:
    st.subheader("Análise de Surf")
    surf = st.session_state.analysis_data['surf_analysis']
    st.write(f"**Sequência Atual (Jogador {get_color_emoji('blue')}):** {surf['player_sequence']}x")
    st.write(f"**Máx. Sequência Histórica (Jogador {get_color_emoji('blue')}):** {surf['max_player_sequence']}x")
    st.write(f"**Sequência Atual (Banca {get_color_emoji('red')}):** {surf['banker_sequence']}x")
    st.write(f"**Máx. Sequência Histórica (Banca {get_color_emoji('red')}):** {surf['max_banker_sequence']}x")
    st.write(f"**Sequência Atual (Empate {get_color_emoji('yellow')}):** {surf['tie_sequence']}x")
    st.write(f"**Máx. Sequência Histórica (Empate {get_color_emoji('yellow')}):** {surf['max_tie_sequence']}x")

with col_tie_analysis:
    st.subheader("Análise de Empate")
    tie_spec = st.session_state.analysis_data['tie_specifics']
    st.write(f"**Frequência de Empate (últimos {NUM_RECENT_RESULTS_FOR_ANALYSIS}):** {tie_spec['tie_frequency_27']}%")
    st.write(f"**Tempo desde o Último Empate:** {tie_spec['time_since_last_tie']} rodadas")
    st.write("**Padrões de Empate Detectados:**")
    if tie_spec['tie_patterns']:
        for pattern, count in tie_spec['tie_patterns'].items():
            st.write(f"- {pattern}: {count}x")
    else:
        st.write("Nenhum padrão de empate específico detectado.")

st.markdown("---")

# --- Performance dos Padrões (IA) ---
st.header("📈 Performance dos Padrões (IA Adaptativa)")
if st.session_state.pattern_performance:
    performance_df = pd.DataFrame.from_dict(st.session_state.pattern_performance, orient='index')
    performance_df.index.name = 'Padrão'
    performance_df['Total'] = performance_df['successes'] + performance_df['failures']
    performance_df['Acerto (%)'] = (performance_df['successes'] / performance_df['Total'] * 100).round(2)
    st.dataframe(performance_df.sort_values(by='Total', ascending=False))
else:
    st.info("A performance dos padrões será rastreada após sugestões com garantia serem feitas e resultados registrados.")

st.markdown("---")

# --- Botão para Limpar Histórico ---
st.button("Limpar Todo o Histórico", on_click=clear_history, help="Apaga todos os resultados e dados de análise.", type="secondary")

st.caption("Desenvolvido para análise de padrões no Bac Bo. Use com cautela e responsabilidade.")
