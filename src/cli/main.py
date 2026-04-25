import argparse
import sys
import logging
from src.core.controller import Controller

# Configuração de Logs básica para a CLI
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

def main():
    parser = argparse.ArgumentParser(
        description="IdeaForge 2 — Motor de Debate e Síntese de Arquitetura Técnica."
    )
    
    parser.add_argument(
        "--idea", 
        type=str, 
        required=True, 
        help="A ideia de produto ou sistema a ser debatida."
    )
    
    parser.add_argument(
        "--model", 
        type=str, 
        help="Override do modelo Ollama (default: llama3)."
    )
    
    parser.add_argument(
        "--interactive", 
        action="store_true", 
        help="[Placeholder] Habilita modo interativo (não implementado na Wave 3)."
    )
    
    parser.add_argument(
        "--debug", 
        action="store_true", 
        help="Exibe dados técnicos (transcript, snapshot) no stderr."
    )
    
    args = parser.parse_args()
    
    controller = Controller()
    
    print("\n" + "="*50)
    print("      🚀 IDEAFORGE 2 — INICIALIZANDO PIPELINE")
    print("="*50 + "\n")
    
    try:
        result = controller.run(
            idea=args.idea,
            model_override=args.model,
            debug=args.debug
        )
        
        if result["status"] == "success":
            print("\n" + "─"*50)
            print("✅ PIPELINE CONCLUÍDO COM SUCESSO!")
            print(f"📄 Relatório: {result['output_path']}")
            print(f"📊 Debate: {result['debate_rounds']} rounds | {result['issues_total']} issues")
            if result.get("fallback_used"):
                print("⚠️  AVISO: O Synthesizer falhou. Relatório gerado via Fallback.")
            print("─"*50 + "\n")
        else:
            print(f"\n❌ ERRO NO PIPELINE: {result.get('error', 'Erro desconhecido')}\n")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n🛑 Operação cancelada pelo usuário.")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 ERRO CRÍTICO INESPERADO: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
