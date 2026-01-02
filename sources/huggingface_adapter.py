"""
ModelShelf Hugging Face Hub Adapter
Implementation of HubAdapter for Hugging Face.
"""

import logging
import re
from typing import List, Optional
from datetime import datetime

import httpx
from huggingface_hub import HfApi, list_models, model_info
from huggingface_hub.hf_api import ModelInfo as HfModelInfo

from .hub_adapter import HubAdapter, ModelInfo, ModelFile, SearchResult

logger = logging.getLogger(__name__)


class HuggingFaceAdapter(HubAdapter):
    """Hugging Face Hub adapter implementation."""
    
    # GGUF quantisation patterns
    QUANT_PATTERNS = [
        r'Q[2-8]_[KM](?:_[SML])?',  # Q4_K_M, Q8_0, etc.
        r'IQ[1-4]_[XYSM]',  # IQ3_XS, etc.
        r'F(?:16|32)',  # F16, F32
    ]
    
    def __init__(self, token: Optional[str] = None):
        """
        Initialise Hugging Face adapter.
        
        Args:
            token: Optional HF API token for gated models
        """
        self.api = HfApi(token=token)
        self.token = token
        self._client = httpx.AsyncClient(timeout=30.0)
    
    async def search_models(
        self,
        query: str = "",
        page: int = 0,
        page_size: int = 20,
        has_gguf: bool = False,
        sort_by: str = "downloads",
        tags: Optional[List[str]] = None
    ) -> SearchResult:
        """
        Search Hugging Face models.
        """
        try:
            # Build search parameters
            search_query = query
            if has_gguf:
                search_query = f"{query} gguf" if query else "gguf"
            
            # Map sort options
            sort_map = {
                "downloads": "downloads",
                "likes": "likes",
                "trending": "trending",
                "recent": "lastModified"
            }
            hf_sort = sort_map.get(sort_by, "downloads")
            
            # Search models
            models_iterator = list_models(
                search=search_query,
                sort=hf_sort,
                direction=-1,  # Descending
                limit=page_size * (page + 1),  # Get up to current page
                token=self.token
            )
            
            # Convert to list and paginate
            all_models = list(models_iterator)
            start_idx = page * page_size
            end_idx = start_idx + page_size
            page_models = all_models[start_idx:end_idx]
            
            # Convert to ModelInfo
            converted_models = []
            for hf_model in page_models:
                model = await self._convert_hf_model(hf_model)
                if model:
                    converted_models.append(model)
            
            return SearchResult(
                models=converted_models,
                total_count=len(all_models),
                page=page,
                page_size=page_size,
                has_next=end_idx < len(all_models)
            )
            
        except Exception as e:
            logger.error(f"Search failed: {e}", exc_info=True)
            return SearchResult(
                models=[],
                total_count=0,
                page=page,
                page_size=page_size,
                has_next=False
            )
    
    async def get_model_info(self, model_id: str) -> Optional[ModelInfo]:
        """
        Get detailed model information.
        """
        try:
            hf_model = model_info(model_id, token=self.token, files_metadata=True)
            return await self._convert_hf_model(hf_model, fetch_files=True)
        except Exception as e:
            logger.error(f"Failed to get model info for {model_id}: {e}")
            return None
    
    async def list_model_files(self, model_id: str) -> List[ModelFile]:
        """
        List all files in a model.
        """
        try:
            hf_model = model_info(model_id, token=self.token, files_metadata=True)
            files = []
            
            if hasattr(hf_model, 'siblings') and hf_model.siblings:
                for file in hf_model.siblings:
                    model_file = self._convert_file(file, model_id)
                    if model_file:
                        files.append(model_file)
            
            # Sort: GGUF files first, then by size
            files.sort(key=lambda f: (not f.is_gguf, -f.size))
            return files
            
        except Exception as e:
            logger.error(f"Failed to list files for {model_id}: {e}")
            return []
    
    def get_download_url(self, model_id: str, filename: str) -> str:
        """
        Get download URL for a file.
        """
        return f"https://huggingface.co/{model_id}/resolve/main/{filename}"
    
    async def _convert_hf_model(
        self,
        hf_model: HfModelInfo,
        fetch_files: bool = False
    ) -> Optional[ModelInfo]:
        """
        Convert HF model to ModelInfo.
        """
        try:
            # Parse author and name
            parts = hf_model.id.split('/', 1)
            author = parts[0] if len(parts) > 1 else "unknown"
            name = parts[1] if len(parts) > 1 else hf_model.id
            
            # Check for GGUF
            has_gguf = False
            total_size = 0
            files = []
            
            if hasattr(hf_model, 'siblings') and hf_model.siblings:
                for file in hf_model.siblings:
                    if file.rfilename.lower().endswith('.gguf'):
                        has_gguf = True
                    if hasattr(file, 'size') and file.size:
                        total_size += file.size
                    
                    if fetch_files:
                        model_file = self._convert_file(file, hf_model.id)
                        if model_file:
                            files.append(model_file)
            
            # Get tags
            tags = list(hf_model.tags) if hasattr(hf_model, 'tags') and hf_model.tags else []
            
            return ModelInfo(
                id=hf_model.id,
                name=name,
                author=author,
                description=getattr(hf_model, 'description', None),
                tags=tags,
                licence=getattr(hf_model, 'license', None),
                downloads=getattr(hf_model, 'downloads', 0) or 0,
                likes=getattr(hf_model, 'likes', 0) or 0,
                created_at=getattr(hf_model, 'created_at', None),
                updated_at=getattr(hf_model, 'last_modified', None),
                has_gguf=has_gguf,
                total_size=total_size,
                files=files
            )
            
        except Exception as e:
            logger.error(f"Failed to convert model {hf_model.id}: {e}")
            return None
    
    def _convert_file(self, hf_file, model_id: str) -> Optional[ModelFile]:
        """
        Convert HF file to ModelFile.
        """
        try:
            filename = hf_file.rfilename
            is_gguf = filename.lower().endswith('.gguf')
            
            # Extract quantisation from filename
            quantisation = None
            if is_gguf:
                for pattern in self.QUANT_PATTERNS:
                    match = re.search(pattern, filename, re.IGNORECASE)
                    if match:
                        quantisation = match.group(0).upper()
                        break
            
            return ModelFile(
                filename=filename,
                size=getattr(hf_file, 'size', 0) or 0,
                url=self.get_download_url(model_id, filename),
                sha256=getattr(hf_file, 'lfs', {}).get('sha256') if hasattr(hf_file, 'lfs') else None,
                is_gguf=is_gguf,
                quantisation=quantisation
            )
            
        except Exception as e:
            logger.error(f"Failed to convert file {hf_file.rfilename}: {e}")
            return None
    
    async def close(self):
        """Close HTTP client."""
        await self._client.aclose()
