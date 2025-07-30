from typing import Dict, Any, List
from server.tools.yahoo_data import YahooFetcher  # Yahoo Tickers
from server.tools.pdf_fetcher import PDFRetriever # RAG
from server.services.lm_engine import LMEngine    # Connection to GROQ
from loguru import logger
from datetime import datetime

class FinanceAgent:
    def __init__(self, model_name: str = "llama-3.1-8b-instant"):
        """
        Initialize financial analysis agent with specified LLM model.
        Available models:
        - llama-3.1-8b-instant (default)
        - llama-3.3-70b-versatile
        - gemma2-9b-it
        """
        self.yahoo = YahooFetcher()
        self.pdfs = PDFRetriever()
        self.lm = LMEngine(model_name)
        self.current_model = model_name  # Track active model
        self.bias_log: List[Dict] = []
        
        self.debiasing_prompt = """
        You are a financial assistant. Follow these rules:
        1. Present balanced perspectives
        2. Disclose data limitations
        3. Avoid stereotypes about regions/markets
        4. Highlight opposing views when available
        5. Use neutral language
        """
        
        self.bias_keywords = {
            "regional": ["third world", "developed", "backward"],
            "gender": ["he should", "female CEO"],
            "absolute": ["always", "never", "must"]
        }

    async def run(self, request) -> Dict[str, Any]:
        """
        Process financial query using selected model and strategy.
        Returns dict with:
        - output: Generated response
        - sources: List of data sources used
        - disclosures: Any bias disclosures
        - model_used: Which model generated the response
        """
        context = {
            "platform": request.platform,
            "audience": request.audience,
            "region": self._neutralize_region(request.region),
            "sources": [],
            "disclosures": []
        }
        
        try:
            # 1. Input validation
            self._detect_input_bias(request.prompt)
            
            # 2. Determine processing strategy
            strategy = await self._determine_strategy(request.prompt)
            logger.info(f"Model: {self.current_model} | Strategy: {strategy}")
            
            # 3. Execute strategy
            result = await self._execute_strategy(strategy, request.prompt, context)
            
            # 4. Apply bias mitigation
            processed_output = self._scan_output_bias(result, context)
            
            return {
                "output": processed_output,
                "sources": context["sources"],
                "disclosures": context["disclosures"],
                "model_used": self.current_model
            }
            
        except Exception as e:
            logger.error(f"Processing failed: {str(e)}")
            return await self._fallback_response(request.prompt, context)

    async def _execute_strategy(self, strategy: str, prompt: str, context: Dict) -> str:
        """Execute the selected processing strategy"""
        strategies = {
            "yahoo": self._yahoo_strategy,
            "pdf": self._pdf_strategy,
            "combined": self._combined_strategy,
            "direct": self._direct_strategy
        }
        return await strategies[strategy](prompt, context)

    async def _yahoo_strategy(self, prompt: str, context: Dict) -> str:
        """Process using only market data"""
        data = self.yahoo.fetch(prompt)
        context["sources"].append("Yahoo Finance")
        
        if not self._validate_source(data, "western"):
            context["disclosures"].append("Market data may be Western-focused")
            
        return await self._debiased_query(
            f"Market Data: {data}\nQuestion: {prompt}",
            context
        )

    async def _pdf_strategy(self, prompt: str, context: Dict) -> str:
        """Process using only document retrieval"""
        docs = self.pdfs.search(prompt)
        context["sources"].extend([doc.metadata.get("source", "PDF") for doc in docs])
        
        if len(docs) < 3:
            context["disclosures"].append("Limited document sources available")
            
        return await self._debiased_query(
            f"Documents: {' | '.join(doc.page_content[:200] for doc in docs)}\nQuestion: {prompt}",
            context
        )

    async def _combined_strategy(self, prompt: str, context: Dict) -> str:
        """Process using both market data and documents"""
        yahoo_data = self.yahoo.fetch(prompt)
        docs = self.pdfs.search(prompt)
        
        context["sources"].extend([
            "Yahoo Finance",
            *[doc.metadata.get("source", "PDF") for doc in docs]
        ])
        
        disclosures = []
        if not self._validate_source(yahoo_data, "diverse"):
            disclosures.append("Market data may lack diversity")
        if len(docs) < 2:
            disclosures.append("Limited supporting documents")
            
        context["disclosures"].extend(disclosures)
        
        return await self._debiased_query(
            f"Market Data: {yahoo_data}\nDocuments: {' | '.join(doc.page_content[:200] for doc in docs)}\nQuestion: {prompt}",
            context
        )

    async def _direct_strategy(self, prompt: str, context: Dict) -> str:
        """Process using only the LLM"""
        context["disclosures"].append("No external data sources used")
        return await self._debiased_query(prompt, context)

    async def _debiased_query(self, prompt: str, context: Dict) -> str:
        """Generate response with bias mitigation"""
        full_prompt = f"""
        {self.debiasing_prompt}
        
        Context: {context}
        Additional Data: {prompt}
        
        Required Format:
        1. Balanced perspective
        2. Source disclosures
        3. Regional neutrality
        4. Multiple viewpoints if possible
        """
        return await self.lm.ask(full_prompt)

    def _scan_output_bias(self, response: str, context: Dict) -> str:
        """Detect and mitigate biases in generated text"""
        for category, terms in self.bias_keywords.items():
            for term in terms:
                if term in response.lower():
                    context["disclosures"].append(
                        f"Mitigated potential {category} bias"
                    )
                    self._log_bias(category, term, response)
                    response = response.replace(term, self._neutral_term(term))
        return response

    def _neutral_term(self, term: str) -> str:
        """Replace biased terms with neutral alternatives"""
        neutral_map = {
            "third world": "developing",
            "developed": "higher-income",
            "backward": "different",
            "always": "often",
            "never": "rarely",
            "must": "may consider"
        }
        return neutral_map.get(term.lower(), term)

    def _neutralize_region(self, region: str) -> str:
        """Remove potentially biased regional descriptors"""
        return region.replace("(Emerging)", "").replace("(Developed)", "").strip()

    def _validate_source(self, data: str, check_type: str) -> bool:
        """Validate data source diversity"""
        if check_type == "western":
            return any(market in data for market in ["Asia", "Latin America", "Africa"])
        return True

    def _detect_input_bias(self, prompt: str):
        """Detect biased language in user input"""
        for category, terms in self.bias_keywords.items():
            found = [term for term in terms if term in prompt.lower()]
            if found:
                self._log_bias(category, ", ".join(found), prompt)

    def _log_bias(self, category: str, evidence: str, context: str):
        """Record bias incidents"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "category": category,
            "evidence": evidence,
            "context": context[:200] + "..." if len(context) > 200 else context
        }
        self.bias_log.append(entry)
        logger.warning(f"Bias detected: {category} - {evidence}")

    async def _fallback_response(self, prompt: str, context: Dict) -> Dict:
        """Generate fallback response when processing fails"""
        context["disclosures"].append("System encountered processing limitations")
        return {
            "output": "I'm unable to provide a fully vetted response at this time. Please consult multiple sources for important financial decisions.",
            "sources": [],
            "disclosures": context["disclosures"],
            "model_used": self.current_model
        }

    async def _determine_strategy(self, prompt: str) -> str:
        """Auto-select processing strategy based on prompt content"""
        prompt_lower = prompt.lower()
        yahoo_triggers = {
            'price', 'ticker', 'quote', 'market', 
            'financial', 'stock', 'exchange'
        }
        pdf_triggers = {
            'report', 'analysis', 'research',
            'document', 'filing', 'statement', 'white paper'
        }
        
        yahoo_score = sum(1 for term in yahoo_triggers if term in prompt_lower)
        pdf_score = sum(1 for term in pdf_triggers if term in prompt_lower)
        
        if yahoo_score > 1 and pdf_score > 1:
            return "combined"
        elif yahoo_score > 0:
            return "yahoo"
        elif pdf_score > 0:
            return "pdf"
        return "direct"