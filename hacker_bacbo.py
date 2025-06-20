20/06/2025   15:43

import streamlit as st
import collections

# --- C

import streamlit as st
import collections

# --- Constantes e FunÃ§Ãµes Auxiliares ---
NUM_RECENT_RESULTS_FOR_ANALYSIS = 27
MAX_HISTORY_TO_STORE = 1000
NUM_HISTORY_TO_DISPLAY = 100 # NÃºmero de resultados do histÃ³rico a serem exibidos
EMOJIS_PER_ROW = 9 # Quantos emojis por linha no histÃ³rico horizontal
MIN_RESULTS_FOR_SUGGESTION = 9

def get_color(result):
    """Retorna a cor associada ao resultado."""
    if result == 'banker':
        return 'red'
    elif result == 'player':
        return 'blue'
    else: # 'tie'
        return 'yellow'

def get_color_emoji(color):
    """Retorna o emoji correspondente Ã  cor."""
    if color == 'red':
        return 'ðŸ”´'
    elif color == 'blue':
        return 'ðŸ”µ'
    elif color == 'yellow':
        return 'ðŸŸ¡'
    return ''

def get_result_emoji(result_type):
    """Retorna o emoji correspondente ao tipo de resultado. Agora retorna uma string vazia para remover os Ã­cones."""
    return ''

# --- FunÃ§Ãµes de AnÃ¡lise ---

def analyze_surf(results):
    """
    Analisa os padrÃµes de "surf" (sequÃªncias de Home/Away/Draw)
    nos Ãºltimos N resultados para 'current' e no histÃ³rico completo para 'max'.
    """
    relevant_results = results[:NUM_RECENT_RESULTS_FOR_ANALYSIS]
    
    current_banker_sequence = 0
    current_player_sequence = 0
    current_tie_sequence = 0
    
    if results:
        # A sequÃªncia atual Ã© sempre do resultado mais recente (results[0])
        current_result = results[0]
        for r in results:  # Usar todo o histÃ³rico para sequÃªncia atual
            if r == current_result:
                if current_result == 'banker': 
                    current_banker_sequence += 1
                elif current_result == 'player': 
                    current_player_sequence += 1
                else: # tie
                    current_tie_sequence += 1
            else:
                break
    
    # Calcular sequÃªncias mÃ¡ximas em todo o histÃ³rico disponÃ­vel para maior precisÃ£o
    max_banker_sequence = 0
    max_player_sequence = 0
    max_tie_sequence = 0
    
    temp_banker_seq = 0
    temp_player_seq = 0
    temp_tie_seq = 0

    for res in results: # Percorre TODOS os resultados (histÃ³rico completo) para o mÃ¡ximo
        if res == 'banker':
            temp_banker_seq += 1
            temp_player_seq = 0
            temp_tie_seq = 0
        elif res == 'player':
            temp_player_seq += 1
            temp_banker_seq = 0
            temp_tie_seq = 0
        else: # tie
            temp_tie_seq += 1
            temp_banker_seq = 0
            temp_player_seq = 0
        
        max_banker_sequence = max(max_banker_sequence, temp_banker_seq)
        max_player_sequence = max(max_player_sequence, temp_player_seq)
        max_tie_sequence = max(max_tie_sequence, temp_tie_seq)

    return {
        'banker_sequence': current_banker_sequence,
        'player_sequence': current_player_sequence,
        'tie_sequence': current_tie_sequence,
        'max_banker_sequence': max_banker_sequence,
        'max_player_sequence': max_player_sequence,
        'max_tie_sequence': max_tie_sequence
    }

def analyze_colors(results):
    """Analisa a contagem e as sequÃªncias de cores nos Ãºltimos N resultados."""
    relevant_results = results[:NUM_RECENT_RESULTS_FOR_ANALYSIS]
    if not relevant_results:
        return {'red': 0, 'blue': 0, 'yellow': 0, 'current_color': '', 'streak': 0, 'color_pattern_27': ''}

    color_counts = {'red': 0, 'blue': 0, 'yellow': 0}

    for result in relevant_results:
        color = get_color(result)
        color_counts[color] += 1

    current_color = get_color(results[0]) if results else ''
    streak = 0
    for result in results: # Streak Ã© sempre do resultado mais recente no histÃ³rico completo
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

def find_complex_patterns(results):
    """
    Identifica padrÃµes de quebra e padrÃµes especÃ­ficos (2x2, 3x3, 3x1, 2x1, etc.)
    nos Ãºltimos N resultados, incluindo os novos padrÃµes.
    Os nomes dos padrÃµes agora sÃ£o concisos, sem exemplos ou emojis.
    """
    patterns = collections.defaultdict(int)
    relevant_results = results[:NUM_RECENT_RESULTS_FOR_ANALYSIS]

    # Converte resultados para cores para facilitar a anÃ¡lise de padrÃµes
    colors = [get_color(r) for r in relevant_results]

    for i in range(len(colors) - 1):
        color1 = colors[i]
        color2 = colors[i+1]

        # 1. Quebra Simples
        if color1 != color2:
            patterns[f"Quebra Simples ({color1.capitalize()} para {color2.capitalize()})"] += 1

        # Verificar padrÃµes que envolvem 3 ou mais resultados
        if i < len(colors) - 2:
            color3 = colors[i+2]
            
            # 2. PadrÃµes 2x1 (Ex: R R B)
            if color1 == color2 and color1 != color3:
                patterns[f"2x1 ({color1.capitalize()} para {color3.capitalize()})"] += 1
            
            # 3. Zig-Zag / PadrÃ£o Alternado (Ex: R B R)
            if color1 != color2 and color2 != color3 and color1 == color3:
                patterns[f"Zig-Zag / Alternado ({color1.capitalize()}-{color2.capitalize()}-{color3.capitalize()})"] += 1

            # 4. AlternÃ¢ncia com Tie no Meio (X Draw Y - Ex: R Y B)
            if color2 == 'yellow' and color1 != 'yellow' and color3 != 'yellow' and color1 != color3:
                patterns[f"AlternÃ¢ncia c/ Tie no Meio ({color1.capitalize()}-Tie-{color3.capitalize()})"] += 1

            # 5. PadrÃ£o Onda 1-2-1 (Ex: R B B R) - variaÃ§Ã£o de espelho ou zig-zag
            if i < len(colors) - 3:
                color4 = colors[i+3]
                if color1 != color2 and color2 == color3 and color3 != color4 and color1 == color4:
                    patterns[f"PadrÃ£o Onda 1-2-1 ({color1.capitalize()}-{color2.capitalize()}-{color3.capitalize()}-{color4.capitalize()})"] += 1

        if i < len(colors) - 3:
            color3 = colors[i+2]
            color4 = colors[i+3]

            # 6. PadrÃµes 3x1 (Ex: R R R B)
            if color1 == color2 and color2 == color3 and color1 != color4:
                patterns[f"3x1 ({color1.capitalize()} para {color4.capitalize()})"] += 1
            
            # 7. PadrÃµes 2x2 (Ex: R R B B)
            if color1 == color2 and color3 == color4 and color1 != color3:
                patterns[f"2x2 ({color1.capitalize()} para {color3.capitalize()})"] += 1
            
            # 8. PadrÃ£o de Espelho (Ex: R B B R)
            if color1 != color2 and color2 == color3 and color1 == color4:
                patterns[f"PadrÃ£o Espelho ({color1.capitalize()}-{color2.capitalize()}-{color3.capitalize()}-{color4.capitalize()})"] += 1

        if i < len(colors) - 5:
            color3 = colors[i+2]
            color4 = colors[i+3]
            color5 = colors[i+4]
            color6 = colors[i+5]

            # 9. PadrÃµes 3x3 (Ex: R R R B B B)
            if color1 == color2 and color2 == color3 and color4 == color5 and color5 == color6 and color1 != color4:
                patterns[f"3x3 ({color1.capitalize()} para {color4.capitalize()})"] += 1

    # 10. Duplas Repetidas (Ex: R R, B B, Y Y) - Contagem de ocorrÃªncias de duplas
    for i in range(len(colors) - 1):
        if colors[i] == colors[i+1]:
            patterns[f"Dupla Repetida ({colors[i].capitalize()})"] += 1
            
    # PadrÃ£o de ReversÃ£o / AlternÃ¢ncia de Blocos (Ex: RR BB RR BB)
    block_pattern_keys = []
    if len(colors) >= 4:
        for block_size in [2, 3]: # Tamanhos de bloco comuns
            if len(colors) >= 2 * block_size:
                block1_colors = colors[:block_size]
                block2_colors = colors[block_size : 2 * block_size]
                
                if all(c == block1_colors[0] for c in block1_colors) and \
                   all(c == block2_colors[0] for c in block2_colors) and \
                   block1_colors[0] != block2_colors[0]:
                    
                    if len(colors) >= 4 * block_size:
                        block3_colors = colors[2 * block_size : 3 * block_size]
                        block4_colors = colors[3 * block_size : 4 * block_size]
                        if all(c == block3_colors[0] for c in block3_colors) and \
                           all(c == block4_colors[0] for c in block4_colors) and \
                           block1_colors[0] == block3_colors[0] and \
                           block2_colors[0] == block4_colors[0]:
                            patterns[f"AlternÃ¢ncia de Blocos {block_size}x{block_size} ({block1_colors[0].capitalize()}-{block2_colors[0].capitalize()})"] += 1
                            block_pattern_keys.append(f"AlternÃ¢ncia de Blocos {block_size}x{block_size} ({block1_colors[0].capitalize()}-{block2_colors[0].capitalize()})")

    return dict(patterns), block_pattern_keys

def analyze_break_probability(results):
    """
    Analisa a probabilidade de quebra das sequÃªncias atuais baseada no histÃ³rico.
    Calcula quando uma sequÃªncia Ã© mais provÃ¡vel de quebrar.
    """
    if len(results) < MIN_RESULTS_FOR_SUGGESTION:
        return {'break_probability': 0, 'sequence_length': 0, 'suggestion': '', 'confidence': 0}
    
    surf_analysis = analyze_surf(results)
    current_color = get_color(results[0]) if results else ''
    
    # Determine a sequÃªncia atual baseada na cor
    if current_color == 'red':
        current_sequence = surf_analysis['banker_sequence']
        max_sequence = surf_analysis['max_banker_sequence']
    elif current_color == 'blue':
        current_sequence = surf_analysis['player_sequence']
        max_sequence = surf_analysis['max_player_sequence']
    else: # yellow
        current_sequence = surf_analysis['tie_sequence']
        max_sequence = surf_analysis['max_tie_sequence']
    
    # Calcular probabilidade de quebra baseada no histÃ³rico
    if max_sequence == 0:
        break_probability = 50  # Default quando nÃ£o hÃ¡ histÃ³rico
    else:
        # Quanto mais prÃ³ximo do mÃ¡ximo histÃ³rico, maior a probabilidade de quebra
        break_probability = min(90, (current_sequence / max_sequence) * 100)
    
    # SugestÃ£o baseada na probabilidade de quebra - sempre uma cor especÃ­fica
    if break_probability > 70:
        if current_color == 'red':
            suggestion = "Apostar em Azul"
        elif current_color == 'blue':
            suggestion = "Apostar em Vermelho"
        else:
            suggestion = "Apostar em Vermelho"
        confidence = min(95, break_probability + 10)
    elif break_probability > 50:
        suggestion = "PossÃ­vel quebra em breve"
        confidence = break_probability
    else:
        suggestion = f"SequÃªncia {current_color.capitalize()} pode continuar"
        confidence = 100 - break_probability
    
    return {
        'break_probability': round(break_probability, 1),
        'sequence_length': current_sequence,
        'suggestion': suggestion,
        'confidence': round(confidence, 1),
        'current_color': current_color,
        'max_historical': max_sequence
    }

def analyze_tie_patterns(results):
    """
    Analisa padrÃµes especÃ­ficos relacionados aos empates.
    Identifica quando os empates sÃ£o mais provÃ¡veis de ocorrer.
    """
    if len(results) < MIN_RESULTS_FOR_SUGGESTION:
        return {'ties_in_last_27': 0, 'last_tie_position': -1, 'tie_frequency': 0, 'suggestion': '', 'confidence': 0}
    
    relevant_results = results[:NUM_RECENT_RESULTS_FOR_ANALYSIS]
    ties_count = sum(1 for r in relevant_results if r == 'tie')
    
    # Encontrar a posiÃ§Ã£o do Ãºltimo empate
    last_tie_position = -1
    for i, result in enumerate(results):
        if result == 'tie':
            last_tie_position = i
            break
    
    # Calcular frequÃªncia de empates (esperada: ~11% ou 3/27)
    expected_ties = NUM_RECENT_RESULTS_FOR_ANALYSIS * 0.11  # ~3 empates esperados
    tie_frequency = (ties_count / NUM_RECENT_RESULTS_FOR_ANALYSIS) * 100
    
    # AnÃ¡lise de padrÃµes RBD (Red-Blue-Draw)
    rbd_patterns = 0
    for i in range(len(results) - 2):
        if ((results[i] == 'banker' and results[i+1] == 'player') or 
            (results[i] == 'player' and results[i+1] == 'banker')) and results[i+2] == 'tie':
            rbd_patterns += 1
    
    # SugestÃ£o baseada na anÃ¡lise
    if ties_count < expected_ties * 0.7:  # Menos de 70% dos empates esperados
        suggestion = "Apostar em Amarelo"
        confidence = min(85, (expected_ties - ties_count) * 20)
    elif last_tie_position > 15:  # Mais de 15 jogos sem empate
        suggestion = "Apostar em Amarelo"
        confidence = min(90, last_tie_position * 4)
    elif last_tie_position <= 3 and ties_count >= expected_ties:
        suggestion = "Apostar em Vermelho"
        confidence = 75
    else:
        suggestion = "PadrÃ£o de empates normal"
        confidence = 50
    
    return {
        'ties_in_last_27': ties_count,
        'last_tie_position': last_tie_position,
        'tie_frequency': round(tie_frequency, 1),
        'expected_ties': round(expected_ties, 1),
        'rbd_patterns': rbd_patterns,
        'suggestion': suggestion,
        'confidence': round(confidence, 1)
    }

def generate_ai_suggestions(results):
    """
    Gera sugestÃµes de apostas usando IA baseada em todos os tipos de anÃ¡lise.
    Combina mÃºltiplas anÃ¡lises para fornecer sugestÃµes mais precisas.
    """
    if len(results) < MIN_RESULTS_FOR_SUGGESTION:
        return {'suggestions': [], 'top_suggestion': '', 'confidence': 0, 'reasoning': 'Dados insuficientes para anÃ¡lise'}
    
    suggestions = []
    
    # 1. AnÃ¡lise Surf
    surf_analysis = analyze_surf(results)
    break_analysis = analyze_break_probability(results)
    
    if break_analysis['confidence'] > 70:
        suggestions.append({
            'type': 'Break Analysis',
            'suggestion': break_analysis['suggestion'],
            'confidence': break_analysis['confidence'],
            'reasoning': f"SequÃªncia atual de {break_analysis['sequence_length']} com {break_analysis['break_probability']}% de probabilidade de quebra"
        })
    
    # 2. AnÃ¡lise de PadrÃµes Complexos
    complex_patterns, block_patterns = find_complex_patterns(results)
    
    # Procurar por padrÃµes de alta confianÃ§a
    high_confidence_patterns = []
    for pattern, count in complex_patterns.items():
        if count >= 3:  # PadrÃ£o que ocorreu 3+ vezes
            confidence = min(95, count * 15)
            if '2x1' in pattern or '3x1' in pattern:
                # Extrair direÃ§Ã£o da quebra
                if 'Red para Blue' in pattern:
                    suggestion_text = "Apostar em Azul"
                elif 'Red para Yellow' in pattern:
                    suggestion_text = "Apostar em Amarelo"
                elif 'Blue para Red' in pattern:  
                    suggestion_text = "Apostar em Vermelho"
                elif 'Blue para Yellow' in pattern:
                    suggestion_text = "Apostar em Amarelo"
                elif 'Yellow para Red' in pattern:
                    suggestion_text = "Apostar em Vermelho"
                elif 'Yellow para Blue' in pattern:
                    suggestion_text = "Apostar em Azul"
                else:
                    suggestion_text = f"PadrÃ£o {pattern} identificado"
                
                high_confidence_patterns.append({
                    'type': 'Pattern Analysis',
                    'suggestion': suggestion_text,
                    'confidence': confidence,
                    'reasoning': f"PadrÃ£o {pattern} ocorreu {count} vezes nos Ãºltimos {NUM_RECENT_RESULTS_FOR_ANALYSIS} resultados"
                })
    
    suggestions.extend(high_confidence_patterns)
    
    # 3. AnÃ¡lise de Ties
    tie_analysis = analyze_tie_patterns(results)
    if tie_analysis['confidence'] > 65:
        suggestions.append({
            'type': 'Draw Analysis',
            'suggestion': tie_analysis['suggestion'],
            'confidence': tie_analysis['confidence'],
            'reasoning': f"Ties: {tie_analysis['ties_in_last_27']}/27 ({tie_analysis['tie_frequency']}%), Ãºltimo empate hÃ¡ {tie_analysis['last_tie_position']} jogos"
        })
    
    # 4. AnÃ¡lise de Cores/Balanceamento
    color_analysis = analyze_colors(results)
    total_relevant = NUM_RECENT_RESULTS_FOR_ANALYSIS
    expected_per_color = total_relevant / 3  # ~9 para cada cor
    
    # Identificar cor mais deficitÃ¡ria
    color_deficits = {
        'red': expected_per_color - color_analysis['red'],
        'blue': expected_per_color - color_analysis['blue'], 
        'yellow': expected_per_color - color_analysis['yellow']
    }
    
    most_deficit_color = max(color_deficits.keys(), key=lambda k: color_deficits[k])
    deficit_amount = color_deficits[most_deficit_color]
    
    if deficit_amount > 3:  # DÃ©ficit significativo
        color_names = {'red': 'Vermelho', 'blue': 'Azul', 'yellow': 'Amarelo'}
        suggestions.append({
            'type': 'Color Balance',
            'suggestion': f"Apostar em {color_names[most_deficit_color]}",
            'confidence': min(85, deficit_amount * 8),
            'reasoning': f"{color_names[most_deficit_color]} com dÃ©ficit de {deficit_amount:.1f} ocorrÃªncias"
        })
    
    # Ordenar sugestÃµes por confianÃ§a
    suggestions.sort(key=lambda x: x['confidence'], reverse=True)
    
    # Determinar sugestÃ£o principal
    if suggestions:
        top_suggestion = suggestions[0]
        return {
            'suggestions': suggestions[:5],  # Top 5
            'top_suggestion': top_suggestion['suggestion'],
            'confidence': top_suggestion['confidence'],
            'reasoning': top_suggestion['reasoning'],
            'analysis_type': top_suggestion['type']
        }
    else:
        return {
            'suggestions': [],
            'top_suggestion': 'Nenhuma sugestÃ£o de alta confianÃ§a disponÃ­vel',
            'confidence': 0,
            'reasoning': 'Nenhum padrÃ£o de alta confianÃ§a identificado',
            'analysis_type': 'None'
        }

def check_guarantee_status(results):
    """
    Verifica se as "garantias" anteriores (sugestÃµes com alta confianÃ§a) foram bem-sucedidas.
    Isso ajuda a validar a precisÃ£o do sistema.
    """
    if 'last_guarantees' not in st.session_state:
        st.session_state.last_guarantees = []
    
    # Verificar garantias anteriores
    verified_guarantees = []
    for guarantee in st.session_state.last_guarantees:
        if guarantee['position'] < len(results):
            actual_result = results[guarantee['position']]
            predicted_correct = False
            
            # Verificar se a prediÃ§Ã£o estava correta
            if ('Vermelho' in guarantee['prediction'] or 'Banker' in guarantee['prediction'] or 'Home' in guarantee['prediction']) and actual_result == 'banker':
                predicted_correct = True
            elif ('Azul' in guarantee['prediction'] or 'Player' in guarantee['prediction'] or 'Away' in guarantee['prediction']) and actual_result == 'player':
                predicted_correct = True
            elif ('Amarelo' in guarantee['prediction'] or 'Tie' in guarantee['prediction'] or 'Draw' in guarantee['prediction']) and actual_result == 'tie':
                predicted_correct = True
            # PrediÃ§Ãµes especÃ­ficas apenas - removido suporte para mÃºltiplas opÃ§Ãµes
            
            guarantee['correct'] = predicted_correct
            guarantee['actual_result'] = actual_result
            verified_guarantees.append(guarantee)
    
    return verified_guarantees

def add_guarantee(prediction, confidence, reasoning):
    """
    Adiciona uma nova garantia (prediÃ§Ã£o de alta confianÃ§a) para verificaÃ§Ã£o futura.
    """
    if 'last_guarantees' not in st.session_state:
        st.session_state.last_guarantees = []
    
    new_guarantee = {
        'prediction': prediction,
        'confidence': confidence,
        'reasoning': reasoning,
        'position': 0,  # PosiÃ§Ã£o 0 = prÃ³ximo resultado
        'timestamp': None  # Simplified without pandas
    }
    
    # Incrementar posiÃ§Ãµes das garantias existentes
    for g in st.session_state.last_guarantees:
        g['position'] += 1
    
    # Adicionar nova garantia
    st.session_state.last_guarantees.insert(0, new_guarantee)
    
    # Manter apenas as Ãºltimas 10 garantias
    st.session_state.last_guarantees = st.session_state.last_guarantees[-10:]

# --- Interface Streamlit ---

def main():
    st.set_page_config(
        page_title="Bac Bo Pro Analyzer",
        page_icon="âš½",
        layout="wide"
    )
    
    # Inicializar estado da sessÃ£o
    if 'results' not in st.session_state:
        st.session_state.results = []
    
    # TÃ­tulo e descriÃ§Ã£o
    st.title("âš½ Bac Bo Pro Analyzer")
    st.markdown("### Sistema AvanÃ§ado de AnÃ¡lise de PadrÃµes e SugestÃµes de Apostas")
    
    # Sidebar para adicionar resultados
    with st.sidebar:
        st.header("ðŸ“Š Adicionar Resultado")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("ðŸ”´ BANKER", use_container_width=True):
                st.session_state.results.insert(0, 'banker')
                if len(st.session_state.results) > MAX_HISTORY_TO_STORE:
                    st.session_state.results = st.session_state.results[:MAX_HISTORY_TO_STORE]
                st.rerun()
        
        with col2:
            if st.button("ðŸ”µ PLAYER", use_container_width=True):
                st.session_state.results.insert(0, 'player')
                if len(st.session_state.results) > MAX_HISTORY_TO_STORE:
                    st.session_state.results = st.session_state.results[:MAX_HISTORY_TO_STORE]
                st.rerun()
        
        with col3:
            if st.button("ðŸŸ¡ TIE", use_container_width=True):
                st.session_state.results.insert(0, 'tie')
                if len(st.session_state.results) > MAX_HISTORY_TO_STORE:
                    st.session_state.results = st.session_state.results[:MAX_HISTORY_TO_STORE]
                st.rerun()
        
        st.markdown("---")
        
        # BotÃ£o para limpar histÃ³rico
        if st.button("ðŸ—‘ï¸ Limpar HistÃ³rico", type="secondary"):
            st.session_state.results = []
            st.session_state.last_guarantees = []
            st.rerun()
        
        # EstatÃ­sticas rÃ¡pidas
        if st.session_state.results:
            st.markdown("### ðŸ“ˆ EstatÃ­sticas RÃ¡pidas")
            recent_results = st.session_state.results[:NUM_RECENT_RESULTS_FOR_ANALYSIS]
            
            banker_count = sum(1 for r in recent_results if r == 'banker')
            player_count = sum(1 for r in recent_results if r == 'player')  
            tie_count = sum(1 for r in recent_results if r == 'tie')
            
            st.metric("ðŸ”´ Banker", banker_count)
            st.metric("ðŸ”µ Player", player_count)
            st.metric("ðŸŸ¡ Tie", tie_count)
            st.metric("ðŸ“Š Total", len(recent_results))
    
    # ConteÃºdo principal
    if not st.session_state.results:
        st.info("ðŸ‘‹ Bem-vindo! Adicione alguns resultados na barra lateral para comeÃ§ar a anÃ¡lise.")
        st.markdown("""
        **Como usar:**
        1. ðŸ”´ Clique em **BANKER** quando a casa ganhar
        2. ðŸ”µ Clique em **PLAYER** quando o visitante ganhar  
        3. ðŸŸ¡ Clique em **TIE** quando houver empate
        4. ðŸ“Š Veja as anÃ¡lises e sugestÃµes em tempo real
        """)
        return
    
    # Verificar status das garantias
    verified_guarantees = check_guarantee_status(st.session_state.results)
    
    # Mostrar status das garantias recentes se existirem
    if verified_guarantees:
        st.markdown("### ðŸŽ¯ Status das Garantias Recentes")
        for guarantee in verified_guarantees[:3]:  # Mostrar apenas as 3 mais recentes
            if guarantee.get('correct'):
                st.success(f"âœ… ACERTOU: {guarantee['prediction']} (ConfianÃ§a: {guarantee['confidence']:.1f}%) - Resultado: {guarantee['actual_result'].upper()}")
            else:
                st.error(f"âŒ ERROU: {guarantee['prediction']} (ConfianÃ§a: {guarantee['confidence']:.1f}%) - Resultado: {guarantee['actual_result'].upper()}")
    
    # Layout principal
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # HistÃ³rico visual
        st.markdown("### ðŸ“‹ HistÃ³rico dos Ãšltimos 100 Resultados")
        
        display_results = st.session_state.results[:NUM_HISTORY_TO_DISPLAY]
        if display_results:
            # Organizar em linhas de N emojis cada
            rows = []
            for i in range(0, len(display_results), EMOJIS_PER_ROW):
                row_results = display_results[i:i + EMOJIS_PER_ROW]
                row_emojis = [get_color_emoji(get_color(r)) for r in row_results]
                rows.append(' '.join(row_emojis))
            
            for row in rows:
                st.markdown(f"<div style='font-size: 24px; text-align: center; margin: 5px 0;'>{row}</div>", 
                           unsafe_allow_html=True)
        
        # AnÃ¡lises detalhadas
        st.markdown("### ðŸ” AnÃ¡lises Detalhadas")
        
        # AnÃ¡lise Surf
        surf_data = analyze_surf(st.session_state.results)
        st.markdown("#### ðŸ„ AnÃ¡lise Surf (SequÃªncias)")
        
        surf_col1, surf_col2, surf_col3 = st.columns(3)
        with surf_col1:
            st.metric("ðŸ”´ Banker Atual", surf_data['banker_sequence'], delta=f"Max: {surf_data['max_banker_sequence']}")
        with surf_col2:
            st.metric("ðŸ”µ Player Atual", surf_data['player_sequence'], delta=f"Max: {surf_data['max_player_sequence']}")
        with surf_col3:
            st.metric("ðŸŸ¡ Tie Atual", surf_data['tie_sequence'], delta=f"Max: {surf_data['max_tie_sequence']}")
        
        # AnÃ¡lise de Cores
        color_data = analyze_colors(st.session_state.results)
        st.markdown("#### ðŸŽ¨ AnÃ¡lise de Cores (Ãšltimos 27)")
        
        color_col1, color_col2, color_col3, color_col4 = st.columns(4)
        with color_col1:
            st.metric("ðŸ”´ Vermelhos", color_data['red'])
        with color_col2:
            st.metric("ðŸ”µ Azuis", color_data['blue'])
        with color_col3:
            st.metric("ðŸŸ¡ Amarelos", color_data['yellow'])
        with color_col4:
            st.metric("ðŸ“ˆ Streak Atual", color_data['streak'], delta=color_data['current_color'].capitalize())
        
        # PadrÃµes Complexos
        patterns, block_patterns = find_complex_patterns(st.session_state.results)
        if patterns:
            st.markdown("#### ðŸ§© PadrÃµes Complexos Identificados")
            
            # Filtrar e exibir apenas os padrÃµes mais relevantes
            relevant_patterns = {k: v for k, v in patterns.items() if v >= 2}
            if relevant_patterns:
                # Criar tabela manualmente sem pandas
                pattern_data = []
                for pattern, count in sorted(relevant_patterns.items(), key=lambda x: x[1], reverse=True):
                    relevancia = 'ðŸ”¥' if count >= 4 else 'âš¡' if count >= 3 else 'ðŸ“Š'
                    pattern_data.append([pattern, count, relevancia])
                
                # Exibir como tabela
                st.markdown("| PadrÃ£o | OcorrÃªncias | RelevÃ¢ncia |")
                st.markdown("|--------|-------------|------------|")
                for row in pattern_data:
                    st.markdown(f"| {row[0]} | {row[1]} | {row[2]} |")
            else:
                st.info("Nenhum padrÃ£o complexo significativo encontrado ainda.")
    
    with col2:
        # SugestÃµes da IA
        st.markdown("### ðŸ¤– SugestÃµes da IA")
        
        ai_suggestions = generate_ai_suggestions(st.session_state.results)
        
        if ai_suggestions['suggestions']:
            # SugestÃ£o principal
            st.markdown("#### ðŸŽ¯ SugestÃ£o Principal")
            confidence_color = "ðŸŸ¢" if ai_suggestions['confidence'] > 80 else "ðŸŸ¡" if ai_suggestions['confidence'] > 60 else "ðŸ”´"
            
            st.markdown(f"""
            **{confidence_color} {ai_suggestions['top_suggestion']}**
            
            **ConfianÃ§a:** {ai_suggestions['confidence']:.1f}%
            
            **AnÃ¡lise:** {ai_suggestions['analysis_type']}
            
            **Motivo:** {ai_suggestions['reasoning']}
            """)
            
            # Adicionar como garantia se confianÃ§a for alta
            if ai_suggestions['confidence'] > 85:
                st.warning("âš ï¸ **ALTA CONFIANÃ‡A** - SugestÃ£o adicionada como 'Garantia' para verificaÃ§Ã£o!")
                add_guarantee(ai_suggestions['top_suggestion'], ai_suggestions['confidence'], ai_suggestions['reasoning'])
            
            # Outras sugestÃµes
            if len(ai_suggestions['suggestions']) > 1:
                st.markdown("#### ðŸ“‹ Outras SugestÃµes")
                for i, suggestion in enumerate(ai_suggestions['suggestions'][1:], 2):
                    with st.expander(f"{i}Â° SugestÃ£o (ConfianÃ§a: {suggestion['confidence']:.1f}%)"):
                        st.write(f"**{suggestion['suggestion']}**")
                        st.write(f"*Motivo:* {suggestion['reasoning']}")
                        st.write(f"*AnÃ¡lise:* {suggestion['type']}")
        else:
            st.info("ðŸ“Š Adicione mais resultados para obter sugestÃµes de IA.")
        
        # AnÃ¡lise de Probabilidade de Quebra
        st.markdown("### âš¡ AnÃ¡lise de Quebra")
        break_data = analyze_break_probability(st.session_state.results)
        
        if break_data['confidence'] > 0:
            st.markdown(f"""
            **SequÃªncia Atual:** {break_data['sequence_length']} ({break_data['current_color'].capitalize()})
            
            **Probabilidade de Quebra:** {break_data['break_probability']}%
            
            **SugestÃ£o:** {break_data['suggestion']}
            
            **ConfianÃ§a:** {break_data['confidence']}%
            """)
        
        # AnÃ¡lise de Ties
        st.markdown("### ðŸŸ¡ AnÃ¡lise de Ties")
        tie_data = analyze_tie_patterns(st.session_state.results)
        
        if tie_data['confidence'] > 0:
            tie_col1, tie_col2 = st.columns(2)
            with tie_col1:
                st.metric("Ties (27)", tie_data['ties_in_last_27'])
                st.metric("Ãšltimo Tie", f"HÃ¡ {tie_data['last_tie_position']} jogos" if tie_data['last_tie_position'] != -1 else "Nenhum")
            with tie_col2:
                st.metric("FrequÃªncia", f"{tie_data['tie_frequency']}%")
                st.metric("Esperado", f"{tie_data['expected_ties']:.1f}")
            
            if tie_data['confidence'] > 60:
                st.markdown(f"**ðŸ’¡ {tie_data['suggestion']}** (ConfianÃ§a: {tie_data['confidence']:.1f}%)")

if __name__ == "__main__":
    main()
