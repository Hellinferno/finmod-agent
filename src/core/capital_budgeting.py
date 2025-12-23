import numpy as np
import numpy_financial as npf
from src.models.project_schemas import ProjectInput

class CapitalBudgetingEngine:
    
    @staticmethod
    def calculate_metrics(project: ProjectInput) -> dict:
        """
        Calculates deterministic metrics: NPV, IRR, Payback, PI.
        """
        # Cash flow stream: [-Initial, CF1, CF2, ...]
        cf_stream = [-project.initial_investment] + project.cash_flows
        cf_array = np.array(cf_stream)
        
        # NPV
        npv = npf.npv(project.discount_rate, cf_array)
        
        # IRR
        try:
            irr = npf.irr(cf_array)
            if np.isnan(irr):
                irr = 0.0
        except:
            irr = 0.0
            
        # Payback Period
        cumulative_cf = np.cumsum(cf_array)
        # Find first index where cumulative >= 0
        # If never positive, payback is undefined (or > lifespan)
        payback_idx = np.where(cumulative_cf >= 0)[0]
        
        if len(payback_idx) > 0:
            # We want exact year. Simple linear interpolation is better but integer year is often accepted MVP.
            # Let's do integer year for safety/simplicity first.
            # Index 0 is Year 0.
            p_year = payback_idx[0]
            # Refinement: Fraction of year
            # Year before recovery: p_year - 1
            # Amount left to recover: abs(cumulative_cf[p_year-1])
            # Cash flow in recovery year: cf_array[p_year]
            if p_year > 0:
                fraction = abs(cumulative_cf[p_year-1]) / cf_array[p_year]
                payback = (p_year - 1) + fraction
            else:
                payback = 0.0 # Instant payback?
        else:
            payback = float('inf') # Never pays back
        
        # Profitability Index (PI) = PV of Future / Initial Investment
        # PV of Future
        future_cfs = np.array(project.cash_flows)
        # Discount factors: 1 / (1+r)^t
        t = np.arange(1, len(future_cfs) + 1)
        pv_future = np.sum(future_cfs / ((1 + project.discount_rate) ** t))
        
        pi = pv_future / project.initial_investment
        
        return {
            "npv": float(npv),
            "irr": float(irr),
            "payback": float(payback),
            "pi": float(pi)
        }

    @staticmethod
    def run_monte_carlo(project: ProjectInput, iterations: int = 5000) -> dict:
        """
        Vectorized Monte Carlo Simulation.
        Output: dict with 'distribution' (list of NPVs) and 'prob_loss' (float).
        """
        np.random.seed(42) # Reproducibility
        
        # Cash Flows: Matrix of shape (iterations, years)
        years = len(project.cash_flows)
        means = np.array(project.cash_flows)
        stds = means * project.volatility
        
        # Generate random CFs
        # shape: (iterations, years)
        # normal(loc, scale, size)
        simulated_cfs = np.random.normal(loc=means, scale=stds, size=(iterations, years))
        
        # Prepend initial investment (constant)
        # shape: (iterations, years+1)
        initial = np.full((iterations, 1), -project.initial_investment)
        full_stream = np.hstack((initial, simulated_cfs))
        
        # Calculate NPV for each row Vectorized
        # NPV = Sum( CF_t / (1+r)^t )
        # t ranges from 0 to years
        t = np.arange(0, years + 1)
        discount_factors = 1 / ((1 + project.discount_rate) ** t)
        
        # Broadcast multiplication: (iterations, years+1) * (years+1,)
        discounted_flows = full_stream * discount_factors
        
        # Sum along axis 1 (years)
        npvs = np.sum(discounted_flows, axis=1)
        
        # Stats
        loss_count = np.sum(npvs < 0)
        prob_loss = loss_count / iterations
        
        return {
            "distribution": npvs.tolist(),
            "prob_loss": float(prob_loss)
        }
