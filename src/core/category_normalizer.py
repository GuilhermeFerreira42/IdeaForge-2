import logging
from typing import Optional, List
from src.core.domain_profile import DomainProfile

logger = logging.getLogger(__name__)

class CategoryNormalizer:
    def __init__(self, profile: Optional[DomainProfile]):
        self.profile = profile
        self._valid_ids = {d.id.upper() for d in profile.validation_dimensions} if profile else set()
        self._keyword_map = self._build_keyword_map()

    def normalize(self, raw_category: str) -> Optional[str]:
        if not raw_category:
            return None
        
        clean = raw_category.strip().upper()
        # Se não houver profile, aceita o que vier (retrocompatibilidade)
        if not self.profile:
             return clean
        
        # 1. Check exact match
        if clean in self._valid_ids:
            return clean
            
        # Match por keywords ou nomes parciais
        for vid, keywords in self._keyword_map.items():
            if any(kw in clean for kw in keywords):
                return vid
        # Se não casou com nenhuma dimensão oficial, retorna a própria string limpa
        # Isso evita propagar NoneType e permite que o sistema crie especialistas generalistas
        return clean

    def _build_keyword_map(self) -> dict:
        kmap = {}
        if not self.profile:
            return kmap
        for d in self.profile.validation_dimensions:
            keywords = [k.upper() for k in d.keywords]
            # Adiciona o próprio nome de exibição como keyword
            keywords.extend(d.display_name.upper().split())
            kmap[d.id.upper()] = keywords
        return kmap
