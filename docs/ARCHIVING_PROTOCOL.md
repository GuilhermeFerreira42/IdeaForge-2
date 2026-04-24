# PROTOCOLO DE ARQUIVAMENTO PÓS-FASE — IdeaForge 2

## Quando Executar
Após a conclusão e validação de cada nova fase do projeto.

## Pré-condição Obrigatória
Antes de iniciar o arquivamento, CONFIRMAR que:
- [ ] A suíte de testes em `tests/` passa integralmente
- [ ] Nenhum arquivo de código-fonte foi deixado em estado inconsistente
- [ ] O blueprint da fase foi fornecido pelo usuário ou já existe em `docs/archive/`

Se qualquer item falhar, PARAR e reportar ao usuário antes de continuar.

## Passos Obrigatórios

### 1. Verificar Testes
Confirmar que a suíte de testes passa. Reportar explicitamente:
- Número total de testes encontrados
- Número de testes passando
- Qualquer falha identificada (não arquivar se houver falha não documentada)

### 2. Arquivar Blueprint Completo
- Salvar o blueprint da fase em `docs/archive/phase_XX_nome.resolved`
- Renomear para `.resolved` para sinalizar que é auditoria humana, não leitura de IA
- Este arquivo NUNCA será lido pela IA

### 3. Reescrever CURRENT_STATE.md
- Abrir `docs/CURRENT_STATE.md`
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
  ```
  ### Fases 0-5 (Consolidado)
  - Arquitetura Blackboard + Orquestrador Adaptativo definida (F0)
  - ValidationBoard + Parser 3 níveis implementados (F1)
  - Debate adaptativo integrado com spawning (F3)
  ```

### 6. Atualizar BACKLOG_FUTURO.md
- Localizar o item da fase recém-concluída
- Alterar `Status` de `PENDENTE` para `CONCLUÍDO`
- Se a fase concluída é a última de uma Onda, verificar se a Meta da Onda foi atingida
- Se novas técnicas foram descobertas, adicionar como item novo na Onda apropriada
- Após atualizar os status dos itens concluídos, verificar se a próxima
  onda ainda não tem CONTRATOS_DA_ONDA preenchido. Se não tiver:
  - Gerar uma proposta de CONTRATOS_DA_ONDA para a próxima onda
    com base no BACKLOG, CURRENT_STATE e DECISION_LOG
  - Inserir a proposta no BACKLOG_FUTURO.md com o marcador [PROPOSTA — aguardando validação do usuário]
  - Informar o usuário ao final do arquivamento:
    "CONTRATOS_DA_ONDA da Onda N gerado como proposta. Revise antes de disparar o NEXUS."

### 7. Limpeza do Projeto
- Mover scripts de verificação temporários para `docs/archive/phase_XX/`
- Remover arquivos `.tmp`, `.bak`, `.old` gerados durante a fase
- Mover o blueprint da fase para `docs/archive/phase_XX/`

### 8. Sugerir Mensagem de Commit
Ao final do arquivamento, sugerir uma mensagem de commit no formato:
```
[FASE N] DESCRIÇÃO CURTA EM MAIÚSCULO — resumo do que foi entregue
```
Exemplo: `[FASE 1] VALIDATION BOARD + PARSER 3 NÍVEIS — fundação do tracking expandido`

## Regras de Leitura para a IA
- **SEMPRE ler**: `docs/CURRENT_STATE.md`
- **Ler no início de cada onda**: `docs/BACKLOG_FUTURO.md`
- **Ler sob demanda**: `docs/DECISION_LOG.md` (apenas quando precisar entender "por quê")
- **NUNCA ler**: `docs/archive/*` (backups para humanos)
