from typing import Dict, Any, List
from server.tools.yahoo_data import YahooFetcher
from server.services.lm_engine import LMEngine
from server.database.chroma_db import query_chroma_db
from loguru import logger
from datetime import datetime
import json
import re

class FinanceAgent:
    def __init__(self, model_name: str = "llama-3.1-8b-instant"):
        self.yahoo = YahooFetcher()
        self.lm = LMEngine(model_name)
        self.current_model = model_name
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
        self.doc_triggers = {
            "report", "analysis", "research", "document", "filing",
            "statement", "white paper", "working paper", "appendix", "review",
            "case study", "policy paper", "position paper", "journal article",
            "bibliography", "footnote", "extract", "compendium"
        }

        self.author_patterns = [
            r"jes(u|ú)s huerta de soto",
            r"ludwig (von )?mises",
            r"friedrich (von )?hayek",
            r"carl menger",
            r"murray rothbard",
            r"hans(-| )hermann hoppe",
            r"peter schiff",
            r"eugen böhm(-| )bawerk",
            r"israel kirzner",
            r"mark thornton",
            r"thomas piketty",
            r"milton friedman",
            r"paul krugman",
            r"kenneth arrow",
            r"amartya sen",
            r"joseph stiglitz",
            r"elinor ostrom",
            r"angus deaton",
            r"robert lucas",
            r"james tobin",
            r"gary becker",
            r"george akerlof",
            r"jean tirole",
            r"esther duflo",
            r"abhijit banerjee",
            r"michael kremer"
        ]
    async def run(self, request) -> Dict[str, Any]:
        context = {
            "platform": request.platform,
            "audience": request.audience,
            "region": self._neutralize_region(request.region),
            "sources": [],
            "disclosures": []
        }

        try:
            self._detect_input_bias(request.prompt)
            strategy = await self._determine_strategy(request.prompt)
            logger.info(f"Model: {self.current_model} | Strategy: {strategy}")
            result = await self._execute_strategy(strategy, request.prompt, context)
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
        strategies = {
            "yahoo": self._yahoo_strategy,
            "simple_rag": self._simple_rag_strategy,
            "combined": self._combined_strategy,
            "direct": self._direct_strategy
        }
        return await strategies[strategy](prompt, context)

    async def _yahoo_strategy(self, prompt: str, context: Dict) -> str:
        data = self.yahoo.fetch(prompt)
        context["sources"].append("Yahoo Finance")

        if not self._validate_source(data, "western"):
            context["disclosures"].append("Market data may be Western-focused")

        return await self._debiased_query(
            f"Market Data: {data}\nQuestion: {prompt}", context
        )

    async def _simple_rag_strategy(self, prompt: str, context: Dict) -> str:
        docs = query_chroma_db(prompt)
        context["sources"].extend([doc.metadata.get("source", "Chroma") for doc in docs])

        if len(docs) < 3:
            context["disclosures"].append("Limited document sources available")

        return await self._debiased_query(
            f"Documents: {' | '.join(doc.page_content[:200] for doc in docs)}\nQuestion: {prompt}",
            context
        )

    async def _combined_strategy(self, prompt: str, context: Dict) -> str:
        yahoo_data = self.yahoo.fetch(prompt)
        docs = query_chroma_db(prompt)

        context["sources"].extend([
            "Yahoo Finance",
            *[doc.metadata.get("source", "Chroma") for doc in docs]
        ])

        if len(docs) < 2:
            context["disclosures"].append("Limited supporting documents")

        return await self._debiased_query(
            f"Market Data: {yahoo_data}\nDocuments: {' | '.join(doc.page_content[:200] for doc in docs)}\nQuestion: {prompt}",
            context
        )

    async def _direct_strategy(self, prompt: str, context: Dict) -> str:
        context["disclosures"].append("No external data sources used")
        return await self._debiased_query(prompt, context)

    async def _debiased_query(self, prompt: str, context: Dict) -> str:
        context_str = json.dumps(context, indent=2)

        full_prompt = f"""
        {self.debiasing_prompt}

        Context:
        {context_str}

        Additional Data:
        {prompt}

        Required Format:
        1. Balanced perspective
        2. Source disclosures
        3. Regional neutrality
        4. Multiple viewpoints if possible
        """
        return await self.lm.ask(full_prompt)

    def _scan_output_bias(self, response: str, context: Dict) -> str:
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
        return region.replace("(Emerging)", "").replace("(Developed)", "").strip()

    def _validate_source(self, data: str, check_type: str) -> bool:
        if check_type == "western":
            return any(market in data for market in ["Asia", "Latin America", "Africa"])
        return True

    def _detect_input_bias(self, prompt: str):
        for category, terms in self.bias_keywords.items():
            found = [term for term in terms if term in prompt.lower()]
            if found:
                self._log_bias(category, ", ".join(found), prompt)

    def _log_bias(self, category: str, evidence: str, context: str):
        entry = {
            "timestamp": datetime.now().isoformat(),
            "category": category,
            "evidence": evidence,
            "context": context[:200] + "..." if len(context) > 200 else context
        }
        self.bias_log.append(entry)
        logger.warning(f"Bias detected: {category} - {evidence}")

    async def _fallback_response(self, prompt: str, context: Dict) -> Dict:
        context["disclosures"].append("System encountered processing limitations")
        return {
            "output": "I'm unable to provide a fully vetted response at this time. Please consult multiple sources for important financial decisions.",
            "sources": [],
            "disclosures": context["disclosures"],
            "model_used": self.current_model
        }

    async def _determine_strategy(self, prompt: str) -> str:
        prompt_lower = prompt.lower()
        yahoo_triggers = {
            'price', 'ticker', 'quote', 'market',
            'financial', 'stock', 'exchange', 'index'
        }
        

        yahoo_score = sum(1 for term in yahoo_triggers if term in prompt_lower)
        doc_score = sum(1 for term in self.doc_triggers if term in prompt_lower)

        # Regex for author or academic names
        for pattern in self.author_patterns:
            if re.search(pattern, prompt_lower):
                doc_score += 1

        if yahoo_score > 1 and doc_score > 1:
            return "combined"
        elif yahoo_score > 0:
            return "yahoo"
        elif doc_score > 0:
            return "simple_rag"  
        return "direct"
