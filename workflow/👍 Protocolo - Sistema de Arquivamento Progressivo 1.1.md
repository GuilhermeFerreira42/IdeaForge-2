``` # Protocolo - Sistema de Arquivamento Progressivo 1.1

Copie, preencha os campos entre `{colchetes}` e cole para a IA executora:

---

## TAREFA: Implantação do Sistema de Arquivamento Progressivo com Compressão Semântica

### CONTEXTO

Projeto: **{NOME_DO_PROJETO}**
Fase atual concluída: **{NUMERO_DA_FASE_ATUAL}**
Diretório do código-fonte: **{CAMINHO_DO_CODIGO}** (ex: `src/`, `app/`, `lib/`)
Diretório de testes: **{CAMINHO_DOS_TESTES}** (ex: `tests/`, `test/`, `__tests__/`)
Diretório de documentação: **{CAMINHO_DOS_DOCS}** (ex: `docs/`)
Diretório de arquivo morto: **{CAMINHO_DO_ARCHIVE}** (ex: `docs/archive/`)

A documentação das fases anteriores (Fase 1 a {NUMERO_DA_FASE_ATUAL}) está acumulada em `{CAMINHO_DO_ARCHIVE}` como blueprints completos. Esse volume consome tokens desnecessários toda vez que você precisa ler o projeto para manter consistência. Implante agora um sistema de 5 camadas que resolve isso permanentemente.

---

### O QUE VOCÊ DEVE FAZER

Executar **6 ações** na seguinte ordem. Não pule nenhuma. Não altere nenhum arquivo de código-fonte.

---

### AÇÃO 1: Criar `{CAMINHO_DOS_DOCS}/CURRENT_STATE.md`

Este arquivo descreve **exclusivamente o estado atual** do projeto. É o **único arquivo** que você precisará ler no futuro para entender onde o projeto está.

**Regras para escrever:**

1. **Sem histórico** — Descreve apenas o que o sistema É agora, nunca o que foi antes
2. **Sem justificativas** — O "porquê" vai no DECISION_LOG
3. **Sem código** — Apenas assinaturas públicas (nome do método + parâmetros + retorno)
4. **Sem exemplos de output** — Apenas especificações
5. **Tabelas sobre prosa** — Cada módulo/componente = 1 linha de tabela
6. **Invariantes como lista numerada** — Máximo 15 itens
7. **Target: ≤ 1500 tokens** — Exceder esse limite inviabiliza o objetivo do arquivo

**Estrutura obrigatória:**

´´´markdown
# CURRENT_STATE — {NOME_DO_PROJETO}
> Última atualização: Fase {NUMERO_DA_FASE_ATUAL} | [data de hoje]

## Arquitetura Ativa
- [padrão arquitetural, orquestração, persistência, integrações principais]

## Módulos e Contratos Vigentes
| Módulo | Arquivo | Contrato Público | Desde |
|---|---|---|---|
| [1 linha por módulo/classe principal com métodos públicos] |

## Fluxo Principal
[descrição compacta do fluxo: 1 linha por etapa, ou DAG se aplicável]

## Invariantes Globais (nunca violar)
[lista numerada de todas as regras que nunca podem ser quebradas]

## Restrições Técnicas Ativas
[configurações, limites, parâmetros que afetam comportamento]

## Testes Obrigatórios
| Suite | Arquivo | Cobertura Aproximada | Comando |
|---|---|---|---|
| [1 linha por suite de testes com comando de execução] |

## Dependências Externas
| Pacote | Versão | Motivo |
|---|---|---|
´´´

**Para preencher**: Leia o código-fonte atual em `{CAMINHO_DO_CODIGO}` e os testes em `{CAMINHO_DOS_TESTES}`. Extraia todos os módulos, contratos, fluxos, invariantes e restrições. Inclua tudo que existe até a Fase {NUMERO_DA_FASE_ATUAL}.

---

### AÇÃO 2: Criar `{CAMINHO_DOS_DOCS}/DECISION_LOG.md`

Registro compacto de **todas as decisões** de cada fase.

**Formato — uma linha por decisão:**

´´´
F{N} | {TIPO} | {DECISÃO} | {MOTIVO} | {ARQUIVOS IMPACTADOS}
´´´

**Tipos:**
- `ADD` = novo arquivo/classe/método/componente
- `MOD` = modificação de existente
- `DEL` = remoção
- `FREEZE` = interface/contrato congelado
- `RULE` = regra arquitetural/operacional estabelecida
- `CFG` = configuração/parâmetro definido
- `FIX` = correção de bug estrutural com impacto arquitetural

**Para preencher**: Leia cada blueprint/documento de fase em `{CAMINHO_DO_ARCHIVE}` e extraia cada decisão relevante. 3-10 linhas por fase. Foque em:
- O que foi criado/modificado/removido
- Que contratos foram definidos ou congelados
- Que regras foram estabelecidas
- Bugs estruturais corrigidos e o motivo da causa raiz

**Estrutura:**

´´´markdown
# DECISION_LOG — {NOME_DO_PROJETO}

## Formato
`[FASE] | [TIPO] | [DECISÃO] | [MOTIVO] | [ARQUIVOS IMPACTADOS]`

Tipos: ADD, MOD, DEL, FREEZE, RULE, CFG, FIX

---

### Fase 1 — [nome da fase]
F1 | ADD | ... | ... | ...

### Fase 2 — [nome da fase]
F2 | MOD | ... | ... | ...

[uma seção por fase até a fase atual]
´´´

---

### AÇÃO 3: Criar `{CAMINHO_DOS_DOCS}/BACKLOG_FUTURO.md`

Registro do roadmap estratégico do projeto com critérios de aceite por fase futura.

**Regras para escrever:**

1. **Cada item tem critério binário** — passou/não passou, nunca "melhoria geral"
2. **Status explícito** — `PENDENTE` ou `CONCLUÍDO` (nunca vazio)
3. **Pré-requisitos declarados** — cada onda/fase declara de quais fases depende
4. **Sem especulação** — inclua apenas o que foi deliberadamente planejado

**Estrutura:**

´´´markdown
# BACKLOG ESTRATÉGICO — {NOME_DO_PROJETO}

## Intenção Original
- **Objetivo:** [objetivo final do projeto em 1-2 frases]
- **Estado Atual:** [descrição concisa do estado após Fase {NUMERO_DA_FASE_ATUAL}]
- **Meta Final:** [onde o projeto deve chegar]

---

## Onda 1 — [Nome do Grupo de Fases]

| ID | Técnica/Feature | Descrição | Arquivos Impactados | Critério de Aceite | Status |
|---|---|---|---|---|---|
| W1-01 | [nome] | [descrição concisa] | [arquivos] | [critério binário verificável] | CONCLUÍDO |
| W1-02 | [nome] | [descrição concisa] | [arquivos] | [critério binário verificável] | PENDENTE |

### Meta da Onda 1
- **Critério binário:** [condição de saída da onda]
- **Status:** CONCLUÍDO / PENDENTE

---

## Onda 2 — [Nome do Grupo de Fases]

[repetir estrutura acima]

---

## Regras do Backlog
1. Itens movem de `PENDENTE` para `CONCLUÍDO` apenas após validação com critério binário
2. Nenhuma Onda inicia sem a anterior concluída
3. Novas técnicas descobertas durante implementação são adicionadas como item novo na Onda apropriada
´´´

**Para preencher**: Leia os blueprints em `{CAMINHO_DO_ARCHIVE}` e extraia as fases planejadas mas ainda não executadas. Se o projeto não tem fases futuras definidas, crie a estrutura com a Onda 1 marcada como CONCLUÍDA e deixe as ondas seguintes com `PENDENTE` e `[A PLANEJAR]` nos campos.

---

### AÇÃO 4: Criar `{CAMINHO_DOS_DOCS}/ARCHIVING_PROTOCOL.md`

Instruções que você seguirá no futuro ao concluir cada nova fase:

´´´markdown
# PROTOCOLO DE ARQUIVAMENTO PÓS-FASE — {NOME_DO_PROJETO}

## Quando Executar
Após a conclusão e validação de cada nova fase do projeto.

## Pré-condição Obrigatória
Antes de iniciar o arquivamento, CONFIRMAR que:
- [ ] A suíte de testes em `{CAMINHO_DOS_TESTES}` passa integralmente
- [ ] Nenhum arquivo de código-fonte foi deixado em estado inconsistente
- [ ] O blueprint da fase foi fornecido pelo usuário ou já existe em `{CAMINHO_DO_ARCHIVE}`

Se qualquer item falhar, PARAR e reportar ao usuário antes de continuar.

## Passos Obrigatórios

### 1. Verificar Testes
Confirmar que a suíte de testes passa. Reportar explicitamente:
- Número total de testes encontrados
- Número de testes passando
- Qualquer falha identificada (não arquivar se houver falha não documentada)

### 2. Arquivar Blueprint Completo
- Salvar o blueprint da fase em `{CAMINHO_DO_ARCHIVE}/phase_XX_nome.resolved`
- Renomear para `.resolved` para sinalizar que é auditoria humana, não leitura de IA
- Este arquivo NUNCA será lido pela IA

### 3. Reescrever CURRENT_STATE.md
- Abrir `{CAMINHO_DOS_DOCS}/CURRENT_STATE.md`
- SUBSTITUIR (não acumular) o conteúdo com o estado atual
- Atualizar: tabela de módulos, fluxo, invariantes, restrições, testes com comandos
- Target: ≤ 1500 tokens
- Se ultrapassar, comprimir — não expandir

### 4. Append ao DECISION_LOG.md
- Adicionar seção `### Fase N — [nome]` ao final
- 1 linha por decisão: `FN | TIPO | DECISÃO | MOTIVO | ARQUIVOS`
- Entre 3-10 linhas por fase
- Incluir FIX se algum bug estrutural foi corrigido durante a fase

### 5. Compressão Progressiva (quando DECISION_LOG > 3000 tokens)
- Consolidar fases antigas em sumário de 1 linha por fase
- Manter as 10 fases mais recentes no formato detalhado
- Exemplo:
  ´´´
  ### Fases 1-10 (Consolidado)
  - Feature X implementada com padrão Y (F1)
  - Migração para arquitetura Z (F3)
  - Otimização de performance em módulo W (F7)
  ´´´

### 6. Atualizar BACKLOG_FUTURO.md
- Localizar o item da fase recém-concluída
- Alterar `Status` de `PENDENTE` para `CONCLUÍDO`
- Se a fase concluída é a última de uma Onda, verificar se a Meta da Onda foi atingida
- Se novas técnicas foram descobertas, adicionar como item novo na Onda apropriada

### 7. Limpeza do Projeto
- Mover scripts de verificação temporários para `{CAMINHO_DO_ARCHIVE}/phase_XX/`
- Remover arquivos `.tmp`, `.bak`, `.old` gerados durante a fase
- Mover o blueprint da fase para `{CAMINHO_DO_ARCHIVE}/phase_XX/`

### 8. Sugerir Mensagem de Commit
Ao final do arquivamento, sugerir uma mensagem de commit no formato:
´´´
[FASE N] DESCRIÇÃO CURTA EM MAIÚSCULO — resumo do que foi entregue
´´´
Exemplo: `[FASE 9.6] RETRY ORCHESTRATOR — recuperação semântica em 3 níveis`

## Regras de Leitura para a IA
- **SEMPRE ler**: `{CAMINHO_DOS_DOCS}/CURRENT_STATE.md`
- **Ler no início de cada onda**: `{CAMINHO_DOS_DOCS}/BACKLOG_FUTURO.md`
- **Ler sob demanda**: `{CAMINHO_DOS_DOCS}/DECISION_LOG.md` (apenas quando precisar entender "por quê")
- **NUNCA ler**: `{CAMINHO_DO_ARCHIVE}/*` (backups para humanos)
´´´

---

### AÇÃO 5: Criar `.ai-context` na raiz do projeto

´´´markdown
# INSTRUÇÕES DE CONTEXTO PARA IA — {NOME_DO_PROJETO}

## Ler OBRIGATORIAMENTE antes de qualquer tarefa
1. `{CAMINHO_DOS_DOCS}/CURRENT_STATE.md` — Estado atual completo do sistema
2. O código-fonte em `{CAMINHO_DO_CODIGO}` — Apenas os arquivos que serão modificados

## Ler no início de cada nova Onda
3. `{CAMINHO_DOS_DOCS}/BACKLOG_FUTURO.md` — Roadmap estratégico e critérios de aceite

## Ler APENAS QUANDO NECESSÁRIO
4. `{CAMINHO_DOS_DOCS}/DECISION_LOG.md` — Quando precisar entender "por quê" uma decisão foi tomada
5. Arquivo específico em `{CAMINHO_DO_ARCHIVE}/` — APENAS se o usuário pedir explicitamente

## NUNCA LER
- `{CAMINHO_DO_ARCHIVE}/*` — Blueprints arquivados (auditoria humana, não operacional)
- `.git/` — Controle de versão
- `__pycache__/`, `node_modules/`, `.cache/`, `dist/`, `build/` — Artefatos de build
- Qualquer arquivo `*.resolved`, `*.bak`, `*.old`, `*.tmp`

## Workflow de nova fase
1. Ler `{CAMINHO_DOS_DOCS}/CURRENT_STATE.md` (entender onde estamos)
2. Ler `{CAMINHO_DOS_DOCS}/BACKLOG_FUTURO.md` (confirmar qual fase é a próxima)
3. Ler o blueprint da fase a implementar (o usuário fornecerá)
4. Ler apenas os arquivos de `{CAMINHO_DO_CODIGO}` que serão modificados
5. Implementar
6. Após validação pelo usuário: executar `{CAMINHO_DOS_DOCS}/ARCHIVING_PROTOCOL.md`

## Regra de log obrigatório
Se qualquer artefato esperado não for encontrado durante a implementação (arquivo ausente,
parsing falhou, dependência não resolvida), NUNCA usar fallback silencioso.
SEMPRE reportar ao usuário: "Artefato [{nome}] não encontrado em [{caminho}]. Aguardando instrução."
´´´

---

### AÇÃO 6: Criar `.humano` na raiz do projeto

´´´
SOBRE O SEU WORKFLOW — LEIA ANTES DE INICIAR QUALQUER FASE
══════════════════════════════════════════════════════════

PROBLEMA QUE ESTE ARQUIVO RESOLVE
──────────────────────────────────
Antes (desperdiçava tokens e contexto)
  "Leia todo o projeto e implemente a fase X"
  → IA lê 50.000+ tokens de arquivos irrelevantes
  → Consome 70% do contexto apenas para carregar
  → Sobra pouco espaço para raciocinar e implementar
  → Resultado: implementação superficial ou com regressões

Depois (otimizado)
  "Leia .ai-context, depois docs/CURRENT_STATE.md.
   Aqui está o blueprint da Fase N: [conteúdo].
   Implemente."
  → IA lê ~2.000 tokens de estado + blueprint da fase
  → IA lê apenas os arquivos de src/ que vai modificar
  → 90%+ do contexto disponível para implementação
  → Resultado: implementação focada, sem distrações

──────────────────────────────────
FLUXO PADRÃO DE CADA FASE
══════════════════════════

PASSO 1 — VOCÊ planeja a fase e escreve o blueprint

PASSO 2 — VOCÊ diz à IA:
  "Leia .ai-context e docs/CURRENT_STATE.md.
   A próxima fase é [Fase N] — [nome da onda] do Backlog.
   Aqui está o blueprint: [cola ou indica o arquivo].
   Implemente."

PASSO 3 — IA implementa lendo apenas os arquivos de código necessários

PASSO 4 — VOCÊ valida (roda os testes, executa manualmente)

PASSO 5 — VOCÊ diz à IA:
  "Fase N concluída e validada.
   Execute o protocolo docs/ARCHIVING_PROTOCOL.md."

PASSO 6 — IA arquiva:
  → Roda e reporta resultado dos testes
  → Atualiza CURRENT_STATE + DECISION_LOG + BACKLOG_FUTURO
  → Arquiva blueprint como .resolved
  → Sugere mensagem de commit

PASSO 7 — Você faz o commit e a próxima fase começa com contexto limpo

──────────────────────────────────
QUANDO A IA PRECISAR VER CÓDIGO QUE NÃO VAI MODIFICAR
  Diga: "Consulte o DECISION_LOG para entender por que [módulo] funciona assim"
  Não faça ela ler o arquivo inteiro.

QUANDO UM ARTEFATO NÃO FOR ENCONTRADO
  A IA deve parar e reportar — nunca usar fallback silencioso.
  Exemplo correto: "Artefato [system_design] não encontrado em [parsed]. Aguardando instrução."
  Exemplo errado: [injeta contexto geral sem avisar e continua]

QUANDO OS TESTES FALHAREM
  A IA não deve arquivar. Deve reportar a falha e aguardar.
  O arquivamento pressupõe suíte de testes passando integralmente.
´´´

---

### VALIDAÇÃO FINAL

Após criar os 6 arquivos, confirme cada item abaixo. Não marque como concluído se qualquer item falhar.

1. ✅ `{CAMINHO_DOS_DOCS}/CURRENT_STATE.md` existe e tem ≤ 1500 tokens
2. ✅ `{CAMINHO_DOS_DOCS}/DECISION_LOG.md` existe e cobre Fases 1 a {NUMERO_DA_FASE_ATUAL}
3. ✅ `{CAMINHO_DOS_DOCS}/BACKLOG_FUTURO.md` existe com itens classificados como CONCLUÍDO ou PENDENTE
4. ✅ `{CAMINHO_DOS_DOCS}/ARCHIVING_PROTOCOL.md` existe com os 8 passos completos
5. ✅ `.ai-context` existe na raiz do projeto
6. ✅ `.humano` existe na raiz do projeto
7. ✅ Arquivos em `{CAMINHO_DO_ARCHIVE}/` **NÃO foram deletados**
8. ✅ Nenhum arquivo de código-fonte foi alterado
9. ✅ A suíte de testes em `{CAMINHO_DOS_TESTES}` foi verificada — reportar: **[N testes encontrados, N passando]**

Liste os 6 arquivos criados com a contagem aproximada de tokens de cada um e o resultado da verificação de testes.

---

## Exemplo de Preenchimento

Para usar, substitua:

| Variável | Exemplo |
|---|---|
| `{NOME_DO_PROJETO}` | `MeuApp` |
| `{NUMERO_DA_FASE_ATUAL}` | `5` |
| `{CAMINHO_DO_CODIGO}` | `src/` |
| `{CAMINHO_DOS_TESTES}` | `tests/` |
| `{CAMINHO_DOS_DOCS}` | `docs/` |
| `{CAMINHO_DO_ARCHIVE}` | `docs/archive/` |

---

## Resumo das Mudanças em Relação à Versão Anterior

| Mudança | Motivo |
|---|---|
| Adicionado `BACKLOG_FUTURO.md` como artefato gerenciado (Ação 3) | Roadmap estratégico com critérios de aceite por onda precisa de arquivo próprio, não vive disperso nos blueprints |
| ARCHIVING_PROTOCOL agora tem Pré-condição com verificação de testes | Arquivar com testes quebrados propaga dívida silenciosa para a próxima fase |
| ARCHIVING_PROTOCOL inclui passo de sugestão de commit (Passo 8) | Padroniza mensagens de commit e elimina decisão manual repetitiva |
| `.ai-context` referencia `BACKLOG_FUTURO.md` no workflow | IA precisa saber qual fase é a próxima antes de implementar, não apenas o estado atual |
| Regra de log obrigatório no `.ai-context` | Fallback silencioso (injetar contexto errado sem avisar) é um anti-padrão que causa bugs invisíveis |
| `.humano` inclui seção sobre artefatos não encontrados | Instrução explícita para a IA parar e reportar em vez de continuar silenciosamente |
| Testes agora têm coluna `Comando` no CURRENT_STATE | IA precisa saber o comando exato para rodar a suíte, não apenas saber que ela existe |
| Tipo `FIX` adicionado ao DECISION_LOG | Bugs estruturais corrigidos durante fases precisam ser rastreáveis separadamente de features |
| Validação final exige resultado de testes (item 9) | Consistência: não faz sentido criar o sistema de arquivamento e não confirmar que a base está limpa |