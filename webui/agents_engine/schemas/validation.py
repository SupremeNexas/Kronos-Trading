# Schema validation for structured outputs

def validate_technical_output(data: dict) -> bool:
    """Validate Technical Analyst output format."""
    required = ["agent", "assessment", "confidence", "evidence", "risks", "important_levels", "kronos_alignment", "summary"]
    for field in required:
        if field not in data:
            raise KeyError(f"Missing required field in Technical Analyst output: {field}")

    if data["agent"] != "technical":
        raise ValueError(f"Agent name must be 'technical', got {data['agent']}")

    assessment = data["assessment"].upper()
    if assessment not in ["BULLISH", "BEARISH", "NEUTRAL"]:
        raise ValueError(f"Invalid assessment: {assessment}")

    if not isinstance(data["confidence"], (int, float)):
        raise TypeError("confidence must be a number")

    if not isinstance(data["evidence"], list) or not isinstance(data["risks"], list):
        raise TypeError("evidence and risks must be lists")

    return True

def validate_fundamental_output(data: dict) -> bool:
    """Validate Fundamental Analyst output format."""
    required = ["agent", "assessment", "confidence", "metrics", "summary"]
    for field in required:
        if field not in data:
            raise KeyError(f"Missing required field in Fundamental Analyst output: {field}")

    if data["agent"] != "fundamental":
        raise ValueError(f"Agent name must be 'fundamental'")

    assessment = data["assessment"].upper()
    if assessment not in ["BULLISH", "BEARISH", "NEUTRAL", "DATA_UNAVAILABLE"]:
        raise ValueError(f"Invalid fundamental assessment: {assessment}")

    return True

def validate_news_output(data: dict) -> bool:
    """Validate News Analyst output format."""
    required = ["agent", "sentiment", "confidence", "news_evaluated", "summary"]
    for field in required:
        if field not in data:
            raise KeyError(f"Missing required field in News Analyst output: {field}")
    return True

def validate_sentiment_output(data: dict) -> bool:
    """Validate Sentiment Analyst output format."""
    required = ["agent", "sentiment", "confidence", "evidence", "risks"]
    for field in required:
        if field not in data:
            raise KeyError(f"Missing required field in Sentiment Analyst output: {field}")

    sentiment = data["sentiment"].upper()
    if sentiment not in ["POSITIVE", "NEGATIVE", "NEUTRAL", "MIXED"]:
        raise ValueError(f"Invalid sentiment bias: {sentiment}")
    return True

def validate_quant_output(data: dict) -> bool:
    """Validate Quant Analyst output format."""
    required = ["agent", "assessment", "metrics_evaluated", "summary"]
    for field in required:
        if field not in data:
            raise KeyError(f"Missing required field in Quant Analyst output: {field}")
    return True

def validate_macro_output(data: dict) -> bool:
    """Validate Macro Analyst output format."""
    required = ["agent", "assessment", "regime", "summary"]
    for field in required:
        if field not in data:
            raise KeyError(f"Missing required field in Macro Analyst output: {field}")
    return True

def validate_debate_output(data: dict) -> bool:
    """Validate Bull/Bear Debate output format."""
    required = ["bull_case", "bear_case", "key_disagreement", "unresolved_risks", "debate_conclusion"]
    for field in required:
        if field not in data:
            raise KeyError(f"Missing required field in Debate output: {field}")
    return True

def validate_trader_output(data: dict) -> bool:
    """Validate Trader Agent output format."""
    required = ["action", "confidence", "thesis", "entry", "take_profit", "stop_loss", "time_horizon", "key_catalysts", "invalidation_conditions"]
    for field in required:
        if field not in data:
            raise KeyError(f"Missing required field in Trader output: {field}")

    action = data["action"].upper()
    if action not in ["BUY", "SELL", "HOLD", "NO_TRADE"]:
        raise ValueError(f"Invalid trader action: {action}")

    if not isinstance(data["entry"], dict) or "min" not in data["entry"] or "max" not in data["entry"]:
        raise TypeError("entry must be a dictionary with 'min' and 'max' pricing keys")

    return True

def validate_portfolio_output(data: dict) -> bool:
    """Validate Portfolio Manager output format."""
    required = ["symbol", "action", "confidence", "thesis", "allocation", "entry", "stop_loss", "take_profit", "risk_level", "reasons", "risks"]
    for field in required:
        if field not in data:
            raise KeyError(f"Missing required field in Portfolio output: {field}")

    action = data["action"].upper()
    if action not in ["BUY", "SELL", "HOLD", "NO_TRADE"]:
        raise ValueError(f"Invalid portfolio manager action: {action}")

    risk_level = data["risk_level"].upper()
    if risk_level not in ["LOW", "MEDIUM", "HIGH", "EXTREME"]:
        raise ValueError(f"Invalid portfolio risk level: {risk_level}")

    return True
