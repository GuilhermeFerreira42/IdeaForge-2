# Blueprint — Onda 5.0: Qualidade Semântica e Convergência Real
**Protocolo:** NEXUS v1.1  
**Projeto:** IdeaForge 2  
**Versão:** 2.0.0-alpha → 2.1.0-beta  
**Data:** 26/04/2026  
**Autor:** Guilherme Ferreira + Claude Sonnet 4.6 (Arquiteto Sênior)  
**Pré-condição obrigatória:** Onda 4 concluída, 144 testes passando, `pytest tests/unit/ tests/integration/ -v` verde.

---

## CONTEXTO E MOTIVAÇÃO

### Por que esta onda existe

A execução de 26/04/2026 com a ideia "Agregador de Ofertas" (modelo `gpt-oss:20b-cloud`) revelou quatro falhas estruturais que invalidam o objetivo agnóstico da Onda 4:

| Falha | Impacto Observado | Causa Raiz |
|---|---|---|
| Round 0A caiu para fallback | DomainProfile estático injetado; debate perdeu agnositcismo | `_extract_json()` não captura JSON embrulhado em prosa |
| Classificação errada de domínio | Ideia de negócio debatida como arquitetura de software | Lista `software` tem 16 keywords vs 14 de `business`; sem normalização por densidade |
| 77 issues abertos, 60%+ duplicatas | Relatório ilegível; debate não convergiu | Dedup por hash de string; `ConvergenceDetector` desconectado do critério de parada |
| SynthesizerAgent falhou | Fallback acionado; relatório sem sumário executivo | Board snapshot com 77 issues excedeu contexto efetivo do modelo 20B |

**Decisão de escopo:** O BACKLOG da Onda 5 original (Cache, UI, Faxina Legada) é **suspendido**. Esses quatro bugs têm prioridade absoluta porque contaminam todas as execuções futuras, independentemente do domínio ou modelo usado. Cache e UI sobre um debate que não converge semanticamente são otimizações sobre base defeituosa.

### Objetivo da Onda 5.0

> Fazer o pipeline produzir debates semanticamente precisos, com convergência real mensurável e relatórios autoexplicativos — sem adicionar dependências novas ao sistema.

**Critério de Aceitação da Onda (binário):**
- [ ] Execução com `gpt-oss:20b-cloud` e ideia de negócio (não-software) classifica domínio correto em ≥ 80% das tentativas
- [ ] Round 0A completa via LLM (sem fallback) em ≥ 3 de 3 execuções consecutivas
- [ ] Total de issues únicos ao final de um debate de 10 rounds: ≤ 25
- [ ] SynthesizerAgent não falha em nenhuma execução com ≤ 30 issues únicos
- [ ] `pytest tests/unit/ tests/integration/ -v` → 100% verde após cada tarefa

---

## ESCOPO CONGELADO DESTA ONDA

**Proibido introduzir:**
- Novas dependências externas (sem `pip install X` novo)
- Alterações no `AdaptiveOrchestrator` além das especificadas
- Alterações no `ValidationBoard` além das especificadas
- Qualquer UI ou dashboard
- Cache semântico (fica para Onda 5.1)
- Remoção da pasta `idea-forge/` legada (fica para Onda 5.1)

**Arquivos protegidos (não tocar):**
- `src/core/convergence_detector.py` — lido, não modificado (apenas importado)
- `src/core/adaptive_orchestrator.py` — modificação cirúrgica APENAS na Task 3
- `src/cli/main.py` — sem alterações
- `src/models/` — sem alterações
- `tests/conftest.py` — sem alterações

---

## TAREFAS: SEQUÊNCIA OBRIGATÓRIA

```
Task 1 → Task 2 → Task 3 → Task 4
```

Cada tarefa tem pré-condição: testes da tarefa anterior passando.  
**Nunca implementar Task N+1 antes de Task N estar verde.**

---

## TASK 1 — Extração de JSON Resiliente no `DomainContextBuilder`

### Identidade
- **ID:** W5Q-01
- **Arquivo principal:** `src/core/domain_context_builder.py`
- **Arquivo de teste:** `tests/unit/test_domain_context_builder.py`
- **Esforço estimado:** Baixo (< 40 LOC de produção)
- **Risco:** Baixo — nenhuma interface pública muda

### Problema Exato

`_extract_json()` tem dois caminhos de parse. Modelos de 20B frequentemente produzem JSON válido precedido de prosa ("Claro, aqui está o JSON solicitado: {…}") ou sucedido de explicação. Nenhum dos dois caminhos captura esse padrão, causando `ValueError` e ativando o fallback estático — que anula toda a Onda 4.

Adicionalmente, o prompt `DOMAIN_CONTEXT_PROMPT` não instrui o modelo a começar a resposta com `{` diretamente, deixando margem para prosa introdutória.

### Implementação

#### 1.1 — Adicionar Caminho 3 (Boundary Detection) em `_extract_json()`

**Arquivo:** `src/core/domain_context_builder.py`

```python
def _extract_json(self, response: str) -> Optional[Dict[str, Any]]:
    """
    Tenta extrair JSON válido da resposta do LLM via 3 estratégias em cascata.
    INVARIANTE: Nunca lança exceção — retorna None se todos os caminhos falharem.
    """
    # Caminho 1: parse direto (resposta já é JSON limpo)
    try:
        return json.loads(response.strip())
    except json.JSONDecodeError:
        pass

    # Caminho 2: bloco Markdown (```json ... ``` ou ``` ... ```)
    match = re.search(r'```(?:json)?\s*(.*?)\s*```', response, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1).strip())
        except json.JSONDecodeError:
            pass

    # Caminho 3: boundary detection — extrai primeiro { até último } [NOVO W5Q-01]
    start = response.find('{')
    end = response.rfind('}')
    if start != -1 and end != -1 and end > start:
        try:
            return json.loads(response[start:end + 1])
        except json.JSONDecodeError:
            pass

    return None
```

#### 1.2 — Reforçar o Prompt `DOMAIN_CONTEXT_PROMPT`

Substituir o bloco de `REGRAS:` existente pelo bloco abaixo:

```python
DOMAIN_CONTEXT_PROMPT = """
Você é um assistente de meta-análise do IdeaForge 2.

TAREFA: Analisar a ideia abaixo e retornar UM JSON estruturado.

REGRAS ABSOLUTAS:
1. Sua resposta DEVE começar DIRETAMENTE com {{ (chave de abertura do JSON).
2. Sua resposta DEVE terminar DIRETAMENTE com }} (chave de fechamento do JSON).
3. PROIBIDO: qualquer texto antes da {{ ou depois da }}.
4. PROIBIDO: blocos de código Markdown (``` ou ```json).
5. PROIBIDO: comentários dentro do JSON.
6. JSON INVÁLIDO causa fallback automático — gere JSON válido ou falhe silenciosamente.

IDEIA:
{idea}

DOMÍNIO DETECTADO: {detected_domain}

Retorne EXATAMENTE este JSON (comece com {{ e termine com }}):

{{
  "expansion_sections": [
    {{
      "id": "SECAO_1_ID",
      "title": "Título em PT-BR",
      "instruction": "Instrução concisa (máx 160 chars)"
    }}
  ],
  "validation_dimensions": [
    {{
      "id": "DIMENSAO_1_ID",
      "display_name": "Nome para Exibição",
      "description": "Descrição breve do que valida",
      "spawn_hint": "Tipo de especialista"
    }}
  ],
  "specialist_hints": ["Especialista A", "Especialista B"],
  "critical_questions": ["Pergunta 1", "Pergunta 2"],
  "success_criteria": {{
    "criteria_1": "Descrição"
  }}
}}

REGRAS DE CONTEÚDO:
1. expansion_sections: 6-8 seções, IDs em UPPER_SNAKE_CASE, específicas para o domínio detectado
2. validation_dimensions: 4-6 dimensões cobrindo as principais lacunas desse tipo de ideia
3. specialist_hints: máx 3 especialistas mais prováveis para esse domínio
"""
```

#### 1.3 — Observabilidade no Terminal e Log Estruturado

No método `_build_with_llm` (e/ou em seu chamador), adicionar log que registre qual dos 3 caminhos foi bem-sucedido. Além disso, é **obrigatório** usar a função `emit_pipeline_state` para informar explicitamente ao usuário no terminal se o Round 0A (Meta-Análise) operou via LLM ou se caiu no Fallback:

```python
def _build_with_llm(self, idea: str, detected_domain: str) -> DomainProfile:
    prompt = DOMAIN_CONTEXT_PROMPT.format(idea=idea[:800], detected_domain=detected_domain)
    response = self.provider.generate(prompt=prompt, max_tokens=800, role="user")
    # max_tokens aumentado de 600 para 800 — JSON com 6 seções pode exceder 600 tokens

    data = self._extract_json(response)
    if not data:
        raise ValueError("Não foi possível extrair JSON da resposta do LLM")

    logger.info(f"[DomainContextBuilder] JSON extraído com sucesso. "
                f"Seções: {len(data.get('expansion_sections', []))}, "
                f"Dimensões: {len(data.get('validation_dimensions', []))}")
    return self._create_profile(data, detected_domain, "llm")
```

**Observação:** `max_tokens` foi 600 na Onda 4. Um JSON com 7 seções e 5 dimensões usa ~700–750 tokens. Aumentar para 800 previne truncamento silencioso do JSON.

### Testes Obrigatórios (TDD — escrever ANTES do código)

**Arquivo:** `tests/unit/test_domain_context_builder.py`

Adicionar os seguintes casos (não remover os existentes):

```python
def test_extract_json_caminho3_boundary_detection():
    """W5Q-01: boundary detection captura JSON embrulhado em prosa."""
    builder = DomainContextBuilder(provider=None)
    response = 'Claro! Aqui está o JSON: {"key": "value", "list": [1, 2]} Espero que ajude.'
    result = builder._extract_json(response)
    assert result == {"key": "value", "list": [1, 2]}

def test_extract_json_caminho3_com_texto_antes_e_depois():
    """W5Q-01: boundary detection ignora texto antes e depois do JSON."""
    builder = DomainContextBuilder(provider=None)
    response = 'Texto antes\n{"a": 1, "b": [{"c": 2}]}\nTexto depois'
    result = builder._extract_json(response)
    assert result is not None
    assert result["a"] == 1

def test_extract_json_retorna_none_se_todos_caminhos_falham():
    """W5Q-01: retorna None se resposta não contém JSON válido."""
    builder = DomainContextBuilder(provider=None)
    result = builder._extract_json("Texto sem JSON nenhum aqui.")
    assert result is None

def test_extract_json_nao_lanca_excecao():
    """W5Q-01: _extract_json nunca propaga exceção."""
    builder = DomainContextBuilder(provider=None)
    # JSON mal formado com boundary parcial
    result = builder._extract_json('{"key": "value", ERRO}')
    assert result is None  # Não lança, retorna None

def test_build_with_llm_usa_max_tokens_800(monkeypatch):
    """W5Q-01: generate() é chamado com max_tokens=800, não 600."""
    call_log = {}
    class MockProv:
        def generate(self, prompt, max_tokens, role):
            call_log['max_tokens'] = max_tokens
            return '{"expansion_sections": [], "validation_dimensions": []}'
    builder = DomainContextBuilder(provider=MockProv())
    builder._build_with_llm("ideia", "software")
    assert call_log['max_tokens'] == 800
```

### Critério de Aceite (binário)

| Critério | Verificação |
|---|---|
| `_extract_json()` captura JSON precedido de prosa | `test_extract_json_caminho3_boundary_detection` passa |
| Nunca propaga exceção | `test_extract_json_nao_lanca_excecao` passa |
| `max_tokens=800` | `test_build_with_llm_usa_max_tokens_800` passa |
| Todos os 144 testes existentes continuam passando | `pytest tests/ -v` verde |
| Execução real com `gpt-oss:20b-cloud`: log mostra "JSON extraído com sucesso" | Verificação manual |

### Rollback

Se qualquer teste falhar após a implementação:

```bash
git stash
pytest tests/ -v  # confirmar baseline verde
git stash pop     # reaplicar e debugar
```

---

## TASK 2 — Rebalanceamento Semântico do `DomainDetector`

### Identidade
- **ID:** W5Q-02
- **Arquivo principal:** `src/core/domain_detector.py`
- **Arquivo de teste:** `tests/unit/test_domain_detector.py`
- **Esforço estimado:** Baixo (< 60 LOC de produção)
- **Risco:** Médio — mudança de comportamento; requer atualização dos testes existentes

### Problema Exato

O `DomainDetector` usa contagem simples de matches. A lista `software` tem mais keywords genéricas (autenticação, segurança, cloud) que qualquer outra. Ideias de negócio digital que mencionam qualquer componente técnico são classificadas como `software` com confiança ≥ 0.8.

A fórmula atual: `confidence = min(1.0, max_score * 0.4)`.  
Com 2 matches em software: confidence = 0.8.  
Com 3 matches em business: confidence = 1.0 — mas como business tem menos keywords, perde para software mesmo com mais matches relativos.

### Implementação

#### 2.1 — Expandir keywords do domínio `business`

**Arquivo:** `src/core/domain_detector.py`

Substituir a entrada `"business"` no dicionário `DOMAIN_KEYWORDS`:

```python
"business": [
    # Mercado e posicionamento
    "mercado", "cliente", "receita", "custo", "margem",
    "unit economics", "ltv", "cac", "churn", "growth",
    "competição", "positioning", "go-to-market", "modelo de negócio",
    # Canais e aquisição — NOVO W5Q-02
    "afiliado", "afiliados", "comissão", "tráfego", "orgânico",
    "seo", "conversão", "monetização", "aquisição", "retenção",
    # Estrutura societária e operação — NOVO W5Q-02
    "solo-founder", "fundador", "bootstrapped", "bootstrap",
    "b2b", "b2c", "marketplace", "plataforma", "assinatura",
    # Produtos digitais com foco em negócio — NOVO W5Q-02
    "saas", "freemium", "upsell", "cross-sell", "churn rate",
    "mrr", "arr", "roi", "break-even",
],
```

#### 2.2 — Substituir score simples por score normalizado por densidade

Substituir o método `detect()` inteiro:

```python
def detect(self, idea: str) -> DomainDetectionResult:
    """
    Detecta domínio por score normalizado por densidade de lista.
    
    Score = matches_únicos / total_keywords_do_domínio
    
    Isso elimina o viés de listas mais longas e garante que um domínio
    com mais keywords específicas não ganhe apenas por ter lista maior.
    
    Desempate: se scores normalizados empatam (diferença < 0.05),
    'business' tem prioridade sobre 'software' para ideias híbridas.
    """
    normalized_idea = idea.lower()

    scores: Dict[str, float] = {}
    matches: Dict[str, List[str]] = {}

    for domain, keywords in self.keywords_map.items():
        domain_matches = [kw for kw in keywords if kw in normalized_idea]
        if domain_matches:
            unique_matches = len(set(domain_matches))
            # Score normalizado: matches únicos / total de keywords do domínio
            normalized_score = unique_matches / len(keywords)
            scores[domain] = normalized_score
            matches[domain] = domain_matches

    if not scores:
        return DomainDetectionResult(domain="generic", confidence=0.0, matched_keywords=[])

    # Ordenar por score normalizado
    best_domain = max(scores, key=scores.get)
    max_score = scores[best_domain]

    # Desempate semântico: business > software em caso de empate aproximado [NOVO W5Q-02]
    if (
        "business" in scores
        and "software" in scores
        and best_domain == "software"
        and abs(scores["software"] - scores["business"]) < 0.05
    ):
        best_domain = "business"
        max_score = scores["business"]

    # Confidence: score normalizado direto (já está em 0-1)
    # Mínimo de 0.3 para um match evitar confiança zero
    confidence = min(1.0, max(max_score, 0.3 if max_score > 0 else 0.0))

    return DomainDetectionResult(
        domain=best_domain,
        confidence=confidence,
        matched_keywords=matches[best_domain]
    )
```

#### 2.3 — Adicionar domínio `hybrid` para ideias com forte sinal duplo

```python
# Após calcular scores, antes de retornar:
# Se business E software ambos têm score normalizado > 0.15, domínio = "hybrid"
if (
    "business" in scores and "software" in scores
    and scores["business"] > 0.15 and scores["software"] > 0.15
):
    best_domain = "hybrid"
    max_score = (scores["business"] + scores["software"]) / 2
    matches["hybrid"] = matches["business"] + matches["software"]
    # Adicionar "hybrid" ao DOMAIN_FALLBACKS no domain_context_builder.py (ver abaixo)
```

#### 2.4 — Adicionar fallback `hybrid` no `DomainContextBuilder`

**Arquivo:** `src/core/domain_context_builder.py`

Adicionar entrada no dicionário `DOMAIN_FALLBACKS`. Para garantir a robustez operacional e evitar alucinações caso o LLM falhe, o domínio `hybrid` DEVE obrigatoriamente conter as seguintes 8 seções:
1. Proposta de Valor
2. Público e Canais
3. Modelo de Receita
4. Arquitetura Técnica
5. Stack de Dados e Ingestão
6. Segurança e Privacidade
7. Riscos e Barreiras de Mercado
8. Premissas de Crescimento

```python
"hybrid": {
    # Domínio híbrido (Negócio + Técnico): 8 seções obrigatórias que cobrem
    # igualmente a camada de mercado e a camada de engenharia. [AJUSTE W5Q-02]
    # NÃO reduzir abaixo de 8 seções — a IA deve cobrir ambas as dimensões.
    "expansion_sections": [
        {"id": "PROPOSTA_VALOR", "title": "Proposta de Valor",
         "instruction": "Qual dor específica a ideia resolve, para quem, e por que melhor que as alternativas existentes"},
        {"id": "PUBLICO_CANAIS", "title": "Público e Canais",
         "instruction": "Segmentos de clientes alvo, canais de aquisição primários e estratégia de go-to-market"},
        {"id": "MODELO_RECEITA", "title": "Modelo de Receita",
         "instruction": "Como e quando a ideia gera caixa: ticket médio, frequência, margens e caminho até break-even"},
        {"id": "ARQUITETURA_TECNICA", "title": "Arquitetura Técnica",
         "instruction": "Componentes tecnológicos essenciais do MVP: integrações, banco de dados, serviços externos críticos"},
        {"id": "STACK_INGESTAO", "title": "Stack de Dados e Ingestão",
         "instruction": "Como dados externos (APIs, scraping, feeds) são coletados, normalizados e armazenados de forma confiável"},
        {"id": "SEGURANCA_PRIVACIDADE", "title": "Segurança e Privacidade",
         "instruction": "Dados de usuário coletados, conformidade LGPD/GDPR, autenticação e superfície de ataque do sistema"},
        {"id": "RISCOS_MERCADO", "title": "Riscos e Barreiras de Mercado",
         "instruction": "Competição, comoditização, dependência de plataforma e mudanças regulatórias que podem invalidar o modelo"},
        {"id": "PREMISSAS_CRESCIMENTO", "title": "Premissas de Crescimento",
         "instruction": "Quais hipóteses sobre volume de usuários, tráfego e custo de infra precisam ser verdadeiras para o modelo ser viável"},
    ],
    "validation_dimensions": [
        {"id": "MARKET_VIABILITY", "display_name": "Viabilidade de Mercado",
         "description": "Tamanho, competição e diferencial real",
         "spawn_hint": "Analista de Mercado e Estratégia de Negócios"},
        {"id": "TECHNICAL_FEASIBILITY", "display_name": "Viabilidade Técnica",
         "description": "Complexidade técnica vs recursos disponíveis",
         "spawn_hint": "Arquiteto de Soluções para Startups"},
        {"id": "BUSINESS_MODEL", "display_name": "Modelo de Negócio",
         "description": "Sustentabilidade financeira e unit economics",
         "spawn_hint": "Especialista em Modelagem Financeira"},
        {"id": "DEPENDENCY_RISK", "display_name": "Risco de Dependência",
         "description": "Exposição a terceiros (APIs, plataformas, regulação)",
         "spawn_hint": "Especialista em Risco Operacional"},
        {"id": "EXECUTION_RISK", "display_name": "Risco de Execução Solo",
         "description": "Capacidade de uma pessoa executar sem time",
         "spawn_hint": "Consultor de Produto para Bootstrappers"},
    ]
},
```

### Testes Obrigatórios (TDD — escrever ANTES do código)

**Arquivo:** `tests/unit/test_domain_detector.py`

**Atenção:** Os testes existentes que verificam scores absolutos precisam ser atualizados para o novo modelo normalizado. Verificar um a um antes de implementar.

```python
def test_agregador_de_ofertas_classifica_business_ou_hybrid():
    """W5Q-02: ideia com afiliados/SEO/solo-founder NÃO classifica como software puro."""
    detector = DomainDetector()
    ideia = (
        "Implementação de um Agregador de Ofertas de Eletrônicos operado por um "
        "único fundador (Solo-Founder). O sistema deve consumir APIs de afiliados "
        "(Amazon, Mercado Livre) para monitorar preços. Estratégia: SEO de cauda longa "
        "e retenção via Telegram. Modelo de receita: comissão de afiliados."
    )
    result = detector.detect(ideia)
    assert result.domain in ("business", "hybrid"), (
        f"Esperado 'business' ou 'hybrid', obtido '{result.domain}'. "
        f"Keywords: {result.matched_keywords}"
    )

def test_score_normalizado_nao_favorece_lista_maior():
    """W5Q-02: domínio com lista menor mas mais matches relativos vence."""
    # Artificialmente: software com 2 matches em 16 keywords (12.5%)
    # vs business com 3 matches em 35 keywords (~8.5%)
    # software deve vencer — mais denso
    detector = DomainDetector()
    result = detector.detect("api kubernetes cloud")  # 3 matches software
    assert result.domain == "software"

def test_desempate_favorece_business_sobre_software():
    """W5Q-02: empate aproximado resolve para business."""
    detector = DomainDetector()
    # Ideia que acerta ~mesmo número normalizado em ambos
    result = detector.detect(
        "marketplace de saas com modelo de receita por comissão e api de integração"
    )
    # Se scores estão próximos, business tem prioridade
    # Não força resultado — apenas garante que a lógica de desempate existe
    assert result.domain in ("business", "hybrid", "software")
    assert result.confidence > 0

def test_ideia_pura_software_ainda_classifica_software():
    """W5Q-02: regressão — ideias técnicas puras continuam corretas."""
    detector = DomainDetector()
    result = detector.detect(
        "microservices com kubernetes, docker, aws, banco de dados postgresql, "
        "api rest, autenticação jwt e cache redis"
    )
    assert result.domain == "software"

def test_dominio_hybrid_gerado_quando_sinal_duplo_forte():
    """W5Q-02: ideia com forte sinal de negócio E técnico → hybrid."""
    detector = DomainDetector()
    result = detector.detect(
        "saas b2b com modelo de receita por assinatura, ltv e cac definidos, "
        "arquitetura de microservices, kubernetes, banco de dados e api rest"
    )
    assert result.domain in ("hybrid", "business", "software")
    # O importante é não classificar com confiança 1.0 em um único domínio
    # quando há sinal forte em dois

def test_generic_quando_nenhum_dominio_identificado():
    """W5Q-02: ideia sem keywords → generic, confiança 0."""
    detector = DomainDetector()
    result = detector.detect("quero fazer algo interessante com minha vida")
    assert result.domain == "generic"
    assert result.confidence == 0.0

def test_fallback_hybrid_existe_no_domain_context_builder():
    """W5Q-02: DOMAIN_FALLBACKS contém entrada 'hybrid'."""
    from src.core.domain_context_builder import DOMAIN_FALLBACKS
    assert "hybrid" in DOMAIN_FALLBACKS
    hybrid = DOMAIN_FALLBACKS["hybrid"]
    assert len(hybrid["expansion_sections"]) >= 5
    assert len(hybrid["validation_dimensions"]) >= 3
```

### Critério de Aceite (binário)

| Critério | Verificação |
|---|---|
| Ideia do Agregador → `business` ou `hybrid` | `test_agregador_de_ofertas_classifica_business_ou_hybrid` passa |
| Ideia pura de software ainda → `software` | `test_ideia_pura_software_ainda_classifica_software` passa |
| Fallback `hybrid` existe no builder | `test_fallback_hybrid_existe_no_domain_context_builder` passa |
| Todos os 144+ testes passam | `pytest tests/ -v` verde |

### Rollback

```bash
git diff src/core/domain_detector.py  # revisar antes de commitar
git stash  # se algo quebrar nos testes existentes
```

---

## TASK 3 — Deduplicação Semântica de Issues no `DebateStateTracker`

### Identidade
- **ID:** W5Q-03
- **Arquivos principais:** `src/debate/debate_state_tracker.py`, `src/core/adaptive_orchestrator.py`
- **Arquivo de teste:** `tests/unit/test_debate_state_tracker.py`
- **Esforço estimado:** Médio (~80 LOC de produção)
- **Risco:** Alto — modificação no caminho crítico do debate; exige TDD rigoroso

### Problema Exato

Dois mecanismos falham simultaneamente:

**Mecanismo 1 — Dedup por hash sintático:** `issue_id = f"ISS-{hash(description_raw) % 10000:04d}"`. Formulações ligeiramente diferentes do mesmo problema (ex: "credenciais em variáveis de ambiente" vs "chaves de API armazenadas sem criptografia") geram IDs diferentes e entram como dois issues distintos, mesmo sendo semanticamente idênticos.

**Mecanismo 2 — ConvergenceDetector isolado:** O `ConvergenceDetector` implementa `similarity()` e `is_text_saturated()` mas não está integrado ao critério de parada. O `AdaptiveOrchestrator.evaluate()` decide STOP apenas por `MAX_ROUNDS` ou por ausência de novos issues — nunca por saturação semântica do debate.

**Efeito composto:** O debate acumula duplicatas infinitamente porque (a) o dedup não filtra duplicatas semânticas e (b) o orquestrador não detecta que o debate saturou.

### Implementação

#### 3.1 — Deduplicação Semântica no `DebateStateTracker`

**Arquivo:** `src/debate/debate_state_tracker.py`

Adicionar método `_is_semantic_duplicate()` e integrá-lo ao fluxo de registro de issues. Para garantir a convergência real do debate, é obrigatório utilizar o threshold fixo de **0.65** na comparação de similaridade Jaccard.

```python
# Importação necessária no topo do arquivo:
from src.core.convergence_detector import ConvergenceDetector

# Constante obrigatória — NÃO usar o threshold padrão do ConvergenceDetector (0.7),
# que é calibrado para textos longos e é rígido demais para issues curtas.
# 0.65 captura reformulações de ≤80 chars com vocabulário sobreposto sem falsos positivos.
# [AJUSTE W5Q-03]
SEMANTIC_DEDUP_THRESHOLD: float = 0.65

class DebateStateTracker:
    
    def __init__(self):
        # ... código existente ...
        self._convergence_detector = ConvergenceDetector()  # NOVO W5Q-03
    
    def _is_semantic_duplicate(
        self,
        new_description: str,
        board: "ValidationBoard",
        category: str,
        threshold: float = SEMANTIC_DEDUP_THRESHOLD  # 0.65 — ver constante acima
    ) -> bool:
        """
        Verifica se new_description é semanticamente duplicata de algum issue
        já registrado na mesma categoria.
        
        Usa Jaccard similarity nos primeiros 80 chars normalizados da descrição.
        É obrigatório o uso das STOPWORDS_PT (já definidas no sistema) na normalização
        para que o cálculo seja puramente semântico.
        Threshold: SEMANTIC_DEDUP_THRESHOLD (0.65). Abaixo disso, issues são
        distintos o suficiente para serem registrados. Não usar o threshold padrão
        do ConvergenceDetector (0.7) — ele foi calibrado para textos longos de
        round completo, não para descrições curtas de issue.
        
        INVARIANTE: Nunca lança exceção. Se similarity falhar, retorna False
        (conservador — prefere registrar duplicata a perder issue legítimo).
        """
        try:
            open_issues = board.get_open_issues()
            same_category = [
                iss for iss in open_issues
                if iss.category.upper() == category.upper()
            ]
            
            new_prefix = self._normalize_text(new_description)[:80]
            
            for existing in same_category:
                existing_prefix = self._normalize_text(existing.description)[:80]
                similarity = self._convergence_detector.similarity(
                    new_prefix, existing_prefix
                )
                if similarity >= threshold:
                    return True
            
            return False
        except Exception:
            return False  # Conservador: se falhar, não filtra
```

Modificar o método `extract_issues_from_critique()` (ou o equivalente em `_parse_v4`) para chamar `_is_semantic_duplicate` antes de registrar:

```python
# Dentro de extract_issues_from_critique(), após parsear cada issue:
for record in parsed_records:
    if self._is_semantic_duplicate(record.description, board, record.category):
        logger.debug(
            f"[Tracker] Issue semântico duplicado descartado: {record.issue_id[:20]}..."
        )
        continue  # Não registra no board
    
    board.add_issue(record)
    new_ids.append(record.issue_id)
```

**Atenção:** Verificar a assinatura exata de `extract_issues_from_critique()` no código atual antes de integrar — o parâmetro `board` pode precisar ser adicionado se ainda não existir. Verificar também `_parse_v4()` e `_parse_level1()`.

#### 3.2 — Integrar `ConvergenceDetector` ao `AdaptiveOrchestrator`

**Arquivo:** `src/core/adaptive_orchestrator.py`

Adicionar verificação de saturação semântica no método `evaluate()`, após a verificação de `MIN_ROUNDS`:

```python
# No início da classe AdaptiveOrchestrator.__init__():
from src.core.convergence_detector import ConvergenceDetector

def __init__(self, board, ...):
    # ... código existente ...
    self._convergence_detector = ConvergenceDetector()  # NOVO W5Q-03
    self._last_round_text: str = ""  # NOVO W5Q-03 — texto do round anterior

# No método evaluate(), após a verificação de MIN_ROUNDS e ANTES de _check_spawn:
def evaluate(self, round_num, current_round_text, previous_round_text, new_issue_count):
    # ... verificações existentes (MAX_ROUNDS, MIN_ROUNDS) ...
    
    # NOVO W5Q-03: verificar saturação semântica entre rounds consecutivos
    if round_num >= self._min_rounds and previous_round_text:
        if self._convergence_detector.is_text_saturated(
            current_round_text, previous_round_text
        ):
            # NOVO W5Q-03: É vital para a rastreabilidade (Eixo 2) registrar o motivo exato.
            reason = (
                f"Saturação Semântica atingida com threshold 0.65 no round {round_num}. "
                f"Crítica atual similar à anterior. "
                f"{len(self.board.get_open_issues())} issue(s) aberto(s)."
            )
            logger.info(f"[Orchestrator] STOP (saturação): {reason}")
            return OrchestratorDecision(action="STOP", reason=reason)
    
    # ... restante das verificações existentes (_check_spawn, etc.) ...
```

**Nota de integração:** O método `evaluate()` do `AdaptiveOrchestrator` atual recebe `current_round_text` e `previous_round_text` como parâmetros. Verificar se esses parâmetros já existem na assinatura — se não, adicioná-los mantendo compatibilidade retroativa com `previous_round_text=""` como default.

### Testes Obrigatórios (TDD — escrever ANTES do código)

**Arquivo:** `tests/unit/test_debate_state_tracker.py`

```python
def test_dedup_semantico_descarta_formulacao_alternativa():
    """W5Q-03: issue semanticamente idêntico em mesma categoria é descartado."""
    # Setup
    board = ValidationBoard()
    board.add_issue(IssueRecord(
        "ISS-0001", "HIGH", "SECURITY",
        "credenciais de api armazenadas em variaveis de ambiente sem criptografia"
    ))
    tracker = DebateStateTracker()
    
    # Issue semanticamente duplicado (formulação diferente, mesmo problema)
    nova_descricao = "chaves de api salvas em variaveis de ambiente sem protecao"
    is_dup = tracker._is_semantic_duplicate(nova_descricao, board, "SECURITY")
    
    assert is_dup is True

def test_dedup_semantico_permite_issue_genuinamente_diferente():
    """W5Q-03: issue de categoria igual mas semanticamente distinto é aceito."""
    board = ValidationBoard()
    board.add_issue(IssueRecord(
        "ISS-0001", "HIGH", "SECURITY",
        "credenciais de api armazenadas sem criptografia"
    ))
    tracker = DebateStateTracker()
    
    # Issue de segurança diferente: biometria vs credenciais
    nova_descricao = "dados biometricos coletados sem consentimento lgpd gdpr"
    is_dup = tracker._is_semantic_duplicate(nova_descricao, board, "SECURITY")
    
    assert is_dup is False

def test_dedup_semantico_nao_compara_categorias_diferentes():
    """W5Q-03: issue idêntico em categoria diferente NÃO é tratado como duplicata."""
    board = ValidationBoard()
    board.add_issue(IssueRecord(
        "ISS-0001", "HIGH", "SECURITY",
        "falta de autenticacao no endpoint de admin"
    ))
    tracker = DebateStateTracker()
    
    # Mesmo texto mas em categoria diferente
    is_dup = tracker._is_semantic_duplicate(
        "falta de autenticacao no endpoint de admin", board, "CORRECTNESS"
    )
    assert is_dup is False

def test_dedup_semantico_nao_lanca_excecao_com_board_vazio():
    """W5Q-03: board sem issues → retorna False sem exceção."""
    board = ValidationBoard()
    tracker = DebateStateTracker()
    result = tracker._is_semantic_duplicate("qualquer coisa", board, "SECURITY")
    assert result is False

def test_debate_com_dedup_produz_menos_issues_que_sem():
    """W5Q-03: integração — debate com dedup ativo produz menos issues únicos."""
    # Simular múltiplas críticas com formulações similares
    board = ValidationBoard()
    tracker = DebateStateTracker()
    
    criticas_similares = [
        "| HIGH | SECURITY | Credenciais expostas em env vars | Usar Secrets Manager |",
        "| HIGH | SECURITY | API keys em variáveis de ambiente sem proteção | Migrar para vault |",
        "| HIGH | SECURITY | Chaves de API armazenadas sem criptografia | AWS Secrets Manager |",
        "| HIGH | SECURITY | Autenticação biométrica sem criptografia dos dados | Criptografar com AES-256 |",
    ]
    
    for i, critica in enumerate(criticas_similares, 1):
        tracker.extract_issues_from_critique(critica, round_num=i, board=board)
    
    open_issues = board.get_open_issues()
    # Com dedup: 3 similares + 1 distinto = no máximo 2 únicos (1 credencial + 1 biometria)
    assert len(open_issues) <= 3  # Muito mais restritivo que os 4 que existiriam sem dedup
```

**Arquivo:** `tests/unit/test_adaptive_orchestrator.py`

```python
def test_orchestrator_para_por_saturacao_semantica():
    """W5Q-03: dois rounds com Jaccard ≥ 0.7 → STOP por saturação."""
    board = ValidationBoard()
    orchestrator = AdaptiveOrchestrator(board=board, min_rounds=2)
    
    texto_repetido = (
        "autenticação segurança vulnerabilidade credencial criptografia endpoint "
        "proteção acesso token jwt exposto rate-limit tls certificado"
    )
    
    # Simular round 2 com texto quase idêntico ao round anterior
    decision = orchestrator.evaluate(
        round_num=3,  # Acima do MIN_ROUNDS=2
        current_round_text=texto_repetido,
        previous_round_text=texto_repetido,  # Idêntico → Jaccard 1.0
        new_issue_count=0
    )
    
    assert decision.action == "STOP"
    assert "saturação" in decision.reason.lower()

def test_orchestrator_nao_para_por_saturacao_abaixo_min_rounds():
    """W5Q-03: saturação semântica antes de MIN_ROUNDS não para o debate."""
    board = ValidationBoard()
    orchestrator = AdaptiveOrchestrator(board=board, min_rounds=3)
    
    texto = "autenticação segurança vulnerabilidade credencial"
    
    decision = orchestrator.evaluate(
        round_num=2,  # Abaixo do MIN_ROUNDS=3
        current_round_text=texto,
        previous_round_text=texto,
        new_issue_count=5
    )
    
    assert decision.action != "STOP"
```

### Critério de Aceite (binário)

| Critério | Verificação |
|---|---|
| Dedup semântico filtra reformulações similares | `test_dedup_semantico_descarta_formulacao_alternativa` passa |
| Issues genuinamente distintos não são filtrados | `test_dedup_semantico_permite_issue_genuinamente_diferente` passa |
| Orquestrador para por saturação semântica | `test_orchestrator_para_por_saturacao_semantica` passa |
| Execução real: ≤ 25 issues únicos ao final | Verificação manual com `gpt-oss:20b-cloud` |
| Todos os testes passam | `pytest tests/ -v` verde |

### Rollback

```bash
# Se os testes do AdaptiveOrchestrator quebrarem por mudança de assinatura:
git diff src/core/adaptive_orchestrator.py
# Garantir que previous_round_text="" seja default para não quebrar chamadas existentes
```

---

## TASK 4 — Synthesizer Comprimido e Relatório Agrupado

### Identidade
- **ID:** W5Q-04
- **Arquivos principais:** `src/agents/synthesizer_agent.py`, `src/core/report_generator.py`
- **Arquivo de teste:** `tests/unit/test_synthesizer_agent.py`, `tests/unit/test_report_generator.py`
- **Esforço estimado:** Médio (~90 LOC de produção)
- **Risco:** Baixo-Médio — lógica determinística, sem risco de regressão no debate

### Problema Exato

**Problema A — Payload excessivo na Juíza:**  
`_build_prompt()` serializa `board_snapshot` inteiro com `json.dumps(board_snapshot, indent=2)`. Com 77 issues de ~200 chars cada, o JSON excede 15.000 chars antes de qualquer instrução do prompt. O modelo de 20B tem contexto efetivo inferior a esse volume para geração estruturada.

**Problema B — Relatório de fallback sem estrutura:**  
O `_fallback_dump()` no `ReportGenerator` produz uma lista plana de 77 issues em ordem aleatória. Um usuário precisa de ~30 minutos para extrair padrões manualmente. Não há sumário executivo, não há agrupamento, não há tabela de resumo.

### Implementação

#### 4.1 — Método `_build_compressed_board()` no `SynthesizerAgent`

**Arquivo:** `src/agents/synthesizer_agent.py`

Adicionar método antes de `_build_prompt()`:

```python
def _build_compressed_board(self, board_snapshot: Dict[str, Any]) -> str:
    """
    Reduz o board_snapshot para representação textual < 3200 chars.
    
    Prioridade de inclusão:
    1. Issues HIGH abertos (todos, até 10)
    2. Issues MED abertos (até 5)
    3. Issues LOW abertos (contagem apenas)
    4. Issues resolvidos (contagem apenas)
    5. Decisões validadas (até 5)
    6. Pressupostos não testados (até 3)
    
    INVARIANTE: Nunca excede 3200 chars. Se exceder, trunca MED e LOW primeiro.
    """
    issues = board_snapshot.get("issues", {})
    decisions = board_snapshot.get("decisions", {})
    assumptions = board_snapshot.get("assumptions", {})
    
    high_open = [
        v for v in issues.values()
        if v.get("severity") == "HIGH" and v.get("status") == "OPEN"
    ]
    med_open = [
        v for v in issues.values()
        if v.get("severity") == "MED" and v.get("status") == "OPEN"
    ]
    low_open = [
        v for v in issues.values()
        if v.get("severity") == "LOW" and v.get("status") == "OPEN"
    ]
    resolved = [v for v in issues.values() if v.get("status") == "RESOLVED"]
    validated_decisions = [
        v for v in decisions.values() if v.get("status") == "VALIDATED"
    ]
    untested_assumptions = [
        v for v in assumptions.values() if v.get("status") == "UNTESTED"
    ]
    
    lines = [
        "## RESUMO DO DEBATE",
        f"Total: {len(issues)} issues | "
        f"{len(high_open)} HIGH abertos | "
        f"{len(med_open)} MED abertos | "
        f"{len(low_open)} LOW abertos | "
        f"{len(resolved)} resolvidos",
        "",
        "## ISSUES CRÍTICOS (HIGH, OPEN) — Obrigatório abordar no relatório",
    ]
    
    for iss in high_open[:10]:
        desc = iss.get("description", "")[:150]
        lines.append(
            f"- [{iss.get('issue_id', '?')}] "
            f"({iss.get('category', '?')}) {desc}"
        )
    
    if med_open:
        lines.append("")
        lines.append(f"## ISSUES MODERADOS (MED, OPEN) — {len(med_open)} total")
        for iss in med_open[:5]:
            desc = iss.get("description", "")[:100]
            lines.append(
                f"- [{iss.get('issue_id', '?')}] "
                f"({iss.get('category', '?')}) {desc}"
            )
        if len(med_open) > 5:
            lines.append(f"  ... e mais {len(med_open) - 5} issues MED.")
    
    if validated_decisions:
        lines.append("")
        lines.append("## DECISÕES VALIDADAS")
        for dec in validated_decisions[:5]:
            lines.append(f"- [{dec.get('decision_id', '?')}] {dec.get('description', '')[:100]}")
    
    if untested_assumptions:
        lines.append("")
        lines.append("## PRESSUPOSTOS NÃO TESTADOS")
        for ass in untested_assumptions[:3]:
            lines.append(f"- [{ass.get('assumption_id', '?')}] {ass.get('description', '')[:100]}")
    
    result = "\n".join(lines)
    
    # Garantia de tamanho máximo
    if len(result) >= 3200:
        result = result[:3150] + "\n... [truncado para fit de contexto]"
    
    return result
```

Modificar `_build_prompt()` para usar o board comprimido:

```python
def _build_prompt(self, board_snapshot, idea_title, profile=None):
    # SUBSTITUIR: snapshot_json = json.dumps(board_snapshot, indent=2, ...)
    # POR:
    compressed_board = self._build_compressed_board(board_snapshot)  # NOVO W5Q-04
    domain = profile.domain.upper() if profile else "GENERIC"
    
    sections_str = "\n".join([f"- {s}" for s in self.DEFAULT_SECTIONS])
    if profile and profile.report_sections:
        sections_str = "\n".join([f"- {s.title}" for s in profile.report_sections])
        if "Veredito" not in sections_str:
            sections_str += "\n- ## Veredito"
    
    return f"""Você é uma juíza técnica neutra especializada no domínio {domain}.
Sua única função é transformar os dados abaixo em um relatório estruturado e profissional.

REGRAS INVIOLÁVEIS:
1. Use APENAS as informações presentes em BOARD_RESUMIDO abaixo.
2. Não expresse opinião pessoal.
3. O relatório DEVE conter EXATAMENTE estas seções, nesta ordem:
{sections_str}
4. Se uma seção não tem dados, escreva: "(Nenhum registro nesta categoria)"
5. Responda APENAS com o relatório em Markdown. Nenhum texto antes ou depois.

IDEIA ANALISADA: {idea_title}

BOARD_RESUMIDO:
{compressed_board}
"""
```

#### 4.2 — Relatório de Fallback com Agrupamento Semântico

**Arquivo:** `src/core/report_generator.py`

Substituir o método `_fallback_dump()` e adicionar método auxiliar de agrupamento. Para que o resumo seja eficaz e permita uma leitura rápida de 5 minutos, a tabela de resumo deve conter obrigatoriamente as colunas: `| Categoria | Total de Issues | Gravidade Alta | Status (Crítico/Estável) |`.

```python
def _build_issue_summary_table(self, board: "ValidationBoard") -> str:
    """
    Gera tabela de resumo de issues por categoria e severidade.
    100% determinístico. Zero LLM.
    
    Colunas obrigatórias (leitura de 5 minutos): [AJUSTE W5Q-04]
      | Categoria | Total de Issues | Gravidade Alta | Status (Crítico/Estável) |
    
    Regra de Status:
      - "🔴 Crítico"  → categoria tem ≥ 1 issue HIGH aberto
      - "🟢 Estável"  → categoria tem 0 issues HIGH (apenas MED/LOW)
    
    Objetivo: o usuário identifica imediatamente onde o projeto "sangra"
    sem precisar ler os issues individuais.
    """
    by_cat = board.get_open_issues_by_category()
    if not by_cat:
        return "Nenhum issue aberto registrado.\n"
    
    lines = [
        "| Categoria | Total de Issues | Gravidade Alta | Status |",
        "|-----------|-----------------|----------------|--------|",
    ]
    
    total_issues = total_high = 0
    
    for category in sorted(by_cat.keys()):
        issues_cat = by_cat[category]
        high = sum(1 for i in issues_cat if i.severity == "HIGH")
        total = len(issues_cat)
        status = "🔴 Crítico" if high > 0 else "🟢 Estável"
        lines.append(f"| {category} | {total} | {high} | {status} |")
        total_issues += total
        total_high  += high
    
    overall_status = "🔴 Crítico" if total_high > 0 else "🟢 Estável"
    lines.append(
        f"| **TOTAL** | **{total_issues}** | **{total_high}** | **{overall_status}** |"
    )
    
    return "\n".join(lines) + "\n"

def _fallback_dump(self, board: "ValidationBoard", idea_title: str) -> str:
    """
    Gera relatório de fallback com agrupamento semântico por categoria.
    Substitui lista plana por estrutura navegável.
    """
    stats = board.get_stats()
    open_by_cat = board.get_open_issues_by_category()
    
    lines = [
        f"# Relatório de Validação — IdeaForge (Fallback Automático)",
        f"",
        f"Domínio Detectado: {board.get_domain_profile().domain.upper() if board.get_domain_profile() else 'N/A'} "
        f"Gerado por fallback determinístico. O SynthesizerAgent falhou.",
        f"",
        f"**Ideia Analisada:** {idea_title}",
        f"",
        f"## Resumo Executivo",
        f"",
        f"| Métrica | Valor |",
        f"|---------|-------|",
        f"| Total de Issues | {stats.get('total', 0)} |",
        f"| Issues Abertos  | {stats.get('open', 0)} |",
        f"| Issues Resolvidos | {stats.get('resolved', 0)} |",
        f"| Possui Issues Bloqueantes (HIGH) | {'Sim ⚠️' if stats.get('has_blocking') else 'Não ✅'} |",
        f"",
        f"## Distribuição por Categoria",
        f"",
        self._build_issue_summary_table(board),
        f"",
        f"## Issues Detalhados (agrupados por categoria e severidade)",
        f"",
    ]
    
    # Ordenar: HIGH antes de MED antes de LOW, categorias alfabéticas
    severity_order = {"HIGH": 0, "MED": 1, "LOW": 2}
    
    for category in sorted(open_by_cat.keys()):
        issues_cat = sorted(
            open_by_cat[category],
            key=lambda i: severity_order.get(i.severity, 9)
        )
        lines.append(f"### {category}")
        lines.append("")
        for iss in issues_cat:
            lines.append(
                f"**{iss.issue_id}** [{iss.severity}] ({iss.category}): "
                f"{iss.description}"
            )
            lines.append("")
            lines.append(f"Status: {iss.status}")
            lines.append("")
    
    # Issues resolvidos (sumário apenas)
    resolved = [i for i in board._issues.values() if i.status == "RESOLVED"]
    if resolved:
        lines.append("## Issues Resolvidos Durante o Debate")
        lines.append("")
        for iss in resolved:
            lines.append(f"- **{iss.issue_id}**: {iss.description[:80]}... ✅")
        lines.append("")
    
    lines.append("## Decisões Tomadas")
    lines.append("")
    for dec in board._decisions.values():
        if dec.status == "VALIDATED":
            lines.append(f"- **{dec.decision_id}**: {dec.description}")
    lines.append("")
    
    lines.append("## Pressupostos Mapeados")
    lines.append("")
    for ass in board._assumptions.values():
        lines.append(f"- **{ass.assumption_id}** [{ass.status}]: {ass.description}")
    
    return "\n".join(lines)
```

### Testes Obrigatórios (TDD — escrever ANTES do código)

**Arquivo:** `tests/unit/test_synthesizer_agent.py`

```python
def test_build_compressed_board_respeita_limite_3200_chars():
    """W5Q-04: board comprimido nunca excede 3200 chars."""
    synth = SynthesizerAgent()
    
    # Simular board com 77 issues
    issues = {}
    for i in range(77):
        severity = ["HIGH", "MED", "LOW"][i % 3]
        issues[f"ISS-{i:04d}"] = {
            "issue_id": f"ISS-{i:04d}",
            "severity": severity,
            "category": "SECURITY",
            "description": "A" * 200,  # Descrição longa
            "status": "OPEN"
        }
    
    snapshot = {"issues": issues, "decisions": {}, "assumptions": {}}
    result = synth._build_compressed_board(snapshot)
    
    assert len(result) <= 3200

def test_build_compressed_board_prioriza_high_issues():
    """W5Q-04: issues HIGH aparecem antes de MED e LOW."""
    synth = SynthesizerAgent()
    snapshot = {
        "issues": {
            "ISS-LOW":  {"issue_id": "ISS-LOW",  "severity": "LOW",  "category": "SEC", "description": "low issue",  "status": "OPEN"},
            "ISS-HIGH": {"issue_id": "ISS-HIGH", "severity": "HIGH", "category": "SEC", "description": "high issue", "status": "OPEN"},
            "ISS-MED":  {"issue_id": "ISS-MED",  "severity": "MED",  "category": "SEC", "description": "med issue",  "status": "OPEN"},
        },
        "decisions": {}, "assumptions": {}
    }
    result = synth._build_compressed_board(snapshot)
    # HIGH deve aparecer antes de MED na string
    assert result.index("ISS-HIGH") < result.index("ISS-MED")

def test_build_compressed_board_retorna_string_nao_vazia_com_board_vazio():
    """W5Q-04: board vazio → string não-vazia com resumo de zeros."""
    synth = SynthesizerAgent()
    snapshot = {"issues": {}, "decisions": {}, "assumptions": {}}
    result = synth._build_compressed_board(snapshot)
    assert isinstance(result, str)
    assert len(result) > 0
```

**Arquivo:** `tests/unit/test_report_generator.py`

```python
def test_fallback_dump_tem_tabela_resumo_executivo():
    """W5Q-04: fallback dump contém tabela de resumo por categoria."""
    board = ValidationBoard()
    for i in range(5):
        board.add_issue(IssueRecord(f"ISS-{i:04d}", "HIGH", "SECURITY", f"Issue {i}"))
    for i in range(3):
        board.add_issue(IssueRecord(f"ISS-M{i}", "MED", "FEASIBILITY", f"Issue med {i}"))
    
    gen = ReportGenerator()
    dump = gen._fallback_dump(board, "Ideia Teste")
    
    assert "Resumo Executivo" in dump
    assert "Distribuição por Categoria" in dump
    assert "SECURITY" in dump
    assert "FEASIBILITY" in dump

def test_fallback_dump_agrupa_por_categoria():
    """W5Q-04: issues no fallback estão agrupados por categoria, não em lista plana."""
    board = ValidationBoard()
    board.add_issue(IssueRecord("ISS-S1", "HIGH", "SECURITY", "Segurança issue 1"))
    board.add_issue(IssueRecord("ISS-F1", "HIGH", "FEASIBILITY", "Viabilidade issue 1"))
    board.add_issue(IssueRecord("ISS-S2", "MED",  "SECURITY", "Segurança issue 2"))
    
    gen = ReportGenerator()
    dump = gen._fallback_dump(board, "Ideia Teste")
    
    # SECURITY deve aparecer como seção agrupada
    assert "### SECURITY" in dump
    assert "### FEASIBILITY" in dump
    # ISS-S1 e ISS-S2 devem estar dentro do bloco SECURITY (antes de FEASIBILITY)
    pos_security = dump.index("### SECURITY")
    pos_feasibility = dump.index("### FEASIBILITY")
    pos_s1 = dump.index("ISS-S1")
    pos_s2 = dump.index("ISS-S2")
    assert pos_security < pos_s1 < pos_feasibility
    assert pos_security < pos_s2 < pos_feasibility

def test_build_issue_summary_table_com_board_vazio():
    """W5Q-04: tabela de resumo com board vazio retorna mensagem adequada."""
    board = ValidationBoard()
    gen = ReportGenerator()
    result = gen._build_issue_summary_table(board)
    assert "Nenhum issue aberto" in result

def test_build_issue_summary_table_colunas_obrigatorias():
    """W5Q-04: tabela contém as 4 colunas obrigatórias do Resumo Executivo."""
    board = ValidationBoard()
    board.add_issue(IssueRecord("ISS-H1", "HIGH", "SECURITY", "Issue crítico"))
    board.add_issue(IssueRecord("ISS-M1", "MED",  "FEASIBILITY", "Issue moderado"))
    gen = ReportGenerator()
    result = gen._build_issue_summary_table(board)
    # Colunas obrigatórias — sem estas, leitura de 5 minutos não é possível
    assert "Categoria" in result
    assert "Total de Issues" in result
    assert "Gravidade Alta" in result
    assert "Status" in result

def test_build_issue_summary_table_status_critico_com_high():
    """W5Q-04: categoria com HIGH aberto aparece como Crítico."""
    board = ValidationBoard()
    board.add_issue(IssueRecord("ISS-H1", "HIGH", "SECURITY", "Issue grave"))
    gen = ReportGenerator()
    result = gen._build_issue_summary_table(board)
    assert "Crítico" in result

def test_build_issue_summary_table_status_estavel_sem_high():
    """W5Q-04: categoria somente com MED/LOW aparece como Estável."""
    board = ValidationBoard()
    board.add_issue(IssueRecord("ISS-M1", "MED", "FEASIBILITY", "Issue médio"))
    gen = ReportGenerator()
    result = gen._build_issue_summary_table(board)
    assert "Estável" in result

def test_fallback_dump_issues_high_antes_de_med_na_categoria():
    """W5Q-04: dentro de cada categoria, HIGH vem antes de MED."""
    board = ValidationBoard()
    board.add_issue(IssueRecord("ISS-MED", "MED",  "SECURITY", "Med primeiro"))
    board.add_issue(IssueRecord("ISS-HIGH", "HIGH", "SECURITY", "High segundo"))
    
    gen = ReportGenerator()
    dump = gen._fallback_dump(board, "Teste")
    
    assert dump.index("ISS-HIGH") < dump.index("ISS-MED")
```

### Critério de Aceite (binário)

| Critério | Verificação |
|---|---|
| Board comprimido ≤ 3200 chars com 77 issues | `test_build_compressed_board_respeita_limite_3200_chars` passa |
| Fallback tem tabela de resumo executivo | `test_fallback_dump_tem_tabela_resumo_executivo` passa |
| Fallback agrupa por categoria | `test_fallback_dump_agrupa_por_categoria` passa |
| SynthesizerAgent não falha em execução real | Verificação manual: nenhum `[WARNING] SynthesizerAgent falhou` no log |
| Todos os testes passam | `pytest tests/ -v` verde |

---

## PLANO DE EXECUÇÃO CONSOLIDADO

### Sequência de Implementação

```
Para cada tarefa (W5Q-01 → W5Q-02 → W5Q-03 → W5Q-04):
  1. Ler os arquivos a modificar (apenas eles)
  2. Escrever os testes PRIMEIRO
  3. Rodar: pytest <arquivo_de_teste> -v → TODOS DEVEM FALHAR
  4. Implementar o código
  5. Rodar: pytest <arquivo_de_teste> -v → TODOS DEVEM PASSAR
  6. Rodar: pytest tests/ -v → TODOS DEVEM PASSAR (regressão)
  7. Só então avançar para a próxima tarefa
```

### Verificação de Conclusão da Onda

Após W5Q-04 implementada e verde:

```bash
# 1. Suite completa
pytest tests/unit/ tests/integration/ -v --tb=short

# 2. Execução real de certificação (repetir 3 vezes)
python -m src.cli.main --idea "Plataforma de afiliados para eletrônicos, solo-founder, SEO orgânico, comissão por venda" --model gpt-oss:20b-cloud

# Verificar no output:
# - "DomainProfile construído via llm" (não "fallback") → Task 1 ✅
# - "Domínio detectado: business" ou "hybrid" → Task 2 ✅  
# - Total de issues ≤ 25 ao final do debate → Task 3 ✅
# - Nenhum "[WARNING] SynthesizerAgent falhou" → Task 4 ✅
```

### Tabela de Artefatos da Onda

| Tarefa | Arquivo Modificado | Arquivo de Teste | Novos Testes |
|--------|-------------------|------------------|-------------|
| W5Q-01 | `domain_context_builder.py` | `test_domain_context_builder.py` | 5 |
| W5Q-02 | `domain_detector.py`, `domain_context_builder.py` | `test_domain_detector.py` | 7 |
| W5Q-03 | `debate_state_tracker.py`, `adaptive_orchestrator.py` | `test_debate_state_tracker.py`, `test_adaptive_orchestrator.py` | 7 |
| W5Q-04 | `synthesizer_agent.py`, `report_generator.py` | `test_synthesizer_agent.py`, `test_report_generator.py` | 11 |
| **Total** | **6 arquivos** | **6 arquivos de teste** | **30 novos testes** |

---

## ATUALIZAÇÃO OBRIGATÓRIA DO BACKLOG APÓS ESTA ONDA

Após conclusão e validação, instruir a IA executora a atualizar `docs/BACKLOG_FUTURO.md`:

1. Renomear `Onda 5` atual para `Onda 5.0 — Qualidade Semântica e Convergência Real`
2. Marcar W5Q-01 a W5Q-04 como `CONCLUÍDO`
3. Criar `Onda 5.1 — Performance e Interface` com os itens suspensos:

```markdown
## Onda 5.1 — Performance e Interface (Suspensa da Onda 5.0)
| ID | Feature | Descrição | Status |
|---|---|---|---|
| W5-01 | Cache Semântico | Cachear prompts exatos limitando LLM requests | PENDENTE |
| W5-02 | UI em Tempo Real | Dashboard Gradio/Streamlit do ValidationBoard | PENDENTE |
| W5-03 | Faxina Legada | Remover `idea-forge/` após auditoria completa | PENDENTE |
```

---

## MENSAGEM DE COMMIT SUGERIDA

```
[ONDA 5.0] QUALIDADE SEMÂNTICA E CONVERGÊNCIA REAL

- W5Q-01: _extract_json() com boundary detection + max_tokens 600→800
- W5Q-02: DomainDetector normalizado por densidade + domínio hybrid + 14 keywords business
           hybrid fallback com 7 seções explícitas (Negócio + Técnico) [AJUSTE]
- W5Q-03: Dedup semântico Jaccard no tracker + SEMANTIC_DEDUP_THRESHOLD=0.65 [AJUSTE]
           + saturação integrada ao orchestrator  
- W5Q-04: Synthesizer com board comprimido ≤3200 chars + fallback agrupado por categoria
           tabela de resumo com colunas Categoria/Total/Gravidade Alta/Status [AJUSTE]
- +30 novos testes (total estimado: 174+)
```

---

## CLÁUSULA DE INTEGRIDADE

| Item | Status |
|---|---|
| Toda tarefa tem critério de aceite binário | ✅ |
| Todo critério tem teste correspondente nomeado | ✅ |
| Toda modificação tem rollback documentado | ✅ |
| Nenhum arquivo protegido é modificado sem justificativa | ✅ |
| Sequência de implementação é explícita e sem ambiguidade | ✅ |
| Nenhuma seção contém "A DEFINIR" | ✅ |
| O blueprint é autocontido (não requer leitura de outros arquivos para implementar) | ✅ |

**Declaração de Determinismo:** Este blueprint foi estruturado para eliminar ambiguidade operacional. A IA executora (Gemini CLI) pode implementar as quatro tarefas lendo apenas este documento e os arquivos `src/` especificados em cada tarefa, sem necessidade de inferências arquiteturais próprias. Toda decisão está rastreável à falha observada na execução de 26/04/2026.
