class RiskManager:
    def __init__(self):
        # Simple fixed risk approach
        self.symbol = "BNB/USDT"  # Symbol moved here
        self.linear = self.symbol.replace('/', '')
        
        # Fixed risk per trade
        self.fixed_risk_usd = 100.0         # Fixed $100 risk per trade
        self.stop_loss_pct = 0.015          # 1.5% stop loss (fallback only)
        
        # Profit management (simple position P&L)
        self.profit_lock_threshold = 3.0    # 3% position profit to activate trailing
        self.trailing_stop_pct = 0.008      # 0.8% trailing stop
        self.take_profit_pct = 0.06         # 6% take profit (4:1 RR)
        print("✅ Structure-Based Stop Loss")
    
    def calculate_position_size(self, balance, entry_price, structure_stop=None):
        """Calculate position size based on actual stop distance"""
        if structure_stop:
            # Use actual structure stop distance
            stop_distance = abs(entry_price - structure_stop)
        else:
            # Fallback to fixed percentage
            stop_distance = entry_price * self.stop_loss_pct
        
        # Calculate position size to risk exactly $100
        position_size_tokens = self.fixed_risk_usd / stop_distance
        
        # Position value in USD
        position_value = position_size_tokens * entry_price
        
        # Don't risk more than 10% of balance
        max_position_value = balance * 0.10
        if position_value > max_position_value:
            position_size_tokens = max_position_value / entry_price
            actual_risk = position_size_tokens * stop_distance
        else:
            actual_risk = self.fixed_risk_usd
            
        return position_size_tokens
    
    def get_stop_loss_price(self, entry_price, side='long', structure_stop=None):
        """Get stop loss price - structure-based if available"""
        if structure_stop:
            return structure_stop
        
        # Fallback to fixed percentage
        if side == 'long':
            return entry_price * (1 - self.stop_loss_pct)
        else:
            return entry_price * (1 + self.stop_loss_pct)
    
    def get_take_profit_price(self, entry_price, side='long', structure_stop=None):
        """Get take profit price based on actual risk"""
        if structure_stop:
            # Calculate actual risk distance
            risk_distance = abs(entry_price - structure_stop)
            # 4:1 reward ratio
            reward_distance = risk_distance * 4
            
            if side == 'long':
                return entry_price + reward_distance
            else:
                return entry_price - reward_distance
        
        # Fallback to fixed percentage
        if side == 'long':
            return entry_price * (1 + self.take_profit_pct)
        else:
            return entry_price * (1 - self.take_profit_pct)
    
    def should_activate_profit_lock(self, entry_price, current_price, side='long'):
        """Check if should activate profit lock"""
        if side == 'long':
            profit_pct = ((current_price - entry_price) / entry_price) * 100
        else:
            profit_pct = ((entry_price - current_price) / entry_price) * 100
            
        return profit_pct >= self.profit_lock_threshold
    
    def get_trailing_stop_price(self, current_price, side='long'):
        """Get trailing stop price"""
        if side == 'long':
            return current_price * (1 - self.trailing_stop_pct)
        else:
            return current_price * (1 + self.trailing_stop_pct)
    
    def get_risk_summary(self, balance, entry_price, structure_stop=None):
        """Get risk summary with structure stops"""
        position_size = self.calculate_position_size(balance, entry_price, structure_stop)
        position_value = position_size * entry_price
        
        if structure_stop:
            actual_risk = position_size * abs(entry_price - structure_stop)
            stop_distance_pct = (abs(entry_price - structure_stop) / entry_price) * 100
        else:
            actual_risk = self.fixed_risk_usd
            stop_distance_pct = self.stop_loss_pct * 100
        
        risk_pct = (actual_risk / balance) * 100
        
        return {
            'symbol': self.symbol,
            'fixed_risk_usd': self.fixed_risk_usd,
            'actual_risk_usd': actual_risk,
            'risk_pct': risk_pct,
            'position_size': position_size,
            'position_value': position_value,
            'stop_distance_pct': stop_distance_pct,
            'structure_based': structure_stop is not None,
            'structure_stop': structure_stop
        }