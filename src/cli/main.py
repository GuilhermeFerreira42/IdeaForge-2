import argparse
import sys
import logging
from typing import Optional, List, Dict

from src.core.controller import Controller
from src.models.ollama_provider import OllamaProvider, OllamaMemoryError, OllamaServiceError

# Configuração básica de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

def _display_header():
    print("\n" + "="*50)
    print("      IDEAFORGE 2 -- INTERFACE INTERATIVA")
    print("="*50 + "\n")

def _select_model(models: List[Dict]) -> str:
    """Apresenta lista de modelos e retorna o nome do selecionado."""
    print("Modelos disponíveis no seu Ollama:")
    for i, m in enumerate(models, 1):
        size_gb = m.get('size', 0) / (1024**3)
        print(f"  [{i}] {m['name']} ({size_gb:.1f} GB)")
    
    while True:
        try:
            choice = input(f"\nEscolha o modelo (1-{len(models)}): ").strip()
            idx = int(choice) - 1
            if 0 <= idx < len(models):
                return models[idx]['name']
            print(f"Por favor, escolha um número entre 1 e {len(models)}.")
        except ValueError:
            print("Entrada inválida. Digite apenas o número.")

def _get_idea(default_idea: Optional[str] = None) -> str:
    """Solicita a ideia ao usuário se não fornecida via flag."""
    if default_idea:
        return default_idea
    
    for _ in range(3):
        idea = input("\nDigite sua ideia para validação: ").strip()
        if idea:
            return idea
        print("A ideia não pode ser vazia.")
    
    print("Limite de tentativas excedido.")
    sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="IdeaForge 2 CLI")
    parser.add_argument("--idea", type=str, help="Ideia a ser validada (pula prompt de ideia)")
    parser.add_argument("--model", type=str, help="Nome do modelo (pula seleção de modelo)")
    parser.add_argument("--debug", action="store_true", help="Ativa logs de debug detalhados")
    args = parser.parse_args()

    controller = Controller()
    _display_header()

    # LOOP principal para permitir reinício em caso de erro de memória
    while True:
        try:
            # 1. Seleção de Modelo
            if args.model:
                model_name = args.model
            else:
                try:
                    available_models = OllamaProvider.list_available_models()
                    if not available_models:
                        print("Nenhum modelo encontrado no Ollama. Use 'ollama pull' primeiro.")
                        sys.exit(1)
                    model_name = _select_model(available_models)
                except OllamaServiceError as e:
                    print(f"\nErro no servico Ollama: {e}")
                    sys.exit(1)

            # 2. Verificação de Thinking
            think = False
            if not args.model: # Só pergunta no modo interativo
                if OllamaProvider.check_thinking_support(model_name):
                    choice = input(f"Ativar pensamento profundo em {model_name}? (s/N): ").strip().lower()
                    think = choice == 's'

            # 3. Coleta de Ideia
            idea = _get_idea(args.idea)

            # 4. Execução
            result = controller.run(
                idea=idea,
                model_name=model_name,
                think=think,
                debug=args.debug
            )

            if result["status"] == "success":
                print("\n" + "---"*15)
                print("PIPELINE CONCLUIDO COM SUCESSO!")
                print(f"Relatorio: {result['output_path']}")
                print(f"Modelo: {result['model_used']}")
                print(f"Debate: {result['debate_rounds']} rounds | {result['issues_total']} issues")
                if result.get("fallback_used"):
                    print("AVISO: O Synthesizer falhou. Relatorio gerado via Fallback.")
                print("---"*15 + "\n")
                break # Sucesso, sai do loop
            
            elif result["status"] == "memory_error":
                print(f"\n[!] Memoria insuficiente: {result['error']}\n")
                print("Tente escolher um modelo menor.")
                # Se foi passado via flag, não adianta tentar de novo no loop automático
                if args.model:
                    sys.exit(1)
                continue # Volta para seleção de modelo
            
            else:
                print(f"\nERRO NO PIPELINE: {result.get('error', 'Erro desconhecido')}\n")
                sys.exit(1)

        except KeyboardInterrupt:
            print("\n\nOperacao cancelada pelo usuario.")
            sys.exit(0)
        except Exception as e:
            print(f"\nERRO CRITICO INESPERADO: {e}")
            sys.exit(1)

if __name__ == "__main__":
    main()
