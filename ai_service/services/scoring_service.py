from models.extraction import TransactionExtraction

class ScoringService:
    @staticmethod
    def calculate_confidence(extraction: TransactionExtraction) -> float:
        """
        Calculates the Aggregate Confidence Score (0.0 to 1.0) based on SAD-04 rules.
        """
        score = 0.0
        
        # Entity Match (Weight 0.3)
        if extraction.intent in ['transfer', 'income', 'capital_injection'] and not extraction.entity:
            # Transfers and some incomes (like capital injections) don't strictly need an entity
            score += 0.3
        elif extraction.entity:
            if extraction.entity.id:
                score += 0.3  # Exact UUID match
            elif not extraction.entity.is_new:
                score += 0.24 # Fuzzy match
            else:
                score += 0.18 # New entity
        
        # Category Match (Weight 0.3)
        # We consider a successful category match if at least one line item has a valid account_id
        if any(line.account_id for line in extraction.line_items):
            score += 0.3 # Exact match
            
        # Amount Extraction (Weight 0.3)
        if extraction.total_amount is not None and extraction.total_amount > 0:
            score += 0.3
            
        # Channel Extraction (Weight 0.1)
        if extraction.payment_channel:
            score += 0.1
            
        return round(score, 2)

    @staticmethod
    def gate_decision(confidence: float) -> str:
        """
        Determines the Confidence Gate routing based on score thresholds.
        
        Returns:
            "auto_approve" if confidence >= 0.95
            "pending_confirmation" if confidence >= 0.85
            "requires_clarification" if confidence < 0.85
        """
        if confidence >= 0.95:
            return "auto_approve"
        elif confidence >= 0.85:
            return "pending_confirmation"
        else:
            return "requires_clarification"
