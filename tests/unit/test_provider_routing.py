"""
test_provider_routing.py
Testes TDD para o Bug de Roteamento de Provedor (W5-HOTFIX-01).

Problema diagnosticado: Controller._get_provider() instancia CloudProvider
(stub sem HTTP) para qualquer modelo com sufixo "-cloud" ou ":cloud", mesmo
que esses modelos sejam servidos localmente pelo Ollama.

Evidência: execução de 26/04/2026 com gpt-oss:20b-cloud completou 2 rounds
em 6ms — impossível com LLM real. O CloudProvider.generate() retorna uma
string hardcoded sem fazer nenhuma chamada HTTP.

Cobertura deste arquivo:
  Bloco A  — Unit: _get_provider() retorna o tipo correto de provider
  Bloco B  — Unit: CloudProvider.generate() é um stub (regressão documentada)
  Bloco C  — Unit: OllamaProvider é instanciado com os parâmetros corretos
  Bloco D  — Unit: detecção de sufixo "-cloud" e ":cloud" no model_name
  Bloco E  — Integração: pipeline com CloudProvider stub produz output inválido
  Bloco F  — Integração: pipeline com OllamaProvider mocado produz output real
  Bloco G  — Regressão: modelos sem sufixo cloud continuam usando OllamaProvider

Critério de aceitação (binário):
  - Todos os testes do Bloco A falham ANTES da correção de _get_provider()
  - Todos os testes do Bloco A passam APÓS a correção
  - Todos os outros blocos passam em ambos os estados (documentação de comportamento)
"""

import pytest
import os
from unittest.mock import MagicMock, patch, call


# ─────────────────────────────────────────────────────────────────────────────
# Fixtures compartilhadas
# ─────────────────────────────────────────────────────────────────────────────

@pytest.fixture
def controller():
    """Controller limpo sem LLM real."""
    from src.core.controller import Controller
    return Controller()


@pytest.fixture
def mock_debate_result():
    """DebateResult mínimo para não travar o pipeline."""
    from src.debate.debate_engine import DebateResult
    return DebateResult(
        final_proposal="# 1. Proposta\nConteúdo válido de proposta expandida.",
        transcript=[
            {"role": "proponent", "content": "Proposta expandida.", "parsing_succeeded": True},
            {"role": "critic",    "content": "| HIGH | SECURITY | Vuln X | Corrigir |", "parsing_succeeded": True},
        ],
        board_snapshot={"issues": {}, "decisions": {}, "assumptions": {}},
        stats={"total_rounds": 2, "stop_reason": "convergência semântica", "issues_raised": 1, "issues_resolved": 0}
    )


@pytest.fixture
def valid_report_result(tmp_path):
    """Resultado de ReportGenerator bem-sucedido."""
    report_path = str(tmp_path / "relatorio.md")
    return {
        "status": "success",
        "output_path": report_path,
        "fallback_used": False,
        "sections_present": ["## Sumário", "## Issues", "## Veredito"],
        "board_stats": {"total_issues": 1, "open": 1, "resolved": 0}
    }


# ─────────────────────────────────────────────────────────────────────────────
# BLOCO A — Unit: _get_provider() retorna o tipo correto de provider
# Estes testes DEVEM FALHAR antes da correção e PASSAR depois.
# ─────────────────────────────────────────────────────────────────────────────

class TestGetProviderRouting:
    """
    Verifica que _get_provider() SEMPRE retorna OllamaProvider para modelos
    com sufixo '-cloud' ou ':cloud', pois esses modelos são servidos pelo
    Ollama local, não por uma API cloud externa.

    ESTADO ESPERADO ANTES DA CORREÇÃO: TODOS FALHAM (retorna CloudProvider).
    ESTADO ESPERADO APÓS A CORREÇÃO:   TODOS PASSAM (retorna OllamaProvider).
    """

    def test_gpt_oss_20b_cloud_retorna_ollama_provider(self, controller):
        """Bug principal: gpt-oss:20b-cloud deve usar OllamaProvider, não CloudProvider."""
        from src.models.ollama_provider import OllamaProvider
        provider = controller._get_provider("gpt-oss:20b-cloud", think=False, is_cloud=True)
        assert isinstance(provider, OllamaProvider), (
            f"Esperado OllamaProvider, obtido {type(provider).__name__}. "
            "Modelos '*-cloud' são servidos localmente pelo Ollama. "
            "CloudProvider é um stub que não faz chamadas HTTP reais."
        )

    def test_gpt_oss_120b_cloud_retorna_ollama_provider(self, controller):
        """Variante 120b: mesmo comportamento esperado."""
        from src.models.ollama_provider import OllamaProvider
        provider = controller._get_provider("gpt-oss:120b-cloud", think=False, is_cloud=True)
        assert isinstance(provider, OllamaProvider)

    def test_qwen3_cloud_retorna_ollama_provider(self, controller):
        """qwen3.5:cloud deve usar OllamaProvider."""
        from src.models.ollama_provider import OllamaProvider
        provider = controller._get_provider("qwen3.5:cloud", think=False, is_cloud=True)
        assert isinstance(provider, OllamaProvider)

    def test_deepseek_cloud_retorna_ollama_provider(self, controller):
        """deepseek-v3.1:671b-cloud deve usar OllamaProvider."""
        from src.models.ollama_provider import OllamaProvider
        provider = controller._get_provider("deepseek-v3.1:671b-cloud", think=False, is_cloud=True)
        assert isinstance(provider, OllamaProvider)

    def test_provider_instanciado_com_model_name_correto(self, controller):
        """model_name deve ser preservado ao instanciar OllamaProvider."""
        with patch("src.core.controller.OllamaProvider") as mock_ollama:
            controller._get_provider("gpt-oss:20b-cloud", think=False, is_cloud=True)
            args, kwargs = mock_ollama.call_args
            assert kwargs.get("model_name") == "gpt-oss:20b-cloud", (
                f"model_name passado incorretamente: {kwargs}"
            )

    def test_provider_instanciado_com_think_false(self, controller):
        """think=False deve ser repassado ao OllamaProvider para modelo cloud."""
        with patch("src.core.controller.OllamaProvider") as mock_ollama:
            controller._get_provider("gpt-oss:20b-cloud", think=False, is_cloud=True)
            _, kwargs = mock_ollama.call_args
            assert kwargs.get("think") is False

    def test_provider_instanciado_com_think_true(self, controller):
        """think=True deve ser repassado ao OllamaProvider para modelo cloud."""
        with patch("src.core.controller.OllamaProvider") as mock_ollama:
            controller._get_provider("gpt-oss:20b-cloud", think=True, is_cloud=True)
            _, kwargs = mock_ollama.call_args
            assert kwargs.get("think") is True


# ─────────────────────────────────────────────────────────────────────────────
# BLOCO B — Unit: CloudProvider.generate() é um stub (regressão documentada)
# Estes testes documentam o comportamento ATUAL do CloudProvider para que
# futuras mudanças não passem silenciosamente.
# ─────────────────────────────────────────────────────────────────────────────

class TestCloudProviderStubBehavior:
    """
    Documenta que CloudProvider.generate() é um stub sem HTTP.
    Estes testes sempre passam — são documentação do bug conhecido,
    não do comportamento desejado.
    """

    def test_cloud_provider_generate_nao_faz_chamada_http(self):
        """CloudProvider.generate() não usa requests — retorna string hardcoded."""
        from src.models.cloud_provider import CloudProvider
        import requests

        provider = CloudProvider(api_key="fake-key", model_name="gpt-oss:20b-cloud")

        # Monkeypatch requests para detectar qualquer chamada HTTP
        with patch.object(requests, "post") as mock_post, \
             patch.object(requests, "get") as mock_get:

            result = provider.generate("Qual o sentido da vida?", role="critic")

            # Confirmar que NENHUMA chamada HTTP foi feita
            assert not mock_post.called, "CloudProvider não deveria chamar requests.post"
            assert not mock_get.called, "CloudProvider não deveria chamar requests.get"

        # Confirmar que retorna string hardcoded
        assert isinstance(result, str)
        assert len(result) < 100, (
            f"CloudProvider retornou string curta hardcoded ({len(result)} chars), "
            "confirmando que é um stub."
        )

    def test_cloud_provider_generate_retorna_mesmo_para_qualquer_prompt(self):
        """Qualquer prompt produz resposta com formato fixo — confirmação de stub."""
        from src.models.cloud_provider import CloudProvider

        provider = CloudProvider(api_key="fake-key", model_name="gpt-oss:20b-cloud")

        resp_a = provider.generate("Ideia de negócio de afiliados", role="proponent")
        resp_b = provider.generate("Qual o sentido da vida?", role="critic")
        resp_c = provider.generate("Síntese do debate completo", role="synthesizer")

        # Todos começam com o mesmo prefixo — stub confirmado
        assert resp_a.startswith("[Cloud Provider"), f"Esperado prefixo de stub, obtido: {resp_a[:50]}"
        assert resp_b.startswith("[Cloud Provider"), f"Esperado prefixo de stub, obtido: {resp_b[:50]}"
        assert resp_c.startswith("[Cloud Provider"), f"Esperado prefixo de stub, obtido: {resp_c[:50]}"

    def test_cloud_provider_sem_api_key_retorna_erro(self):
        """Sem LLM_API_KEY, CloudProvider retorna mensagem de erro explícita."""
        from src.models.cloud_provider import CloudProvider

        provider = CloudProvider(api_key="", model_name="qualquer-modelo")
        result = provider.generate("Prompt qualquer")

        assert "Error" in result or "error" in result.lower(), (
            f"Esperado mensagem de erro sem API key, obtido: {result}"
        )


# ─────────────────────────────────────────────────────────────────────────────
# BLOCO C — Unit: OllamaProvider instanciado com parâmetros corretos
# Garantias de contrato após a correção.
# ─────────────────────────────────────────────────────────────────────────────

class TestOllamaProviderInstanciation:
    """Verifica que OllamaProvider recebe todos os parâmetros necessários."""

    def test_modelo_local_instancia_ollama_com_parametros_corretos(self, controller):
        """Modelo sem sufixo cloud: OllamaProvider com model_name e think corretos."""
        with patch("src.core.controller.OllamaProvider") as mock_ollama:
            controller._get_provider("llama3.2:3b", think=False, is_cloud=False)
            _, kwargs = mock_ollama.call_args
            assert kwargs.get("model_name") == "llama3.2:3b"
            assert kwargs.get("think") is False

    def test_show_thinking_falso_quando_think_falso(self, controller):
        """think=False → show_thinking=False para não exibir raciocínio no terminal."""
        with patch("src.core.controller.OllamaProvider") as mock_ollama:
            controller._get_provider("qualquer-modelo", think=False, is_cloud=False)
            _, kwargs = mock_ollama.call_args
            # show_thinking deve espelhar think para consistência visual
            assert kwargs.get("show_thinking") is False, (
                "show_thinking=True com think=False causa exibição indevida de "
                "raciocínio no terminal (Bug B documentado)."
            )

    def test_show_thinking_verdadeiro_quando_think_verdadeiro(self, controller):
        """think=True → show_thinking=True."""
        with patch("src.core.controller.OllamaProvider") as mock_ollama:
            controller._get_provider("qualquer-modelo", think=True, is_cloud=False)
            _, kwargs = mock_ollama.call_args
            assert kwargs.get("show_thinking") is True


# ─────────────────────────────────────────────────────────────────────────────
# BLOCO D — Unit: detecção de sufixo "-cloud" e ":cloud" no run()
# ─────────────────────────────────────────────────────────────────────────────

class TestCloudSuffixDetection:
    """
    Verifica que Controller.run() detecta corretamente o sufixo cloud
    e chama _get_provider com is_cloud=True nos casos corretos.
    """

    def _run_com_modelo(self, controller, model_name, mock_debate_result, valid_report_result):
        """Helper: executa run() com mocks mínimos e captura a chamada ao provider."""
        with patch.object(controller, "_get_provider", wraps=controller._get_provider) as spy_provider, \
             patch("src.core.controller.OllamaProvider") as mock_ollama, \
             patch("src.core.controller.CloudProvider") as mock_cloud, \
             patch("src.core.controller.DomainDetector") as mock_detector, \
             patch("src.core.controller.DomainContextBuilder") as mock_builder, \
             patch("src.core.controller.ValidationBoard"), \
             patch("src.core.controller.ContextBuilder"), \
             patch("src.core.controller.DebateEngine") as mock_engine, \
             patch.object(controller.generator, "generate", return_value=valid_report_result):

            mock_domain = MagicMock()
            mock_domain.domain = "generic"
            mock_domain.confidence = 0.0
            mock_detector.return_value.detect.return_value = mock_domain

            mock_profile = MagicMock()
            mock_profile.source = "llm"
            mock_builder.return_value.build.return_value = mock_profile

            mock_engine.return_value.run_debate.return_value = mock_debate_result

            controller.run("Qualquer ideia", model_name=model_name)
            return spy_provider

    def test_sufixo_hifen_cloud_detecta_is_cloud_true(self, controller, mock_debate_result, valid_report_result):
        """'gpt-oss:20b-cloud' → is_cloud=True passado a _get_provider."""
        spy = self._run_com_modelo(controller, "gpt-oss:20b-cloud", mock_debate_result, valid_report_result)
        _, _, is_cloud = spy.call_args[0]
        assert is_cloud is True, "Sufixo '-cloud' deve resultar em is_cloud=True"

    def test_sufixo_dois_pontos_cloud_detecta_is_cloud_true(self, controller, mock_debate_result, valid_report_result):
        """'qwen3.5:cloud' → is_cloud=True passado a _get_provider."""
        spy = self._run_com_modelo(controller, "qwen3.5:cloud", mock_debate_result, valid_report_result)
        _, _, is_cloud = spy.call_args[0]
        assert is_cloud is True

    def test_modelo_sem_cloud_detecta_is_cloud_false(self, controller, mock_debate_result, valid_report_result):
        """'llama3.2:3b' → is_cloud=False passado a _get_provider."""
        spy = self._run_com_modelo(controller, "llama3.2:3b", mock_debate_result, valid_report_result)
        _, _, is_cloud = spy.call_args[0]
        assert is_cloud is False

    def test_modelo_qwen_local_sem_cloud_detecta_false(self, controller, mock_debate_result, valid_report_result):
        """'qwen2.5:3b' (sem ':cloud') → is_cloud=False."""
        spy = self._run_com_modelo(controller, "qwen2.5:3b", mock_debate_result, valid_report_result)
        _, _, is_cloud = spy.call_args[0]
        assert is_cloud is False


# ─────────────────────────────────────────────────────────────────────────────
# BLOCO E — Integração: pipeline com CloudProvider stub produz output inválido
# Documenta o comportamento defeituoso ANTES da correção.
# ─────────────────────────────────────────────────────────────────────────────

class TestPipelineComCloudProviderStub:
    """
    Executa o pipeline completo usando o CloudProvider stub (comportamento atual
    antes da correção). Documenta que o output é inválido/vazio.

    Estes testes são marcados como xfail: documentam comportamento ERRADO
    que DEVE SER CORRIGIDO pelo W5-HOTFIX-01.
    """

    def test_cloud_provider_stub_nao_gera_issues_reais(self, tmp_path):
        """
        Com CloudProvider stub, o debate termina sem issues semânticos reais.
        O 'debate' foi completado em < 100ms — impossível com LLM real.
        """
        from src.models.cloud_provider import CloudProvider
        from src.core.validation_board import ValidationBoard
        from src.debate.debate_state_tracker import DebateStateTracker
        from src.debate.context_builder import ContextBuilder
        from src.debate.debate_engine import DebateEngine
        from src.core.domain_context_builder import DomainContextBuilder

        provider = CloudProvider(api_key="fake", model_name="gpt-oss:20b-cloud")
        board = ValidationBoard()
        tracker = DebateStateTracker()
        builder = ContextBuilder(board=board)

        # DomainContextBuilder com CloudProvider stub: JSON não extraível → fallback
        ctx_builder = DomainContextBuilder(provider=provider)
        profile = ctx_builder.build("qual o sentido da vida", "generic")

        # O profile vem do fallback, não do LLM — source deve ser "fallback"
        assert profile.source == "fallback", (
            f"Com CloudProvider stub, DomainContextBuilder deve usar fallback. "
            f"Obtido source='{profile.source}'"
        )

    def test_cloud_provider_stub_resposta_identica_em_todos_rounds(self):
        """
        CloudProvider retorna sempre a mesma string → ConvergenceDetector
        para o debate no Round 2 por saturação (Jaccard=1.0 entre rounds idênticos).
        """
        from src.models.cloud_provider import CloudProvider

        provider = CloudProvider(api_key="fake", model_name="gpt-oss:20b-cloud")

        resp1 = provider.generate("Prompt do round 1 de crítica", role="critic")
        resp2 = provider.generate("Prompt do round 2 de crítica", role="critic")
        resp3 = provider.generate("Prompt completamente diferente", role="proponent")

        # Todas as respostas começam com o mesmo prefixo → Jaccard ≈ 1.0
        assert resp1[:20] == resp2[:20] == resp3[:20], (
            "CloudProvider retorna respostas idênticas para qualquer prompt, "
            "causando saturação imediata e debate em 6ms."
        )

    def test_timing_anormal_indica_stub(self):
        """
        Um debate real com gpt-oss:20b-cloud leva > 5 segundos.
        Um debate com CloudProvider stub termina em < 100ms.
        Este teste documenta o critério de detecção de stub.
        """
        import time
        from src.models.cloud_provider import CloudProvider

        provider = CloudProvider(api_key="fake", model_name="gpt-oss:20b-cloud")

        start = time.perf_counter()
        for _ in range(10):
            provider.generate("Prompt de teste " + "x" * 500, role="critic")
        elapsed_ms = (time.perf_counter() - start) * 1000

        assert elapsed_ms < 50, (
            f"CloudProvider stub deveria completar 10 calls em < 50ms. "
            f"Levou {elapsed_ms:.1f}ms. Se este teste falhar, o CloudProvider "
            f"pode ter sido corrigido para fazer chamadas HTTP reais."
        )


# ─────────────────────────────────────────────────────────────────────────────
# BLOCO F — Integração: pipeline com OllamaProvider mocado produz output real
# Documenta o comportamento CORRETO após a correção.
# ─────────────────────────────────────────────────────────────────────────────

class TestPipelineComOllamaProviderMocado:
    """
    Substitui o provider por um MockProvider que simula respostas LLM reais.
    Verifica que o pipeline completo produz um relatório válido.
    """

    def _build_mock_provider(self):
        """MockProvider que simula o LLM respondendo corretamente em cada papel."""
        from tests.conftest import MockProvider

        EXPANSION_RESPONSE = (
            "# 1. Visão Geral\nAnálise filosófica do sentido da vida.\n"
            "# 2. Problema\nA questão existencial central da humanidade.\n"
            "# 3. Solução/Tese Central\nO sentido é construído, não descoberto.\n"
            "# 4. Operação/Implementação\nPráticas contemplativas e ação ética.\n"
            "# 5. Riscos\nNilismo, relativismo extremo.\n"
            "# 6. Premissas\nO ser humano busca significado intrinsecamente.\n"
            "# 7. Critérios de Sucesso\nVida com propósito, coerência e bem-estar."
        )
        CONTEXT_JSON = (
            '{"expansion_sections": ['
            '{"id": "PROBLEMA", "title": "Problema", "instruction": "Definir o problema"},'
            '{"id": "SOLUCAO", "title": "Solucao", "instruction": "Propor solucao"},'
            '{"id": "RISCOS", "title": "Riscos", "instruction": "Mapear riscos"},'
            '{"id": "PREMISSAS", "title": "Premissas", "instruction": "Listar premissas"},'
            '{"id": "SUCESSO", "title": "Sucesso", "instruction": "Definir sucesso"},'
            '{"id": "PUBLICO", "title": "Publico", "instruction": "Identificar publico"}'
            '], "validation_dimensions": ['
            '{"id": "FEASIBILITY", "display_name": "Viabilidade", "description": "Viabilidade", "spawn_hint": "Filósofo"},'
            '{"id": "CONSISTENCY", "display_name": "Consistência", "description": "Consistência", "spawn_hint": "Logicista"}'
            '], "specialist_hints": ["Filósofo"], '
            '"critical_questions": ["O sentido é objetivo ou subjetivo?"], '
            '"success_criteria": {"clarity": "Proposta coerente e defensável"}}'
        )
        CRITIQUE_RESPONSE = (
            "| HIGH | CONSISTENCY | A tese ignora perspectivas objetivistas | "
            "Incorporar argumento de Nagel sobre o absurdo |\n"
            "| MED | COMPLETENESS | Falta análise de tradições orientais | "
            "Incluir perspectiva budista |\n"
        )
        DEFENSE_RESPONSE = (
            "## Pontos Aceitos\n"
            "- ISS-0001: Concordo com a necessidade de incluir perspectiva budista.\n"
            "## Melhorias Propostas\n"
            "| Solução | Adicionado argumento de Nagel | Corrige inconsistência apontada |\n"
        )
        SYNTHESIS_RESPONSE = (
            "## Sumário Executivo\nA ideia foi debatida com rigor filosófico.\n"
            "## Decisões Validadas\n- A tese construtivista foi mantida após debate.\n"
            "## Issues Pendentes\n- ISS-0001: Perspectiva objetivista não totalmente resolvida.\n"
            "## Matriz de Risco\n- Risco de relativismo: MED\n"
            "## Veredito\nA proposta é filosoficamente defensável com as ressalvas apontadas."
        )

        def route(prompt, role=None, **kwargs):
            # DomainContextBuilder (role="user", contém "{idea}")
            if role == "user" or "meta-análise" in prompt.lower():
                return CONTEXT_JSON
            # Round 0 Expansion (role="proponent", contém "ESTRUTURA OBRIGATÓRIA")
            if "ESTRUTURA OBRIGATÓRIA" in prompt or "proposta estruturada" in prompt.lower():
                return EXPANSION_RESPONSE
            # Critic (role="critic")
            if role == "critic" or "Agente Crítico" in prompt:
                return CRITIQUE_RESPONSE
            # Defense (role="proponent", contém "defendendo")
            if role == "proponent" or "defendendo" in prompt.lower():
                return DEFENSE_RESPONSE
            # Synthesizer (role="synthesizer" ou "juíza")
            if "juíza técnica" in prompt.lower() or role == "synthesizer":
                return SYNTHESIS_RESPONSE
            return "Resposta genérica do mock."

        return MockProvider(responses=route)

    def test_pipeline_completo_com_mock_ollama_retorna_success(self, tmp_path):
        """Pipeline completo com MockProvider (simula OllamaProvider) → status success."""
        from src.core.controller import Controller

        mock_provider = self._build_mock_provider()
        ctrl = Controller()

        with patch("src.core.controller.OllamaProvider", return_value=mock_provider), \
             patch.object(ctrl, "_get_provider", return_value=mock_provider), \
             patch.object(ctrl, "_get_output_path", return_value=str(tmp_path / "relatorio.md")):

            result = ctrl.run("qual o sentido da vida", model_name="gpt-oss:20b-cloud")

        assert result["status"] == "success", (
            f"Pipeline com MockProvider deve retornar status=success. "
            f"Obtido: {result}"
        )

    def test_pipeline_completo_com_mock_ollama_gera_relatorio_em_disco(self, tmp_path):
        """Pipeline com MockProvider gera arquivo de relatório em disco."""
        from src.core.controller import Controller

        mock_provider = self._build_mock_provider()
        ctrl = Controller()
        output_path = str(tmp_path / "relatorio.md")

        with patch("src.core.controller.OllamaProvider", return_value=mock_provider), \
             patch.object(ctrl, "_get_provider", return_value=mock_provider), \
             patch.object(ctrl, "_get_output_path", return_value=output_path):

            result = ctrl.run("qual o sentido da vida", model_name="gpt-oss:20b-cloud")

        assert os.path.exists(result["output_path"]), (
            f"Arquivo de relatório deve existir em disco: {result['output_path']}"
        )
        with open(result["output_path"], encoding="utf-8") as f:
            content = f.read()
        assert len(content) > 100, "Relatório gerado não pode ser praticamente vazio."

    def test_pipeline_completo_com_mock_ollama_registra_issues(self, tmp_path):
        """Pipeline com MockProvider registra pelo menos 1 issue no board."""
        from src.core.controller import Controller

        mock_provider = self._build_mock_provider()
        ctrl = Controller()

        with patch("src.core.controller.OllamaProvider", return_value=mock_provider), \
             patch.object(ctrl, "_get_provider", return_value=mock_provider), \
             patch.object(ctrl, "_get_output_path", return_value=str(tmp_path / "r.md")):

            result = ctrl.run("qual o sentido da vida", model_name="gpt-oss:20b-cloud")

        # O MockProvider gera crítica com 1 HIGH e 1 MED → pelo menos 1 issue
        assert result.get("issues_total", 0) >= 1, (
            f"O debate deve registrar pelo menos 1 issue. "
            f"Obtido issues_total={result.get('issues_total')}. "
            f"Com CloudProvider stub, nenhum issue é gerado por parsing de lixo."
        )

    def test_domain_context_builder_usa_json_do_mock_provider(self, tmp_path):
        """DomainContextBuilder extrai o JSON do MockProvider → profile.source == 'llm'."""
        from src.core.domain_context_builder import DomainContextBuilder
        from tests.conftest import MockProvider

        json_response = (
            '{"expansion_sections": ['
            '{"id": "PROBLEMA", "title": "Problema", "instruction": "Definir"},'
            '{"id": "SOLUCAO", "title": "Solução", "instruction": "Propor"},'
            '{"id": "RISCOS", "title": "Riscos", "instruction": "Mapear"},'
            '{"id": "PREMISSAS", "title": "Premissas", "instruction": "Listar"},'
            '{"id": "SUCESSO", "title": "Sucesso", "instruction": "Definir"},'
            '{"id": "CRITERIOS", "title": "Critérios", "instruction": "Medir"}'
            '], "validation_dimensions": ['
            '{"id": "FEASIBILITY", "display_name": "Viab", "description": "V", "spawn_hint": "E"}'
            '], "specialist_hints": [], "critical_questions": [], "success_criteria": {}}'
        )

        mock_provider = MockProvider(responses=lambda p, **kw: json_response)
        ctx_builder = DomainContextBuilder(provider=mock_provider)
        profile = ctx_builder.build("qual o sentido da vida", "generic")

        assert profile.source == "llm", (
            f"Com MockProvider que retorna JSON válido, DomainContextBuilder deve "
            f"usar source='llm'. Obtido source='{profile.source}'. "
            f"Com CloudProvider stub (que retorna lixo), source seria 'fallback'."
        )
        assert len(profile.expansion_sections) >= 5


# ─────────────────────────────────────────────────────────────────────────────
# BLOCO G — Regressão: modelos sem sufixo cloud continuam usando OllamaProvider
# Garante que a correção não quebra o comportamento existente.
# ─────────────────────────────────────────────────────────────────────────────

class TestRegressaoModelosLocais:
    """
    Garante que a correção do W5-HOTFIX-01 não afeta modelos locais
    (sem sufixo '-cloud' ou ':cloud'). Todos devem continuar usando OllamaProvider.
    """

    @pytest.mark.parametrize("model_name", [
        "llama3.2:3b-instruct-q4_0",
        "qwen2.5-coder:3b",
        "qwen2.5-coder:1.5b",
        "qwen3.5:0.8b",
        "qwen3.5:9b",
        "gemma3:1b",
        "gemma4:e2b",
        "phi3:3.8b",
        "deepseek-v3.1:671b",  # sem sufixo -cloud
        "qwen2.5:0.5b",
        "gemma2:2b",
    ])
    def test_modelo_local_usa_ollama_provider(self, controller, model_name):
        """Modelo sem sufixo cloud → is_cloud=False → OllamaProvider."""
        from src.models.ollama_provider import OllamaProvider

        # is_cloud=False (calculado no run() para esses modelos)
        provider = controller._get_provider(model_name, think=False, is_cloud=False)
        assert isinstance(provider, OllamaProvider), (
            f"Modelo local '{model_name}' deve usar OllamaProvider. "
            f"Obtido: {type(provider).__name__}"
        )

    @pytest.mark.parametrize("model_name", [
        "llama3.2:3b-instruct-q4_0",
        "qwen2.5-coder:3b",
        "gemma3:1b",
    ])
    def test_modelo_local_recebe_think_correto(self, controller, model_name):
        """think=True/False deve ser repassado corretamente para modelos locais."""
        with patch("src.core.controller.OllamaProvider") as mock_ollama:
            controller._get_provider(model_name, think=True, is_cloud=False)
            _, kwargs = mock_ollama.call_args
            assert kwargs.get("think") is True

            controller._get_provider(model_name, think=False, is_cloud=False)
            _, kwargs = mock_ollama.call_args
            assert kwargs.get("think") is False

    def test_ideia_vazia_retorna_erro_sem_chamar_provider(self, controller):
        """Ideia vazia deve retornar erro antes de instanciar qualquer provider."""
        with patch("src.core.controller.OllamaProvider") as mock_ollama, \
             patch("src.core.controller.CloudProvider") as mock_cloud:

            result = controller.run("", model_name="gpt-oss:20b-cloud")

            assert result["status"] == "error"
            assert not mock_ollama.called, "OllamaProvider não deve ser instanciado para ideia vazia"
            assert not mock_cloud.called, "CloudProvider não deve ser instanciado para ideia vazia"


# ─────────────────────────────────────────────────────────────────────────────
# BLOCO H — Smoke: verificação rápida pós-correção sem Ollama real
# ─────────────────────────────────────────────────────────────────────────────

class TestSmokePostCorrecao:
    """
    Verificação rápida de que a correção não quebrou nenhuma importação
    ou inicialização do sistema.
    """

    def test_controller_importa_sem_erro(self):
        """Controller importa corretamente após a correção."""
        from src.core.controller import Controller
        ctrl = Controller()
        assert ctrl is not None

    def test_controller_tem_metodo_get_provider(self):
        """_get_provider ainda existe e é chamável."""
        from src.core.controller import Controller
        ctrl = Controller()
        assert callable(getattr(ctrl, "_get_provider", None))

    def test_get_provider_aceita_tres_argumentos(self):
        """_get_provider aceita (model_name, think, is_cloud) sem TypeError."""
        from src.core.controller import Controller
        with patch("src.core.controller.OllamaProvider"):
            ctrl = Controller()
            # Não deve levantar TypeError
            ctrl._get_provider("qualquer-modelo", False, True)
            ctrl._get_provider("qualquer-modelo", False, False)
