from chat.intelligent_search import IntelligentSearch

class LitigationChat:
    """Chat with intelligent progressive search"""
    
    def __init__(self, orchestrator):
        self.orchestrator = orchestrator
        self.intelligent_search = IntelligentSearch(orchestrator)
        self.conversation_history = []
    
    def query(self, user_question: str) -> str:
        """
        Process user query with intelligent search
        
        Examples:
        - "Documents about Taiga" → Fast search only
        - "Show me full EMAIL-2847" → Loads complete PDF
        - "Detailed analysis of SPA breach" → Loads top 3 full PDFs
        """
        
        # Detect if user wants deep analysis
        deep_indicators = ['full', 'complete', 'detailed', 'analyze']
        allow_deep = any(term in user_question.lower() 
                        for term in deep_indicators)
        
        # Intelligent search (may load full PDFs)
        results = self.intelligent_search.search(
            query=user_question,
            top_k=20,
            allow_deep_search=allow_deep
        )
        
        # Check if any full PDFs were loaded
        full_pdfs = [d for d in results if d.get('full_pdf_loaded')]
        
        if full_pdfs:
            print(f"\n   📄 Loaded {len(full_pdfs)} complete PDFs for deep analysis")
        
        # Get knowledge graph context
        kg_context = self.orchestrator.knowledge_graph.get_context_for_phase('query')
        
        # Build prompt for Claude
        prompt = self._build_analysis_prompt(
            question=user_question,
            documents=results[:10],  # Top 10 (some may be full PDFs)
            context=kg_context
        )
        
        # Call Claude
        response, metadata = self.orchestrator.api_client.call_claude(
            prompt=prompt,
            task_type='chat_query',
            phase='chat'
        )
        
        # Track in history
        self._update_history(user_question, response, results, metadata)
        
        return self._format_response(response, results)