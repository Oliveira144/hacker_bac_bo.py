import streamlit as st
import collections

# --- Constantes e Funções Auxiliares ---
NUM_RECENT_RESULTS_FOR_ANALYSIS = 27
MAX_HISTORY_TO_STORE = 1000
NUM_HISTORY_TO_DISPLAY = 100 # Número de resultados do histórico a serem exibidos
EMOJIS_PER_ROW = 9 # Quantos emojis por linha no histórico horizontal
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
    """Retorna o emoji correspondente à cor."""
    if color == 'red':
        return '🔴'
    elif color == 'blue':
        return '🔵'
    elif color == 'yellow':
        return '🟡'
    return ''

def get_result_emoji(result_type):
    """Retorna o emoji correspondente ao tipo de resultado. Agora retorna uma string vazia para remover os ícones."""
    return ''

# --- Funções de Análise ---

def analyze_surf(results):
    """
    Analisa os padrões de "surf" (sequências de Home/Away/Draw)
    nos últimos N resultados para 'current' e no histórico completo para 'max'.
    """
    relevant_results = results[:NUM_RECENT_RESULTS_FOR_ANALYSIS]

    current_banker_sequence = 0
    current_player_sequence = 0
    current_tie_sequence = 0

    if results:
        # A sequência atual é sempre do resultado mais recente (results[0])
        current_result = results[0]
        for r in results:  # Usar todo o histórico para sequência atual
            if r == current_result:
                if current_result == 'banker':
                    current_banker_sequence += 1
                elif current_result == 'player':
                    current_player_sequence += 1
                else: # tie
                    current_tie_sequence += 1
            else:
                break

    # Calcular sequências máximas em todo o histórico disponível para maior precisão
    max_banker_sequence = 0
    max_player_sequence = 0
    max_tie_sequence = 0

    temp_banker_seq = 0
    temp_player_seq = 0
    temp_tie_seq = 0

    for res in results: # Percorre TODOS os resultados (histórico completo) para o máximo
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
    """Analisa a contagem e as sequências de cores nos últimos N resultados."""
    relevant_results = results[:NUM_RECENT_RESULTS_FOR_ANALYSIS]
    if not relevant_results:
        return {'red': 0, 'blue': 0, 'yellow': 0, 'current_color': '', 'streak': 0, 'color_pattern_27': ''}

    color_counts = {'red': 0, 'blue': 0, 'yellow': 0}

    for result in relevant_results:
        color = get_color(result)
        color_counts[color] += 1

    current_color = get_color(results[0]) if results else ''
    streak = 0
    for result in results: # Streak é sempre do resultado mais recente no histórico completo
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
    Identifica padrões de quebra e padrões específicos (2x2, 3x3, 3x1, 2x1, etc.)
    nos últimos N resultados, incluindo os novos padrões.
    Os nomes dos padrões agora são concisos, sem exemplos ou emojis.
    """
    patterns = collections.defaultdict(int)
    relevant_results = results[:NUM_RECENT_RESULTS_FOR_ANALYSIS]

    # Converte resultados para cores para facilitar a análise de padrões
    colors = [get_color(r) for r in relevant_results]

    for i in range(len(colors) - 1):
        color1 = colors[i]
        color2 = colors[i+1]

        # 1. Quebra Simples
        if color1 != color2:
            patterns[f"Quebra Simples ({color1.capitalize()} para {color2.capitalize()})"] += 1

        # Verificar padrões que envolvem 3 ou mais resultados
        if i < len(colors) - 2:
            color3 = colors[i+2]

            # 2. Padrões 2x1 (Ex: R R B)
            if color1 == color2 and color1 != color3:
                patterns[f"2x1 ({color1.capitalize()} para {color3.capitalize()})"] += 1

            # 3. Zig-Zag / Padrão Alternado (Ex: R B R)
            if color1 != color2 and color2 != color3 and color1 == color3:
                patterns[f"Zig-Zag / Alternado ({color1.capitalize()}-{color2.capitalize()}-{color3.capitalize()})"] += 1

            # 4. Alternância com Tie no Meio (X Draw Y - Ex: R Y B)
            if color2 == 'yellow' and color1 != 'yellow' and color3 != 'yellow' and color1 != color3:
                patterns[f"Alternância c/ Tie no Meio ({color1.capitalize()}-Tie-{color3.capitalize()})"] += 1

            # 5. Padrão Onda 1-2-1 (Ex: R B B R) - variação de espelho ou zig-zag
            if i < len(colors) - 3:
                color4 = colors[i+3]
                if color1 != color2 and color2 == color3 and color3 != color4 and color1 == color4:
                    patterns[f"Padrão Onda 1-2-1 ({color1.capitalize()}-{color2.capitalize()}-{color3.capitalize()}-{color4.capitalize()})"] += 1

        if i < len(colors) - 3:
            color3 = colors[i+2]
            color4 = colors[i+3]

            # 6. Padrões 3x1 (Ex: R R R B)
            if color1 == color2 and color2 == color3 and color1 != color4:
                patterns[f"3x1 ({color1.capitalize()} para {color4.capitalize()})"] += 1

            # 7. Padrões 2x2 (Ex: R R B B)
            if color1 == color2 and color3 == color4 and color1 != color3:
                patterns[f"2x2 ({color1.capitalize()} para {color3.capitalize()})"] += 1

            # 8. Padrão de Espelho (Ex: R B B R)
            if color1 != color2 and color2 == color3 and color1 == color4:
                patterns[f"Padrão Espelho ({color1.capitalize()}-{color2.capitalize()}-{color3.capitalize()}-{color4.capitalize()})"] += 1

        if i < len(colors) - 5:
            color3 = colors[i+2]
            color4 = colors[i+3]
            color5 = colors[i+4]
            color6 = colors[i+5]

            # 9. Padrões 3x3 (Ex: R R R B B B)
            if color1 == color2 and color2 == color3 and color4 == color5 and color5 == color6 and color1 != color4:
                patterns[f"3x3 ({color1.capitalize()} para {color4.capitalize()})"] += 1

    # 10. Duplas Repetidas (Ex: R R, B B, Y Y) - Contagem de ocorrências de duplas
    for i in range(len(colors) - 1):
        if colors[i] == colors[i+1]:
            patterns[f"Dupla Repetida ({colors[i].capitalize()})"] += 1

    # Padrão de Reversão / Alternância de Blocos (Ex: RR BB RR BB)
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
                            patterns[f"Alternância de Blocos {block_size}x{block_size} ({block1_colors[0].capitalize()}-{block2_colors[0].capitalize()})"] += 1
                            block_pattern_keys.append(f"Alternância de Blocos {block_size}x{block_size} ({block1_colors[0].capitalize()}-{block2_colors[0].capitalize()})")

    return dict(patterns), block_pattern_keys

def analyze_break_probability(results):
    """
    Analisa a probabilidade de quebra das sequências atuais baseada no histórico.
    Calcula quando uma sequência é mais provável de quebrar.
    """
    if len(results) < MIN_RESULTS_FOR_SUGGESTION:
        return {'break_probability': 0, 'sequence_length': 0, 'suggestion': '', 'confidence': 0}

    surf_analysis = analyze_surf(results)
    current_color = get_color(results[0]) if results else ''

    # Determine a sequência atual baseada na cor
    if current_color == 'red':
        current_sequence = surf_analysis['banker_sequence']
        max_sequence = surf_analysis['max_banker_sequence']
    elif current_color == 'blue':
        current_sequence = surf_analysis['player_sequence']
        max_sequence = surf_analysis['max_player_sequence']
    else: # yellow
        current_sequence = surf_analysis['tie_sequence']
        max_sequence = surf_analysis['max_tie_sequence']

    # Calcular probabilidade de quebra baseada no histórico
    if max_sequence == 0:
        break_probability = 50  # Default quando não há histórico
    else:
        # Quanto mais próximo do máximo histórico, maior a probabilidade de quebra
        break_probability = min(90, (current_sequence / max_sequence) * 100)

    # Sugestão baseada na probabilidade de quebra - sempre uma cor específica
    if break_probability > 70:
        if current_color == 'red':
            suggestion = "Apostar em Azul"
        elif current_color == 'blue':
            suggestion = "Apostar em Vermelho"
        else:
            suggestion = "Apostar em Vermelho"
        confidence = min(95, break_probability + 10)
    elif break_probability > 50:
        suggestion = "Possível quebra em breve"
        confidence = break_probability
    else:
        suggestion = f"Sequência {current_color.capitalize()} pode continuar"
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
    Analisa padrões específicos relacionados aos empates.
    Identifica quando os empates são mais prováveis de ocorrer.
    """
    if len(results) < MIN_RESULTS_FOR_SUGGESTION:
        return {'ties_in_last_27': 0, 'last_tie_position': -1, 'tie_frequency': 0, 'suggestion': '', 'confidence': 0}

    relevant_results = results[:NUM_RECENT_RESULTS_FOR_ANALYSIS]
    ties_count = sum(1 for r in relevant_results if r == 'tie')

    # Encontrar a posição do último empate
    last_tie_position = -1
    for i, result in enumerate(results):
        if result == 'tie':
            last_tie_position = i
            break

    # Calcular frequência de empates (esperada: ~11% ou 3/27)
    expected_ties = NUM_RECENT_RESULTS_FOR_ANALYSIS * 0.11  # ~3 empates esperados
    tie_frequency = (ties_count / NUM_RECENT_RESULTS_FOR_ANALYSIS) * 100

    # Análise de padrões RBD (Red-Blue-Draw)
    rbd_patterns = 0
    for i in range(len(results) - 2):
        if ((results[i] == 'banker' and results[i+1] == 'player') or
            (results[i] == 'player' and results[i+1] == 'banker')) and results[i+2] == 'tie':
            rbd_patterns += 1

    # Sugestão baseada na análise
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
        suggestion = "Padrão de empates normal"
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
    Gera sugestões de apostas usando IA baseada em todos os tipos de análise.
    Combina múltiplas análises para fornecer sugestões mais precisas.
    """
    if len(results) < MIN_RESULTS_FOR_SUGGESTION:
        return {'suggestions': [], 'top_suggestion': '', 'confidence': 0, 'reasoning': 'Dados insuficientes para análise'}

    suggestions = []

    # 1. Análise Surf
    surf_analysis = analyze_surf(results)
    break_analysis = analyze_break_probability(results)

    if break_analysis['confidence'] > 70:
        suggestions.append({
            'type': 'Break Analysis',
            'suggestion': break_analysis['suggestion'],
            'confidence': break_analysis['confidence'],
            'reasoning': f"Sequência atual de {break_analysis['sequence_length']} com {break_analysis['break_probability']}% de probabilidade de quebra"
        })

    # 2. Análise de Padrões Complexos
    complex_patterns, block_patterns = find_complex_patterns(results)

    # Procurar por padrões de alta confiança
    high_confidence_patterns = []

    for pattern, count in complex_patterns.items():
        if count >= 3:  # Padrão que ocorreu 3+ vezes
            confidence = min(95, count * 15)
            if '2x1' in pattern or '3x1' in pattern:
                # Extrair direção da quebra
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
                    suggestion_text = f"Padrão {pattern} identificado"

                high_confidence_patterns.append({
                    'type': 'Pattern Analysis',
                    'suggestion': suggestion_text,
                    'confidence': confidence,
                    'reasoning': f"Padrão {pattern} ocorreu {count} vezes nos últimos {NUM_RECENT_RESULTS_FOR_ANALYSIS} resultados"
                })

    suggestions.extend(high_confidence_patterns)

    # 3. Análise de Ties
    tie_analysis = analyze_tie_patterns(results)
    if tie_analysis['confidence'] > 65:
        suggestions.append({
            'type': 'Draw Analysis',
            'suggestion': tie_analysis['suggestion'],
            'confidence': tie_analysis['confidence'],
            'reasoning': f"Ties: {tie_analysis['ties_in_last_27']}/27 ({tie_analysis['tie_frequency']}%), último empate há {tie_analysis['last_tie_position']} jogos"
        })

    # 4. Análise de Cores/Balanceamento
    color_analysis = analyze_colors(results)
    total_relevant = NUM_RECENT_RESULTS_FOR_ANALYSIS
    expected_per_color = total_relevant / 3  # ~9 para cada cor

    # Identificar cor mais deficitária
    color_deficits = {
        'red': expected_per_color - color_analysis['red'],
        'blue': expected_per_color - color_analysis['blue'],
        'yellow': expected_per_color - color_analysis['yellow']
    }

    most_deficit_color = max(color_deficits.keys(), key=lambda k: color_deficits[k])
    deficit_amount = color_deficits[most_deficit_color]

    if deficit_amount > 3:  # Déficit significativo
        color_names = {'red': 'Vermelho', 'blue': 'Azul', 'yellow': 'Amarelo'}
        suggestions.append({
            'type': 'Color Balance',
            'suggestion': f"Apostar em {color_names[most_deficit_color]}",
            'confidence': min(85, deficit_amount * 8),
            'reasoning': f"{color_names[most_deficit_color]} com déficit de {deficit_amount:.1f} ocorrências"
        })

    # Ordenar sugestões por confiança
    suggestions.sort(key=lambda x: x['confidence'], reverse=True)

    # Determinar sugestão principal
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
            'top_suggestion': 'Nenhuma sugestão de alta confiança disponível',
            'confidence': 0,
            'reasoning': 'Nenhum padrão de alta confiança identificado',
            'analysis_type': 'None'
        }

def check_guarantee_status(results):
    """
    Verifica se as "garantias" anteriores (sugestões com alta confiança) foram bem-sucedidas.
    Isso ajuda a validar a precisão do sistema.
    """
    if 'last_guarantees' not in st.session_state:
        st.session_state.last_guarantees = []

    # Verificar garantias anteriores
    verified_guarantees = []
    for guarantee in st.session_state.last_guarantees:
        if guarantee['position'] < len(results):
            actual_result = results[guarantee['position']]
            predicted_correct = False

            # Verificar se a predição estava correta
            if ('Vermelho' in guarantee['prediction'] or 'Banker' in guarantee['prediction'] or 'Home' in guarantee['prediction']) and actual_result == 'banker':
                predicted_correct = True
            elif ('Azul' in guarantee['prediction'] or 'Player' in guarantee['prediction'] or 'Away' in guarantee['prediction']) and actual_result == 'player':
                predicted_correct = True
            elif ('Amarelo' in guarantee['prediction'] or 'Tie' in guarantee['prediction'] or 'Draw' in guarantee['prediction']) and actual_result == 'tie':
                predicted_correct = True
            # Predições específicas apenas - removido suporte para múltiplas opções

            guarantee['correct'] = predicted_correct
            guarantee['actual_result'] = actual_result
            verified_guarantees.append(guarantee)

    return verified_guarantees

def add_guarantee(prediction, confidence, reasoning):
    """
    Adiciona uma nova garantia (predição de alta confiança) para verificação futura.
    """
    if 'last_guarantees' not in st.session_state:
        st.session_state.last_guarantees = []

    new_guarantee = {
        'prediction': prediction,
        'confidence': confidence,
        'reasoning': reasoning,
        'position': 0,  # Posição 0 = próximo resultado
        'timestamp': None  # Simplified without pandas
    }

    # Incrementar posições das garantias existentes
    for g in st.session_state.last_guarantees:
        g['position'] += 1

    # Adicionar nova garantia
    st.session_state.last_guarantees.insert(0, new_guarantee)

    # Manter apenas as últimas 10 garantias
    st.session_state.last_guarantees = st.session_state.last_guarantees[-10:]

# --- Interface Streamlit ---

def main():
    st.set_page_config(
        page_title="Bac Bo Pro Analyzer",
        page_icon="⚽",
        layout="wide"
    )

    # Inicializar estado da sessão
    if 'results' not in st.session_state:
        st.session_state.results = []

    # Título e descrição
    st.title("⚽ Bac Bo Pro Analyzer")
    st.markdown("### Sistema Avançado de Análise de Padrões e Sugestões de Apostas")

    # Sidebar para adicionar resultados
    with st.sidebar:
        st.header("📊 Adicionar Resultado")

        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("🔴 BANKER", use_container_width=True):
                st.session_state.results.insert(0, 'banker')
                if len(st.session_state.results) > MAX_HISTORY_TO_STORE:
                    st.session_state.results = st.session_state.results[:MAX_HISTORY_TO_STORE]
                st.rerun()

        with col2:
            if st.button("🔵 PLAYER", use_container_width=True):
                st.session_state.results.insert(0, 'player')
                if len(st.session_state.results) > MAX_HISTORY_TO_STORE:
                    st.session_state.results = st.session_state.results[:MAX_HISTORY_TO_STORE]
                st.rerun()

        with col3:
            if st.button("🟡 TIE", use_container_width=True):
                st.session_state.results.insert(0, 'tie')
                if len(st.session_state.results) > MAX_HISTORY_TO_STORE:
                    st.session_state.results = st.session_state.results[:MAX_HISTORY_TO_STORE]
                st.rerun()

        st.markdown("---")

        # Botão para limpar histórico
        if st.button("🗑️ Limpar Histórico", type="secondary"):
            st.session_state.results = []
            st.session_state.last_guarantees = []
            st.rerun()

        # Estatísticas rápidas
        if st.session_state.results:
            st.markdown("### 📈 Estatísticas Rápidas")
            recent_results = st.session_state.results[:NUM_RECENT_RESULTS_FOR_ANALYSIS]

            banker_count = sum(1 for r in recent_results if r == 'banker')
            player_count = sum(1 for r in recent_results if r == 'player')
            tie_count = sum(1 for r in recent_results if r == 'tie')

            st.metric("🔴 Banker", banker_count)
            st.metric("🔵 Player", player_count)
            st.metric("🟡 Tie", tie_count)
            st.metric("📊 Total", len(recent_results))

    # Conteúdo principal
    if not st.session_state.results:
        st.info("👋 Bem-vindo! Adicione alguns resultados na barra lateral para começar a análise.")
        st.markdown("""
        **Como usar:**
        1. 🔴 Clique em **BANKER** quando a casa ganhar
        2. 🔵 Clique em **PLAYER** quando o visitante ganhar
        3. 🟡 Clique em **TIE** quando houver empate
        4. 📊 Veja as análises e sugestões em tempo real
        """)
        return

    # Verificar status das garantias
    verified_guarantees = check_guarantee_status(st.session_state.results)

    # Mostrar status das garantias recentes se existirem
    if verified_guarantees:
        st.markdown("### 🎯 Status das Garantias Recentes")
        for guarantee in verified_guarantees[:3]:  # Mostrar apenas as 3 mais recentes
            if guarantee.get('correct'):
                st.success(f"✅ ACERTOU: {guarantee['prediction']} (Confiança: {guarantee['confidence']:.1f}%) - Resultado: {guarantee['actual_result'].upper()}")
            else:
                st.error(f"❌ ERROU: {guarantee['prediction']} (Confiança: {guarantee['confidence']:.1f}%) - Resultado: {guarantee['actual_result'].upper()}")

    # Layout principal
    col1, col2 = st.columns([2, 1])

    with col1:
        # Histórico visual
        st.markdown("### 📋 Histórico dos Últimos 100 Resultados")

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

        # Análises detalhadas
        st.markdown("### 🔍 Análises Detalhadas")

        # Análise Surf
        surf_data = analyze_surf(st.session_state.results)
        st.markdown("#### 🏄 Análise Surf (Sequências)")

        surf_col1, surf_col2, surf_col3 = st.columns(3)
        with surf_col1:
            st.metric("🔴 Banker Atual", surf_data['banker_sequence'], delta=f"Max: {surf_data['max_banker_sequence']}")
        with surf_col2:
            st.metric("🔵 Player Atual", surf_data['player_sequence'], delta=f"Max: {surf_data['max_player_sequence']}")
        with surf_col3:
            st.metric("🟡 Tie Atual", surf_data['tie_sequence'], delta=f"Max: {surf_data['max_tie_sequence']}")

        # Análise de Cores
        color_data = analyze_colors(st.session_state.results)
        st.markdown("#### 🎨 Análise de Cores (Últimos 27)")

        color_col1, color_col2, color_col3, color_col4 = st.columns(4)
        with color_col1:
            st.metric("🔴 Vermelhos", color_data['red'])
        with color_col2:
            st.metric("🔵 Azuis", color_data['blue'])
        with color_col3:
            st.metric("🟡 Amarelos", color_data['yellow'])
        with color_col4:
            st.metric("📈 Streak Atual", color_data['streak'], delta=color_data['current_color'].capitalize())

        # Padrões Complexos
        patterns, block_patterns = find_complex_patterns(st.session_state.results)
        if patterns:
            st.markdown("#### 🧩 Padrões Complexos Identificados")

            # Filtrar e exibir apenas os padrões mais relevantes
            relevant_patterns = {k: v for k, v in patterns.items() if v >= 2}
            if relevant_patterns:
                # Criar tabela manualmente sem pandas
                pattern_data = []
                for pattern, count in sorted(relevant_patterns.items(), key=lambda x: x[1], reverse=True):
                    relevancia = '🔥' if count >= 4 else '⚡' if count >= 3 else '📊'
                    pattern_data.append([pattern, count, relevancia])

                # Exibir como tabela
                st.markdown("| Padrão | Ocorrências | Relevância |")
                st.markdown("|--------|-------------|------------|")
                for row in pattern_data:
                    st.markdown(f"| {row[0]} | {row[1]} | {row[2]} |")
            else:
                st.info("Nenhum padrão complexo significativo encontrado ainda.")

    with col2:
        # Sugestões da IA
        st.markdown("### 🤖 Sugestões da IA")

        ai_suggestions = generate_ai_suggestions(st.session_state.results)

        if ai_suggestions['suggestions']:
            # Sugestão principal
            st.markdown("#### 🎯 Sugestão Principal")
            confidence_color = "🟢" if ai_suggestions['confidence'] > 80 else "🟡" if ai_suggestions['confidence'] > 60 else "🔴"

            st.markdown(f"""
            **{confidence_color} {ai_suggestions['top_suggestion']}**

            **Confiança:** {ai_suggestions['confidence']:.1f}%

            **Análise:** {ai_suggestions['analysis_type']}

            **Motivo:** {ai_suggestions['reasoning']}
            """)

            # Adicionar como garantia se confiança for alta
            if ai_suggestions['confidence'] > 85:
                st.warning("⚠️ **ALTA CONFIANÇA** - Sugestão adicionada como 'Garantia' para verificação!")
                add_guarantee(ai_suggestions['top_suggestion'], ai_suggestions['confidence'], ai_suggestions['reasoning'])

            # Outras sugestões
            if len(ai_suggestions['suggestions']) > 1:
                st.markdown("#### 📋 Outras Sugestões")
                for i, suggestion in enumerate(ai_suggestions['suggestions'][1:], 2):
                    with st.expander(f"{i}° Sugestão (Confiança: {suggestion['confidence']:.1f}%)"):
                        st.write(f"**{suggestion['suggestion']}**")
                        st.write(f"*Motivo:* {suggestion['reasoning']}")
                        st.write(f"*Análise:* {suggestion['type']}")
        else:
            st.info("📊 Adicione mais resultados para obter sugestões de IA.")

        # Análise de Probabilidade de Quebra
        st.markdown("### ⚡ Análise de Quebra")
        break_data = analyze_break_probability(st.session_state.results)

        if break_data['confidence'] > 0:
            st.markdown(f"""
            **Sequência Atual:** {break_data['sequence_length']} ({break_data['current_color'].capitalize()})

            **Probabilidade de Quebra:** {break_data['break_probability']}%

            **Sugestão:** {break_data['suggestion']}

            **Confiança:** {break_data['confidence']}%
            """)

        # Análise de Ties
        st.markdown("### 🟡 Análise de Ties")
        tie_data = analyze_tie_patterns(st.session_state.results)

        if tie_data['confidence'] > 0:
            tie_col1, tie_col2 = st.columns(2)
            with tie_col1:
                st.metric("Ties (27)", tie_data['ties_in_last_27'])
                st.metric("Último Tie", f"Há {tie_data['last_tie_position']} jogos" if tie_data['last_tie_position'] != -1 else "Nenhum")
            with tie_col2:
                st.metric("Frequência", f"{tie_data['tie_frequency']}%")
                st.metric("Esperado", f"{tie_data['expected_ties']:.1f}")

            if tie_data['confidence'] > 60:
                st.markdown(f"**💡 {tie_data['suggestion']}** (Confiança: {tie_data['confidence']:.1f}%)")

if __name__ == "__main__":
    main()
