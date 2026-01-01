"""
ModelShelf Hugging Face Hub Adapter
Implementation of HubInterface for Hugging Face.
"""

import logging
from typing import List, Optional
from datetime import datetime

try:
    from huggingface_hub import HfApi, hf_hub_url
    from huggingface_hub.utils import HfHubHTTPError
except ImportError:
    HfApi = None
    hf_hub_url = None
    HfHubHTTPError = Exception

from sources.hub_interface import HubInterface
from domain.models import Model, ModelFile, SearchFilter, SearchResult

logger = logging.getLogger(__name__)


class HuggingFaceHub(HubInterface):
    """
    Hugging Face Hub adapter.
    Implements model search and file discovery.
    """
    
    def __init__(self, token: Optional[str] = None):
        """
        Initialise Hugging Face Hub adapter.
        
        Args:
            token: Optional HF token for accessing gated models
        """
        if HfApi is None:
            raise ImportError(
                "huggingface_hub is required. "
                "Install with: pip install huggingface-hub"
            )
        
        self.api = HfApi(token=token)
        self.token = token
        logger.info("Hugging Face Hub adapter initialised")
    
    @property
    def source_name(self) -> str:
        return "huggingface"
    
    def search_models(self, search_filter: SearchFilter) -> SearchResult:
        """
        Search Hugging Face Hub for models.
        
        Args:
            search_filter: Search and filter parameters
        
        Returns:
            SearchResult with matching models
        """
        try:
            logger.info(f"Searching HF Hub: query='{search_filter.query}', page={search_filter.page}")
            
            # Build search parameters
            search_kwargs = {
                "limit": search_filter.per_page * 2,  # Fetch extra for filtering
                "sort": self._map_sort_field(search_filter.sort_by),
                "direction": -1 if search_filter.sort_order == "desc" else 1,
            }
            
            # Add search query
            if search_filter.query:
                search_kwargs["search"] = search_filter.query
            
            # Add tag filters
            if search_filter.tags:
                search_kwargs["tags"] = search_filter.tags
            
            # Fetch models
            models_info = list(self.api.list_models(**search_kwargs))
            
            logger.info(f"Found {len(models_info)} models from HF Hub")
            
            # Convert to domain models
            models = []
            for info in models_info:
                try:
                    model = self._convert_model_info(info)
                    
                    # Apply GGUF filter if needed
                    if search_filter.has_gguf:
                        # Need to fetch files to check for GGUF
                        model = self._enrich_with_files(model)
                        if not model.has_gguf:
                            continue
                    
                    # Apply other filters
                    if search_filter.matches(model):
                        models.append(model)
                    
                    # Stop if we have enough for this page
                    if len(models) >= search_filter.per_page * search_filter.page:
                        break
                        
                except Exception as e:
                    logger.warning(f"Failed to convert model {getattr(info, 'id', 'unknown')}: {e}")
                    continue
            
            # Paginate results
            start_idx = (search_filter.page - 1) * search_filter.per_page
            end_idx = start_idx + search_filter.per_page
            page_models = models[start_idx:end_idx]
            
            result = SearchResult(
                models=page_models,
                total_count=len(models),  # Approximate
                page=search_filter.page,
                per_page=search_filter.per_page,
                has_next=len(models) > end_idx,
                has_previous=search_filter.page > 1
            )
            
            logger.info(f"Returning page {search_filter.page} with {len(page_models)} models")
            return result
            
        except Exception as e:
            logger.error(f"Search failed: {e}", exc_info=True)
            # Return empty result on error
            return SearchResult(
                models=[],
                total_count=0,
                page=search_filter.page,
                per_page=search_filter.per_page,
                has_next=False,
                has_previous=False
            )
    
    def get_model_details(self, model_id: str) -> Optional[Model]:
        """
        Get detailed information about a specific model.
        
        Args:
            model_id: Model identifier (e.g., "TheBloke/Llama-2-7B-GGUF")
        
        Returns:
            Model with full details including files
        """
        try:
            logger.info(f"Fetching details for model: {model_id}")
            
            # Get model info
            info = self.api.model_info(model_id)
            model = self._convert_model_info(info)
            
            # Enrich with file list
            model = self._enrich_with_files(model)
            
            logger.info(f"Model {model_id} has {len(model.files)} files, {model.gguf_count} GGUF")
            return model
            
        except HfHubHTTPError as e:
            logger.error(f"Failed to fetch model {model_id}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error getting model details: {e}", exc_info=True)
            return None
    
    def get_model_files(self, model_id: str) -> List[ModelFile]:
        """
        Get list of files for a model.
        
        Args:
            model_id: Model identifier
        
        Returns:
            List of ModelFile objects
        """
        try:
            files_info = self.api.list_repo_files(model_id, repo_type="model")
            files = []
            
            for filepath in files_info:
                # Get file metadata
                try:
                    file_url = hf_hub_url(model_id, filepath)
                    # Note: Getting size requires additional API call, skip for now
                    files.append(ModelFile(
                        filename=filepath,
                        size=0,  # Will be enriched later if needed
                        url=file_url
                    ))
                except Exception as e:
                    logger.debug(f"Skipping file {filepath}: {e}")
            
            return files
            
        except Exception as e:
            logger.error(f"Failed to get files for {model_id}: {e}")
            return []
    
    def _convert_model_info(self, info) -> Model:
        """
        Convert HF ModelInfo to domain Model.
        
        Args:
            info: HuggingFace ModelInfo object
        
        Returns:
            Domain Model object
        """
        return Model(
            id=info.id,
            name=info.id.split('/')[-1] if '/' in info.id else info.id,
            author=info.author if hasattr(info, 'author') else info.id.split('/')[0],
            description=getattr(info, 'description', None),
            tags=list(info.tags) if hasattr(info, 'tags') else [],
            licence=getattr(info, 'license', None),
            downloads=getattr(info, 'downloads', 0) or 0,
            likes=getattr(info, 'likes', 0) or 0,
            created_at=getattr(info, 'created_at', None),
            updated_at=getattr(info, 'last_modified', None),
            source=self.source_name
        )
    
    def _enrich_with_files(self, model: Model) -> Model:
        """
        Fetch and add file list to model.
        
        Args:
            model: Model to enrich
        
        Returns:
            Model with files populated
        """
        try:
            files_info = self.api.list_repo_files(model.id, repo_type="model")
            
            # Convert to ModelFile objects with size info
            files = []
            for filepath in files_info:
                # Only include common model file extensions
                if any(filepath.lower().endswith(ext) for ext in 
                       ['.gguf', '.safetensors', '.bin', '.pt', '.pth', '.onnx']):
                    try:
                        file_url = hf_hub_url(model.id, filepath)
                        # Try to get file size from siblings if available
                        size = 0
                        if hasattr(model, '_siblings'):
                            for sibling in model._siblings:
                                if sibling.get('rfilename') == filepath:
                                    size = sibling.get('size', 0)
                                    break
                        
                        files.append(ModelFile(
                            filename=filepath,
                            size=size,
                            url=file_url
                        ))
                    except Exception as e:
                        logger.debug(f"Skipping file {filepath}: {e}")
            
            model.files = files
            
            # Sort files: GGUF first, then by name
            model.files.sort(key=lambda f: (not f.is_gguf, f.filename.lower()))
            
        except Exception as e:
            logger.warning(f"Failed to enrich model {model.id} with files: {e}")
        
        return model
    
    def _map_sort_field(self, sort_by: str) -> str:
        """
        Map domain sort field to HF API field.
        
        Args:
            sort_by: Domain sort field
        
        Returns:
            HF API sort field
        """
        mapping = {
            "downloads": "downloads",
            "likes": "likes",
            "updated": "lastModified",
            "created": "createdAt",
        }
        return mapping.get(sort_by.lower(), "downloads")
