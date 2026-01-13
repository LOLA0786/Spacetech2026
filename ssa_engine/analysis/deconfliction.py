class ManeuverDeconflictor:
    def __init__(self, propagator, conjunction_engine):
        self.propagator = propagator
        self.conjunction_engine = conjunction_engine

    def is_maneuver_safe(self, state, burn_dv, debris_catalog, duration_secs=3600):
        """
        Screens the post-burn trajectory for new conjunctions.
        """
        # 1. Apply the proposed burn
        from ssa_engine.physics.execution import ManeuverExecutor
        new_vel = ManeuverExecutor.apply_burn(state['velocity'], burn_dv)
        
        # 2. Propagate along the new path
        future_state = self.propagator.propagate(state['position'], new_velocity, duration_secs)
        
        # 3. Check for secondary conjunctions
        new_risks = self.conjunction_engine.check_close_approach(future_state, debris_catalog)
        
        if new_risks:
            return False, new_risks
        return True, []
