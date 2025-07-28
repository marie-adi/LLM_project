from typing import List

DEEP_KEYWORDS = [
    ### CORE ECONOMIC CONCEPTS ###
    # Inflation
    "inflation", "inflación", "inflation", "inflazione", "инфляция",
    # Fiscal Policy
    "fiscal policy", "política fiscal", "politique budgétaire", "politica fiscale", "бюджетная политика",
    # Monetary Policy
    "monetary policy", "política monetaria", "politique monétaire", "politica monetaria", "денежно-кредитная политика",
    # General Equilibrium
    "general equilibrium", "equilibrio general", "équilibre général", "equilibrio generale", "общее равновесие",
    # Utility Maximization
    "utility maximization", "maximización de utilidad", "maximisation d'utilité", "massimizzazione dell'utilità", "максимизация полезности",
    # Market Failure
    "market failure", "fallo de mercado", "défaillance du marché", "fallimento del mercato", "сбой рынка",
    # Externalities
    "externalities", "externalidades", "externalités", "esternalità", "внешние эффекты",
    # Public Goods
    "public goods", "bienes públicos", "biens publics", "beni pubblici", "общественные блага",
    # Price Signals
    "price signals", "señales de precio", "signaux de prix", "segnali di prezzo", "ценовые сигналы",
    # Asymmetric Info
    "asymmetric information", "información asimétrica", "information asymétrique", "informazione asimmetrica", "асимметричная информация",
    # Moral Hazard
    "moral hazard", "riesgo moral", "aléa moral", "azzardo morale", "моральный риск",
    # Game Theory
    "game theory", "teoría de juegos", "théorie des jeux", "teoria dei giochi", "теория игр",
    # Economic Modeling
    "economic modeling", "modelos económicos", "modélisation économique", "modellazione economica", "экономическое моделирование",

    ### ECONOMIC SCHOOLS OF THOUGHT ###
    "Keynes", "Keynesiano", "Keynésien", "Keynesiano", "Кейнс",
    "Hayek", "Austrian school", "Escuela Austriaca", "École autrichienne", "Scuola austriaca", "Австрийская школа",
    "Neoclassical", "Neoclásico", "Néoclassique", "Neoclassico", "Неоклассическая теория",
    "Post-Keynesian", "Postkeynesiano", "Post-keynésien", "Post-keynesiano", "Посткейнсианство",
    "Classical economics", "economía clásica", "économie classique", "economia classica", "классическая экономика",
    "Chicago school", "Escuela de Chicago", "École de Chicago", "Scuola di Chicago", "Чикагская школа",
    "Marxist economics", "economía marxista", "économie marxiste", "economia marxista", "марксистская экономика",
    "Institutional economics", "economía institucional", "économie institutionnelle", "economia istituzionale", "институциональная экономика",
    "Behavioral economics", "economía conductual", "économie comportementale", "economia comportamentale", "поведенческая экономика",
    "Development economics", "economía del desarrollo", "économie du développement", "economia dello sviluppo", "экономика развития",
    "Ecological economics", "economía ecológica", "économie écologique", "economia ecologica", "экологическая экономика",
    "Feminist economics", "economía feminista", "économie féministe", "economia femminista", "феминистская экономика",

    ### STATE & POLICY ###
    "central planning", "planificación central", "planification centrale", "pianificazione centrale", "централизованное планирование",
    "economic regulation", "regulación económica", "réglementation économique", "regolamentazione economica", "экономическое регулирование",
    "income redistribution", "redistribución del ingreso", "redistribution des revenus", "redistribuzione del reddito", "перераспределение доходов",
    "tax system", "sistema tributario", "système fiscal", "sistema fiscale", "налоговая система",
    "labor market", "mercado laboral", "marché du travail", "mercato del lavoro", "рынок труда",
    "welfare state", "estado de bienestar", "État providence", "stato sociale", "государство благосостояния",
    "public expenditure", "gasto público", "dépenses publiques", "spesa pubblica", "государственные расходы",
    "debt crisis", "crisis de deuda", "crise de la dette", "crisi del debito", "долговой кризис",
    "budget deficit", "déficit fiscal", "déficit budgétaire", "deficit di bilancio", "бюджетный дефицит",
    "shadow economy", "economía informal", "économie informelle", "economia sommersa", "теневая экономика",

    ### MACRO GLOBAL TERMS ###
    "macroeconomic indicators", "indicadores macroeconómicos", "indicateurs macroéconomiques", "indicatori macroeconomici", "макроэкономические показатели",
    "international trade", "comercio internacional", "commerce international", "commercio internazionale", "международная торговля",
    "exchange rates", "tipos de cambio", "taux de change", "tassi di cambio", "обменные курсы",
    "foreign direct investment", "inversión extranjera directa", "investissement direct étranger", "investimenti diretti esteri", "прямые иностранные инвестиции",
    "capital flows", "flujos de capital", "flux de capitaux", "flussi di capitale", "движение капитала",
    "globalization", "globalización", "mondialisation", "globalizzazione", "глобализация"
]


def is_deep_query(query: str, threshold: int = 2) -> bool:
    """
    Determines if a query is 'deep' enough to require arXiv PDF enrichment.
    
    Args:
        query (str): User's question or prompt.
        threshold (int): Minimum keyword hits to trigger depth. Default is 2.
    
    Returns:
        bool: True if query is deep, False otherwise.
    """
    query_lower = query.lower()
    matches = [kw for kw in DEEP_KEYWORDS if kw.lower() in query_lower]
    
    # Optionally include a length heuristic
    long_query = len(query.split()) > 12
    
    return len(matches) >= threshold or long_query
